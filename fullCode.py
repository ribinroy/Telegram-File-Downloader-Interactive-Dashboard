import os
import json
import asyncio
import logging
import threading
import traceback
from datetime import datetime
from telethon import TelegramClient, events, errors
from flask import Flask, jsonify, render_template_string, request

# ======== CONFIG ========
BASE_DIR = "/home/hs/telegram_downloader"
DOWNLOAD_DIR = "/mnt/newhdd/Downloads/Telegram"
API_ID = 29621450
API_HASH = "9f7724268952b35c84f76f41c6c10642"
CHAT_ID = -4903711319
WEB_PORT = 4444
MAX_RETRIES = 6
DOWNLOADS_JSON = os.path.join(BASE_DIR, "downloads.json")
# ========================

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

client = TelegramClient(os.path.join(BASE_DIR, "downloader_session"), API_ID, API_HASH)

# Shared download state
downloads = []
download_tasks = {}  # key: filename, value: asyncio.Task

# Setup logging
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "telegram_downloader.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load previous downloads
try:
    with open(DOWNLOADS_JSON, "r") as f:
        saved_data = json.load(f)
        if isinstance(saved_data, list):
            downloads.extend(saved_data)
        else:
            downloads.extend(saved_data.get("downloads", []))
except Exception:
    downloads = []

# ======== HELPERS ========
def save_state():
    with open(DOWNLOADS_JSON, "w") as f:
        json.dump(downloads, f, indent=2, default=str)

