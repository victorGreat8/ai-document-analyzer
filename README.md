# AI Document Analyzer

A command-line tool that uses the Claude API to extract structured information from any text document.

## What it does

Feed it a folder of `.txt` files and it returns:

- Title and document type
- 2–3 sentence summary
- Up to 5 key points
- Sentiment (positive / negative / neutral)
- Entities — people, organizations, and dates mentioned
- Action items or follow-ups

## Project structure

```
ai-document-analyzer/
├── main.py          # Entry point
├── analyzer.py      # Claude API integration
├── extractor.py     # Extraction schema and prompt builder
├── display.py       # Terminal output formatting
├── saver.py         # Auto-saves results to results/ folder
├── sample_docs/     # Put your .txt documents here
├── results/         # Auto-created — JSON result files saved here (gitignored)
├── requirements.txt
└── .env.example
```

## Setup

1. Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY=your-key-here
```

## Usage

Run on the included sample documents:

```bash
python3 main.py
```

Run on a different folder:

```bash
python3 main.py path/to/your/folder
```

Every `.txt` file in the folder is analyzed. Results are printed in the terminal and automatically saved as JSON files in the `results/` folder.

## Customizing what gets extracted

Edit [extractor.py](extractor.py) — the `EXTRACTION_SCHEMA` dict controls what fields Claude is asked to return, and `build_prompt` controls the instructions sent to the model.

## Requirements

- Python 3.8+
- [Anthropic API key](https://console.anthropic.com/)
