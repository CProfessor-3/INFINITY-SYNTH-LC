# Infinity-Synth: High-Quality Synthetic Document Data Generation

## Quick Start
  
### 🧭 Step 1: Google Chrome Headless Setup

This document provides instructions for checking, installing, and running Google Chrome in headless mode — useful for web automation, screenshots, PDF rendering, or server-side rendering tasks.

#### 1. Check Installed Chrome Version

You can verify if Chrome (or Chromium) is already installed and check its version by running:

```shell
google-chrome --version
```
or

```shell
chromium-browser --version
```

#### 2. Install Google Chrome (Ubuntu Example)

```shell
# Update package index
sudo apt-get update
# Install dependencies
sudo apt-get install -y libappindicator1 fonts-liberation
# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# Install the package
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install
# Verify installation
google-chrome --version
```

#### 3. Please download Chromedriver, place it in the drive directory, name it chromedriver, and grant it execution permission.
    
### 🚀 Step 2: Run Data Synthesis

**Fixed column layout** (1 / 2 / 3 columns):

```shell
python main.py --config=examples/base.yaml              # default: 3 columns (from YAML)
python main.py --config=examples/base.yaml --columns 1  # 1-column layout
python main.py --config=examples/base.yaml --columns 2  # 2-column layout
python main.py --config=examples/base.yaml --columns 3  # 3-column layout
```

`--columns` overrides `layout_config.columns` in the YAML at runtime, so a single config file covers all layouts.

Add `--check` to write boxed preview images to `defaults.save_path` (default: `Temp/`):

```shell
python main.py --config=examples/base.yaml --columns 2 --check
```

### 🧩 Step 3: Convert Synthesized Data into Markdown

```shell
python scripts/doc_parser.py --config=examples/base.yaml
```

📁 Images, HTML sources, and ground-truth JSONs share the same UUID filename and are saved under:
- `work_path.save_image_dir` — rendered page images
- `work_path.html_dir` — HTML sources
- `work_path.output_gt_dir` — bounding-box ground-truth JSON


### 🛠️ Optional: Extending Template and Style Diversity
If you want to add new layout styles, modify the template specified by `work_path.template_file` and the corresponding data-filling function defined in `work_path.template_get_data`.  
These control the structure and content generation logic of the synthetic samples.  
For additional customization, please refer to the following parameters.

```
data_paths:
  text: "examples/data/text.json"
  image: "examples/data/figure.json"   # list of {"type": "figure", "path": "/abs/path/to/image.jpg", "caption": "..."}
  table: "examples/data/table.json"
  formula: "examples/data/formula.json"
  title: ""
```

```
work_path:
  template_path: "templates"
  template_file: "three_columns/document.html.jinja"
  template_get_data: "three_columns/getData"
  html_dir: "working/html"
  save_image_dir: "working/image"
  output_gt_dir: "working/ground_truth"
```

- `html_dir`: Directory for rendered HTML sources (one file per sample, named by UUID).
- `save_image_dir`: Directory for final rendered page images.
- `output_gt_dir`: Directory for bounding-box ground-truth JSON files.

```
defaults:
  save_path: "Temp"   # --check preview images saved here
  save_every_n: 4     # checkpoint frequency (ground-truth flush interval)
```

```
layout_config:
  element:
    table: 2      # max tables per page
    figure: 1     # max figures per page (0 to disable)
    title: 0
    text: 8       # max text blocks per page
    formula: 0
    header: 0
    footer: 0
    page_footnote: 0
  columns: 3      # default column count; override with --columns 1/2/3
```

- element: defines the **maximum** number of elements per page.
- columns: number of document columns (1 / 2 / 3). Can be overridden at runtime with `--columns`.

```
num_workers: 10
nums: 1000
```
- num_workers: The number of parallel workers/processes to be used.

- nums: The total number of data samples to be processed.
