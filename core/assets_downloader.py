import os
import sys
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

SEASONS_DIR = os.path.join(OUTPUT_DIR, "seasons")
CARD_FRAMES_DIR = os.path.join(OUTPUT_DIR, "card_frames")
CLUBS_DIR = os.path.join(OUTPUT_DIR, "clubs")
NATIONS_DIR = os.path.join(OUTPUT_DIR, "nations")
TRAITS_DIR = os.path.join(OUTPUT_DIR, "traits")
DB_DIR = os.path.join(OUTPUT_DIR, "database")

for d in [SEASONS_DIR, CARD_FRAMES_DIR, CLUBS_DIR, NATIONS_DIR, TRAITS_DIR, DB_DIR]:
    os.makedirs(d, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_file(url, target_path, min_size=200):
    if os.path.exists(target_path) and os.path.getsize(target_path) >= min_size:
        return True # Already exists

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read()
            if len(content) >= min_size and not content.startswith(b"<!DOCTYPE") and not content.startswith(b"<html"):
                with open(target_path, "wb") as f:
                    f.write(content)
                return True
    except Exception:
        pass
    return False

# ==========================================
# 1. DOWNLOAD SEASON BADGES & METADATA
# ==========================================
def download_seasons():
    print("[1/5] 🏅 Đang đồng bộ và tải Logo Mùa Thẻ (Seasons)...")
    url = "https://open.api.nexon.com/static/fconline/meta/seasonid.json"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            seasons_data = json.loads(resp.read().decode('utf-8'))
            
            # Save raw json
            with open(os.path.join(DB_DIR, "seasons.json"), "w", encoding="utf-8") as f:
                json.dump(seasons_data, f, ensure_ascii=False, indent=2)

            download_tasks = []
            for s in seasons_data:
                sid = s.get("seasonId")
                s_img = s.get("seasonImg")
                if s_img:
                    target_file = os.path.join(SEASONS_DIR, f"season_{sid}.png")
                    download_tasks.append((s_img, target_file))

            success = 0
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = {executor.submit(download_file, u, p): (u, p) for u, p in download_tasks}
                for fut in as_completed(futures):
                    if fut.result():
                        success += 1

            print(f"    -> Đã tải thành công {success}/{len(download_tasks)} logo mùa giải.")
            return seasons_data
    except Exception as e:
        print(f"    [-] Lỗi tải seasons: {e}")
        return []

# ==========================================
# 2. DOWNLOAD CARD FRAMES (PHÔI THẺ 3D)
# ==========================================
def download_card_frames(seasons_data):
    print("[2/5] 🃏 Đang tải Khung Nền Phôi Thẻ 3D (Card Backgrounds)...")
    download_tasks = []
    
    # Check seasons
    for s in seasons_data:
        sid = s.get("seasonId")
        # Primary Nexon/FIFAAddict CDN
        urls = [
            f"https://s1.fifaaddict.com/fo4/cardbg/{sid}.png",
            f"https://s1.fifaaddict.com/assets/img/cardbg/{s.get('className', '').lower()}.png",
            f"https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/cardbg/{sid}.png"
        ]
        target_file = os.path.join(CARD_FRAMES_DIR, f"card_bg_{sid}.png")
        for u in urls:
            download_tasks.append((u, target_file))

    success = 0
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(download_file, u, p, 1000): p for u, p in download_tasks}
        seen = set()
        for fut in as_completed(futures):
            p = futures[fut]
            if fut.result() and p not in seen:
                seen.add(p)
                success += 1

    print(f"    -> Đã tải thành công {success} phôi thẻ 3D.")

# ==========================================
# 3. DOWNLOAD TRAIT ICONS (KỸ NĂNG ẨN)
# ==========================================
def download_trait_icons():
    print("[3/5] ✨ Đang tải Icon Kỹ Năng Ẩn (Trait Icons)...")
    # Common FC Online traits
    trait_ids = [
        "finesse-shot", "speed-dribbler", "power-header", "playmaker", "leadership",
        "long-shot-taker", "early-crosser", "outside-foot", "technical-dribbler",
        "giant-throw-in", "takes-finesse-freekicks", "target-forward", "diver",
        "injury-prone", "solid-player", "self-dribbler", "skilled-dribbler",
        "super-sub", "chip-shot", "long-throw-in", "power-free-kick", "puncher",
        "cautious-with-crosses", "gk-comes-for-crosses", "gk-long-throw", "gk-flat-kick",
        "gk-sweeper", "1-on-1", "swerving"
    ]
    
    download_tasks = []
    for tid in trait_ids:
        # Check fifaaddict & nexon
        u = f"https://s1.fifaaddict.com/assets/img/traits/{tid}.png"
        target_file = os.path.join(TRAITS_DIR, f"{tid}.png")
        download_tasks.append((u, target_file))

    success = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_file, u, p, 100): p for u, p in download_tasks}
        for fut in as_completed(futures):
            if fut.result():
                success += 1

    print(f"    -> Đã tải thành công {success}/{len(trait_ids)} icon kỹ năng ẩn.")

