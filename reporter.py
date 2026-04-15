"""
reporter.py — Generates a combined HTML report for all analyzed documents.

Called once at the end of a run with all results collected.
Output: results/report_YYYY-MM-DD_HH-MM-SS.html
"""

import os
from datetime import datetime

RESULTS_DIR = "results"


def generate_report(results: list[dict]) -> str:
    """
    Builds a single HTML report from a list of extracted document results.

    Args:
        results: List of dicts, each being one document's extracted data

    Returns:
        The path to the saved HTML file
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(RESULTS_DIR, f"report_{timestamp}.html")

    html = _build_html(results, timestamp)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _sentiment_color(sentiment: str) -> str:
    colors = {
        "positive": "#22c55e",
        "negative": "#ef4444",
        "neutral":  "#f59e0b",
    }
    return colors.get(sentiment.lower(), "#94a3b8")


def _build_cards(results: list[dict]) -> str:
    cards = []

    for data in results:
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

        cards.append(f"""
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
        </div>""")

    return "\n".join(cards)


def _build_html(results: list[dict], timestamp: str) -> str:
    date_label = datetime.now().strftime("%B %d, %Y")
    doc_count = len(results)
    cards_html = _build_cards(results)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Analysis Report — {date_label}</title>
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

        .card {{
            background: white;
            border-radius: 12px;
            padding: 28px;
            max-width: 860px;
            margin: 0 auto 24px;
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

        .entity-table tr td:last-child {{
            color: #1e293b;
        }}
    </style>
</head>
<body>
    <header>
        <h1>Document Analysis Report</h1>
        <p>{date_label} &mdash; {doc_count} document{"s" if doc_count != 1 else ""} analyzed</p>
    </header>

    {cards_html}
</body>
</html>"""
