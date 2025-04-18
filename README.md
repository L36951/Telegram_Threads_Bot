# Threads → Telegram Bot

A Python bot that **grabs a Threads™ post (media + caption) and reposts it to a Telegram chat**.  It automatically downloads every video/picture from the first `data‑pressable‑container`, then ships them as a media‑group message.

---

## ✨ Features

|                           |                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| 📜 **Auto‑caption**       | Uses the post’s `<meta name="description">` as caption (strips “翻譯”).                          |
| 🎞 **Multi‑media**        | Downloads **all** videos & images in the first Threads container.                              |
| 🛂 **Group whitelist**    | Only stays in groups whose *chat ID* is listed in `.env → ```; otherwise leaves automatically. |
| 🔒 **.env config**        | Token & whitelist kept out of source control.                                                  |
| 🌀 **systemd ready**      | Sample service file included for auto‑restart on EC2 / any Linux.                              |
| 🖥️ **Headless Chromium** | Works in headless mode (Selenium 4 + Chromium + ChromeDriver).                                 |

---


## 🚀 Quick Start (local)

```bash
# 1. Clone
$ git clone https://github.com/<you>/threads-telegram-bot.git
$ cd threads-telegram-bot

# 2. Python 3.12+ virtual‑env
$ sudo apt install -y python3-venv python3-pip
$ python3 -m venv botenv
$ source botenv/bin/activate

# 3. Install deps
(botenv)$ pip install -r requirements.txt

# 4. Create .env
(botenv)$ cat > .env <<EOF
BOT_TOKEN=<YOUR_BOT_ID>
ALLOWED_GROUPS=<YOUR_GROUP_CHAT_ID>, <YOUR_GROUP_CHAT_ID>      # comma‑separated list of chat IDs
EOF

# 5. Run
(botenv)$ python telegram_threads_bot.py
```

> **Chrome/Driver**   Ubuntu 24.04 Snap build works out‑of‑box:
>
> ```bash
> sudo apt install -y chromium-browser chromium-chromedriver fonts-liberation
> ```

---

## 🔑 Environment Variables

| Name             | Description                                                                                     | Example                      |
| ---------------- | ----------------------------------------------------------------------------------------------- | ---------------------------- |
| `BOT_TOKEN`      | Your bot’s API token from @BotFather                                                            | `123456:ABC...`              |
| `ALLOWED_GROUPS` | Comma‑separated list of *signed* chat IDs the bot may stay in. Use a negative value for groups. | `-47424329,-1009876543210` |

---

## ❓ Finding a Telegram Group ID

- **Fastest**: add [@RawDataBot](https://t.me/RawDataBot) to the group → `/start` → it replies with the chat ID.
- **Inside this bot**: temporarily add
  ```python
  print(update.effective_chat.id)
  ```
  to `handle_threads()`, send any message, read the log.

---

## 🖥️ Run as a systemd service (Ubuntu server)

`/etc/systemd/system/threadsbot.service`:

```ini
[Unit]
Description=Threads ➜ Telegram Bot
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/threads-telegram-bot
Environment=BOT_TOKEN=123456:ABC...
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/ubuntu/threads-telegram-bot/botenv/bin/python telegram_threads_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now threadsbot
journalctl -fu threadsbot   # view logs
```

---

## ☁️ Deploy on AWS EC2 (Ubuntu 24.04 mini)

```bash
# Basic system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y git build-essential python3-venv python3-pip \
                    chromium-browser chromium-chromedriver fonts-liberation

# Clone & set up (as above)
```

> **Tip**: use IAM role + SSM Session Manager if you don’t want to open port 22.

---

## 📝 Roadmap / TODO

-

---

## 📄 License

MIT — see `LICENSE` file.

