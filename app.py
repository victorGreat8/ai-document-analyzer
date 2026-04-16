"""
app.py — Flask web server for the AI Document Analyzer.

Run with:
    python app.py

Then open: http://localhost:8080
"""

import os
import subprocess
import sys
from flask import Flask, send_from_directory, redirect, request, jsonify

app = Flask(__name__)

RESULTS_DIR = os.path.abspath("results")


@app.route("/")
def index():
    """Serves the history report."""
    if not os.path.exists(os.path.join(RESULTS_DIR, "index.html")):
        return "<p>No results yet. Run <code>python main.py</code> first.</p>", 404
    return send_from_directory(RESULTS_DIR, "index.html")


SAMPLE_DOCS_DIR = os.path.abspath("sample_docs")
ALLOWED_EXTENSIONS = {".txt", ".pdf"}


@app.route("/upload", methods=["POST"])
def upload_file():
    """Receives a file from the browser and saves it to sample_docs/."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Only .txt and .pdf files are allowed"}), 400

    save_path = os.path.join(SAMPLE_DOCS_DIR, file.filename)
    file.save(save_path)

    return jsonify({"success": True, "filename": file.filename})


@app.route("/run")
def run_analysis():
    """Triggers main.py and redirects back to the index when done."""
    subprocess.run([sys.executable, "main.py"], check=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
