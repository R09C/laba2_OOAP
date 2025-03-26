from flask import Flask, request, jsonify
import os
import shutil
import logging
import uuid
from ..config import Config
import json
from ..repo.mongo_bd import MongoSave

app = Flask(__name__)
app.config.from_object(Config)
logging.basicConfig(level=logging.INFO)

task_statuses = {}


@app.route("/status/<task_id>")
def task_status(task_id):
    return jsonify(
        task_statuses.get(task_id, {"message": "Task not found", "status": "error"})
    ), (200 if task_id in task_statuses else 404)


@app.route("/upload_dataset", methods=["POST"])
def upload_dataset():
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

    is_json = file.filename.endswith(".json")
    json_data = None
    mongoSave = MongoSave()
    if is_json:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            mongoSave.save_json(json_data)
        except (json.JSONDecodeError, Exception) as e:
            task_statuses[task_id] = {
                "status": "error",
                "message": f"Failed to parse JSON: {str(e)}",
                "path": file_path,
            }
            return (
                jsonify(
                    {
                        "message": f"Failed to parse JSON: {str(e)}",
                        "status": "error",
                        "task_id": task_id,
                    }
                ),
                400,
            )

    task_statuses[task_id] = {
        "status": "success",
        "message": "Dataset uploaded successfully"
        + (" and JSON saved to MongoDB" if is_json else ""),
        "path": file_path,
        "is_json": is_json,
        "json_data": mongoSave.get_all() if is_json else None,
    }

    print(task_statuses)

    return (
        jsonify(
            {
                "message": "Dataset uploaded successfully"
                + (" and JSON saved to MongoDB" if is_json else ""),
                "status": "success",
                "task_id": task_id,
            }
        ),
        200,
    )
