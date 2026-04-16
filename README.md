# WoT Clan Reserves Telegram Bot

A Telegram bot that notifies you when your World of Tanks clan activates reserves (boosts). Supports English, Ukrainian, and Russian.

## Features

- Notifications for every clan reserve activation (credits, XP, free XP, etc.)
- Precise start and end times for each reserve
- Supports EU, NA, and Asia servers
- Works in private chats and group chats
- Auto-detects user language from Telegram interface settings
- Warns when your Wargaming auth token is about to expire

## Setup

### 1. Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABC-DEF...`)

### 2. Register a Wargaming Application

1. Go to [developers.wargaming.net](https://developers.wargaming.net/)
2. Sign in with your Wargaming account
3. Go to **My Applications** → **Add Application**
4. Name: anything you like (e.g., "Clan Reserves Bot")
5. Type: **Server** (for the IP field, enter `0.0.0.0`)
6. Save and copy the **Application ID**

### 3. Deploy to Railway (free tier / ~$5/mo)

1. Push this code to a GitHub repository
2. Go to [railway.app](https://railway.app/) and sign in with GitHub
3. Click **New Project** → **Deploy from GitHub Repo** → select your repo
4. Go to **Settings** → **Variables** and add:
   - `TELEGRAM_BOT_TOKEN` = your bot token from step 1
   - `WG_APPLICATION_ID` = your application ID from step 2
   - `PUBLIC_URL` = your Railway app URL (find it in **Settings** → **Networking** → **Generate Domain**, e.g. `https://your-app.up.railway.app`)
5. Railway will auto-deploy. Check **Deployments** for logs.

### 4. Test the Bot

Open your bot on Telegram, press **Start**, select your server, and log in!

## Running Locally

```bash
# Clone and install
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# For local development, you need a public URL for the auth callback.
# Use ngrok or similar:
#   ngrok http 8080
# Then set PUBLIC_URL to the ngrok URL

# Run
python bot.py
```

## Commands

| Command     | Description                          |
|-------------|--------------------------------------|
| `/start`    | Start the bot / reset setup          |
| `/login`    | Log in with Wargaming account        |
| `/status`   | Show current monitoring status       |
| `/language` | Change notification language         |
| `/server`   | Change game server                   |
| `/timezone` | Change your timezone                 |
| `/stop`     | Stop notifications                   |
| `/help`     | Show help message                    |

## Architecture

- **bot.py** — Main entry point, Telegram command handlers
- **wg_api.py** — Wargaming API client (auth, reserves, account info)
- **auth_server.py** — HTTP server for Wargaming OAuth callback
- **reserve_monitor.py** — Background task polling for active reserves every 60s
- **database.py** — SQLite storage for users, tokens, notification state
- **i18n.py** — Translations (EN, UK, RU)
- **config.py** — Environment-based configuration
