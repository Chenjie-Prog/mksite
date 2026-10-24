<div align="center">

# mksite

**A zero-dependency static site generator — built entirely on the Python standard library**

[![Tests](https://github.com/USER/mksite/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/mksite/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PyPI](https://img.shields.io/badge/dependencies-0-brightgreen)](#why-mksite)

[Live demo](https://USER.github.io/mksite/) · [中文文档](README.md)

</div>

---

## Why mksite

- **Zero dependencies** — Python standard library only. No long `pip install`,
  no node_modules. You can even copy the single `mksite/` package into your
  project and it just works.
- **Small enough to fully understand** — the Markdown engine, template
  renderer, build pipeline and dev server total under 1,000 lines of source.
  Every line is readable and yours to change.
- **Batteries included** — Markdown rendering (headings / tables / code fences /
  nested lists / blockquotes…), RSS feed, sitemap, and a dev server with
  automatic rebuilds.
- **The theme is one HTML file** — `{{ variable }}` placeholders; customize
  your theme in five minutes.

## Install

Requires Python 3.9+. That's the whole story.

```bash
# Install from GitHub
pip install git+https://github.com/USER/mksite.git

# Or run straight from a clone, no install needed
git clone https://github.com/USER/mksite.git
cd mksite
python -m mksite --help
```

## Quick start

```bash
mksite init myblog            # 1. scaffold a new site
mksite new "My first post" -s myblog   # 2. create a post
mksite serve -s myblog        # 3. preview at http://127.0.0.1:8000 (auto-rebuild on save)
mksite build -s myblog        # 4. build static files into myblog/public/
```

Deploy `public/` to any static host: GitHub Pages, Netlify, Vercel,
Cloudflare Pages — they all work.

## Project layout

```
myblog/
├── site.json            # site config: name, language, base_url, author
├── templates/
│   └── page.html        # page template (the only "theme" file you need)
├── static/              # assets copied verbatim (css/js/images)
└── content/             # Markdown pages; directory structure = site structure
    ├── index.md         # home page
    └── posts/           # posts (pages with a date automatically join the RSS feed)
```

## Writing

Each Markdown file may start with front-matter:

```markdown
---
title: Post title
date: 2026-10-24
description: Optional summary (auto-truncated to 160 chars if omitted)
tags: [python, ssg]
---

Body starts here…
```

Template variables: `{{ title }}`, `{{ content }}`, `{{ root }}` (relative
prefix to the site root), `{{ name }}`, `{{ language }}` (from site.json), plus
any string field from the front-matter.

## Deploy to GitHub Pages

1. Push the repo, then under **Settings → Pages** choose **Deploy from a
   branch**, branch `main`, folder `/docs`.
2. The repo also ships `.github/workflows/pages.yml` (builds the `example/`
   site and deploys it). To use that instead, set
   **Settings → Pages → Source: GitHub Actions**.

## Development

```bash
python -m unittest discover -s tests   # run the test suite (53 cases)
python -m mksite serve -s example      # preview the example site
python -m mksite build -s example -o docs   # rebuild docs/ (used by GitHub Pages)
```

Issues and PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository layout

```
mksite/
├── mksite/              # the core package (~1,000 lines)
│   ├── markdown.py      # Markdown → HTML engine
│   ├── frontmatter.py   # metadata parsing
│   ├── templates.py     # {{ variable }} template rendering
│   ├── build.py         # build pipeline, RSS, sitemap
│   ├── server.py        # dev server + file watcher
│   └── cli.py           # init / build / serve / new
├── tests/               # unit tests
├── example/             # a runnable example site
└── docs/                # built output of example/ (deployed to GitHub Pages)
```

## License

[MIT](LICENSE)
