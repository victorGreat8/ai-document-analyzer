"""
main.py — Entry point for the AI Document Analyzer.

Run with:
    python main.py
    python main.py path/to/your/document.txt
"""

import sys
import os
from dotenv import load_dotenv
from analyzer import analyze_document
from display import display_results

# Load ANTHROPIC_API_KEY from .env file
load_dotenv()


def read_document(file_path: str) -> str:
    """Reads a text file and returns its content."""
    if not os.path.exists(file_path):
        print(f"Error: File not found — '{file_path}'")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    # Use a custom file path if provided, otherwise use the sample
    file_path = sys.argv[1] if len(sys.argv) > 1 else "sample_docs/sample.txt"

    print(f"Reading document: {file_path}")
    document_text = read_document(file_path)

    # Send to Claude and get structured data back
    extracted_data = analyze_document(document_text)

    # Print the results
    display_results(extracted_data)


if __name__ == "__main__":
    main()
