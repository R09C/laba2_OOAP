from flask import Flask, request, jsonify, render_template
from pyngrok import ngrok
import os
import uuid
import logging
import shutil
import argparse
import requests
from server.config import Config

app = Flask(
    __name__, template_folder=os.path.join(os.path.dirname(__file__), "templates")
)
app.config.from_object(Config)
logging.basicConfig(level=logging.INFO)

task_statuses = {}


def upload_dataset(file_path, server_url):
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{server_url}/upload_dataset", files=files)
            response.raise_for_status()
            result = response.json()
            if result["status"] == "success":
                print(f"File uploaded successfully: {result['message']}")
                print(f"Task ID: {result['task_id']}")
            else:
                print(f"File upload failed: {result['message']}")
    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error during upload request: {e}")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/status/<task_id>")
def task_status(task_id):
    if task_id in task_statuses:
        return jsonify(task_statuses[task_id]), 200
    return jsonify({"message": "Task not found", "status": "error"}), 404


@app.route("/upload_dataset", methods=["POST"])
def upload_dataset_route():
    if "file" not in request.files:
        return jsonify({"message": "No file part in request", "status": "error"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No file selected", "status": "error"}), 400
    task_id = str(uuid.uuid4())
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], task_id)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, file.filename)
    file.save(file_path)
    task_statuses[task_id] = {
        "status": "success",
        "message": "Dataset uploaded successfully",
        "path": file_path,
    }
    return (
        jsonify(
            {
                "message": "Dataset uploaded successfully",
                "status": "success",
                "task_id": task_id,
            }
        ),
        200,
    )


def setup_ngrok():
    public_url = ngrok.connect(Config.API_GATEWAY_PORT)
    print(f"Server running at: {public_url}")
    return public_url


def main():
    parser = argparse.ArgumentParser(
        description="Upload a dataset file to the server or start the server."
    )
    parser.add_argument("--file_path", type=str, help="Path to the file to upload.")
    parser.add_argument(
        "--server_url", type=str, help="URL of the server (if uploading a file)."
    )
    args = parser.parse_args()
    if os.path.exists(Config.UPLOAD_FOLDER):
        shutil.rmtree(Config.UPLOAD_FOLDER)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    if args.file_path:
        if not args.server_url:
            print("Error: --server_url must be provided when uploading a file.")
            return
        upload_dataset(args.file_path, args.server_url)
    else:
        public_url = setup_ngrok()
        app.run(port=Config.API_GATEWAY_PORT, debug=Config.DEBUG, use_reloader=False)


if __name__ == "__main__":
    main()
