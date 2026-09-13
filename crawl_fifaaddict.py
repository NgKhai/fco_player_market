"""Import Vietnamese FIFAAddict player data into the local SQLite database."""

import argparse
import re
import time
import urllib.request

from config import DEFAULT_HEADERS
from core.db_builder import DatabaseManager
from core.fifaaddict_client import FIFAAddictClient


def get_season_codes(client):
    url = f"https://{client.locale}.fifaaddict.com/fo4db"
    html = client.opener.open(urllib.request.Request(url, headers=DEFAULT_HEADERS), timeout=20).read()
    return list(dict.fromkeys(re.findall(r'name="season" value="([a-z0-9_-]+)"', html.decode("utf-8", "ignore"))))


def crawl(limit_seasons=None, delay=0.5):
    db = DatabaseManager()
    client = FIFAAddictClient(db, locale="vn")
    seasons = get_season_codes(client)
    if limit_seasons:
        seasons = seasons[:limit_seasons]
    total = 0
    for index, season in enumerate(seasons, 1):
        players = client.get_season_players(season)
        saved = db.save_fifaaddict_players(season, players)
        total += saved
        print(f"[{index}/{len(seasons)}] {season}: {saved} players")
        time.sleep(delay)
    print(f"Imported {total} FIFAAddict records into SQLite.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-seasons", type=int, help="Only import the first N seasons for a smoke test")
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()
    crawl(args.limit_seasons, args.delay)
