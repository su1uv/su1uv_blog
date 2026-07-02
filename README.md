# suv1te

> A zero-dependency static site generator written in pure Python. Markdown in, HTML out.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-52%20passing-brightgreen.svg)](#testing)
[![Dependencies](https://img.shields.io/badge/dependencies-none-success.svg)](#tech-stack)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](#license)

`suv1te` turns a folder of Markdown files into a static website. It ships its **own**
Markdown parser and HTML renderer — no `markdown`, no `jinja2`, no third-party packages
whatsoever. Just the Python standard library, a small hand-rolled template engine, and
an object-oriented render tree.

---

## Table of contents

- [Live demo](#live-demo)
- [Features](#features)
- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Project structure](#project-structure)
- [Markdown support](#markdown-support)
- [Tech stack](#tech-stack)
- [Testing](#testing)
- [Background](#background)
- [License](#license)

---

## Live demo

The demo site (a themed Tolkien fan club) is built into [`docs/`](docs/) and served via
GitHub Pages:

**https://suv1uv.github.io/suv1te/**

---

## Features

- **Hand-written Markdown parser** — block-level and inline parsing implemented from
  scratch with the `re` module, no external libraries.
- **Object-oriented HTML tree** — `HTMLNode` → `LeafNode` / `ParentNode` with a
  recursive `to_html()` renderer. Parsing and rendering are cleanly decoupled.
- **Two-stage parsing pipeline** — split into blocks, classify each block, then resolve
  inline formatting. Mirrors how CommonMark-style parsers are structured.
- **Tiny template engine** — `{{ Title }}` / `{{ Content }}` placeholders injected into
  [`template.html`](template.html).
- **Basepath rewriting** — every `href="/..."` and `src="/..."` is rewritten to a
  configurable base path, so the same site deploys cleanly to a project subdirectory
  (e.g. GitHub Pages) or a domain root.
- **Recursive content walking** — nested directories of Markdown become a mirrored
  tree of HTML pages; static assets are copied verbatim.
- **Fully type-annotated** — modern `str | None`, `list[...]` annotations throughout.
- **Tested** — 52 unit tests covering the parser, node types, and end-to-end conversion.

---

## How it works

The build pipeline runs in two phases: copy static assets, then render every Markdown
page through the template.

```
 content/*.md ──┐
                │      ┌───────────────────────────────────────────────┐
 template.html ─┼────► │  suv1te build                                  │
                │      │  1. wipe output dir                            │      ┌────────────┐
 static/* ──────┘      │  2. copy static assets  ───────────────────────│────► │ docs/*      │
                      │  3. split markdown into blocks & classify       │      │ (HTML +    │
                      │  4. parse inline syntax → TextNodes → LeafNodes │      │  assets)   │
                      │  5. assemble ParentNode tree → to_html()        │      │            │
                      │  6. inject {{ Title }} / {{ Content }}          │      └────────────┘
                      │  7. rewrite href/src with basepath              │
                      └───────────────────────────────────────────────┘
```

### The Markdown → HTML chain

Parsing flows through a composable chain of small, single-purpose modules:

```
str                     markdown_to_blocks()        →  list[str]          (raw blocks)
                        block_to_block_type()       →  BlockType          (header / quote / list / code / p)
                        block_to_html()             →  (tag, children)
  inline:               text_to_textnodes()         →  list[TextNode]     (**bold**, _italic_, `code`, img, link)
                        text_node_to_html_node()    →  LeafNode
  assemble:             ParentNode(tag, children)   →  HTMLNode tree
  render:               .to_html()                  →  str                (final HTML)
```

On the HTML side, `ParentNode.to_html()` recursively renders its children, so an entire
page is one tree-walk away from a string. This separation makes each stage independently
testable — which is why the test suite grew to 52 cases without touching the file system.

---

## Quick start

```bash
# 1. production build → docs/  (basepath set for a GitHub Pages project page)
./build.sh

# 2. build + serve locally on http://localhost:8888
./main.sh

# 3. run the test suite
./test.sh
```

You only need Python 3.10+ — no virtualenv, no `pip install`.

### Authoring content

- Write Markdown under [`content/`](content/). Each `.md` file must start with a single
  `# H1` (used as the page `<title>`).
- Drop assets (images, CSS, fonts) into [`static/`](static/); they're copied as-is.
- Edit [`template.html`](template.html) to change the site shell.

### Deploying elsewhere

Pass a base path as the argument so links resolve correctly under a subdirectory:

```bash
python3 src/main.py "/your-subpath/"
# or "/" for a domain root / user page
python3 src/main.py "/"
```

---

## Project structure

```
suv1te/
├── src/
│   ├── main.py                # entry point; orchestrates the build
│   ├── generate.py            # pipeline: wipe, copy assets, render pages recursively
│   ├── block_markdown.py      # split markdown into blocks & classify (BlockType enum)
│   ├── inline_markdown.py     # parse inline syntax: bold, italic, code, images, links
│   ├── markdown_to_html.py    # block → HTMLNode tree → HTML; title extraction
│   ├── textnode.py            # TextNode + TextType; maps to LeafNode
│   ├── htmlnode.py            # HTMLNode tree: LeafNode (terminal) / ParentNode (container)
│   └── test_*.py              # 52 unit tests
├── content/                   # Markdown source — the site you author
├── static/                    # assets copied verbatim to docs/
├── template.html              # HTML template with {{ Title }} / {{ Content }}
├── docs/                      # generated output (served by GitHub Pages)
├── build.sh                   # production build (basepath /suv1te/)
├── main.sh                    # build + local dev server on :8888
└── test.sh                    # run the unittest suite
```

---

## Markdown support

| Element        | Syntax                  |
| -------------- | ----------------------- |
| Headings       | `#` … `######`          |
| Paragraphs     | plain text, blank-line separated |
| Bold           | `**text**`              |
| Italic         | `_text_`                |
| Inline code    | `` `code` ``            |
| Code block     | ` ``` ` fenced          |
| Block quote    | `> quote`               |
| Unordered list | `- item`                |
| Ordered list   | `1. item`               |
| Links          | `[text](url)`           |
| Images         | `![alt](url)`           |

---

## Tech stack

- **Python 3.10+** — standard library only (`os`, `shutil`, `re`, `sys`, `enum`).
- **No runtime dependencies.** No `requirements.txt`, no lock file, nothing to install.
- **`unittest`** for the test suite.

---

## Testing

```bash
./test.sh
# Ran 52 tests in 0.001s ... OK
```

Tests live next to the modules they cover (`src/test_*.py`) and exercise every layer:
`TextNode` equality/repr, `LeafNode`/`ParentNode` rendering (including edge cases like
self-closing `<img/>` and missing values), block classification, inline splitting for
each delimiter and for images/links, and full Markdown-to-HTML conversion.

---

## Background

The core engine was built following the
[Build a Static Site Generator](https://www.boot.dev/courses/build-static-site-generator-python)
course on [Boot.dev](https://www.boot.dev) — that served as the foundation for
understanding how Markdown parsers and template engines work under the hood, by writing
one from scratch rather than reaching for a library. `suv1te` is now being extended
beyond that baseline with new features of my own.

---

## License

Released under the **MIT License**.
