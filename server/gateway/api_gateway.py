from flask import Flask, request, jsonify, render_template
from pyngrok import ngrok
import requests
import logging
import os
from ..config import Config

app = Flask(
    __name__, template_folder=os.path.join(os.path.dirname(__file__), "..", "templates")
)
app.config.from_object(Config)
logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/status/<task_id>")
def task_status(task_id):
    try:
        response = requests.get(
            f"{Config.DOWNLOAD_SERVICE_URL}/status/{task_id}", timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"Status check error: {e}", "status": "error"}), 503


@app.route("/upload_dataset", methods=["POST"])
def upload_dataset():
    if "file" not in request.files:
        return jsonify({"message": "No file part in request", "status": "error"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected", "status": "error"}), 400

    try:
        files = {"file": (file.filename, file.stream, file.mimetype)}
        response = requests.post(
            f"{Config.DOWNLOAD_SERVICE_URL}/upload_dataset", files=files, timeout=30
        )
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return (
            jsonify({"message": f"Upload service error: {e}", "status": "error"}),
            503,
        )


def setup_ngrok():
    public_url = ngrok.connect(Config.API_GATEWAY_PORT)
    print(f"API Gateway running at: {public_url}")
