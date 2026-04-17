"""
reporter.py — Generates a persistent index.html with full history.

Reads all JSON files ever saved in results/, groups them by date,
and rebuilds results/index.html after every run.
"""

import html
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
    Loads all JSON files from results/, deduplicates (keeps newest per document),
    groups into runs (files within 2 minutes = same run), newest run first.
    """
    pattern = os.path.join(RESULTS_DIR, "*.json")
    json_files = sorted(glob.glob(pattern), reverse=True)  # newest first

    # Deduplicate — since files are sorted newest first, first seen = keep
    seen_docs: set[str] = set()
    entries = []

    for filepath in json_files:
        filename = os.path.basename(filepath)
        ts = _extract_timestamp(filename)
        if not ts:
            continue

        # Strip timestamp to get base document name e.g. "sample1"
        stem = filename.replace(f"_{ts}.json", "")
        if stem in seen_docs:
            continue
        seen_docs.add(stem)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append((ts, stem, data))
        except (json.JSONDecodeError, OSError):
            continue

    if not entries:
        return {}

    # Re-sort by timestamp newest first (dedup broke the order)
    entries.sort(key=lambda x: x[0], reverse=True)

    # Group into runs — files within 120 seconds of each other = same run
    runs: dict[str, list[dict]] = {}
    current_run_key = None
    current_run_time = None

    for ts, stem, data in entries:
        dt = datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")
        if current_run_time is None or (current_run_time - dt).total_seconds() > 120:
            current_run_key = ts
            current_run_time = dt
        runs.setdefault(current_run_key, []).append((stem, data))

    return runs


def _extract_timestamp(filename: str) -> str | None:
    """Extracts YYYY-MM-DD_HH-MM-SS from a filename like sample_2026-04-15_15-10-07.json"""
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.json$", filename)
    return match.group(1) if match else None


def _format_run_label(ts: str) -> str:
    """Converts '2026-04-15_15-10-07' to 'April 15, 2026 at 15:10'"""
    return datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S").strftime("%B %d, %Y at %H:%M")


def _sentiment_color(sentiment: str) -> str:
    colors = {
        "positive": "#22c55e",
        "negative": "#ef4444",
        "neutral":  "#f59e0b",
    }
    return colors.get(sentiment.lower(), "#94a3b8")


def _build_card(stem: str, data: dict) -> str:
    stem = html.escape(stem)
    sentiment = data.get("sentiment", "").lower()
    color = _sentiment_color(sentiment)

    key_points = data.get("key_points", [])
    key_points_html = "".join(f"<li>{html.escape(p)}</li>" for p in key_points)

    action_items = data.get("action_items", [])
    action_items_html = "".join(f"<li>{html.escape(a)}</li>" for a in action_items)

    entities = data.get("entities", {})
    people = html.escape(", ".join(entities.get("people", [])) or "—")
    orgs = html.escape(", ".join(entities.get("organizations", [])) or "—")
    dates = html.escape(", ".join(entities.get("dates", [])) or "—")

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
                    <div class="doc-title">{html.escape(data.get("title", "Untitled"))}</div>
                    <div class="doc-type">{html.escape(data.get("document_type", ""))}</div>
                </div>
                <span class="sentiment-badge" style="background:{color}">
                    {sentiment.capitalize()}
                </span>
            </div>
            <div class="section">
                <h3>Summary</h3>
                <p>{html.escape(data.get("summary", ""))}</p>
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
            <button class="delete-btn" onclick="deleteDoc('{stem}', this)">Delete</button>
        </div>"""


def _build_html(grouped: dict[str, list[dict]]) -> str:
    total = sum(len(docs) for docs in grouped.values())  # each docs is list of (stem, data) tuples
    today = datetime.now().strftime("%B %d, %Y")
    dates = sorted(grouped.keys(), reverse=True)

    sections_html = ""
    for i, date in enumerate(dates):
        docs = grouped[date]
        label = _format_run_label(date)
        count = len(docs)
        cards_html = "".join(_build_card(s, d) for s, d in docs)

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

        .delete-btn {{
            display: block;
            margin-top: 20px;
            margin-left: auto;
            background: none;
            border: 1px solid #fca5a5;
            color: #ef4444;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 5px 14px;
            border-radius: 6px;
            cursor: pointer;
        }}

        .delete-btn:hover {{
            background: #ef4444;
            color: white;
            border-color: #ef4444;
        }}

        .drop-zone {{
            max-width: 860px;
            margin: 0 auto 32px;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            color: #94a3b8;
            font-size: 0.95rem;
            transition: border-color 0.2s, background 0.2s;
            cursor: pointer;
        }}

        .drop-zone.dragover {{
            border-color: #1e293b;
            background: #f8fafc;
            color: #1e293b;
        }}

        .drop-zone.uploaded {{
            border-color: #22c55e;
            background: #f0fdf4;
            color: #16a34a;
        }}

        .drop-zone p {{
            margin-top: 6px;
            font-size: 0.85rem;
        }}

        .run-btn.loading {{
            background: #475569;
            cursor: not-allowed;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .spinner {{
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            flex-shrink: 0;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Document Analysis</h1>
            <p>Last updated {today} &mdash; {total} document{"s" if total != 1 else ""} in history</p>
        </div>
        <button id="runBtn" class="run-btn" onclick="runAnalysis()">Run Analysis</button>
    </header>

    <div class="drop-zone" id="dropZone">
        Drop a .txt or .pdf file here to upload
        <p>File will be saved to sample_docs/ ready for analysis</p>
    </div>

    {sections_html}

    <script>
        function deleteDoc(stem, btn) {{
            if (!confirm('Delete this document from history?')) return;
            fetch('/delete/' + stem, {{ method: 'POST' }})
                .then(res => res.json())
                .then(() => window.location.reload())
                .catch(() => alert('Delete failed.'));
        }}

        function runAnalysis() {{
            const btn = document.getElementById('runBtn');
            btn.classList.add('loading');
            btn.innerHTML = '<div class="spinner"></div> Analyzing...';
            btn.disabled = true;

            fetch('/run')
                .then(res => {{
                    if (res.ok || res.redirected) {{
                        window.location.reload();
                    }} else {{
                        btn.classList.remove('loading');
                        btn.innerHTML = 'Run Analysis';
                        btn.disabled = false;
                        alert('Analysis failed. Check the terminal for details.');
                    }}
                }})
                .catch(() => {{
                    btn.classList.remove('loading');
                    btn.innerHTML = 'Run Analysis';
                    btn.disabled = false;
                    alert('Could not reach the server.');
                }});
        }}

        const zone = document.getElementById('dropZone');

        zone.addEventListener('dragover', (e) => {{
            e.preventDefault();
            zone.classList.add('dragover');
        }});

        zone.addEventListener('dragleave', () => {{
            zone.classList.remove('dragover');
        }});

        zone.addEventListener('drop', (e) => {{
            e.preventDefault();
            zone.classList.remove('dragover');

            const file = e.dataTransfer.files[0];
            if (!file) return;

            const allowed = file.name.endsWith('.txt') || file.name.endsWith('.pdf');
            if (!allowed) {{
                zone.textContent = 'Only .txt and .pdf files are supported';
                return;
            }}

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {{ method: 'POST', body: formData }})
                .then(res => res.json())
                .then(data => {{
                    zone.classList.add('uploaded');
                    zone.innerHTML = `✓ "${{file.name}}" uploaded — click Run Analysis to extract`;
                }})
                .catch(() => {{
                    zone.textContent = 'Upload failed. Is the server running?';
                }});
        }});
    </script>
</body>
</html>"""