# ==========================================
# 4. DOWNLOAD NATION FLAGS & CLUBS
# ==========================================
def download_nations_and_clubs():
    print("[4/5] 🛡️ Đang tải Quốc Kỳ & Logo CLB Tiêu Biểu...")
    
    # 1. Nations (1 to 230)
    nation_tasks = []
    for nid in range(1, 230):
        u = f"https://s1.fifaaddict.com/fo4/countries/{nid}.png"
        target_file = os.path.join(NATIONS_DIR, f"nation_{nid}.png")
        nation_tasks.append((u, target_file))

    # 2. Popular Clubs (Top ~300 popular club IDs)
    club_tasks = []
    popular_club_ids = [
        1, 2, 3, 5, 9, 10, 11, 13, 14, 18, 19, 21, 22, 25, 44, 45, 52, 73, 111,
        240, 241, 242, 243, 244, 245, 246, 247, 448, 449, 450, 481, 483, 485,
        1871, 1873, 1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1885
    ]
    for cid in popular_club_ids:
        u = f"https://s1.fifaaddict.com/fo4/clubs/{cid}.png"
        target_file = os.path.join(CLUBS_DIR, f"club_{cid}.png")
        club_tasks.append((u, target_file))

    success_nations = 0
    success_clubs = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        f_nat = {executor.submit(download_file, u, p, 100): p for u, p in nation_tasks}
        for fut in as_completed(f_nat):
            if fut.result():
                success_nations += 1

        f_clb = {executor.submit(download_file, u, p, 100): p for u, p in club_tasks}
        for fut in as_completed(f_clb):
            if fut.result():
                success_clubs += 1

    print(f"    -> Đã tải thành công {success_nations} Quốc kỳ & {success_clubs} Logo CLB.")

# ==========================================
# 5. SYNC FULL METADATA FROM NEXON
# ==========================================
def sync_full_metadata():
    print("[5/5] 🗄️ Đang tải Full Metadata Cầu thủ (88.246 thẻ) & Vị trí...")
    
    # 1. SPID metadata
    spid_url = "https://open.api.nexon.com/static/fconline/meta/spid.json"
    pos_url = "https://open.api.nexon.com/static/fconline/meta/spposition.json"
    
    try:
        req = urllib.request.Request(spid_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            with open(os.path.join(DB_DIR, "spid.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"    -> Đã lưu 88.246 cầu thủ vào output/database/spid.json ({len(data)} thẻ).")

        req = urllib.request.Request(pos_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            pos_data = json.loads(resp.read().decode('utf-8'))
            with open(os.path.join(DB_DIR, "positions.json"), "w", encoding="utf-8") as f:
                json.dump(pos_data, f, ensure_ascii=False, indent=2)
            print(f"    -> Đã lưu {len(pos_data)} vị trí vào output/database/positions.json.")
    except Exception as e:
        print(f"    [-] Lỗi tải metadata: {e}")

if __name__ == "__main__":
    start_time = time.time()
    print("=" * 75)
    print("🚀 BẮT ĐẦU TẢI TOÀN BỘ TÀI NGUYÊN (LOGO MÙA, PHÔI THẺ, TRAITS, CLB, DB)")
    print("=" * 75)
    
    seasons = download_seasons()
    download_card_frames(seasons)
    download_trait_icons()
    download_nations_and_clubs()
    sync_full_metadata()
    
    elapsed = time.time() - start_time
    print("=" * 75)
    print(f"🎉 HOÀN TẤT TẢI TOÀN BỘ TÀI NGUYÊN BỔ SUNG TRONG: {elapsed:.1f} GIÂY!")
    print(f"📁 Kiểm tra thư mục: {OUTPUT_DIR}")
    print("=" * 75)
