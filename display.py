"""
display.py — Formats and prints extracted results.

Keeps all print/formatting logic out of the business logic files.
In a real app, this could be replaced with a web UI or JSON API response.
"""


def display_results(data: dict) -> None:
    """Prints the extracted document data in a readable format."""

    divider = "=" * 55

    print(f"\n{divider}")
    print("  DOCUMENT ANALYSIS RESULTS")
    print(divider)

    print(f"\n  Title       : {data.get('title', 'N/A')}")
    print(f"  Type        : {data.get('document_type', 'N/A')}")
    print(f"  Sentiment   : {_sentiment_label(data.get('sentiment', ''))}")

    print(f"\n  SUMMARY")
    print(f"  {data.get('summary', 'N/A')}")

    key_points = data.get("key_points", [])
    if key_points:
        print(f"\n  KEY POINTS")
        for i, point in enumerate(key_points, 1):
            print(f"  {i}. {point}")

    entities = data.get("entities", {})
    people = entities.get("people", [])
    orgs = entities.get("organizations", [])
    dates = entities.get("dates", [])

    if any([people, orgs, dates]):
        print(f"\n  ENTITIES FOUND")
        if people:
            print(f"  People        : {', '.join(people)}")
        if orgs:
            print(f"  Organizations : {', '.join(orgs)}")
        if dates:
            print(f"  Dates         : {', '.join(dates)}")

    action_items = data.get("action_items", [])
    if action_items:
        print(f"\n  ACTION ITEMS")
        for item in action_items:
            print(f"  - {item}")

    print(f"\n{divider}\n")


def _sentiment_label(sentiment: str) -> str:
    icons = {"positive": "Positive", "negative": "Negative", "neutral": "Neutral"}
    return icons.get(sentiment.lower(), sentiment)
