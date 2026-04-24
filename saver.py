"""
saver.py — Saves analysis results to the results/ folder.

Each document gets its own JSON file named after the source file + timestamp.
Example: results/sample_2026-04-05_14-32-10.json
"""

import json
import os
import re
import glob
from datetime import datetime


RESULTS_DIR = "results"


def find_cached_result(filename: str) -> dict | None:
    """
    Looks for an existing JSON result for this document in results/.
    Returns the cached data if found, otherwise None.

    Args:
        filename: The original document filename (e.g. 'sample.txt')
    """
    base = os.path.splitext(filename)[0]
    pattern = os.path.join(RESULTS_DIR, f"{base}_*.json")
    matches = sorted(glob.glob(pattern))

    if not matches:
        return None

    # Sort by timestamp in filename to get the most recent
    matches.sort(key=lambda f: (m := re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", f)) and m.group() or "", reverse=True)

    with open(matches[0], "r", encoding="utf-8") as f:
        return json.load(f)


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
