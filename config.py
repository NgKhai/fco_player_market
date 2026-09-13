import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folders
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATABASE_DIR = os.path.join(OUTPUT_DIR, "database")
MINIFACES_DIR = os.path.join(OUTPUT_DIR, "minifaces")
LOCALIZATION_DIR = os.path.join(OUTPUT_DIR, "localization")

# Output files
SQLITE_DB_PATH = os.path.join(DATABASE_DIR, "fconline.sqlite")
JSON_DB_PATH = os.path.join(DATABASE_DIR, "players_db.json")
SEASONS_JSON_PATH = os.path.join(DATABASE_DIR, "seasons.json")

# Game Directory (Read-Only)
GAME_DIR = r"C:\Garena\Games\32837"

# Nexon Open API Endpoints
NEXON_META_BASE = "https://open.api.nexon.com/static/fconline/meta"
NEXON_SPID_URL = f"{NEXON_META_BASE}/spid.json"
NEXON_SEASON_URL = f"{NEXON_META_BASE}/seasonid.json"
NEXON_POSITION_URL = f"{NEXON_META_BASE}/spposition.json"

# Miniface CDN URLs
CDN_ACTION_MINIFACE = "https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{spid}.png"
CDN_BASE_MINIFACE = "https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/players/p{pid}.png"

# Headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Create required directories
for d in [OUTPUT_DIR, DATABASE_DIR, MINIFACES_DIR, LOCALIZATION_DIR]:
    os.makedirs(d, exist_ok=True)
