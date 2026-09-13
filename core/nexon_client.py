import urllib.request
import json
import logging
import sys
from config import (
    NEXON_SEASON_URL,
    NEXON_POSITION_URL,
    NEXON_SPID_URL,
    DEFAULT_HEADERS
)
from core.db_builder import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

class NexonMetaClient:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()

    def fetch_json(self, url):
        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def sync_all_metadata(self):
        print("="*60)
        print("[+] 1. Đang tải danh sách Mùa giải (Seasons)...")
        seasons = self.fetch_json(NEXON_SEASON_URL)
        self.db.save_seasons(seasons)
        print(f"    -> Đã lưu {len(seasons)} mùa giải vào Database.")

        print("[+] 2. Đang tải danh sách Vị trí thi đấu (Positions)...")
        positions = self.fetch_json(NEXON_POSITION_URL)
        self.db.save_positions(positions)
        print(f"    -> Đã lưu {len(positions)} vị trí vào Database.")

        print("[+] 3. Đang tải danh mục Cầu thủ toàn cầu (SPID Metadata)...")
        players = self.fetch_json(NEXON_SPID_URL)
        print(f"    -> Nhận được {len(players):,} cầu thủ từ máy chủ.")
        self.db.batch_insert_players_meta(players)
        print(f"    -> Đã đồng bộ thành công vào SQLite Database.")
        print("="*60)
        return len(players)

if __name__ == "__main__":
    client = NexonMetaClient()
    client.sync_all_metadata()
