import threading
import logging
import os
import shutil
from server.gateway.api_gateway import app as gateway_app, setup_ngrok
from server.services.download_service import app as download_app
from server.config import Config
from pyngrok.exception import PyngrokNgrokError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_gateway():
    try:
        setup_ngrok()
        logger.info(f"Starting API Gateway on port {Config.API_GATEWAY_PORT}")
        gateway_app.run(
            port=Config.API_GATEWAY_PORT, debug=Config.DEBUG, use_reloader=False
        )
    except PyngrokNgrokError as e:
        logger.error(f"Failed to start ngrok: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Gateway: {e}")
        raise


def run_download_service():
    try:
        logger.info(f"Starting Download Service on port {Config.DOWNLOAD_SERVICE_PORT}")
        download_app.run(
            port=Config.DOWNLOAD_SERVICE_PORT, debug=Config.DEBUG, use_reloader=False
        )
    except Exception as e:
        logger.error(f"Unexpected error in Download Service: {e}")
        raise


if __name__ == "__main__":
    # Установка рабочей директории
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.info(f"Current working directory: {os.getcwd()}")

    # Инициализация папки uploads
    if os.path.exists(Config.UPLOAD_FOLDER):
        shutil.rmtree(Config.UPLOAD_FOLDER)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    gateway_thread = threading.Thread(target=run_gateway, name="GatewayThread")
    download_thread = threading.Thread(
        target=run_download_service, name="DownloadThread"
    )

    logger.info("Starting Download Service and API Gateway...")
    download_thread.start()
    gateway_thread.start()

    try:
        download_thread.join()
        gateway_thread.join()
    except KeyboardInterrupt:
        logger.info("Shutting down services...")
