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
from saver import save_result

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
    folder = sys.argv[1] if len(sys.argv) > 1 else "sample_docs"

    txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]

    if not txt_files:
        print(f"No .txt files found in '{folder}'")
        sys.exit(1)

    for filename in txt_files:
        path = os.path.join(folder, filename)
        print(f"\nReading document: {path}")
        document_text = read_document(path)

        extracted_data = analyze_document(document_text)
        display_results(extracted_data)

        saved_path = save_result(filename, extracted_data)
        print(f"  Result saved to: {saved_path}")


if __name__ == "__main__":
    main()
