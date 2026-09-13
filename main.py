import os
import sys
import json
import time
from config import SQLITE_DB_PATH, JSON_DB_PATH, MINIFACES_DIR, OUTPUT_DIR
from core.db_builder import DatabaseManager
from core.nexon_client import NexonMetaClient
from core.fifaaddict_client import FIFAAddictClient
from core.miniface_downloader import MinifaceDownloader

sys.stdout.reconfigure(encoding='utf-8')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("=" * 75)
    print("      ⚽ BỘ CÔNG CỤ TRÍCH XUẤT DỮ LIỆU & TTCN FC ONLINE ⚽      ")
    print("               Workspace: D:\\Coding\\ToolFCO                     ")
    print("=" * 75)

def show_database_status(db: DatabaseManager):
    stats = db.get_stats()
    print(f"\n📊 TÌNH TRẠNG CƠ SỞ DỮ LIỆU HIỆN TẠI:")
    print(f"   • Tổng số cầu thủ trong DB : {stats['total_players']:,}")
    print(f"   • Tổng số mùa giải (Seasons): {stats['total_seasons']}")
    print(f"   • File SQLite Database     : {SQLITE_DB_PATH}")
    print(f"   • Thư mục ảnh Minifaces    : {MINIFACES_DIR}")
    print("-" * 75)

def option_sync_metadata(db: DatabaseManager):
    print("\n[+] Đang tiến hành đồng bộ toàn bộ Metadata từ máy chủ...")
    client = NexonMetaClient(db)
    total = client.sync_all_metadata()
    print(f"\n[✓] Hoàn tất đồng bộ {total:,} cầu thủ vào SQLite Database!")

