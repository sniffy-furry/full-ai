import os
import json
from dotenv import load_dotenv

load_dotenv()

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

# Modele Ollama
GATEKEEPER_MODEL = "qwen2.5:1.5b"
FILTER_MODEL = "qwen2.5:3b"
RESPONDER_MODEL = "dolphin-llama3:latest"
VISION_MODEL = "llava-phi3:latest"

# Limite și ritm
GLOBAL_COOLDOWN = 4.0
HISTORY_LIMIT = 50
MESSAGE_TTL_SECONDS = 900
CLEANUP_INTERVAL_SECONDS = 300

# Mesaje spontane
SPONTANEOUS_ENABLED = True
MIN_SPONTANEOUS_INTERVAL = 1800
MAX_SPONTANEOUS_INTERVAL = 7200

# Memorie conversațională
MAX_CONVERSATION_TURNS = 8

# Voice
DEFAULT_VOLUME = 0.5
VOICE_TIMEOUT_SECONDS = 300

# Dashboard Web
WEB_HOST = "0.0.0.0"
WEB_PORT = 8081

# Fișiere de stare
STATS_FILE = "stats.json"
IGNORED_CHANNELS_FILE = "ignored_channels.json"
TRUSTED_USERS_FILE = "trusted_users.json"

# Coadă
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

def load_ignored_channels():
    try:
        with open(IGNORED_CHANNELS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_ignored_channels(channels):
    with open(IGNORED_CHANNELS_FILE, "w") as f:
        json.dump(list(channels), f, indent=2)

def load_trusted_users():
    """Încarcă lista de utilizatori de încredere (AI nerestricționat)."""
    try:
        with open(TRUSTED_USERS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_trusted_users(users):
    """Salvează lista de utilizatori de încredere."""
    with open(TRUSTED_USERS_FILE, "w") as f:
        json.dump(list(users), f, indent=2)

def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
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
        }

def save_stats(stats):
    if stats["start_time"] is None:
        from datetime import datetime
        stats["start_time"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)
