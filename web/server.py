import os
import sys
import json
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import signal
import time

# Add parent directory to path to import core modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import SQLITE_DB_PATH, MINIFACES_DIR, OUTPUT_DIR
from core.db_builder import DatabaseManager
from core.fifaaddict_client import FIFAAddictClient
from core.garena_vn_client import GarenaVNClient
from core.miniface_downloader import MinifaceDownloader

sys.stdout.reconfigure(encoding='utf-8')

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
db_manager = DatabaseManager()
fa_client = FIFAAddictClient(db_manager, locale="vn")
garena_client = GarenaVNClient(db_manager)
miniface_downloader = MinifaceDownloader()
remote_image_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _local_player(row):
    """Shape Nexon SQLite rows like the FIFAAddict card objects."""
    season = row["class_name"] or "FO4"
    return {
        "id": row["spid"],
        "spid": row["spid"],
        "pid": row["pid"],
        "uid": str(row["pid"]),
        "name": row["name_kr"] or str(row["pid"]),
        "year": season,
        "year_short": season,
        "pos": row["main_pos"] or "-",
        "pos1": row["main_pos"] or "-",
        "attrA": row["salary"] or 0,
        "attrB": row["ovr"] or 0,
        "salary": row["salary"] or 0,
        "foot_left": row["foot_left"],
        "foot_right": row["foot_right"],
        "skill_level": row["skill_moves"],
        "season_id": row["season_id"],
    }


def _local_players(keyword="", season=""):
    conn = db_manager.get_connection()
    try:
        if keyword:
            value = f"%{keyword}%"
            rows = conn.execute(
                """SELECT p.*, s.class_name FROM players p
                   LEFT JOIN seasons s ON s.season_id = p.season_id
                   WHERE p.name_kr LIKE ? OR CAST(p.spid AS TEXT) = ?
                      OR CAST(p.pid AS TEXT) = ?
                   ORDER BY p.spid LIMIT 200""",
                (value, keyword, keyword),
            ).fetchall()
        else:
            season_key = "".join(c for c in season.lower() if c.isalnum())
            season_ids = []
            for row in conn.execute("SELECT season_id, class_name FROM seasons"):
                class_key = "".join(c for c in row["class_name"].lower() if c.isalnum())
                aliases = {"26ts": "26tots"}
                if season_key in class_key or aliases.get(season_key, season_key) in class_key:
                    season_ids.append(row["season_id"])
            if not season_ids:
                return []
            marks = ",".join("?" for _ in season_ids)
            rows = conn.execute(
                f"""SELECT p.*, s.class_name FROM players p
                    LEFT JOIN seasons s ON s.season_id = p.season_id
                    WHERE p.season_id IN ({marks})
                    ORDER BY p.spid LIMIT 200""",
                season_ids,
            ).fetchall()
        return [_local_player(row) for row in rows]
    finally:
        conn.close()


def _local_player_detail(uid, spid=""):
    value = spid if str(spid).isdigit() else str(uid).removeprefix("pid")
    if not value.isdigit():
        return None
    conn = db_manager.get_connection()
    try:
        row = conn.execute(
            """SELECT p.*, s.class_name, s.display_name FROM players p
               LEFT JOIN seasons s ON s.season_id = p.season_id
               WHERE p.spid = ? OR p.pid = ? LIMIT 1""",
            (int(value), int(value)),
        ).fetchone()
        if not row:
            return None
        card = _local_player(row)
        card.update({
            "season_full": row["class_name"] or "FO4",
            "season_name": row["display_name"] or row["class_name"] or "FO4",
            "current_ovr": row["ovr"] or "-",
            "bodytype_name": "-",
            "height": row["height"] or "-",
            "weight": row["weight"] or "-",
            "foot_pref": row["foot_pref"] or "right",
            "team_name": row["team_name"] or "-",
        })
        return {"db": card, "price": {}, "traits": {}, "source": "SQLite local"}
    finally:
        conn.close()

class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

class FCOHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            body_data = json.loads(post_body)
        except Exception:
            body_data = {}

        # 1. API: Đăng nhập trực tiếp bằng Tài khoản & Mật khẩu Garena
        if path == "/api/garena/login":
            username = body_data.get("username", "").strip()
            password = body_data.get("password", "").strip()
            
            success, msg = garena_client.login_with_credentials(username, password)
            res = {
                "status": "success" if success else "error",
                "message": msg,
                "connected": success
            }
            self._send_json(res)
            return

        # 2. API: Cấu hình Token thủ công
        elif path == "/api/garena/token":
            token = body_data.get("token", "").strip()
            uid = body_data.get("uid", "").strip()
            if token:
                garena_client.set_token(token, uid)
                res = {"status": "success", "message": "Đã lưu token Garena VN thành công!", "connected": True}
            else:
                garena_client.set_token("", "")
                res = {"status": "success", "message": "Đã xóa token Garena VN.", "connected": False}
            self._send_json(res)
            return

        # 3. API: Đăng xuất Garena
        elif path == "/api/garena/logout":
            garena_client.set_token("", "")
            res = {"status": "success", "message": "Đã đăng xuất tài khoản Garena.", "connected": False}
            self._send_json(res)
            return

        self.send_error(404, "Not found")

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # ----------------- API ROUTES -----------------
        if path.startswith("/api/"):
            self.handle_api(path, query)
            return

        if path.startswith("/seasons/"):
            filename = urllib.parse.unquote(path.removeprefix("/seasons/"))
            if filename.startswith("season_") and filename.endswith(".png") and filename[7:-4].isdigit():
                full_path = os.path.join(OUTPUT_DIR, "seasons", filename)
                if os.path.isfile(full_path):
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Cache-Control", "max-age=86400")
                    self.end_headers()
                    with open(full_path, "rb") as f:
                        self.wfile.write(f.read())
                    return
            self.send_error(404, "Season image not found")
            return

        # ----------------- MINIFACE ASSETS ROUTE -----------------
        if path.startswith("/minifaces/"):
            rel_file = path.replace("/minifaces/", "")
            full_path = os.path.join(MINIFACES_DIR, rel_file)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                with open(full_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Miniface not found")
                return

        # Proxy remote FIFAAddict images through localhost so browser proxy settings cannot block them.
        if path.startswith("/remote-minifaces/"):
            uid = urllib.parse.unquote(path.rsplit("/", 1)[-1]).removesuffix(".png")
            if uid and all(c.isalnum() or c in "-_" for c in uid):
                try:
                    url = f"https://s1.fifaaddict.com/fo4/players/{uid}.png"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with remote_image_opener.open(req, timeout=10) as resp:
                        data = resp.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception:
                    pass
            self.send_error(404, "Remote miniface not found")
            return

        # Default static file serving (index.html, style.css, app.js)
        super().do_GET()

    def handle_api(self, path, query):
        response_data = {"status": "error", "message": "Endpoint not found"}
        status_code = 200

        try:
            # 1. API: Danh sách mùa giải
            if path == "/api/seasons":
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT season_id, class_name, season_img, display_name FROM seasons ORDER BY season_id DESC")
                seasons = [dict(r) for r in cursor.fetchall()]
                conn.close()
                response_data = {"status": "success", "data": seasons}

            # 2. API: Tìm kiếm cầu thủ (theo từ khóa hoặc mùa giải)
            elif path == "/api/players/search":
                keyword = query.get("q", [""])[0].strip().strip('"').strip("'").strip()
                season = query.get("season", [""])[0].strip().lower()

                try:
                    if keyword:
                        players = fa_client.search_players_by_name(keyword)
                    else:
                        players = fa_client.get_season_players(season or "icontm")
                except Exception:
                    players = []

                if not players:
                    players = _local_players(keyword, season or "icontm")

                response_data = {
                    "status": "success",
                    "total": len(players),
                    "data": players
                }

            # 3. API: Chi tiết cầu thủ & Bảng giá TTCN (Hỗ trợ ưu tiên VN và fallback KR)
            elif path == "/api/players/detail":
                uid = query.get("uid", [""])[0].strip()
                spid = query.get("spid", [""])[0].strip()
                if not uid:
                    response_data = {"status": "error", "message": "Missing uid parameter"}
                    status_code = 400
                else:
                    try:
                        detail = fa_client.get_player_full_detail(uid)
                    except Exception:
                        detail = None

                    if not detail:
                        detail = _local_player_detail(uid, spid)
                    
                    price_vn = None
                    if spid and spid.isdigit():
                        price_vn = garena_client.fetch_player_vn_price(int(spid))
                    
                    if detail:
                        detail["garena_connected"] = garena_client.is_connected()
                        if price_vn:
                            detail["price_vn"] = price_vn
                            detail["active_server"] = "VN"
                        else:
                            detail["active_server"] = "KR"

                    response_data = {
                        "status": "success",
                        "data": detail
                    }

            # 4. API: Trạng thái Garena
            elif path == "/api/garena/status":
                response_data = {
                    "status": "success",
                    "connected": garena_client.is_connected(),
                    "uid": garena_client.get_uid()
                }

            # 5. API: Tải ảnh Miniface
            elif path == "/api/miniface/download":
                spid = query.get("spid", [""])[0].strip()
                if spid.isdigit():
                    _, has_action, has_base = miniface_downloader.download_player_faces(int(spid))
                    response_data = {
                        "status": "success",
                        "has_action": has_action,
                        "has_base": has_base
                    }
                else:
                    response_data = {"status": "error", "message": "Invalid SPID"}

            # 6. API: Thống kê hệ thống
            elif path == "/api/stats":
                stats = db_manager.get_stats()
                stats["garena_connected"] = garena_client.is_connected()
                response_data = {"status": "success", "data": stats}

        except Exception as e:
            response_data = {"status": "error", "message": str(e)}
            status_code = 500

        self._send_json(response_data, status_code)

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def run_server(port=8080, auto_open=False):
    server_address = ('', port)
    
    try:
        httpd = ReusableHTTPServer(server_address, FCOHandler)
    except Exception as e:
        print(f"[-] Không thể mở port {port}: {e}")
        return

    url = f"http://localhost:{port}"
    print("=" * 75)
    print(f"  🚀 FC ONLINE WEB SERVER ĐANG CHẠY TẠI: {url}")
    print(f"  👉 Nhấn Ctrl + C hoặc gõ 'q' rồi Enter để dừng server bất kỳ lúc nào.")
    print("=" * 75)
    
    if auto_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    
    is_running = True

    def stop_server(sig=None, frame=None):
        nonlocal is_running
        if is_running:
            is_running = False
            print("\n[!] Đã nhận tín hiệu dừng. Đang tắt server...")

    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)

    def console_listener():
        nonlocal is_running
        while is_running:
            try:
                line = sys.stdin.readline()
                if not line or 'q' in line.lower():
                    stop_server()
                    break
            except Exception:
                break

    if sys.stdin and sys.stdin.isatty():
        listener_thread = threading.Thread(target=console_listener, daemon=True)
        listener_thread.start()

    httpd.timeout = 0.5
    try:
        while is_running:
            httpd.handle_request()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        try:
            httpd.server_close()
        except Exception:
            pass
        print("[✓] Server đã được dừng hoàn toàn.")

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port=port, auto_open=False)
