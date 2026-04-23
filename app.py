"""
app.py — Flask web server for the AI Document Analyzer.

Run with:
    python app.py

Then open: http://localhost:8080
"""

import glob
import os
import re
import subprocess
import sys
from flask import Flask, send_from_directory, redirect, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

RESULTS_DIR = os.path.abspath("results")
os.makedirs(os.path.abspath("sample_docs"), exist_ok=True)


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
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Only .txt and .pdf files are allowed"}), 400

    save_path = os.path.join(SAMPLE_DOCS_DIR, filename)
    file.save(save_path)

    return jsonify({"success": True, "filename": filename})


@app.route("/queue")
def queue():
    """Returns the list of files currently in sample_docs/."""
    files = sorted(f for f in os.listdir(SAMPLE_DOCS_DIR) if f.endswith((".txt", ".pdf")))
    return jsonify({"files": files})


@app.route("/remove/<filename>", methods=["POST"])
def remove_queued(filename):
    """Removes a file from sample_docs/."""
    if not re.fullmatch(r"[\w\-. ]+", filename):
        return jsonify({"error": "Invalid filename"}), 400

    path = os.path.join(SAMPLE_DOCS_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    return jsonify({"success": True})


@app.route("/delete/<stem>", methods=["POST"])
def delete_result(stem):
    """Deletes all JSON files for a document stem and rebuilds the report."""
    if not re.fullmatch(r"[\w\-. ]+", stem):
        return jsonify({"error": "Invalid document name"}), 400

    pattern = os.path.join(RESULTS_DIR, f"{stem}_*.json")
    for f in glob.glob(pattern):
        os.remove(f)

    from reporter import generate_report
    generate_report()
    return jsonify({"success": True})


@app.route("/run")
def run_analysis():
    """Triggers main.py and redirects back to the index when done."""
    docs = [f for f in os.listdir(SAMPLE_DOCS_DIR) if f.endswith((".txt", ".pdf"))]
    if not docs:
        return jsonify({"error": "No documents found in sample_docs/. Upload a file first."}), 400

    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError:
        return jsonify({"error": "Analysis failed. Check the terminal for details."}), 500
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
