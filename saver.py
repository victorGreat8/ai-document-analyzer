"""
saver.py — Saves analysis results to the results/ folder.

Each document gets its own JSON file named after the source file + timestamp.
Example: results/sample_2026-04-05_14-32-10.json
"""

import json
import os
from datetime import datetime


RESULTS_DIR = "results"


def save_result(filename: str, data: dict) -> str:
    """
    Saves extracted data as a JSON file in the results/ folder.

    Args:
        filename: The original document filename (e.g. 'sample.txt')
        data: The extracted data dict from analyze_document()

    Returns:
        The path to the saved file
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    base = os.path.splitext(filename)[0]  # 'sample.txt' -> 'sample'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(RESULTS_DIR, f"{base}_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path
