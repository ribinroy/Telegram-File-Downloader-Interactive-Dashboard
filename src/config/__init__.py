"""
Configuration module for Telegram Downloader
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory - adjust this to your project root
BASE_DIR = Path(__file__).parent.parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
LOGS_DIR = BASE_DIR / "logs"

# Telegram API Configuration - loaded from environment variables
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', 'your_api_hash_here')
CHAT_ID = int(os.getenv('CHAT_ID', '0'))

# Validate configuration
def validate_config():
    """Validate that required configuration is set"""
    errors = []
    
    if API_ID == 0 or API_ID == '0':
        errors.append("API_ID is not set or is invalid")
    
    if API_HASH == 'your_api_hash_here' or not API_HASH:
        errors.append("API_HASH is not set")
    
    if CHAT_ID == 0 or CHAT_ID == '0':
        errors.append("CHAT_ID is not set or is invalid")
    
    if errors:
        print("❌ Configuration Error:")
        for error in errors:
            print(f"   - {error}")
        print("\n📝 Please set up your .env file:")
        print("   1. Copy .env.example to .env: cp .env.example .env")
        print("   2. Edit .env with your actual API credentials")
        print("   3. Get credentials from https://my.telegram.org")
        return False
    
    return True

# Web Interface Configuration
WEB_PORT = int(os.getenv('WEB_PORT', '4444'))
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')

# Download Configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '6'))
SESSION_FILE = BASE_DIR / "downloader_session"
DOWNLOADS_JSON = BASE_DIR / "downloads.json"
LOG_FILE = LOGS_DIR / "telegram_downloader.log"

# Create necessary directories
DOWNLOAD_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Media type folders
MEDIA_FOLDERS = {
    "Documents": "Documents",
    "Images": "Images", 
    "Videos": "Videos"
}
