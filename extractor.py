"""
extractor.py — Defines what to extract from documents.

This is where you control the AI's behavior:
- The SCHEMA tells Claude what fields to return
- The PROMPT tells Claude how to analyze the document

To extract different information, just edit this file.
"""

# The fields we want Claude to extract from any document
EXTRACTION_SCHEMA = {
    "title": "The document title or best inferred title",
    "document_type": "Type of document (e.g. business report, news article, contract, email)",
    "summary": "A concise 2-3 sentence summary of the document",
    "key_points": "A list of the most important points (max 5)",
    "sentiment": "Overall tone: positive, negative, or neutral",
    "entities": {
        "people": "List of people mentioned",
        "organizations": "List of organizations mentioned",
        "dates": "List of dates or time periods mentioned",
    },
    "action_items": "Any tasks, decisions, or follow-ups mentioned (empty list if none)",
}


def build_prompt(document_text: str) -> str:
    """
    Builds the prompt we send to Claude.
    Combines the document text with clear instructions to return structured JSON.
    """
    schema_description = """
{
  "title": "string",
  "document_type": "string",
  "summary": "string",
  "key_points": ["string", "string", "..."],
  "sentiment": "positive | negative | neutral",
  "entities": {
    "people": ["string"],
    "organizations": ["string"],
    "dates": ["string"]
  },
  "action_items": ["string"]
}"""

    prompt = f"""Analyze the following document and extract structured information from it.

Return ONLY a valid JSON object with this exact structure:
{schema_description}

Rules:
- Return only JSON, no explanation or markdown
- If a field has no data, use an empty list [] or empty string ""
- Keep the summary under 3 sentences
- Limit key_points to the 5 most important

DOCUMENT:
{document_text}"""

    return prompt
