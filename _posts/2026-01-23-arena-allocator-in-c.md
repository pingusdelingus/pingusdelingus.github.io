---
layout: post
Title: arena allocator in C
date: 2026-01-23 02:59 +0400
tags: [c, dynamic memory]
math: true
author: <007
pin: true
description: why & how to implement an Arena Allocator (in C!)
mermaid: true
toc:true

comments: false


---


> BE CAREFUL!
{: .prompt-danger }

my first introduction to memory management in C was in an example as follows:

```c
struct Vector {
  float x;
  float y;
}

void do_something_to_vector(struct Vector*v )
{
 v->x += 1;
 v->y += 1;
}

#include <stdlib.h>

int main(void)
{
  // requesting the OS for ~8 bytes to be allocated on the heap
  struct Vector* vec1_ptr = (struct Vector*) malloc(sizeof(struct Vector));
  if (vec1_ptr == NULL){
    perror("malloc failed!");
  }

  vec1_ptr->x 2.3;
  vec1_ptr->y 9.5;
  
  do_something_to_vector(vec1_ptr);

    
  free(vec1_ptr);
}
```

while this example illustrates the simplicity of the malloc/free interfaces, it implicitly
asserts that 1 (dynamically allocated )struct == 1 malloc. 

this paradigm works fine in small deployments and you can even get away with it in some production codebaases. 
its one fatal flaw, as with anything in C, is performance. 

iterated individual mallocs create enrounmous performance bottlenecks.
malloc in itself performs system calls to OS interfaces which can slow down execution to a halt.

of course, as a snot-nosed undergrad, i was oblivious to this fact until i began writing larger and larger 
pieces of (spaghetti) code and began profiling.

coincidentally, a few days after this, i came across a video by magicalbat which directly addressed this sort of issue

{% include embed/youtube.html id='{jgiMagdjA1s}' %}


i then fell down the rabbit hole of arena allocators and have been trying to implement one for the past week now. 

i thought i'd share my original implementations, thoughts, concerns and improvements.


