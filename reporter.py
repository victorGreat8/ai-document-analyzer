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
    content = _build_html(grouped)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)

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
        <div class="card" style="border-left: 6px solid {color}" data-stem="{stem}">
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
            <div class="card-footer">
                <label class="card-checkbox">
                    <input type="checkbox" class="doc-checkbox" onchange="updateExportBtn()"> Select
                </label>
                <div class="card-actions">
                    <button class="reanalyze-btn" onclick="reanalyzeDoc('{stem}', this)">Re-analyze</button>
                    <button class="delete-btn" onclick="deleteDoc('{stem}', this)">Delete</button>
                </div>
            </div>
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

        open_attr = "open" if i == 0 else ""
        sections_html += f"""
        <details class="run-section" {open_attr}>
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
            background-color: #0a0f1e;
            background-image: linear-gradient(rgba(10, 15, 30, 0.72), rgba(10, 15, 30, 0.72)), url('/static/bg.jpg');
            background-size: cover;
            background-position: 50% 50%;
            background-attachment: fixed;
            color: #1e293b;
            padding: 0;
        }}

        header {{
            background: rgba(10, 15, 30, 0.85);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid rgba(56, 114, 224, 0.2);
            padding: 20px 32px;
            margin-bottom: 40px;
            width: 100%;
        }}

        header h1 {{ color: white; }}
        header p {{ color: #94a3b8; }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .search-input {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 0.9rem;
            color: white;
            outline: none;
            width: 220px;
            transition: border-color 0.2s, background 0.2s;
        }}

        .search-input::placeholder {{ color: #94a3b8; }}

        .search-input:focus {{
            border-color: rgba(255,255,255,0.5);
            background: rgba(255,255,255,0.15);
        }}

        .header-inner {{
            max-width: 860px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        header h1 {{
            font-size: 1.6rem;
            font-weight: 700;
        }}

        header p {{
            color: #64748b;
            margin-top: 4px;
            font-size: 0.9rem;
        }}

        .page-content {{
            padding: 0 20px 40px;
        }}

        .run-btn {{
            background: #1e293b;
            color: white;
            border: none;
            padding: 12px 26px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: background 0.15s, box-shadow 0.15s;
        }}

        .run-btn:hover {{
            background: #334155;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
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
            color: white;
        }}

        .run-count {{
            font-size: 0.8rem;
            color: #cbd5e1;
            background: rgba(255,255,255,0.15);
            padding: 2px 10px;
            border-radius: 999px;
        }}

        details .run-header::before {{
            content: "▶";
            font-size: 0.7rem;
            color: #cbd5e1;
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
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .card:hover {{
            transform: scale(1.04) translateY(-8px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.18);
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

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
        }}

        .card-checkbox {{
            font-size: 0.9rem;
            color: #64748b;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .card-checkbox input[type="checkbox"] {{
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}

        .export-all-col {{
            position: relative;
        }}

        .export-hint {{
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.72rem;
            color: #94a3b8;
            white-space: nowrap;
            margin-top: 4px;
        }}

        .export-btn {{
            background: none;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 10px 18px;
            border-radius: 8px;
            cursor: pointer;
            white-space: nowrap;
            transition: background 0.15s;
        }}

        .export-btn:hover:not(:disabled) {{
            background: rgba(255,255,255,0.1);
        }}

        .export-btn:disabled {{
            opacity: 0.35;
            cursor: not-allowed;
        }}

        .card-actions {{
            display: flex;
            gap: 8px;
        }}

        .reanalyze-btn {{
            background: none;
            border: 2px solid #93c5fd;
            color: #3b82f6;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 5px 14px;
            border-radius: 10px;
            cursor: pointer;
        }}

        .reanalyze-btn:hover {{
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }}

        .reanalyze-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
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

        .queue-bar {{
            max-width: 860px;
            margin: 0 auto 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
            border-radius: 10px;
            padding: 14px 20px;
            font-size: 0.9rem;
            font-weight: 600;
            color: #1e293b;
            cursor: pointer;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            transition: background 0.15s;
        }}

        .queue-bar:hover {{ background: #f8fafc; }}

        .queue-arrow {{
            font-size: 0.7rem;
            color: #94a3b8;
            transition: transform 0.2s;
        }}

        .queue-list {{
            max-width: 860px;
            margin: 0 auto 24px;
            background: white;
            border-radius: 0 0 10px 10px;
            padding: 4px 18px 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            font-size: 0.9rem;
            color: #334155;
            line-height: 2;
        }}

        .queue-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
        }}

        .queue-remove-btn {{
            background: none;
            border: 1px solid #fca5a5;
            color: #ef4444;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 6px;
            cursor: pointer;
        }}

        .queue-remove-btn:hover {{
            background: #ef4444;
            color: white;
            border-color: #ef4444;
        }}

        .empty-state {{
            max-width: 860px;
            margin: 20px auto 40px;
            text-align: center;
            padding: 48px 32px;
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .empty-icon {{
            font-size: 3rem;
            margin-bottom: 16px;
        }}

        .empty-state h2 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 12px;
        }}

        .empty-state p {{
            font-size: 0.95rem;
            color: #94a3b8;
            line-height: 1.7;
        }}

        .empty-sub {{
            margin-top: 8px;
            font-size: 0.88rem !important;
        }}

        .drop-zone {{
            max-width: 860px;
            margin: 0 auto 32px;
            border: 2px dashed #94a3b8;
            border-radius: 12px;
            padding: 36px;
            text-align: center;
            color: #64748b;
            font-size: 0.95rem;
            background: white;
            transition: border-color 0.2s, background 0.2s;
            cursor: pointer;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
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

        .browse-link {{
            color: #1e293b;
            font-weight: 600;
            text-decoration: underline;
            cursor: pointer;
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
        <div class="header-inner">
            <div>
                <h1>Document Analysis</h1>
                <p>Last updated {today} &mdash; {total} document{"s" if total != 1 else ""} in history</p>
            </div>
            <div class="header-actions">
                <input type="text" id="searchInput" class="search-input" placeholder="Search documents..." oninput="filterCards()">
                <button id="runBtn" class="run-btn" onclick="runAnalysis()">Run Analysis</button>
                <div class="export-all-col">
                    <button class="export-btn" onclick="window.location='/export'" {"disabled" if total == 0 else ""}>Export All</button>
                    <span class="export-hint">or select specific cards</span>
                </div>
                <button id="exportSelectedBtn" class="export-btn" onclick="exportSelected()" style="visibility:hidden">Export Selected</button>
            </div>
        </div>
    </header>

    <div class="page-content">

    <div class="queue-bar" id="queueBar" onclick="toggleQueue()">
        <span id="queueLabel">Loading queue...</span>
        <span class="queue-arrow" id="queueArrow">▶</span>
    </div>
    <div class="queue-list" id="queueList" style="display:none"></div>

    <div class="drop-zone" id="dropZone">
        <span id="zoneText">Drop a file here or <span class="browse-link">click to browse</span></span>
        <p>Supports .txt and .pdf — saved to sample_docs/ ready for analysis</p>
        <input type="file" id="fileInput" accept=".txt,.pdf" multiple style="display:none">
    </div>

    {"" if sections_html.strip() else '''
    <div class="empty-state">
        <div class="empty-icon">📄</div>
        <h2>Welcome to Document Analyzer</h2>
        <p>Drop a <strong>.txt</strong> or <strong>.pdf</strong> file in the box to get started.</p>
        <p class="empty-sub">Then click <strong>Run Analysis</strong> to extract insights from your document.</p>
    </div>'''}

    {sections_html}

    <script>
        function updateExportBtn() {{
            const checked = document.querySelectorAll('.doc-checkbox:checked').length;
            document.getElementById('exportSelectedBtn').style.visibility = checked > 0 ? 'visible' : 'hidden';
        }}

        function exportSelected() {{
            const stems = Array.from(document.querySelectorAll('.doc-checkbox:checked'))
                .map(cb => cb.closest('.card').dataset.stem);
            window.location = '/export?stems=' + stems.join(',');
        }}

        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.card');
            const sections = document.querySelectorAll('details.run-section');

            if (!query) {{
                // Reset everything to default state
                cards.forEach(card => card.style.display = '');
                sections.forEach((s, i) => {{
                    s.open = i === 0;
                    s.style.display = '';
                }});
                return;
            }}

            cards.forEach(card => {{
                const matches = card.innerText.toLowerCase().includes(query);
                card.style.display = matches ? '' : 'none';
                const details = card.closest('details');
                if (details && matches) details.open = true;
            }});

            sections.forEach(section => {{
                const visible = section.querySelectorAll('.card:not([style*="none"])').length;
                section.style.display = visible > 0 ? '' : 'none';
            }});
        }}

        function loadQueue() {{
            fetch('/queue')
                .then(res => res.json())
                .then(data => {{
                    const count = data.files.length;
                    const label = document.getElementById('queueLabel');
                    const list = document.getElementById('queueList');
                    const runBtn = document.getElementById('runBtn');

                    label.textContent = count === 0
                        ? 'No files queued'
                        : `${{count}} file${{count > 1 ? 's' : ''}} queued in sample_docs/`;
                    list.innerHTML = data.files.map(f =>
                        `<div class="queue-item">📄 ${{f}}<button class="queue-remove-btn" onclick="removeQueued('${{f}}')">Remove</button></div>`
                    ).join('');

                    runBtn.disabled = count === 0;
                    runBtn.style.opacity = count === 0 ? '0.35' : '';
                    runBtn.style.cursor = count === 0 ? 'not-allowed' : '';
                }});
        }}

        function removeQueued(filename) {{
            fetch('/remove/' + encodeURIComponent(filename), {{ method: 'POST' }})
                .then(res => res.json())
                .then(() => fetch('/queue'))
                .then(res => res.json())
                .then(data => {{
                    loadQueue();
                    if (data.files.length === 0) {{
                        uploadedNames.length = 0;
                        zone.classList.remove('uploaded');
                        document.getElementById('zoneText').innerHTML = 'Drop a file here or <span class="browse-link">click to browse</span>';
                    }}
                }})
                .catch(() => alert('Could not remove file.'));
        }}

        function toggleQueue() {{
            const list = document.getElementById('queueList');
            const arrow = document.getElementById('queueArrow');
            const open = list.style.display !== 'none';
            list.style.display = open ? 'none' : 'block';
            arrow.style.transform = open ? '' : 'rotate(90deg)';
        }}

        loadQueue();

        function reanalyzeDoc(stem, btn) {{
            if (!confirm('Re-analyze this document? The current result will be replaced.')) return;
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
            fetch('/reanalyze/' + stem, {{ method: 'POST' }})
                .then(res => res.json())
                .then(data => {{
                    if (data.error) {{
                        alert(data.error);
                        btn.disabled = false;
                        btn.textContent = 'Re-analyze';
                    }} else {{
                        window.location.reload();
                    }}
                }})
                .catch(() => {{
                    alert('Re-analyze failed.');
                    btn.disabled = false;
                    btn.textContent = 'Re-analyze';
                }});
        }}

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
                        return res.json().then(data => {{
                            btn.classList.remove('loading');
                            btn.innerHTML = 'Run Analysis';
                            btn.disabled = false;
                            alert(data.error || 'Analysis failed. Check the terminal for details.');
                        }});
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
        const fileInput = document.getElementById('fileInput');
        const uploadedNames = [];

        function updateZoneLabel() {{
            const first = uploadedNames[0];
            const rest = uploadedNames.length - 1;
            const label = rest > 0
                ? `✓ "${{first}}" and ${{rest}} other file${{rest > 1 ? 's' : ''}} — Run Analysis to extract`
                : `✓ "${{first}}" uploaded — click Run Analysis to extract or drop more files`;
            zone.classList.add('uploaded');
            document.getElementById('zoneText').textContent = label;
        }}

        zone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', () => {{
            const files = Array.from(fileInput.files);
            if (files.length) uploadFiles(files);
        }});

        zone.addEventListener('dragover', (e) => {{
            e.preventDefault();
            zone.classList.add('dragover');
        }});

        zone.addEventListener('dragleave', () => {{
            zone.classList.remove('dragover');
        }});

        function uploadFiles(files) {{
            const allowed = files.filter(f => f.name.endsWith('.txt') || f.name.endsWith('.pdf'));
            if (!allowed.length) {{
                zone.textContent = 'Only .txt and .pdf files are supported';
                return;
            }}

            const uploads = allowed.map(file => {{
                const formData = new FormData();
                formData.append('file', file);
                return fetch('/upload', {{ method: 'POST', body: formData }})
                    .then(res => res.json())
                    .then(() => uploadedNames.push(file.name));
            }});

            Promise.all(uploads)
                .then(() => {{ updateZoneLabel(); loadQueue(); }})
                .catch(() => {{
                    zone.textContent = 'Upload failed. Is the server running?';
                }});
        }}

        zone.addEventListener('drop', (e) => {{
            e.preventDefault();
            zone.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            if (files.length) uploadFiles(files);
        }});
        let mouseX = 0, mouseY = 0;

        document.addEventListener('mousemove', (e) => {{
            mouseX = (e.clientX / window.innerWidth - 0.5) * 60;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 60;
            updateBackground();
        }});

        window.addEventListener('scroll', () => {{
            updateBackground();
        }});

        function updateBackground() {{
            const scrollY = window.scrollY * 0.15;
            document.body.style.backgroundPosition = `calc(50% + ${{-mouseX}}px) calc(50% + ${{-mouseY + scrollY}}px)`;
        }}
    </script>

    </div>
</body>
</html>"""
