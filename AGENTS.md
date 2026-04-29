# Repository Guidelines

## Project Structure & Module Organization
`main.py` is the entry point for synthetic data generation. It reads a YAML config, splits work across processes, and dispatches each worker to `pipeline.py`. Core rendering and content assembly live in `core/`, shared helpers in `utils/`, and style/config defaults in `config/`. Jinja templates are stored under `templates/`, with the active example layout in `templates/three_columns/`. Example configs and seed data live in `examples/` and `examples/data/`. Utility conversion scripts such as `scripts/doc_parser.py` turn generated output into Markdown-oriented artifacts.

## Build, Test, and Development Commands
Use the repository as a plain Python project; no build system is defined.

```bash
python main.py --config=examples/three_columns.yaml
```
Generates synthetic documents and bounding-box JSON using the configured template.

```bash
python main.py --config=examples/three_columns.yaml --check
```
Also writes boxed preview images to the configured `defaults.save_path`.

```bash
python scripts/doc_parser.py --config=examples/three_columns.yaml
```
Converts generated results into Markdown-friendly output.

Before running, place the ChromeDriver binary at `drive/chromedriver` and ensure `work_path.html_path` is absolute.

## Coding Style & Naming Conventions
Follow the existing Python style: 4-space indentation, snake_case for functions and variables, PascalCase for classes, and short module names such as `Render.py` or `ReadFile.py` only when matching existing patterns. Keep config keys and YAML paths descriptive and stable. Prefer small, single-purpose helpers in `utils/` over duplicating logic inside templates or pipeline code.

## Testing Guidelines
No automated test suite is present in this snapshot. Validate changes by running a small sample config from `examples/` and confirming that images, HTML, and JSON outputs are produced without Chrome rendering failures. For parser or extraction changes, compare `results.json` structure and use `--check` to inspect bounding boxes visually.

## Commit & Pull Request Guidelines
Git history is not available in this workspace snapshot, so use concise imperative commit subjects such as `Add footer bbox validation`. Keep commits scoped to one logical change. Pull requests should describe the config or template touched, list reproduction commands, link related issues, and include screenshots when layout, rendering, or boxed previews change.

## Configuration & Asset Tips
Treat `examples/*.yaml` as runnable references. Store reusable source data in `examples/data/`, keep template assets under `templates/`, and avoid hardcoding machine-specific paths outside config files.
