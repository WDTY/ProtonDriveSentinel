![ProtonDriveSentinel Logo](assets/proton-drive-sentinel_logo.png)
# ProtonDriveSentinel

ProtonDriveSentinel is a **real-time monitoring tool** that watches a **Proton Drive** shared link for new **files and directories**. When changes are detected, it sends alerts via **WhatsApp (Twilio) or Telegram**.

## 🚀 Features

✅ **Monitors Proton Drive for new files and folders**  
✅ **Supports configurable file filters** (e.g., `.wav`, `.mp3`, `.csv`)  
✅ **Sends alerts via Twilio (WhatsApp) or Telegram**  
✅ **Runs inside a Docker container** for easy deployment  
✅ **Automatically detects folder changes**  
✅ **Provides debug logging for troubleshooting**  

## 📦 Installation

### 1️⃣ **Clone the repository**

```bash
git clone https://github.com/your-username/ProtonDriveSentinel.git
cd ProtonDriveSentinel
```

### 2️⃣ **Build and run with Docker**

```bash
docker-compose build --no-cache && docker-compose up
```

## ⚙️ Configuration

Modify the `config.ini` file before running the project:

```ini
[general]
alert_service = twilio  # Options: 'twilio' or 'telegram'
proton_drive_url = https://drive.proton.me/urls/YOUR_SHARE_LINK

[twilio]
account_sid = your_twilio_account_sid
auth_token = your_twilio_auth_token
whatsapp_number = your_twilio_whatsapp_number
target_number = target_whatsapp_number

[telegram]
bot_token = your_telegram_bot_token
chat_id = your_telegram_chat_id
```

## 📜 How It Works

1. The script **scrapes Proton Drive** and **extracts files & folders** using Selenium.  
2. If a **new file or folder** is detected, an **alert** is sent via **WhatsApp or Telegram**.  
3. The script **runs inside Docker** and **checks every 60 seconds**.  
4. Debugging logs are available in Docker logs.  

## 📝 Example Use Cases

🔹 **Monitoring `.wav` files** in a shared folder for automatic processing.  
🔹 **Tracking new directories** created inside Proton Drive.  
🔹 **Getting WhatsApp notifications** when new documents are uploaded.  

## 🛠 Debugging & Logs

To check logs inside Docker, run:

```bash
docker logs -f <container_id>
```

If the script fails to detect files, **check the debug page**:

```bash
docker cp <container_id>:/app/debug_page.html ./
```

Open `debug_page.html` in a browser to inspect Proton Drive’s structure.

## 🎯 Future Enhancements

✅ Add **support for nested directories**  
✅ Improve **handling of large Proton Drive folders**  
✅ Implement **email notifications** as an option  

## 📜 License

MIT License. Feel free to contribute and improve this project!

---

💬 **Need help?** Open an issue or contact me! 🚀
