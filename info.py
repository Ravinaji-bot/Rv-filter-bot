import os

API_ID = int(os.environ.get("API_ID", "24358501"))
API_HASH = os.environ.get("API_HASH", "fa51ce8876c215d8a76c98c755e6d2d3")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

DATABASE_URI = os.environ.get("DATABASE_URI", "mongodb+srv://...")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "Cluster0")

VDISK_API_KEY = os.environ.get("VDISK_API_KEY", "your_vdiskpro_api_key")
TMDB_API_KEY = os.environ.get("OMDB_API_KEY", "your_omdb_api_key")

ADMIN_ID = int(os.environ.get("ADMIN_ID", "1834715690"))

REQUEST_CHANNEL = int(os.environ.get("REQUEST_CHANNEL", "-1003987425981"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003994576731"))