def option_search_players(db: DatabaseManager):
    raw_input = input("\n🔍 Nhập tên cầu thủ (ví dụ: Ronaldo, Messi, Son, Gullit...) hoặc SPID: ")
    keyword = raw_input.strip().strip('"').strip("'").strip()
    
    if not keyword:
        print("[-] Bạn chưa nhập từ khóa tìm kiếm.")
        return

    fa_client = FIFAAddictClient(db, locale="vn")
    
    # 1. Nếu người dùng nhập mã số (SPID / PID)
    if keyword.isdigit():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, s.class_name 
        FROM players p 
        LEFT JOIN seasons s ON p.season_id = s.season_id 
        WHERE p.spid = ? OR p.pid = ?
        """, (int(keyword), int(keyword)))
        rows = cursor.fetchall()
        conn.close()
        if rows:
            print(f"\n[+] Kết quả tìm thấy trong Database SQLite:")
            for r in rows:
                print(f"    • SPID: {r['spid']} | Tên: {r['name_kr']} | Mùa: {r['class_name']}")
        else:
            print(f"[-] Không tìm thấy ID {keyword} trong DB.")
        return

    # 2. Tìm kiếm theo tên cầu thủ trên máy chủ FIFAAddict
    print(f"\n[+] Đang tìm kiếm cầu thủ '{keyword}' trên máy chủ...")
    try:
        results = fa_client.search_players_by_name(keyword)
        if not results:
            print(f"[-] Không tìm thấy kết quả nào cho '{keyword}'.")
            print("💡 Gợi ý: Hãy nhập tên tiếng Anh hoặc họ tên (ví dụ: Ronaldo, Messi, Gullit, Pele, Son...)")
            return

        print(f"\n[✓] Tìm thấy {len(results)} thẻ cầu thủ phù hợp:")
        print(f"{'STT':<4} | {'Tên cầu thủ':<24} | {'Mùa thẻ':<10} | {'Vị trí':<6} | {'OVR':<5} | {'Lương':<5} | {'Giá TTCN (+1)':<12}")
        print("-" * 75)

        display_count = min(len(results), 20)
        for i in range(display_count):
            p = results[i]
            stt = i + 1
            name = p.get('name', '')[:24]
            season = (p.get('year_short') or p.get('year') or '')[:10]
            pos = p.get('pos1') or p.get('pos') or '-'
            ovr = str(p.get('pos1val') or p.get('attrB') or '-')
            salary = str(p.get('attrA') or '-')
            price = str(p.get('pricekr') or '-')
            print(f"{stt:<4} | {name:<24} | {season:<10} | {pos:<6} | {ovr:<5} | {salary:<5} | {price:<12}")

        if len(results) > 20:
            print(f"... (và còn {len(results) - 20} thẻ cầu thủ khác)")

        # Cho phép người dùng xem chi tiết bảng giá TTCN
        detail_choice = input("\n👉 Nhập STT để xem CHI TIẾT & BẢNG GIÁ TTCN (hoặc Enter để quay lại): ").strip()
        if detail_choice.isdigit():
            idx = int(detail_choice) - 1
            if 0 <= idx < len(results):
                chosen_player = results[idx]
                show_player_full_detail(fa_client, chosen_player)
    except Exception as e:
        print(f"[-] Lỗi khi tìm kiếm: {e}")

def show_player_full_detail(client: FIFAAddictClient, player_summary):
    uid = player_summary.get('uid')
    print(f"\n[+] Đang tải dữ liệu chi tiết cho: {player_summary.get('name')} (UID: {uid})...")
    detail = client.get_player_full_detail(uid)
    if not detail or 'db' not in detail:
        print("[-] Không tải được chi tiết cầu thủ.")
        return

    db_info = detail['db']
    price_info = detail.get('price', {})
    traits_info = detail.get('traits', {})

    print("\n" + "=" * 75)
    print(f"📋 THÔNG TIN CHI TIẾT: {db_info.get('name').upper()}")
    print("=" * 75)
    print(f"  • Mùa giải      : {db_info.get('season_full')} ({db_info.get('season_name', '').upper()})")
    print(f"  • Chỉ số OVR    : {db_info.get('current_ovr')}")
    print(f"  • Mức lương     : {db_info.get('salary')} FP")
    print(f"  • Vị trí chính  : {db_info.get('pos1')} / {db_info.get('pos2')}")
    print(f"  • Thể hình      : {db_info.get('bodytype_name')} ({db_info.get('height')}cm / {db_info.get('weight')}kg)")
    print(f"  • Chân thuận    : {db_info.get('foot_pref', '').upper()} (Trái {db_info.get('foot_left')} - Phải {db_info.get('foot_right')})")
    print(f"  • Kỹ thuật      : {'★' * int(db_info.get('skill_level', 1))}")
    if traits_info:
        traits_list = list(traits_info.keys())
        print(f"  • Chỉ số ẩn     : {', '.join(traits_list)}")

    print("\n💰 BẢNG GIÁ THỊ TRƯỜNG CHUYỂN NHƯỢNG (TTCN LIVE):")
    print(f"  (Cập nhật gần nhất: {price_info.get('updatetime', 'Hôm nay')})")
    print("-" * 75)
    
    levels = [
        ("+1", price_info.get("kr1")),
        ("+2", price_info.get("kr2")),
        ("+3", price_info.get("kr3")),
        ("+4", price_info.get("kr4")),
        ("+5", price_info.get("kr5")),
        ("+6", price_info.get("kr6")),
        ("+7", price_info.get("kr7")),
        ("+8", price_info.get("kr8")),
        ("+9", price_info.get("kr9")),
        ("+10", price_info.get("kr10")),
    ]
    for lvl, pr in levels:
        if pr:
            print(f"  • Thẻ {lvl:<3} : {pr:>12} BP")
    print("=" * 75)

def option_download_minifaces(db: DatabaseManager):
    print("\n[+] TÙY CHỌN TẢI ẢNH MINIFACE:")
    print("    1. 🚀 TẢI TOÀN BỘ MINIFACE CHO TẤT CẢ 88.246 CẦU THỦ (Tốc độ cao 35 workers)")
    print("    2. Tải ảnh cho toàn bộ cầu thủ mùa giải ICON TM (Season 100)")
    print("    3. Tải ảnh cho danh sách top 100 cầu thủ đầu tiên")
    print("    4. Tải ảnh cho một mã SPID cụ thể")
    print("    5. Tải ảnh hàng loạt theo Season ID tùy chọn")
    sub_opt = input("👉 Chọn tùy chọn (1-5): ").strip()

    conn = db.get_connection()
    cursor = conn.cursor()

    if sub_opt == "1":
        cursor.execute("SELECT spid FROM players")
        spids = [row[0] for row in cursor.fetchall()]
        downloader = MinifaceDownloader(max_workers=35)
        downloader.batch_download(spids)
    elif sub_opt == "2":
        cursor.execute("SELECT spid FROM players WHERE season_id = 100")
        spids = [row[0] for row in cursor.fetchall()]
        downloader = MinifaceDownloader(max_workers=20)
        downloader.batch_download(spids)
    elif sub_opt == "3":
        cursor.execute("SELECT spid FROM players LIMIT 100")
        spids = [row[0] for row in cursor.fetchall()]
        downloader = MinifaceDownloader(max_workers=10)
        downloader.batch_download(spids)
    elif sub_opt == "4":
        spid_input = input("Nhập SPID: ").strip()
        if spid_input.isdigit():
            downloader = MinifaceDownloader(max_workers=5)
            downloader.batch_download([int(spid_input)])
    elif sub_opt == "5":
        season_input = input("Nhập Season ID (ví dụ: 100, 241...): ").strip()
        if season_input.isdigit():
            cursor.execute("SELECT spid FROM players WHERE season_id = ?", (int(season_input),))
            spids = [row[0] for row in cursor.fetchall()]
            if spids:
                downloader = MinifaceDownloader(max_workers=15)
                downloader.batch_download(spids)
            else:
                print(f"[-] Không có cầu thủ nào cho mùa giải ID {season_input}")
    conn.close()

def option_fetch_vietnamese_details(db: DatabaseManager):
    print("\n[+] Lấy dữ liệu chi tiết, chỉ số & giá TTCN từ FIFAAddict theo mùa thẻ:")
    season_code = input("👉 Nhập mã mùa thẻ (ví dụ: icontm, 24toty, icon, btb, ln...): ").strip().lower()
    if not season_code:
        season_code = "icontm"

    fa_client = FIFAAddictClient(db, locale="vn")
    print(f"\n[+] Đang tải danh sách cầu thủ mùa [{season_code}]...")
    try:
        players = fa_client.get_season_players(season_code)
        print(f"[+] Tìm thấy {len(players)} cầu thủ. Bắt đầu lấy chi tiết từng cầu thủ & giá TTCN...")
        
        for idx, p in enumerate(players, 1):
            uid = p.get("uid")
            p_name = p.get("name")
            print(f"    [{idx}/{len(players)}] Cầu thủ: {p_name} (UID: {uid})")
            detail = fa_client.get_player_full_detail(uid)
            
            if detail and 'db' in detail:
                db_info = detail['db']
                price_info = detail.get('price', {})
                print(f"         -> OVR: {db_info.get('current_ovr')}, Lương: {db_info.get('salary')}, Thể hình: {db_info.get('bodytype_name')}")
                if price_info.get('kr1'):
                    print(f"         -> Giá TTCN +1: {price_info.get('kr1')} | +5: {price_info.get('kr5', '-')} | +8: {price_info.get('kr8', '-')}")
            time.sleep(0.1)
        print(f"\n[✓] Đã hoàn thành lấy dữ liệu mùa [{season_code}]!")
    except Exception as e:
        print(f"[-] Lỗi: {e}")

def option_export_json(db: DatabaseManager):
    print("\n[+] Đang xuất dữ liệu ra file JSON...")
    count = db.export_to_json(JSON_DB_PATH)
    print(f"[✓] Đã xuất thành công {count:,} cầu thủ ra file:\n    -> {JSON_DB_PATH}")

def main():
    db = DatabaseManager()
    while True:
        print_banner()
        show_database_status(db)
        print("MENU CHỨC NĂNG:")
        print("  1. 🔄 Đồng bộ toàn bộ Metadata cầu thủ & mùa giải (Nexon Server API)")
        print("  2. 🖼️  Tải kho ảnh Miniface HD (Action & Base PNG đa luồng)")
        print("  3. 🔍 Tra cứu cầu thủ & Bảng giá TTCN Live (Ronaldo, Messi, Son...)")
        print("  4. 🇻🇳 Lấy thông số chi tiết, Tiếng Việt & Giá TTCN theo Mùa thẻ")
        print("  5. 💾 Xuất toàn bộ Database ra file JSON sạch")
        print("  0. ❌ Thoát")
        print("=" * 75)

        choice = input("👉 Chọn chức năng (0-5): ").strip()
        if choice == "1":
            option_sync_metadata(db)
        elif choice == "2":
            option_download_minifaces(db)
        elif choice == "3":
            option_search_players(db)
        elif choice == "4":
            option_fetch_vietnamese_details(db)
        elif choice == "5":
            option_export_json(db)
        elif choice == "0":
            print("\n👋 Tạm biệt! Hẹn gặp lại.")
            break
        else:
            print("[-] Lựa chọn không hợp lệ, vui lòng chọn lại.")
        
        input("\nNhấn Enter để tiếp tục...")
        clear_screen()

if __name__ == "__main__":
    main()
