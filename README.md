# Telegram Downloader

A Python application that automatically downloads files from a Telegram chat and provides a real-time web dashboard to monitor download progress.

---

## 🚀 Features

- **Automatic Downloads**: Detects and downloads files automatically from a chosen Telegram chat
- **Real-time Progress**: Live progress, speed, and ETA tracking
- **Web Dashboard**: Clean web UI for monitoring downloads
- **File Organization**: Automatically sorts files into folders (`Images`, `Videos`, `Documents`)
- **Retry Mechanism**: Automatic retry logic for failed downloads
- **Download Management**: Stop, retry, or delete downloads from the dashboard
- **Persistent State**: Keeps download history across restarts
- **Chat Reactions**: Automatically reacts in Telegram with ⬇️ ✅ ❌ to indicate download state

---

## 🧩 Project Structure

```
telegram_downloader/
├── src/
│   ├── config/             # Configuration and environment management
│   ├── telegram_handler/   # Telegram client and downloader logic
│   ├── web_app/            # Flask web application
│   └── utils/              # Helper utilities
├── downloads/              # Auto-created download directory
├── logs/                   # Log files
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
└── README.md               # This file
```

---

## 🧰 Prerequisites

- **Python 3.8+**
- **Telegram API credentials**
- Internet access

---

## 🧑‍💻 Step 1: Get Telegram API Credentials

To use the Telegram API, you must create a **Telegram application** and get an **API ID** and **API HASH**.

### 1. Go to [https://my.telegram.org](https://my.telegram.org)

- Log in with your Telegram account.

### 2. Click on **API Development Tools**

- You’ll be prompted to create a new app.

### 3. Fill out the form:

| Field      | Example               |
| ---------- | --------------------- |
| App title  | `Telegram Downloader` |
| Short name | `tgdloader`           |
| Platform   | `Desktop`             |

After submission, you’ll see your **API ID** and **API HASH** — keep them safe.  
You’ll use these in your `.env` file.

---

## ⚙️ Step 2: Installation

### 🪟 **Windows Setup**

```bash
# Clone the repo
git clone https://github.com/yourusername/telegram_downloader.git
cd telegram_downloader

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Then copy the environment file:

```bash
copy .env.example .env
```

Edit `.env` in Notepad and fill in:

```bash
API_ID=your_api_id_here
API_HASH=your_api_hash_here
CHAT_ID=-1001234567890
WEB_PORT=4444
DOWNLOAD_DIR=C:\Users\<you>\Downloads\Telegram
```

Start the app:

```bash
python main.py
```

Then visit:  
➡️ **http://localhost:4444**

---

### 🍎 **macOS Setup**

```bash
# Clone the repo
git clone https://github.com/yourusername/telegram_downloader.git
cd telegram_downloader

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

Copy `.env`:

```bash
cp .env.example .env
```

Edit with:

```bash
nano .env
```

Start the app:

```bash
python3 main.py
```

Then open **http://localhost:4444** in your browser.

---

### 🐧 **Ubuntu / Linux Setup**

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/yourusername/telegram_downloader.git
cd telegram_downloader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env` and edit:

```bash
cp .env.example .env
nano .env
```

Fill your Telegram credentials and paths.

Start:

```bash
python3 main.py
```

Access the dashboard:  
➡️ **http://localhost:4444**

---

## ⚙️ Step 3: Configure `.env`

```bash
API_ID=12345678
API_HASH=abcd1234efgh5678ijkl
CHAT_ID=-1001234567890
DOWNLOAD_DIR=/mnt/Downloads/Telegram
WEB_PORT=4444
MAX_RETRIES=6
```

### Notes:

- `CHAT_ID`: Use a **negative number** for group or channel chats
- To get your chat ID:
  - Forward any message from the chat to [@userinfobot](https://t.me/userinfobot)
  - It will return something like: `Chat ID: -1001234567890`

---

## 🖥️ Step 4: Running as a Background Service (Linux only)

To auto-run this on boot:

Create a service file:

```bash
sudo nano /etc/systemd/system/telegram_downloader.service
```

Paste:

```ini
[Unit]
Description=Telegram Downloader Service
After=network.target

[Service]
User=hs
WorkingDirectory=/home/hs/telegram_downloader
ExecStart=/home/hs/telegram_downloader/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram_downloader
sudo systemctl start telegram_downloader
sudo journalctl -u telegram_downloader -f
```

---

## 🌐 Web Dashboard

Access the dashboard at:

👉 [http://localhost:4444](http://localhost:4444)

### Features:

- Live download progress updates
- Pause/Stop/Delete controls
- Search filter using URL query (`?search=keyword`)
- Download stats summary (speed, pending bytes, etc.)

---

## 📂 File Organization

Files are automatically sorted into:

```
Downloads/
├── Images/
├── Videos/
└── Documents/
```

---

## 🧠 Troubleshooting

| Issue                     | Cause               | Fix                                              |
| ------------------------- | ------------------- | ------------------------------------------------ |
| `Invalid API credentials` | Wrong API ID/HASH   | Check at my.telegram.org                         |
| `Chat not found`          | Incorrect CHAT_ID   | Ensure bot has access; use negative for groups   |
| `Permission denied`       | No write permission | `chmod -R 777 downloads` (or adjust user rights) |
| Downloads not updating    | Long Telegram delay | Check logs or restart the app                    |

View logs:

```bash
tail -f logs/telegram_downloader.log
```

---

## 🧑‍🔬 Development

### Modules

- `src/telegram_handler/`: Telethon client, reactions, retries
- `src/web_app/`: Flask API, HTML template
- `src/utils/`: Size/time formatters
- `src/config/`: Environment + constants

### To Add Features

1. Add new file handler in `telegram_handler/`
2. Update dashboard HTML for new buttons
3. Add REST endpoint in `web_app/`

---

## 💡 Example Screenshot Previews

### Web Dashboard

![Dashboard Preview](screenshots/Dashboard.png)

### Telegram Integration

![Telegram Reaction Examples](screenshots/Telegram.png)
![Downloading](screenshots/Screenshot%202025-10-22%20at%2000.03.47.png)
![Stopped](screenshots/Screenshot%202025-10-22%20at%2000.03.59.png)

---

## 🪪 License

Licensed under the [MIT License](LICENSE).

---

## ❤️ Support & Contributions

1. Check [Issues](https://github.com/yourusername/telegram_downloader/issues)
2. Open a new issue if not listed
3. PRs welcome — please follow the coding style and test locally

---

## 🧾 Changelog

### **v1.0.0**

- Initial release
- Automatic Telegram file downloads
- Flask dashboard with live tracking
- File organization and persistent state
- Telegram message reactions (⬇️ ✅ ❌)
