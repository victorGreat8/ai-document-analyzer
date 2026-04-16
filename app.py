"""
app.py — Flask web server for the AI Document Analyzer.

Run with:
    python app.py

Then open: http://localhost:8080
"""

import os
import subprocess
import sys
from flask import Flask, send_from_directory, redirect

app = Flask(__name__)

RESULTS_DIR = os.path.abspath("results")


@app.route("/")
def index():
    """Serves the history report."""
    if not os.path.exists(os.path.join(RESULTS_DIR, "index.html")):
        return "<p>No results yet. Run <code>python main.py</code> first.</p>", 404
    return send_from_directory(RESULTS_DIR, "index.html")


@app.route("/run")
def run_analysis():
    """Triggers main.py and redirects back to the index when done."""
    subprocess.run([sys.executable, "main.py"], check=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
