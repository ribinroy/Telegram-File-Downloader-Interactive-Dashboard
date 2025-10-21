"""
Main entry point for Telegram Downloader
"""
import os
import json
import logging
import threading
from src.config import LOG_FILE, DOWNLOADS_JSON, validate_config
from src.utils import load_state
from src.telegram_handler import TelegramDownloader
from src.web_app import WebApp


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )


def main():
    """Main function to start the Telegram Downloader"""
    # Validate configuration first
    if not validate_config():
        return
    
    # Setup logging
    setup_logging()
    
    # Load previous downloads
    downloads = load_state(DOWNLOADS_JSON)
    
    # Shared download state
    download_tasks = {}  # key: filename, value: asyncio.Task
    
    # Initialize components
    telegram_downloader = TelegramDownloader(downloads, download_tasks)
    web_app = WebApp(downloads, download_tasks)
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=web_app.run, daemon=True)
    flask_thread.start()
    
    # Start Telegram client (this will block)
    telegram_downloader.start()


if __name__ == "__main__":
    main()
