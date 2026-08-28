import os
import json
from dotenv import load_dotenv

load_dotenv()

# === AUTENTIFICARE ===
OWNER_ID = int(os.getenv("OWNER_ID", 0))
TOKEN_FILE = "token.txt"

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())

USER_TOKEN = load_token()

# === MODELE AI ===
GATEKEEPER_MODEL = "llama3.2:1.5b"
FILTER_MODEL = "llama3.2:3b"
RESPONDER_MODEL = "llama3.2:7b"
VISION_MODEL = "llava:7b"

# === LIMITE ȘI RITM ===
GLOBAL_COOLDOWN = 4.0
HISTORY_LIMIT = 50
MESSAGE_TTL_SECONDS = 900
CLEANUP_INTERVAL_SECONDS = 300

# === MESAJE SPONTANE ===
SPONTANEOUS_ENABLED = True
MIN_SPONTANEOUS_INTERVAL = 1800
MAX_SPONTANEOUS_INTERVAL = 7200

# === VOICE ===
DEFAULT_VOLUME = 0.5
VOICE_TIMEOUT_SECONDS = 300

# === WEB DASHBOARD ===
WEB_HOST = "0.0.0.0"
WEB_PORT = 8081

# === FIȘIERE DE STARE ===
STATS_FILE = "stats.json"
IGNORED_CHANNELS_FILE = "ignored_channels.json"
TRUSTED_USERS_FILE = "trusted_users.json"

# === COADĂ ===
MESSAGE_QUEUE_TIMEOUT_SECONDS = 600
MAX_QUEUE_LOW_PRIORITY = 3

# === FILTRU TOXICITATE ===
FORBIDDEN_WORDS = [
    "prost", "idiot", "tâmpit", "retard", "cretin",
    "laș", "jigodie", "măgar", "bou", "vită",
    "insultă", "omor", "sinucidere", "viol",
]
MUTE_MINUTES = 10
MAX_WARNINGS = 3

# === FILTRU SPAM ===
SPAM_DETECTION_ENABLED = True
MIN_MESSAGE_LENGTH = 3
MAX_REPEATED_CHAR_PERCENT = 80
SPAM_CACHE_SIZE = 5
REPEAT_COOLDOWN_SECONDS = 30

# === UTILITARE ===
def load_json_file(filename, default=None):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}

def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_ignored_channels():
    return set(load_json_file(IGNORED_CHANNELS_FILE, []))

def save_ignored_channels(channels):
    save_json_file(IGNORED_CHANNELS_FILE, list(channels))

def load_trusted_users():
    return set(load_json_file(TRUSTED_USERS_FILE, []))

def save_trusted_users(users):
    save_json_file(TRUSTED_USERS_FILE, list(users))

def load_stats():
    stats = load_json_file(STATS_FILE, {
        "messages_processed": 0,
        "responses_sent": 0,
        "facts_extracted": 0,
        "spontaneous_messages": 0,
        "toxic_blocked": 0,
        "warnings_issued": 0,
        "mutes_activated": 0,
        "spam_blocked": 0,
        "sensitive_blocked": 0,
        "commands_used": {},
        "start_time": None
    })
    return stats

def save_stats(stats):
    if stats["start_time"] is None:
        from datetime import datetime
        stats["start_time"] = datetime.now().isoformat()
    save_json_file(STATS_FILE, stats)