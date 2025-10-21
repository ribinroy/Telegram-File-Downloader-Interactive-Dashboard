#!/usr/bin/env python3
"""
Setup script for Telegram Downloader
"""
import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating necessary directories...")
    directories = ["downloads", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_config():
    """Check if configuration needs to be updated"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  Please create .env file from .env.example:")
            print("   cp .env.example .env")
            print("   Then edit .env with your API credentials")
        else:
            print("⚠️  Please create .env file with your API credentials")
        return False
    
    with open(env_file, "r") as f:
        content = f.read()
        if "your_api_id_here" in content or "your_api_hash_here" in content:
            print("⚠️  Please update your API credentials in .env file")
            print("   - Get API_ID and API_HASH from https://my.telegram.org")
            print("   - Update CHAT_ID with your target chat ID")
            return False
    print("✅ Configuration looks good!")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Telegram Downloader...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check configuration
    config_ok = check_config()
    
    print("\n🎉 Setup completed!")
    if not config_ok:
        print("⚠️  Remember to update your configuration before running the application!")
    print("\nTo start the application, run:")
    print("  python main.py")

if __name__ == "__main__":
    main()
