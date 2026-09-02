import re
import os
from os import environ, getenv

# Import Script safely
try:
    from Script import script
    DEFAULT_CAPTION = getattr(script, 'CAPTION', "{file_name}")
    DEFAULT_IMDB = getattr(script, 'IMDB_TEMPLATE_TXT', "{title}")
except Exception:
    DEFAULT_CAPTION = "<b>🎬 {file_name}</b>\n\n<b>📌 Quality:</b> {quality}\n<b>🔊 Audio:</b> {languages}"
    DEFAULT_IMDB = "<b>🎬 Title:</b> {title}\n<b>⭐ Rating:</b> {rating}\n<b>🎭 Genre:</b> {genres}"

# Regex pattern for numeric IDs
id_pattern = re.compile(r'^[-+]?\d+$')

def is_enabled(value, default=False):
    if value is None:
        return default
    value = str(value).strip().lower()
    if value in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

def parse_id_list(env_var, default=""):
    raw_list = environ.get(env_var, default).split()
    parsed = []
    for item in raw_list:
        item = item.strip()
        if id_pattern.match(item):
            parsed.append(int(item))
        elif item:
            parsed.append(item)
    return parsed

# ============================
# Bot Information Configuration
# ============================
SESSION = environ.get('SESSION', 'vdisk_search_bot')
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', '')
USER_SESSION = environ.get('USER_SESSION', '') # String Session for batch indexing

# ============================
# Bot Settings Configuration
# ============================
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', "True"), True)
INDEX_CAPTION = is_enabled(environ.get('SAVE_CAPTION', "True"), True)
COVERX = is_enabled(environ.get('COVERX', "True"), True)

PICS = environ.get('PICS', 'https://graph.org/file/56b5deb73f3b132e2bb73.jpg https://graph.org/file/5303692652d91d52180c2.jpg').split()
NOR_IMG = environ.get("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")
MELCOW_PHOTO = environ.get("MELCOW_PHOTO", "https://graph.org/file/56b5deb73f3b132e2bb73.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://graph.org/file/13702ae26fb05df52667c.jpg")
FSUB_PICS = environ.get('FSUB_PICS', 'https://graph.org/file/7478ff3eac37f4329c3d8.jpg').split()

# ============================
# Channels & Users Configuration (3 Channels Only)
# ============================
ADMINS = parse_id_list('ADMINS', '634637418')

# 1. Database Channel (Where movie files are stored & indexed)
DB_CHANNEL = [int(ch) if id_pattern.match(ch.strip()) else ch for ch in environ.get('DB_CHANNEL', '-100').split()]

# 2. Log Channel
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-100'))

# 3. Request Channel
REQST_CHANNEL = int(environ.get('REQST_CHANNEL_ID', '-100')) if id_pattern.match(environ.get('REQST_CHANNEL_ID', '').strip()) else None

# Support Chat Links
SUPPORT_CHAT_ID = int(environ.get('SUPPORT_CHAT_ID', '-100')) if id_pattern.match(environ.get('SUPPORT_CHAT_ID', '').strip()) else None
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/')

# Backward Compatibility (Taaki purane bot scripts me error na aaye)
CHANNELS = DB_CHANNEL
BIN_CHANNEL = LOG_CHANNEL

# ============================
# Vdiskpro Streaming Configuration
# ============================
VDISK_API = environ.get('VDISK_API', '') # API Key for Vdiskpro / Direct Streamer
VDISK_DOMAIN = environ.get('VDISK_DOMAIN', 'https://vdiskpro.com')

# ============================
# Database Configuration
# ============================
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'vdisk_files')

MULTIPLE_DB = is_enabled(environ.get('MULTIPLE_DB', "False"), False)
DATABASE_URI2 = environ.get('DATABASE_URI2', "") if MULTIPLE_DB else DATABASE_URI

# ============================
# Movie Notification & Metadata
# ============================
MOVIE_UPDATE_NOTIFICATION = is_enabled(environ.get('MOVIE_UPDATE_NOTIFICATION', "False"), False)
MOVIE_UPDATE_CHANNEL = int(environ.get('MOVIE_UPDATE_CHANNEL', '-100'))
TMDB_API_KEY = environ.get('TMDB_API_KEY', '')
TMDB_POSTER = is_enabled(environ.get('TMDB_POSTER', "True"), True)
LANDSCAPE_POSTER = is_enabled(environ.get('LANDSCAPE_POSTER', "True"), True)

# ============================
# Verification Settings
# ============================
IS_VERIFY = is_enabled(environ.get('IS_VERIFY', 'False'), False)
LOG_VR_CHANNEL = LOG_CHANNEL
VERIFY_IMG = environ.get("VERIFY_IMG", "https://telegra.ph/file/9ecc5d6e4df5b83424896.jpg")

