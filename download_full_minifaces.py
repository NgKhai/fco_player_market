import sys
import os

# Set UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.miniface_downloader import HighSpeedMinifaceDownloader
import json

if __name__ == "__main__":
    spid_file = os.path.join(os.path.dirname(__file__), "output", "database", "spid.json")
    if not os.path.exists(spid_file):
        print(f"[-] Không tìm thấy file {spid_file}. Đang đồng bộ metadata trước...")
        import core.assets_downloader
        core.assets_downloader.sync_full_metadata()

    with open(spid_file, "r", encoding="utf-8") as f:
        spid_data = json.load(f)
        all_spids = [p["id"] for p in spid_data]

    print(f"[+] Tìm thấy tổng cộng {len(all_spids):,} thẻ cầu thủ trong cơ sở dữ liệu.")
    downloader = HighSpeedMinifaceDownloader(max_workers=35)
    downloader.batch_download(all_spids)
