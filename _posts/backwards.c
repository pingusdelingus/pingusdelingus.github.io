#include <stdio.h>

int main(void)
{

  int nums[] = {1,40,3,5};
  
  int index_two = 1;

  int second_num = nums[index_two];

  int other_second_num = index_two[nums];


  printf("Second num is : %d\n", second_num);
  printf("Other second num is : %d\n", other_second_num);

  return 0;
}// end of main