TUTORIAL = environ.get("TUTORIAL", "https://t.me/")
SHORTENER_API = environ.get("SHORTENER_API", "")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", "")

# ============================
# Links & Authorization
# ============================
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/')
UPDATE_CHNL_LNK = environ.get('UPDATE_CHNL_LNK', 'https://t.me/')

auth_users = parse_id_list('AUTH_USERS', '')
AUTH_USERS = list(set(auth_users + ADMINS))

# ============================
# Formatting & Filter Options
# ============================
ULTRA_FAST_MODE = is_enabled(environ.get('ULTRA_FAST_MODE', "True"), True)
MAX_B_TN = environ.get("MAX_B_TN", "5")
PORT = int(environ.get("PORT", "8080"))
MSG_ALRT = environ.get('MSG_ALRT', 'Share & Support Us ♥️')
DELETE_TIME = int(environ.get("DELETE_TIME", "300"))

CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", DEFAULT_CAPTION)
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", DEFAULT_IMDB)

MAX_LIST_ELM = int(environ.get("MAX_LIST_ELM", "10"))
INDEX_REQ_CHANNEL = LOG_CHANNEL
NO_RESULTS_MSG = is_enabled(environ.get("NO_RESULTS_MSG", "True"), True)
MAX_BTN = is_enabled(environ.get('MAX_BTN', "True"), True)
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF', "False"), False)
IMDB = is_enabled(environ.get('IMDB', "True"), True)
TMDB_ON_SEARCH = is_enabled(environ.get('TMDB_ON_SEARCH', "True"), True)
AUTO_FFILTER = is_enabled(environ.get('AUTO_FFILTER', "True"), True)
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE', "True"), True)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "False"), False)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "False"), False)
PM_SEARCH = is_enabled(environ.get('PM_SEARCH', "True"), True)
EMOJI_MODE = is_enabled(environ.get('EMOJI_MODE', "True"), True)
BUTTON_MODE = is_enabled(environ.get('BUTTON_MODE', "True"), True)
STREAM_MODE = is_enabled(environ.get('STREAM_MODE', "True"), True)
MAINTENANCE = is_enabled(environ.get('MAINTENANCE', "False"), False)

LANGUAGES = {"ᴍᴀʟᴀʏᴀʟᴀᴍ":"mal","ᴛᴀᴍɪ🇱":"tam","ᴇɴɢʟɪsʜ":"eng","ʜɪɴᴅɪ":"hin","ᴛᴇʟᴜɢᴜ":"tel","ᴋᴀɴɴᴀᴅᴀ":"kan","ɢᴜᴊᴀʀᴀᴛɪ":"guj","ᴍᴀʀᴀᴛʜɪ":"mar","ᴘᴜɴᴊᴀʙɪ":"pun"}
QUALITIES = ["360P", "480P", "720P", "1080P", "1440P", "2160P", "4K"]

BAD_WORDS = {
    "PrivateMovieZ", "toonworld4all", "themoviesboss", "1tamilmv", 
    "tamilblasters", "1tamilblasters", "skymovieshd", "extraflix", 
    "hdm2", "moviesmod", "hdhub4u", "mkvcinemas", "primefix"
}

# ============================
# Server & Web Engine
# ============================
ON_HEROKU = 'DYNO' in environ
APP_NAME = environ.get('APP_NAME', None) if ON_HEROKU else None
BIND_ADDRESS = getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0')

FQDN = (
    environ.get('FQDN', BIND_ADDRESS)
    if not ON_HEROKU or environ.get('FQDN')
    else f"{APP_NAME}.herokuapp.com"
)
FQDN = re.sub(r'^https?://', '', str(FQDN)).rstrip('/')
NO_PORT = is_enabled(environ.get('NO_PORT'), False)
HAS_SSL = is_enabled(getenv('HAS_SSL'), True)

if HAS_SSL:
    URL = f"https://{FQDN}/"
else:
    URL = f"http://{FQDN}/" if NO_PORT else f"http://{FQDN}:{PORT}/"

SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
WORKERS = int(environ.get('WORKERS', '4'))
SESSION_NAME = str(environ.get('SESSION_NAME', 'vdisk_stream_bot'))
MULTI_CLIENT = False
name = str(environ.get('name', 'VDISK_STREAM_BOT'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "298"))

REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"]

Bot_cmds = {
    "start": "Start Bot",
    "stats": "Get Bot Stats",
    "alive": "Check Bot Status",
    "settings": "Change Settings",
    "id": "Get Telegram ID",
    "info": "Get User Info",
    "restart": "Restart Bot",
    "maintenance": "Maintenance Mode",
          }
