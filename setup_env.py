#!/usr/bin/env python3
"""
Environment setup script for Telegram Downloader
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from .env.example"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    # Copy .env.example to .env
    with open(env_example, "r") as f:
        content = f.read()
    
    with open(env_file, "w") as f:
        f.write(content)
    
    print("✅ Created .env file from .env.example")
    print("📝 Please edit .env file with your actual API credentials:")
    print("   - Get API_ID and API_HASH from https://my.telegram.org")
    print("   - Update CHAT_ID with your target chat ID")
    return True

def get_user_input():
    """Get API credentials from user"""
    print("\n🔧 Let's set up your API credentials:")
    print("1. Go to https://my.telegram.org")
    print("2. Log in with your phone number")
    print("3. Go to 'API development tools'")
    print("4. Create a new application")
    print()
    
    api_id = input("Enter your API_ID: ").strip()
    api_hash = input("Enter your API_HASH: ").strip()
    chat_id = input("Enter your CHAT_ID (negative number for groups): ").strip()
    
    if not api_id or not api_hash or not chat_id:
        print("❌ All fields are required!")
        return None, None, None
    
    return api_id, api_hash, chat_id

def update_env_file(api_id, api_hash, chat_id):
    """Update .env file with user credentials"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, "r") as f:
        content = f.read()
    
    # Replace values
    content = content.replace("API_ID=your_api_id_here", f"API_ID={api_id}")
    content = content.replace("API_HASH=your_api_hash_here", f"API_HASH={api_hash}")
    content = content.replace("CHAT_ID=your_chat_id_here", f"CHAT_ID={chat_id}")
    
    # Write back
    with open(env_file, "w") as f:
        f.write(content)
    
    print("✅ Updated .env file with your credentials")
    return True

def main():
    """Main setup function"""
    print("🚀 Telegram Downloader Environment Setup")
    print("=" * 40)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Get user credentials
    api_id, api_hash, chat_id = get_user_input()
    if not api_id:
        return
    
    # Update .env file
    if update_env_file(api_id, api_hash, chat_id):
        print("\n🎉 Setup completed successfully!")
        print("You can now run: python main.py")
    else:
        print("\n❌ Setup failed!")

if __name__ == "__main__":
    main()
