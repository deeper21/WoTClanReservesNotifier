"""Bot configuration loaded from environment variables."""

import os

# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# Wargaming Application ID (from developers.wargaming.net)
WG_APPLICATION_ID = os.environ["WG_APPLICATION_ID"]

# Public URL where the bot's auth callback is reachable
# e.g. https://your-app.up.railway.app
PUBLIC_URL = os.environ["PUBLIC_URL"].rstrip("/")

# Auth callback path
AUTH_CALLBACK_PATH = "/auth/callback"
AUTH_CALLBACK_URL = f"{PUBLIC_URL}{AUTH_CALLBACK_PATH}"

# Web server port for the auth callback
PORT = int(os.environ.get("PORT", "8080"))

# SQLite database path
DATABASE_PATH = os.environ.get("DATABASE_PATH", "bot_data.db")

# Reserve polling interval in seconds
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))

# Token expiry warning – notify user this many seconds before token expires
TOKEN_EXPIRY_WARNING = int(os.environ.get("TOKEN_EXPIRY_WARNING", "86400"))  # 24h

# Wargaming API base URLs per region
WG_API_REGIONS = {
    "eu": {
        "api": "https://api.worldoftanks.eu",
        "name": "Europe",
    },
    "na": {
        "api": "https://api.worldoftanks.com",
        "name": "North America",
    },
    "asia": {
        "api": "https://api.worldoftanks.asia",
        "name": "Asia",
    },
}

# Wargaming auth token max lifetime (14 days)
WG_TOKEN_MAX_LIFETIME = 14 * 24 * 3600
