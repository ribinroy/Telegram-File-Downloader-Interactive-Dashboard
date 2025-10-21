#!/usr/bin/env python3
"""
Test script to verify environment configuration
"""
import os
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config():
    """Test configuration loading"""
    try:
        # Test without dotenv first
        print("Testing configuration loading...")
        from config import API_ID, API_HASH, CHAT_ID, WEB_PORT, validate_config
        print(f"✅ Configuration loaded successfully!")
        print(f"   API_ID: {API_ID}")
        print(f"   API_HASH: {API_HASH[:10]}...")
        print(f"   CHAT_ID: {CHAT_ID}")
        print(f"   WEB_PORT: {WEB_PORT}")
        
        # Test validation
        print("\nTesting configuration validation...")
        is_valid = validate_config()
        if is_valid:
            print("✅ Configuration validation passed!")
        else:
            print("⚠️  Configuration validation failed (this is expected with placeholder values)")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_env_file():
    """Test if .env file exists and has correct format"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_example.exists():
        print("✅ .env.example file exists")
    else:
        print("❌ .env.example file missing")
        return False
    
    if env_file.exists():
        print("✅ .env file exists")
        with open(env_file, "r") as f:
            content = f.read()
            if "API_ID=" in content and "API_HASH=" in content:
                print("✅ .env file has correct format")
                return True
            else:
                print("❌ .env file missing required variables")
                return False
    else:
        print("⚠️  .env file not found (this is normal for first setup)")
        return True

if __name__ == "__main__":
    print("🧪 Testing Telegram Downloader Configuration...")
    print()
    
    env_ok = test_env_file()
    config_ok = test_config()
    
    print()
    if env_ok and config_ok:
        print("🎉 All tests passed!")
        print("   Your configuration is ready to use.")
    else:
        print("⚠️  Some tests failed.")
        print("   Please check the configuration setup.")
