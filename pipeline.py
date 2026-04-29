import os
import logging
import logging.handlers
import uuid
from utils.ReadFile import read_files
from utils.utils import extract_form_from_json, draw_boxes_on_image,save_data_to_file, read_table_text
from config.styles import get_styles_num
from core.getData import GetData
from core.Render import Jinja_render, chrome_render
from utils.table_html import produce_table_html
from utils.utils import get_args
from bs4 import BeautifulSoup
import yaml
from typing import List


def _count_table_cols(html_str: str) -> int:
    soup = BeautifulSoup(html_str, 'html.parser')
    for section in (soup.find('thead'), soup.find('tbody'), soup.find('table')):
        if section:
            first_row = section.find('tr')
            if first_row:
                return len(first_row.find_all(['th', 'td']))
    return 0


def determine_doc_columns(input_content: dict, config: dict) -> int:
    cfg_cols = str(config["layout_config"].get("columns", 3))
    if cfg_cols != "auto":
        return int(cfg_cols)

    thresholds = config.get("column_thresholds", {"wide": 6, "medium": 4})
    max_cols = max(
        (_count_table_cols(ele.get("html", "")) for ele in input_content.get("body", []) if ele.get("type") == "table"),
        default=0,
    )

    if max_cols >= thresholds.get("wide", 6):
        return 1
    elif max_cols >= thresholds.get("medium", 4):
        return 2
    else:
        return 3


def pipeline(title: List[dict], text: List[dict], table: List[dict], formula: List[dict], figure: List[dict], nums: int, process_id: int):
    args = get_args()
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    work_path = config["work_path"]
    html_dir = work_path["html_dir"]
    save_image_dir = work_path["save_image_dir"]
    output_gt_dir = work_path["output_gt_dir"]

    render = chrome_render()
    total_count = 0

    Input_data = GetData(title, text, table, formula, figure, process_id)
    template_path = work_path["template_path"]
    template = work_path["template_file"]

    while True:
        if total_count >= nums:
            break

        input_content = Input_data.getData()
        if input_content is None:
            continue

        unique_id = str(uuid.uuid4())
        html_path = os.path.join(html_dir, f"{unique_id}.html")

        doc_columns = determine_doc_columns(input_content, config)
        styles = get_styles_num(config, columns=doc_columns)

        Jinja_render(template_path, input_content, template, styles, html_path)

        url = f"file://{html_path}"

        # Fill loop: keep adding text until remaining space < threshold
        FILL_THRESHOLD_PX = 30
        for _ in range(8):
            render.driver.get(url)
            remaining = render.get_remaining_space()
            if remaining < FILL_THRESHOLD_PX:
                break
            to_add = max(1, int(remaining / 80))
            for _ in range(to_add):
                input_content['body'].append(next(Input_data.text_iter))
            Jinja_render(template_path, input_content, template, styles, html_path)

        save_image_path = os.path.join(save_image_dir, f"{unique_id}.png")

        cross_column_paragraphs = render.get_location(url, save_image_path)
        print(cross_column_paragraphs)
        if cross_column_paragraphs is not None:
            location_info = extract_form_from_json(save_image_path, cross_column_paragraphs)
            gt_path = os.path.join(output_gt_dir, f"{unique_id}.json")
            save_data_to_file(location_info, gt_path)
            total_count += 1
            if args.check:
                os.makedirs(config['defaults']['save_path'], exist_ok=True)
                draw_boxes_on_image(save_image_path, location_info, config['defaults']['save_path'])
            print(f"Process id {process_id}, Acc {total_count}")

    render.close()



