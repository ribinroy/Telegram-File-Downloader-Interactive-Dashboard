# Telegram Downloader

A Python application that automatically downloads files from a Telegram chat and provides a web dashboard to monitor download progress.

## Features

- **Automatic Downloads**: Automatically detects and downloads files from a specified Telegram chat
- **Real-time Progress**: Live download progress with speed and ETA information
- **Web Dashboard**: Beautiful web interface to monitor downloads
- **File Organization**: Automatically organizes files into folders (Images, Videos, Documents)
- **Retry Mechanism**: Built-in retry logic for failed downloads
- **Download Management**: Start, stop, and delete downloads from the web interface
- **Persistent State**: Maintains download history and state across restarts

## Project Structure

```
telegram_downloader/
├── src/
│   ├── config/          # Configuration settings
│   ├── telegram_handler/ # Telegram client and download logic
│   ├── web_app/         # Flask web application
│   └── utils/           # Utility functions
├── downloads/           # Downloaded files (auto-created)
├── logs/               # Log files (auto-created)
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Telegram API Credentials**:
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application to get `API_ID` and `API_HASH`

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/telegram_downloader.git
   cd telegram_downloader
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Or use the setup script:

   ```bash
   python setup.py
   ```

3. **Configure the application**:
   Copy the example environment file and update with your values:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and update the following values:

   ```bash
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   CHAT_ID=your_chat_id_here  # Negative number for groups/channels
   ```

   Or use the interactive setup script:

   ```bash
   python setup_env.py
   ```

4. **Get Chat ID**:
   - Add your bot to the chat or forward a message from the chat to @userinfobot
   - The chat ID will be displayed (use negative number for groups)

## Usage

1. **Start the application**:

   ```bash
   python main.py
   ```

2. **Access the web dashboard**:
   Open your browser and go to `http://localhost:4444`

3. **Send files to Telegram**:
   Send any file to the configured chat, and it will automatically start downloading

## Configuration

### Basic Configuration

Edit `.env` file to customize:

- `API_ID` and `API_HASH`: Your Telegram API credentials
- `CHAT_ID`: The chat ID to monitor for files
- `WEB_PORT`: Port for the web dashboard (default: 4444)
- `DOWNLOAD_DIR`: Directory to save downloaded files
- `MAX_RETRIES`: Maximum retry attempts for failed downloads

### Advanced Configuration

- **Download Directory**: Change `DOWNLOAD_DIR` in `src/config/__init__.py` to your preferred location
- **Web Interface**: Modify `WEB_HOST` and `WEB_PORT` in `.env` for different network access
- **Logging**: Adjust log level and file location in `main.py`

## Web Dashboard Features

- **Real-time Status**: See download progress, speed, and ETA
- **File Management**: Retry failed downloads, stop active downloads, delete entries
- **Search**: Filter downloads by filename
- **Statistics**: View total downloaded size, pending bytes, and overall speed

## File Organization

Files are automatically organized into folders:

- **Images**: Files with image MIME types
- **Videos**: Files with video MIME types
- **Documents**: All other file types

## Troubleshooting

### Common Issues

1. **"Invalid API credentials"**:

   - Verify your `API_ID` and `API_HASH` are correct
   - Make sure you've created an application at my.telegram.org

2. **"Chat not found"**:

   - Verify the `CHAT_ID` is correct
   - Ensure the bot/user has access to the chat
   - Use negative numbers for group chats

3. **"Permission denied"**:

   - Check file permissions for the download directory
   - Ensure the application has write access

4. **Downloads not starting**:
   - Check the logs in `logs/telegram_downloader.log`
   - Verify the chat is being monitored correctly

### Logs

Check `logs/telegram_downloader.log` for detailed error messages and debugging information.

## Development

### Project Structure

- `src/config/`: Configuration management
- `src/telegram_handler/`: Telegram client and download logic
- `src/web_app/`: Flask web application and API endpoints
- `src/utils/`: Utility functions for file operations and formatting

### Adding Features

1. **New Download Sources**: Extend `TelegramDownloader` class
2. **Web Interface**: Modify `WebApp` class and HTML template
3. **File Processing**: Add handlers in `utils` module
4. **Configuration**: Add new settings in `config` module

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m "Add feature"`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/telegram_downloader/issues) page
2. Create a new issue with detailed information
3. Include logs and configuration details (without sensitive information)

## Changelog

### Version 1.0.0

- Initial release with modular architecture
- Automatic file downloads from Telegram
- Web dashboard with real-time monitoring
- File organization and management features
