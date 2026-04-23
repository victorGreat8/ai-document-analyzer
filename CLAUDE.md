# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AI Document Analyzer — a web-based tool that sends `.txt` and `.pdf` documents to the Claude API (claude-opus-4-6) and extracts structured information: title, type, summary, key points, sentiment, entities, and action items. Results are saved as JSON and displayed in a persistent browser history at `http://localhost:8080`.

## How to run

Always use the virtual environment:

```bash
source venv/bin/activate
python app.py        # starts the web server at http://localhost:8080
python main.py       # runs analysis from the terminal directly
```

**Important:** Port 5000 is blocked by Apple AirPlay on Mac. The server runs on **port 8080**.

After changing `reporter.py` or `app.py`, restart the server — Flask does not hot-reload HTML generation.

## Architecture

The flow is: `app.py` → `main.py` → `analyzer.py` → `extractor.py`, with results saved by `saver.py` and the HTML report rebuilt by `reporter.py`.

- **`app.py`** — Flask server. Three routes: `/` serves `results/index.html`, `/upload` saves dropped files to `sample_docs/`, `/run` triggers `main.py` as a subprocess.
- **`main.py`** — loops through all `.txt` and `.pdf` files in a folder, checks cache before calling Claude, then calls `generate_report()` at the end.
- **`analyzer.py`** — sends document text to Claude, strips markdown fences, parses JSON response.
- **`extractor.py`** — defines `EXTRACTION_SCHEMA` and builds the prompt. Edit this file to change what Claude extracts.
- **`saver.py`** — saves each result as `results/{docname}_{timestamp}.json`. Also provides `find_cached_result()` which checks if a document has already been analyzed.
- **`reporter.py`** — reads all JSON files from `results/`, deduplicates (newest per document), groups into runs (files within 120 seconds = same run), and writes `results/index.html`.
- **`display.py`** — terminal-only formatting, not used by the web flow.

## Key design decisions

- **No database** — JSON files in `results/` are the storage layer. Each document gets one JSON file named `{docname}_{YYYY-MM-DD_HH-MM-SS}.json`.
- **Cache before API call** — `find_cached_result()` in `saver.py` checks for existing JSON before sending to Claude. Already-analyzed documents are never re-sent (saves API cost).
- **Run grouping** — `reporter.py` groups JSON files into "runs" using a 120-second time window. Files saved within 2 minutes of each other are considered the same run. The `results/` folder is gitignored.
- **HTML escaping** — all Claude-generated content is passed through `html.escape()` in `reporter.py` before being inserted into HTML.
- **Filename security** — uploaded filenames are sanitized with `werkzeug.utils.secure_filename` before saving.

## Storage layout

```
sample_docs/    ← source documents (.txt and .pdf)
results/        ← gitignored; contains per-document JSON files + index.html
```

## How to approach changes

When making a bigger change — adding a feature, fixing multiple files, or changing how something works — always go step by step:

1. State what the change is and why before touching any code
2. Make one change at a time and explain what each step does
3. Verify each step works before moving to the next
4. Don't make several edits at once without explaining them

This keeps the user informed and makes it easy to catch mistakes early.

## Before committing and pushing to GitHub

Always check if `README.md` needs to be updated to reflect any changes made. Update it if the usage, structure, features, or setup instructions have changed, then include it in the commit.