def human_readable_size(num_bytes):
    for unit in ['B','KB','MB','GB','TB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}PB"

def format_time(seconds):
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

# ======== TELETHON DOWNLOAD ========
async def edit_status_message(event, entry, status=None):
    """Edits the Telegram message with the current download status."""
    try:
        client = event.client
        if not entry.get("_status_msg_id"):
            return
        msg = await client.get_messages(event.chat_id, ids=entry["_status_msg_id"])
        emoji_map = {"Downloading":"⬇️","Downloaded":"✅","Failed":"❌","Stopped":"🛑"}
        if status is None:
            text = f"⬇️ Status: Downloading {entry.get('progress',0)}% ({human_readable_size(entry.get('downloaded_bytes',0))}/{human_readable_size(entry.get('total_bytes',0))})"
        else:
            text = f"{emoji_map.get(status,'')} Status: {status}"
        await msg.edit(text)
    except Exception as e:
        logging.error(f"Failed to edit status message: {e}")

async def safe_download(event, path, entry):
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
                save_state()

                # Throttle edits: 1 per second
                timestamp = now.timestamp()
                if entry.get("_status_msg_id") and timestamp - last_update >= 20:
                    last_update = timestamp
                    asyncio.create_task(edit_status_message(event, entry))

            await event.download_media(file=path, progress_callback=progress_callback)

            # Final update
            entry["status"] = "done"
            entry["progress"] = 100
            entry["speed"] = 0
            entry["pending_time"] = 0
            save_state()
            if entry.get("_status_msg_id"):
                await edit_status_message(event, entry, "Downloaded")
            return

        except asyncio.CancelledError:
            entry["status"] = "stopped"
            entry["speed"] = 0
            save_state()
            if entry.get("_status_msg_id"):
                await edit_status_message(event, entry, "Stopped")
            return
        except Exception as e:
            entry["error"] = f"Attempt {attempt}/{MAX_RETRIES} failed: {str(e)}"
            logging.error(entry["error"])
            await asyncio.sleep(5)

    entry["status"] = "failed"
    entry["speed"] = 0
    entry["pending_time"] = None
    save_state()
    if entry.get("_status_msg_id"):
        await edit_status_message(event, entry, "Failed")

@client.on(events.NewMessage(chats=CHAT_ID))
async def handle_new_file(event):
    if not event.file:
        return
    kind = "Documents"
    if event.file.mime_type:
        if event.file.mime_type.startswith("image/"):
            kind = "Images"
        elif event.file.mime_type.startswith("video/"):
            kind = "Videos"

    folder = os.path.join(DOWNLOAD_DIR, kind)
    os.makedirs(folder, exist_ok=True)

    filename = event.file.name or f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    path = os.path.join(folder, filename)

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
    downloads.insert(0, entry)
    save_state()

    # Start the download task
    task = asyncio.create_task(safe_download(event, path, entry))
    download_tasks[filename] = task

# ======== FLASK DASHBOARD & API ========
app = Flask(__name__)
HTML_TEMPLATE =  """
<!DOCTYPE html>
<html>
<head>
<title>Telegram Downloader</title>
<meta http-equiv="refresh" content="2">
<style>
body { font-family: Arial; background: #111; color: #ddd; padding: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border-bottom: 1px solid #333; text-align: left; }
.status-downloading { color: #00d9ff; }
.status-done { color: #00ff88; }
.status-failed { color: #ff5555; }
.status-stopped { color: #ffaa00; }
button { padding: 4px 8px; margin-left: 4px; }
</style>
<script>
function retryDownload(index){
    fetch("/api/retry",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({index:index})})
    .then(()=>{location.reload();});
}
function stopDownload(file){
    fetch("/api/stop",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file:file})})
    .then(()=>{location.reload();});
}
function deleteEntry(file){
    if(!confirm("Are you sure?")) return;
    fetch("/api/delete",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file:file})})
    .then(()=>{location.reload();});
}
</script>
</head>
<body>
<h2>📥 Telegram Downloader Status</h2>
<h3>
Items: {{ downloaded_count }}/{{ total_count }} |
Total Downloaded: {{ human_readable_size(total_downloaded) }} / {{ human_readable_size(total_size) }} [{{ human_readable_size(pending_bytes) }}] |
Total Speed: {{ human_readable_size(total_speed*1024) }}/s
</h3>
<table>
<tr><th>#</th><th>File</th><th>Status</th><th>Progress</th><th>Speed(KB/s)</th>
<th>Downloaded</th><th>Pending</th><th>ETA</th><th>Error</th><th>Action</th><th>Remove</th></tr>
{% for d in downloads %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ d.get('file','') }}</td>
<td class="status-{{ d.get('status','') }}">{{ d.get('status','') }}</td>
<td>{{ d.get('progress',0) }}%</td>
<td>{{ d.get('speed',0) }}</td>
<td>{{ human_readable_size(d.get('downloaded_bytes',0)) }}/{{ human_readable_size(d.get('total_bytes',0)) }}</td>
<td>{{ human_readable_size(d.get('total_bytes',0)-d.get('downloaded_bytes',0)) }}</td>
<td>{{ format_time(d.get('pending_time')) }}</td>
<td>{{ d.get('error','') }}</td>
<td>
{% if d.get('status') == 'failed' %}
<button onclick="retryDownload({{ loop.index0 }})">Retry</button>
{% elif d.get('status') == 'downloading' %}
<button onclick="stopDownload('{{ d.get('file','') }}')">Stop</button>
{% endif %}
</td>
<td>
<button onclick="deleteEntry('{{ d.get('file','') }}')">Delete</button>
</td>
</tr>
{% endfor %}
</table>
</body>
</html>
""" 


@app.route("/")
def dashboard():
    query = request.args.get("search","").lower()
    sorted_list = sorted(downloads, key=lambda x: 0 if x["status"]=="downloading" else 1)
    filtered_list = [d for d in sorted_list if query in d.get("file","").lower()] if query else sorted_list
    total_downloaded = sum(d.get("downloaded_bytes",0) for d in filtered_list)
    total_size = sum(d.get("total_bytes",0) for d in filtered_list)
    pending_bytes = total_size - total_downloaded
    total_speed = sum(d.get("speed",0) for d in filtered_list)
    downloaded_count = sum(1 for d in filtered_list if d.get("status")=="done")
    total_count = len(filtered_list)
    return render_template_string(
        HTML_TEMPLATE,
        downloads=filtered_list,
        human_readable_size=human_readable_size,
        format_time=format_time,
        total_downloaded=total_downloaded,
        total_size=total_size,
        pending_bytes=pending_bytes,
        total_speed=total_speed,
        downloaded_count=downloaded_count,
        total_count=total_count
    )

@app.route("/api/retry", methods=["POST"])
def api_retry():
    data = request.json
    index = data.get("index")
    if index is not None and 0 <= index < len(downloads):
        entry = downloads[index]
        if entry["status"] in ["failed","stopped"]:
            entry["status"] = "downloading"
            entry["progress"] = 0
            entry["speed"] = 0
            entry["error"] = None
            entry["timestamp"] = datetime.now().isoformat()
            save_state()
            async def retry_task():
                class FakeEvent:
                    file=type('file',(),{})()
                    file.name=entry["file"]
                    file.mime_type=None
                    chat_id=CHAT_ID
                    id=None
                path=os.path.join(DOWNLOAD_DIR,entry["file"])
                download_tasks[entry["file"]] = asyncio.create_task(safe_download(FakeEvent(), path, entry))
            asyncio.get_event_loop().create_task(retry_task())
    return jsonify({"status":"ok"})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    data = request.json
    file = data.get("file")
    task = download_tasks.get(file)
    if task and not task.done():
        task.cancel()
    return jsonify({"status":"stopped"})

@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.json
    file = data.get("file")
    entry = next((d for d in downloads if d.get("file")==file), None)
    if entry:
        task = download_tasks.get(file)
        if task and not task.done():
            task.cancel()
        download_tasks.pop(file,None)
        downloads.remove(entry)
        save_state()
    return jsonify({"status":"deleted"})

# ======== RUN FLASK & TELETHON ========
def run_flask():
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)

def run_telethon():
    print("🚀 Telegram Downloader running...")
    client.start()
    client.run_until_disconnected()

if __name__=="__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_telethon()
