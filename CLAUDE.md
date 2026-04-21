# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jekyll-based static blog site using the [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme (~7.3), hosted on GitHub Pages at https://pingusdelingus.github.io.

## Commands

```bash
./tools/run.sh          # Start dev server with live reload
./tools/run.sh -p       # Run in production mode
./tools/test.sh         # Build and run html-proofer link tests
```

Ruby version is pinned to 3.1.1 (`.ruby-version`). Install dependencies with `bundle install`.

## Architecture

- **`_posts/`** — Blog posts as Markdown files named `YYYY-MM-DD-title.md`
- **`_tabs/`** — Static pages rendered as sidebar tabs (about, archives, categories, tags)
- **`_data/`** — YAML configs for authors, contact links, and social sharing
- **`_plugins/`** — Custom Jekyll plugins (e.g., `posts-lastmod-hook.rb` for last-modified tracking)
- **`assets/lib/`** — Git submodule for Chirpy's static assets; do not edit directly
- **`_config.yml`** — Main config: site metadata, analytics (all disabled by default), comments (disabled), PWA, SASS, pagination, and permalink structure

## Post Front Matter

Posts support these Chirpy-specific fields:

```yaml
---
title: ""
date: YYYY-MM-DD HH:MM:SS +/-TTTT
categories: [Category, Subcategory]
tags: [tag1, tag2]           # lowercase
pin: true                    # optional
math: true                   # enable KaTeX
mermaid: true                # enable Mermaid diagrams
image:
  path: /path/to/image.jpg
  alt: description
---
```

## Deployment

Pushing to `main` triggers `.github/workflows/pages-deploy.yml`, which builds with `jekyll b` (production) and runs `html-proofer` before deploying to GitHub Pages. Do not merge posts with broken external links.

## Code Style

`.editorconfig` enforces: 2-space indentation, UTF-8, LF line endings, single quotes in JS/CSS/SCSS, double quotes in YAML. Prettier is the default formatter in VSCode.
