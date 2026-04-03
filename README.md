# AI Document Analyzer

A command-line tool that uses the Claude API to extract structured information from any text document.

## What it does

Feed it a `.txt` file and it returns:

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
├── sample_docs/
│   └── sample.txt   # Example document (Q1 business review)
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

Run on the included sample document:

```bash
python main.py
```

Run on your own document:

```bash
python main.py path/to/your/document.txt
```

## Customizing what gets extracted

Edit [extractor.py](extractor.py) — the `EXTRACTION_SCHEMA` dict controls what fields Claude is asked to return, and `build_prompt` controls the instructions sent to the model.

## Requirements

- Python 3.8+
- [Anthropic API key](https://console.anthropic.com/)
