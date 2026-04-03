"""
analyzer.py — Talks to the Claude API.

This module has one job: send a document to Claude and return
the structured JSON response. All API configuration lives here.
"""

import json
import anthropic
from extractor import build_prompt


def analyze_document(document_text: str) -> dict:
    """
    Sends the document to Claude and returns extracted data as a Python dict.

    Args:
        document_text: The raw text content of the document

    Returns:
        A dict containing the extracted structured information
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

    prompt = build_prompt(document_text)

    print("Sending document to Claude for analysis...")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    # Extract the text content from Claude's response
    raw_output = response.content[0].text

    # Strip markdown code fences if Claude wrapped the JSON in ```json ... ```
    raw_output = raw_output.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.split("\n", 1)[-1]  # remove first line (```json)
        raw_output = raw_output.rsplit("```", 1)[0]  # remove closing ```
        raw_output = raw_output.strip()

    # Parse the JSON string into a Python dict
    extracted_data = json.loads(raw_output)

    return extracted_data
