"""
Telegram client and download handler
"""
import os
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events, errors
from src.config import API_ID, API_HASH, CHAT_ID, DOWNLOAD_DIR, MAX_RETRIES, SESSION_FILE
from src.utils import save_state, human_readable_size


class TelegramDownloader:
    def __init__(self, downloads, download_tasks):
        self.downloads = downloads
        self.download_tasks = download_tasks
        self.client = TelegramClient(str(SESSION_FILE), API_ID, API_HASH)
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """Setup Telegram event handlers"""
        @self.client.on(events.NewMessage(chats=CHAT_ID))
        async def handle_new_file(event):
            await self._handle_new_file(event)

    async def edit_status_message(self, event, entry, status=None):
        """Edits the Telegram message with the current download status."""
        try:
            client = event.client
            if not entry.get("_status_msg_id"):
                return
            msg = await client.get_messages(event.chat_id, ids=entry["_status_msg_id"])
            emoji_map = {"Downloading": "⬇️", "Downloaded": "✅", "Failed": "❌", "Stopped": "🛑"}
            if status is None:
                text = f"⬇️ Status: Downloading {entry.get('progress', 0)}% ({human_readable_size(entry.get('downloaded_bytes', 0))}/{human_readable_size(entry.get('total_bytes', 0))})"
            else:
                text = f"{emoji_map.get(status, '')} Status: {status}"
            await msg.edit(text)
        except Exception as e:
            logging.error(f"Failed to edit status message: {e}")

    async def safe_download(self, event, path, entry):
        """Downloads the media safely with live progress."""
        last_bytes = 0
        start_time = datetime.now()
        last_update = 0  # timestamp of last message edit

        # Send initial "Downloading" message
        try:
            msg = await event.reply("⬇️ Status: Downloading")
            entry["_status_msg_id"] = msg.id
        except Exception as e:
            logging.error(f"Failed to send initial status message: {e}")
            entry["_status_msg_id"] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                def progress_callback(current, total):
                    nonlocal last_bytes, start_time, last_update
                    now = datetime.now()
                    delta = (now - start_time).total_seconds()
                    if delta > 0:
                        entry["speed"] = round((current - last_bytes) / 1024 / delta, 1)
                    last_bytes = current
                    start_time = now

                    entry["progress"] = round(current / total * 100, 1)
                    entry["downloaded_bytes"] = current
                    entry["total_bytes"] = total
                    if entry["speed"] > 0:
                        remaining_bytes = total - current
                        entry["pending_time"] = remaining_bytes / (entry["speed"] * 1024)
                    else:
                        entry["pending_time"] = None
                    save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")

                    # Throttle edits: 1 per second
                    timestamp = now.timestamp()
                    if entry.get("_status_msg_id") and timestamp - last_update >= 20:
                        last_update = timestamp
                        asyncio.create_task(self.edit_status_message(event, entry))

                await event.download_media(file=path, progress_callback=progress_callback)

                # Final update
                entry["status"] = "done"
                entry["progress"] = 100
                entry["speed"] = 0
                entry["pending_time"] = 0
                save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")
                if entry.get("_status_msg_id"):
                    await self.edit_status_message(event, entry, "Downloaded")
                return

            except asyncio.CancelledError:
                entry["status"] = "stopped"
                entry["speed"] = 0
                save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")
                if entry.get("_status_msg_id"):
                    await self.edit_status_message(event, entry, "Stopped")
                return
            except Exception as e:
                entry["error"] = f"Attempt {attempt}/{MAX_RETRIES} failed: {str(e)}"
                logging.error(entry["error"])
                await asyncio.sleep(5)

        entry["status"] = "failed"
        entry["speed"] = 0
        entry["pending_time"] = None
        save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")
        if entry.get("_status_msg_id"):
            await self.edit_status_message(event, entry, "Failed")

    async def _handle_new_file(self, event):
        """Handle new file messages from Telegram"""
        if not event.file:
            return
        
        from src.utils import get_media_folder
        kind = get_media_folder(event.file.mime_type)
        
        folder = DOWNLOAD_DIR / kind
        folder.mkdir(exist_ok=True)

        filename = event.file.name or f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        path = folder / filename

        entry = {
            "file": filename,
            "status": "downloading",
            "progress": 0,
            "speed": 0,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "downloaded_bytes": 0,
            "total_bytes": 0,
            "pending_time": None,
            "_status_msg_id": None
        }
        self.downloads.insert(0, entry)
        save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")

        # Start the download task
        task = asyncio.create_task(self.safe_download(event, str(path), entry))
        self.download_tasks[filename] = task

    def start(self):
        """Start the Telegram client"""
        print("🚀 Telegram Downloader running...")
        self.client.start()
        self.client.run_until_disconnected()

    def stop(self):
        """Stop the Telegram client"""
        self.client.disconnect()
