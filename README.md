# AI Document Analyzer

> This project was built with [Claude Code](https://claude.ai/code) by Anthropic. The code, structure, and features were developed through a conversation-driven workflow with Claude as the coding assistant.

A web-based tool that uses the Claude API to extract structured information from text and PDF documents, with a local browser interface for viewing results and triggering analysis.

## What it does

Drop `.txt` or `.pdf` files into a folder and it returns:

- Title and document type
- 2–3 sentence summary
- Up to 5 key points
- Sentiment (positive / negative / neutral)
- Entities — people, organizations, and dates mentioned
- Action items or follow-ups

Results are printed in the terminal, saved as individual JSON files, and compiled into a clean HTML report you can open in any browser.

## Project structure

```
ai-document-analyzer/
├── main.py          # Entry point, loops through all files
├── analyzer.py      # Claude API integration
├── extractor.py     # Extraction schema and prompt builder
├── display.py       # Terminal output formatting
├── saver.py         # Auto-saves each result as JSON
├── reporter.py      # Generates persistent history HTML report
├── app.py           # Flask web server
├── sample_docs/     # Drop your .txt and .pdf files here
├── results/         # Auto-created — JSON + HTML output (gitignored)
├── requirements.txt
└── .env.example
```

## Setup

1. Clone the repo and create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY=your-key-here
```

## Usage

Start the web server:

```bash
source venv/bin/activate
python app.py
```

Then open `http://localhost:8080` in your browser.

From there:
1. Drag and drop a `.txt` or `.pdf` file onto the drop zone, or click it to browse — files are saved to `sample_docs/` automatically
2. Check the queue panel to see and remove files before running
3. Click **Run Analysis** to analyze any new files
4. Results appear on the page grouped by run, newest at the top

First-time visitors see a welcome screen with instructions. Export All and Run Analysis buttons are disabled when there are no documents. Already analyzed documents are skipped — only new files are sent to Claude. All results are stored as JSON in `results/` and displayed in a full history view with each run collapsible. Individual results can be deleted from the history. Use the search bar to filter by any text, and export results to CSV via Export All or by selecting individual documents.

## Customizing what gets extracted

Edit [extractor.py](extractor.py) — the `EXTRACTION_SCHEMA` dict controls what fields Claude is asked to return, and `build_prompt` controls the instructions sent to the model.

## Requirements

- Python 3.8+
- [Anthropic API key](https://console.anthropic.com/)
