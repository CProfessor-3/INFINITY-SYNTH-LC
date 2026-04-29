# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Infinity-Synth is a synthetic document image generation pipeline. It produces A4-sized document page images (PNG + PDF) alongside bounding-box JSON ground-truth annotations. Each page is assembled from seed data (text, tables, formulas, figures), rendered into HTML via Jinja2, and then captured by a headless Chrome browser.

## Prerequisites

- Google Chrome and ChromeDriver must be installed. Place the ChromeDriver binary at `drive/chromedriver` and ensure it is executable.
- `work_path.html_path` in your config YAML must be an **absolute path**.

## Running

Generate synthetic documents:
```bash
python main.py --config=examples/three_columns.yaml
```

Add `--check` to also write boxed preview images to `defaults.save_path` (default: `Temp/`):
```bash
python main.py --config=examples/three_columns.yaml --check
```

Convert generated ground-truth JSON to Markdown-friendly output:
```bash
python scripts/doc_parser.py --config=examples/three_columns.yaml
```

Results accumulate in `working/ground_truth/result_of_id{i}.json` (per worker) and merge into the path set by `work_path.result` (default: `results.json`).

## Architecture

### Data flow

```
YAML config
    │
    ▼
main.py  ──── loads seed data (text/table/formula/figure JSON)
    │          splits corpus across num_workers processes
    ▼
pipeline.py (one process per worker)
    │
    ├─ core/getData.py::GetData   — cycles through seed items, assembles page content dict
    │      └─ dynamically imports work_path.template_get_data (e.g. templates/three_columns/getData.py)
    │         which applies layout_config rules and Config style randomisation
    │
    ├─ core/Render.py::Jinja_render  — renders HTML from Jinja template + content dict + styles
    │
    └─ core/Render.py::chrome_render — drives headless Chrome via Selenium
           ├─ navigates to file:// HTML
           ├─ executes JS to collect element bounding boxes (pageData)
           ├─ overflow detection
           └─ Page.printToPDF → saves .pdf and .png, returns pageData
```

### Key modules

| Path | Role |
|------|------|
| `main.py` | Entry point: loads config/data, spawns worker processes |
| `pipeline.py` | Per-worker loop: generate → render → capture → save |
| `core/getData.py` | `GetData` class wraps seed iterators; delegates to template-specific `get_data()` |
| `core/Render.py` | `Jinja_render` (HTML generation) + `chrome_render` (Selenium/CDP capture) |
| `config/Config.py` | Style constants (fonts, colors, sizes); `get_config_value()` picks randomly |
| `config/styles.py` | `get_styles_num()` — builds a full styles dict from Config for one render pass |
| `utils/` | Shared helpers: file I/O, bbox extraction, text cleaning, table HTML, LaTeX normalisation, header/footer generation |
| `templates/` | Jinja2 HTML/CSS templates + per-layout `getData.py` |
| `examples/` | Reference YAML configs and seed JSON data |

### Adding a new layout

1. Create `templates/<name>/document.html.jinja` and `templates/<name>/document.css.jinja`.
2. Create `templates/<name>/getData.py` with a `get_data(input_data: GetData, layout_config: dict) -> dict` function.
3. Point a new YAML config at the new template via `work_path.template_file` and `work_path.template_get_data`.

### Config YAML structure

```yaml
data_paths:          # paths to seed JSON files (text, image, table, formula, title)
work_path:           # template paths, output paths (html_path must be absolute)
defaults:            # save_path for --check previews, save_every_n checkpoint frequency
layout_config:       # element counts per page (max), number of columns
num_workers: 10      # parallel processes
nums: 1000           # total samples to generate
```
