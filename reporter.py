"""
reporter.py — Generates a persistent index.html with full history.

Reads all JSON files ever saved in results/, groups them by date,
and rebuilds results/index.html after every run.
"""

import json
import os
import re
import glob
from datetime import datetime

RESULTS_DIR = "results"
INDEX_PATH = os.path.join(RESULTS_DIR, "index.html")


def generate_report() -> str:
    """
    Scans all JSON files in results/, groups by date, and writes index.html.

    Returns:
        Path to the saved index.html
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    grouped = _load_and_group_results()
    html = _build_html(grouped)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    return INDEX_PATH


def _load_and_group_results() -> dict[str, list[dict]]:
    """
    Loads all JSON files from results/ and groups them by date (YYYY-MM-DD).
    Returns a dict ordered most recent date first.
    """
    pattern = os.path.join(RESULTS_DIR, "*.json")
    json_files = sorted(glob.glob(pattern), reverse=True)

    grouped: dict[str, list[dict]] = {}

    for filepath in json_files:
        filename = os.path.basename(filepath)
        date = _extract_date(filename)
        if not date:
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            grouped.setdefault(date, []).append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return grouped


def _extract_date(filename: str) -> str | None:
    """Extracts YYYY-MM-DD from a filename like sample_2026-04-15_15-10-07.json"""
    match = re.search(r"(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}-\d{2}\.json$", filename)
    return match.group(1) if match else None


def _format_date_label(date_str: str) -> str:
    """Converts '2026-04-15' to 'April 15, 2026'"""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")


def _sentiment_color(sentiment: str) -> str:
    colors = {
        "positive": "#22c55e",
        "negative": "#ef4444",
        "neutral":  "#f59e0b",
    }
    return colors.get(sentiment.lower(), "#94a3b8")


def _build_card(data: dict) -> str:
    sentiment = data.get("sentiment", "").lower()
    color = _sentiment_color(sentiment)

    key_points = data.get("key_points", [])
    key_points_html = "".join(f"<li>{p}</li>" for p in key_points)

    action_items = data.get("action_items", [])
    action_items_html = "".join(f"<li>{a}</li>" for a in action_items)

    entities = data.get("entities", {})
    people = ", ".join(entities.get("people", [])) or "—"
    orgs = ", ".join(entities.get("organizations", [])) or "—"
    dates = ", ".join(entities.get("dates", [])) or "—"

    actions_block = ""
    if action_items:
        actions_block = f"""
            <div class="section">
                <h3>Action Items</h3>
                <ul>{action_items_html}</ul>
            </div>"""

    return f"""
        <div class="card">
            <div class="card-header">
                <div>
                    <div class="doc-title">{data.get("title", "Untitled")}</div>
                    <div class="doc-type">{data.get("document_type", "")}</div>
                </div>
                <span class="sentiment-badge" style="background:{color}">
                    {sentiment.capitalize()}
                </span>
            </div>
            <div class="section">
                <h3>Summary</h3>
                <p>{data.get("summary", "")}</p>
            </div>
            <div class="section">
                <h3>Key Points</h3>
                <ul>{key_points_html}</ul>
            </div>
            <div class="section">
                <h3>Entities</h3>
                <table class="entity-table">
                    <tr><td>People</td><td>{people}</td></tr>
                    <tr><td>Organizations</td><td>{orgs}</td></tr>
                    <tr><td>Dates</td><td>{dates}</td></tr>
                </table>
            </div>
            {actions_block}
        </div>"""


def _build_html(grouped: dict[str, list[dict]]) -> str:
    total = sum(len(docs) for docs in grouped.values())
    today = datetime.now().strftime("%B %d, %Y")
    dates = sorted(grouped.keys(), reverse=True)

    sections_html = ""
    for i, date in enumerate(dates):
        docs = grouped[date]
        label = _format_date_label(date)
        count = len(docs)
        cards_html = "".join(_build_card(d) for d in docs)

        if i == 0:
            # Most recent — shown open
            sections_html += f"""
        <div class="run-section">
            <div class="run-header">
                <span class="run-date">{label}</span>
                <span class="run-count">{count} document{"s" if count != 1 else ""}</span>
            </div>
            {cards_html}
        </div>"""
        else:
            # Older runs — collapsible
            sections_html += f"""
        <details class="run-section">
            <summary class="run-header">
                <span class="run-date">{label}</span>
                <span class="run-count">{count} document{"s" if count != 1 else ""}</span>
            </summary>
            {cards_html}
        </details>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Analysis — History</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f1f5f9;
            color: #1e293b;
            padding: 40px 20px;
        }}

        header {{
            max-width: 860px;
            margin: 0 auto 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        header h1 {{
            font-size: 1.8rem;
            font-weight: 700;
        }}

        header p {{
            color: #64748b;
            margin-top: 4px;
            font-size: 0.95rem;
        }}

        .run-btn {{
            background: #1e293b;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
        }}

        .run-btn:hover {{
            background: #334155;
        }}

        .run-section {{
            max-width: 860px;
            margin: 0 auto 32px;
        }}

        .run-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            cursor: pointer;
            list-style: none;
        }}

        details > summary {{ list-style: none; }}
        details > summary::-webkit-details-marker {{ display: none; }}

        .run-date {{
            font-size: 1rem;
            font-weight: 700;
            color: #1e293b;
        }}

        .run-count {{
            font-size: 0.8rem;
            color: #94a3b8;
            background: #e2e8f0;
            padding: 2px 10px;
            border-radius: 999px;
        }}

        details .run-header::before {{
            content: "▶";
            font-size: 0.7rem;
            color: #94a3b8;
            transition: transform 0.2s;
        }}

        details[open] .run-header::before {{
            transform: rotate(90deg);
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 28px;
            margin-bottom: 16px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }}

        .doc-title {{
            font-size: 1.15rem;
            font-weight: 600;
        }}

        .doc-type {{
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 3px;
        }}

        .sentiment-badge {{
            color: white;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
            white-space: nowrap;
        }}

        .section {{
            margin-top: 18px;
        }}

        .section h3 {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
            margin-bottom: 8px;
        }}

        .section p {{
            font-size: 0.95rem;
            line-height: 1.6;
            color: #334155;
        }}

        .section ul {{
            padding-left: 18px;
            font-size: 0.95rem;
            line-height: 1.8;
            color: #334155;
        }}

        .entity-table {{
            font-size: 0.9rem;
            border-collapse: collapse;
            width: 100%;
        }}

        .entity-table tr td:first-child {{
            color: #64748b;
            width: 130px;
            padding: 3px 0;
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Document Analysis</h1>
            <p>Last updated {today} &mdash; {total} document{"s" if total != 1 else ""} in history</p>
        </div>
        <a href="/run" class="run-btn">Run Analysis</a>
    </header>

    {sections_html}
</body>
</html>"""