i started by looking at [this](https://www.rfleury.com/p/untangling-lifetimes-the-arena-allocator) article for an interface / header file to get me going. 

```c
// create or destroy a 'stack' - an "arena"
Arena *ArenaAlloc(void);
void ArenaRelease(Arena *arena);

// push some bytes onto the 'stack' - the way to allocate
void *ArenaPush(Arena *arena, U64 size);
void *ArenaPushZero(Arena *arena, U64 size);

// pop some bytes off the 'stack' - the way to free
void ArenaPop(Arena *arena, U64 size);

// get the # of bytes currently allocated.
U64 ArenaGetPos(Arena *arena);

// also some useful popping helpers:
void ArenaSetPosBack(Arena *arena, U64 pos);
void ArenaClear(Arena *arena);
```


from here, i went on to implement the constructor as follows:


```c
static const i64 INITIAL_SIZE = 500; // 500 bytes

Arena* ArenaAlloc(void)
{
  Arena* arena = (Arena*) malloc(sizeof(Arena));  
  if (arena == NULL){
    perror("malloc failed!");
  }

  arena->buffer = (char*) malloc(INITIAL_SIZE);
  if (arena->buffer == NULL){
    perror("malloc failed!");
  }

  arena->max_capacity = INITIAL_SIZE; 
  arena->ptr = 0; // point at first index !

  return arena; // will not get deleted after scope ends
}// end of ArenaAlloc (constructor)

```

note that we don't actually have to use malloc here. 

it would be acceptable (& possibly more desireable ) to shoot the middleman and use the OS specific system call instead.
either mmap or virtualalloc for unix or windows respectively.


after this, we of course implement a desctructor to respect lifetimes of these struct's

```c


void ReleaseArena(Arena * a)
{
  // free buff
  free(a->buffer);

  // free arena itself
  free(a);
}// end of ReleaseArena (~destructor)

```


just a standard free. again, we could of course use munmap if we used sys calls here.

now, we get to the meat & potatoes with my 1st push implementation


```c

void* ArenaPush(Arena* arena, u64 size)
{
  u64 req_plus_used = size + arena->ptr; 
  if (req_plus_used > arena->max_capacity){
    perror("trying to request more than available");
    return NULL;
  }

  char* current_ptr = &(arena->buffer[arena->ptr]); // return this in a bit
  arena->ptr += size;
  return current_ptr; 
}// end of ArenaPush

```

first, we make a few sanity checks, then return a generic pointer to a
buffer of memory that was allocated in the constructor. This aims to reduce the time complexity of allocating 
to ~ O(1) as we are just computing pointer arithmetic.

of course, there is no support for when you try to push to a full arena, which is what i tried to tackle on my 2nd try.


for my pop, i tried to imitate the push logic in reverse

```c

void ArenaPop(Arena* arena, u64 size)
{
  u64 used_minus_size = arena->ptr - size;
  
  u64 delete_size = size;

  if (used_minus_size < 0){
    delete_size = arena->ptr;
  }

  u64 stop_index = arena->ptr - delete_size;
  for (u64 i = arena->ptr; i >= stop_index; i++){
      arena->buffer[i] = '\0';
  } 
  arena->ptr -= delete_size;
  return; 
}// end of ArenaPop
```

again, pretty standard, using dummy checks & zero'ing 'released' memory


this implementation does leave a lot to be desired. mostly the issue not being able to push when the arena is near full.


my second iteration had a slight problem. 

see if you can find it.

> THIS IS CODE IS UNSAFE AND NOT WORKING!
{: .prompt-danger }


```c
void* ArenaPush(Arena* arena, i64 s)
{
  i64 size = s;
  if (size % ALIGNMENT_BYTES != 0){
    size = (size) + (ALIGNMENT_BYTES - (size % ALIGNMENT_BYTES) );
  }

  i64 req_plus_used = size + arena->ptr; 
  if (req_plus_used > arena->max_capacity){
    *arena = ArenaRealloc(arena);
  }

  char* current_ptr = &(arena->buffer[arena->ptr]); // return this in a bit
  arena->ptr += size;
  return current_ptr; 
}// end of ArenaPush


Arena ArenaRealloc(Arena* prev)
{
  Arena out;
  i64 size = a->max_capacity;
  
  char* new_buff = (char* ) realloc (a->buffer, 2 * size);
  if (new_buff == NULL){
    return NULL;
  }
  out.max_capacity *= 2;
  
  out.buffer = new_buff;

  return out;
}// end of ArenaRealloc

```
this code has a major flaw.

i made the naive assumption that rellaoc works in place, when it in fact does not.

that is, realloc maintains no guarantee that realloc'd memory will stay in the same location.
it is in fact, quite common to have realloc allocate a larger buffer elsewhere, and copy all previous data to the new location.


at this point, i went to a whiteboard and began plotting out other architectures to address this issue.

i found that a simple workaround would be to implement arenas as a doubly linked list.
this does add some additional complexity, but i think the functionality is worth it.


this endeavor required a new headerfile...

```c

typedef struct ArenaBlock {
  struct ArenaBlock* next;
  struct ArenaBlock* prev;
  char* buffer;
  i64 max_capacity;
  i64 ptr;
  b8 isFull;
} ArenaBlock;


ArenaBlock* AllocArenaBlock(void );// constructor 
void ReleaseArenaBlocks(ArenaBlock * a); // ~destructor
void* ArenaBlockPush(ArenaBlock* arena, i64 size, b8 doSizeCheck);
void* ArenaBlockPushZeroes(ArenaBlock* arena, i64 size, b8 doSizeCheck);
void ArenaBlockPop(ArenaBlock* arena, i64 size);
i64 GetArenaBlockSize(ArenaBlock* arena);


// ---------------------------------------------------------------------------
typedef struct{
  ArenaBlock* current;
  ArenaBlock* genesis;
} Arena;

Arena* ArenaConstruct(void);
void ArenaDestruct(Arena* a);

void* ArenaPush(Arena* a, i64 size);
void* ArenaPushZeroes(Arena* a, i64 size);

void ArenaPop(Arena* a, i64 size);
i64 GetArenaSize(Arena* a);

```



