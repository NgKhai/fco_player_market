import os
import sys
import json
import urllib.request
import concurrent.futures
import time

# Add base directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import MINIFACES_DIR, CDN_ACTION_MINIFACE, CDN_BASE_MINIFACE, DEFAULT_HEADERS
from core.db_builder import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

class HighSpeedMinifaceDownloader:
    def __init__(self, output_dir=MINIFACES_DIR, max_workers=35):
        self.output_dir = output_dir
        self.action_dir = os.path.join(output_dir, "action")
        self.base_dir = os.path.join(output_dir, "base")
        self.max_workers = max_workers
        os.makedirs(self.action_dir, exist_ok=True)
        os.makedirs(self.base_dir, exist_ok=True)

    def _download_file(self, urls, save_path, min_size=500):
        if os.path.exists(save_path) and os.path.getsize(save_path) >= min_size:
            return True, "exists"

        if isinstance(urls, str):
            urls = [urls]

        for url in urls:
            try:
                req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
                with urllib.request.urlopen(req, timeout=6) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        if len(data) >= min_size and not data.startswith(b"<!DOCTYPE") and not data.startswith(b"<html"):
                            with open(save_path, "wb") as f:
                                f.write(data)
                            return True, "downloaded"
            except Exception:
                continue
        return False, "failed"

    def download_player_faces(self, spid):
        spid = int(spid)
        pid = spid % 1000000

        action_path = os.path.join(self.action_dir, f"p{spid}.png")
        base_path = os.path.join(self.base_dir, f"p{pid}.png")

        # 1. Action Miniface (Nexon CDN -> FIFAAddict fallback)
        action_urls = [
            CDN_ACTION_MINIFACE.format(spid=spid),
            f"https://s1.fifaaddict.com/fo4/players/p{spid}.png"
        ]
        has_action, _ = self._download_file(action_urls, action_path)

        # 2. Base Avatar (Nexon CDN -> FIFAAddict fallback)
        base_urls = [
            CDN_BASE_MINIFACE.format(pid=pid),
            f"https://s1.fifaaddict.com/fo4/players/p{pid}.png"
        ]
        has_base, _ = self._download_file(base_urls, base_path)

        return spid, has_action, has_base

    def batch_download(self, spid_list, show_progress=True):
        total = len(spid_list)
        print("=" * 75)
        print(f"🚀 BẮT ĐẦU TẢI FULL MINIFACE CHO {total:,} CẦU THỦ")
        print(f"⚡ Số luồng đồng thời: {self.max_workers} Workers | Hỗ trợ Resume tự động")
        print(f"📁 Lưu tại: {self.output_dir}")
        print("=" * 75)

        start_time = time.time()
        success_action = 0
        success_base = 0
        completed = 0

        # Pre-check existing
        existing_action = len([f for f in os.listdir(self.action_dir) if f.endswith('.png')])
        existing_base = len([f for f in os.listdir(self.base_dir) if f.endswith('.png')])
        print(f"[*] Đã có sẵn trong máy: {existing_action:,} Action Minifaces | {existing_base:,} Base Avatars")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_spid = {executor.submit(self.download_player_faces, spid): spid for spid in spid_list}
            for future in concurrent.futures.as_completed(future_to_spid):
                spid, has_action, has_base = future.result()
                if has_action:
                    success_action += 1
                if has_base:
                    success_base += 1
                completed += 1

                if show_progress and (completed % 25 == 0 or completed == total):
                    elapsed = time.time() - start_time
                    speed = completed / elapsed if elapsed > 0 else 0
                    percent = (completed / total) * 100
                    remaining = (total - completed) / speed if speed > 0 else 0
                    print(
                        f"\r[{percent:5.1f}%] {completed:,}/{total:,} thẻ | "
                        f"Action: {success_action:,} | Base: {success_base:,} | "
                        f"Tốc độ: {speed:.1f} thẻ/s | Còn lại: {remaining/60:.1f}p",
                        end="", flush=True
                    )

        total_elapsed = time.time() - start_time
        print("\n" + "=" * 75)
        print(f"🎉 HOÀN THÀNH TẢI MINIFACE TRONG {total_elapsed/60:.1f} PHÚT ({total_elapsed:.1f}s)!")
        print(f"    - Tổng Action Minifaces đã tải: {success_action:,} ảnh")
        print(f"    - Tổng Base Avatars đã tải: {success_base:,} ảnh")
        print("=" * 75)

MinifaceDownloader = HighSpeedMinifaceDownloader

if __name__ == "__main__":
    # Load all SPIDs from spid.json or DB
    spid_file = os.path.join(BASE_DIR, "output", "database", "spid.json")
    if os.path.exists(spid_file):
        with open(spid_file, "r", encoding="utf-8") as f:
            spid_data = json.load(f)
            all_spids = [p["id"] for p in spid_data]
    else:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT spid FROM players")
            all_spids = [row[0] for row in cursor.fetchall()]

    downloader = HighSpeedMinifaceDownloader(max_workers=35)
    downloader.batch_download(all_spids)
