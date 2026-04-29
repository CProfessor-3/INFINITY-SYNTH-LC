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


PAGE_CONTENT_WIDTH_PX = 625.0
COLUMN_GAP_PX = 16.0
CHAR_WIDTH_PX = 9.0
CELL_PADDING_PX = 4.0


def _char_width(text: str) -> float:
    """CJK chars count as 2 units, ASCII as 1."""
    w = 0
    for ch in text:
        w += 2 if '一' <= ch <= '鿿' else 1
    return w


def estimate_table_width(html_str: str) -> float:
    soup = BeautifulSoup(html_str, 'html.parser')
    rows = soup.find_all('tr')
    if not rows:
        return 0.0
    num_cols = max(len(r.find_all(['th', 'td'])) for r in rows)
    if num_cols == 0:
        return 0.0
    col_max_chars = [0.0] * num_cols
    for row in rows:
        cells = row.find_all(['th', 'td'])
        for i, cell in enumerate(cells[:num_cols]):
            col_max_chars[i] = max(col_max_chars[i], _char_width(cell.get_text()))
    return sum(max(c, 4) * CHAR_WIDTH_PX + CELL_PADDING_PX for c in col_max_chars)


def column_width_px(doc_columns: int) -> float:
    return (PAGE_CONTENT_WIDTH_PX - (doc_columns - 1) * COLUMN_GAP_PX) / doc_columns


def annotate_table_spans(input_content: dict, doc_columns: int) -> None:
    col_width = column_width_px(doc_columns)
    for ele in input_content.get('body', []):
        if ele.get('type') == 'table':
            est = estimate_table_width(ele.get('html', ''))
            ele['span'] = est > col_width


def get_doc_columns(config: dict) -> int:
    return int(config["layout_config"].get("columns", 3))


def pipeline(title: List[dict], text: List[dict], table: List[dict], formula: List[dict], figure: List[dict], nums: int, process_id: int):
    args = get_args()
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    if args.columns is not None:
        config["layout_config"]["columns"] = args.columns

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
        html_path = os.path.join(os.path.abspath(html_dir), f"{unique_id}.html")

        doc_columns = get_doc_columns(config)
        styles = get_styles_num(config, columns=doc_columns)
        annotate_table_spans(input_content, doc_columns)

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



