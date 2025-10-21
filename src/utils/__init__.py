"""
Utility functions for Telegram Downloader
"""
import os
import json
from datetime import datetime
from pathlib import Path


def save_state(downloads, downloads_json_path):
    """Save download state to JSON file"""
    with open(downloads_json_path, "w") as f:
        json.dump(downloads, f, indent=2, default=str)


def load_state(downloads_json_path):
    """Load previous downloads from JSON file"""
    try:
        with open(downloads_json_path, "r") as f:
            saved_data = json.load(f)
            if isinstance(saved_data, list):
                return saved_data
            else:
                return saved_data.get("downloads", [])
    except Exception:
        return []


def human_readable_size(num_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}PB"


def format_time(seconds):
    """Format seconds into human readable time"""
    if not seconds:
        return "-"
    seconds = int(seconds)
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"


def get_media_folder(mime_type):
    """Determine folder based on mime type"""
    if mime_type:
        if mime_type.startswith("image/"):
            return "Images"
        elif mime_type.startswith("video/"):
            return "Videos"
    return "Documents"
