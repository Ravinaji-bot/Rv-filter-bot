import os

API_ID = int(os.environ.get("API_ID", "1234567"))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token_here")

DATABASE_URI = os.environ.get("DATABASE_URI", "your_mongodb_url_here")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Cluster0")

ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "123456789").split()]
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-100123456789"))
PORT = int(os.environ.get("PORT", "8080"))

