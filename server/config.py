import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB
    DOWNLOAD_SERVICE_URL = "http://127.0.0.1:5001"
    API_GATEWAY_PORT = 5000
    DOWNLOAD_SERVICE_PORT = 5001
    DEBUG = True
