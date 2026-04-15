# AI Document Analyzer

> This project was built with [Claude Code](https://claude.ai/code) by Anthropic. The code, structure, and features were developed through a conversation-driven workflow with Claude as the coding assistant.

A command-line tool that uses the Claude API to extract structured information from text and PDF documents.

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
├── reporter.py      # Generates combined HTML report
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

Analyze all documents in the default folder:

```bash
source venv/bin/activate
python main.py
```

Analyze documents in a different folder:

```bash
python main.py path/to/your/folder
```

Both `.txt` and `.pdf` files are supported. After each run:
- Each document is saved as a JSON file in `results/`
- A combined HTML report is saved in `results/` — open it in any browser to view all results in one place

## Customizing what gets extracted

Edit [extractor.py](extractor.py) — the `EXTRACTION_SCHEMA` dict controls what fields Claude is asked to return, and `build_prompt` controls the instructions sent to the model.

## Requirements

- Python 3.8+
- [Anthropic API key](https://console.anthropic.com/)
