"""
Flask web application for Telegram Downloader dashboard
"""
import os
import asyncio
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from src.config import WEB_PORT, WEB_HOST, DOWNLOAD_DIR, CHAT_ID
from src.utils import human_readable_size, format_time, save_state


class WebApp:
    def __init__(self, downloads, download_tasks):
        self.downloads = downloads
        self.download_tasks = download_tasks
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route("/")
        def dashboard():
            query = request.args.get("search", "").lower()
            sorted_list = sorted(self.downloads, key=lambda x: 0 if x["status"] == "downloading" else 1)
            filtered_list = [d for d in sorted_list if query in d.get("file", "").lower()] if query else sorted_list
            total_downloaded = sum(d.get("downloaded_bytes", 0) for d in filtered_list)
            total_size = sum(d.get("total_bytes", 0) for d in filtered_list)
            pending_bytes = total_size - total_downloaded
            total_speed = sum(d.get("speed", 0) for d in filtered_list)
            downloaded_count = sum(1 for d in filtered_list if d.get("status") == "done")
            total_count = len(filtered_list)
            return render_template_string(
                self.get_html_template(),
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

        @self.app.route("/api/retry", methods=["POST"])
        def api_retry():
            data = request.json
            index = data.get("index")
            if index is not None and 0 <= index < len(self.downloads):
                entry = self.downloads[index]
                if entry["status"] in ["failed", "stopped"]:
                    entry["status"] = "downloading"
                    entry["progress"] = 0
                    entry["speed"] = 0
                    entry["error"] = None
                    entry["timestamp"] = datetime.now().isoformat()
                    save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")
                    
                    # Note: This retry functionality would need proper integration with TelegramDownloader
                    # For now, we'll just update the status
            return jsonify({"status": "ok"})

        @self.app.route("/api/stop", methods=["POST"])
        def api_stop():
            data = request.json
            file = data.get("file")
            task = self.download_tasks.get(file)
            if task and not task.done():
                task.cancel()
            return jsonify({"status": "stopped"})

        @self.app.route("/api/delete", methods=["POST"])
        def api_delete():
            data = request.json
            file = data.get("file")
            entry = next((d for d in self.downloads if d.get("file") == file), None)
            if entry:
                task = self.download_tasks.get(file)
                if task and not task.done():
                    task.cancel()
                self.download_tasks.pop(file, None)
                self.downloads.remove(entry)
                save_state(self.downloads, DOWNLOAD_DIR.parent / "downloads.json")
            return jsonify({"status": "deleted"})

    def get_html_template(self):
        """Return the HTML template for the dashboard"""
        return """
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

    def run(self):
        """Run the Flask application"""
        self.app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)
