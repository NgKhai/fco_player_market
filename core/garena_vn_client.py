import urllib.request
import urllib.parse
import http.cookiejar
import hashlib
import json
import time
import sys
from config import DEFAULT_HEADERS
from core.db_builder import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

class GarenaVNClient:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.api_base = "https://fcom.garena.vn/api"
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPCookieProcessor(self.cj),
        )

    def get_token(self):
        return self.db.get_setting("garena_session_token", "")

    def get_uid(self):
        return self.db.get_setting("garena_uid", "")

    def set_token(self, token, uid=""):
        self.db.set_setting("garena_session_token", token.strip())
        if uid:
            self.db.set_setting("garena_uid", str(uid).strip())
        return True

    def is_connected(self):
        token = self.get_token()
        return bool(token and len(token) > 5)

    def login_with_credentials(self, username, password):
        """
        Authenticate with Garena SSO using username & password.
        """
        username = username.strip()
        password = password.strip()
        if not username or not password:
            return False, "Vui lòng nhập đầy đủ tài khoản và mật khẩu."

        # Pass 1: Garena OAuth / SSO Token Grant Flow
        try:
            pass_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            # Garena OAuth Token Endpoint
            url = "https://auth.garena.com/oauth/token/grant"
            payload = {
                "account": username,
                "password": pass_hash,
                "client_id": "100067",
                "redirect_uri": "https://fo4.garena.vn/",
                "response_type": "token"
            }
            
            data_encoded = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=data_encoded,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Content-Type': 'application/json',
                    'Referer': 'https://sso.garena.com/',
                    'Origin': 'https://sso.garena.com'
                }
            )
            
            with self.opener.open(req, timeout=12) as resp:
                res_text = resp.read().decode('utf-8')
                res_json = json.loads(res_text)
                
                access_token = res_json.get("access_token") or res_json.get("token") or res_json.get("sso_token")
                uid = res_json.get("uid") or res_json.get("garena_uid")
                
                if access_token:
                    self.set_token(access_token, uid or "")
                    return True, "Đăng nhập thành công! Đã tự động kết nối với máy chủ Garena VN."
                
                if "error" in res_json:
                    err = res_json.get("error")
                    if err == "error_auth":
                        return False, "Sai tài khoản hoặc mật khẩu Garena."
                    elif err == "error_captcha":
                        return False, "Tài khoản cần xác thực Captcha/OTP. Hãy chuyển sang tab 'Dán Token' để nhập token trực tiếp."
                    return False, f"Lỗi xác thực Garena: {err}"
        except urllib.error.HTTPError as e:
            if e.code in [400, 401]:
                return False, "Tài khoản hoặc mật khẩu không chính xác."
            elif e.code in [403, 429]:
                return False, "Máy chủ Garena yêu cầu xác thực Captcha chống bot. Hãy dùng tab 'Dán Token' để lấy token từ F12."
            return False, f"Lỗi kết nối Garena (HTTP {e.code}). Bạn có thể dùng tab 'Dán Token'."
        except Exception as e:
            return False, f"Không thể kết nối đến máy chủ Garena: {e}"

        return False, "Không nhận được phiên đăng nhập. Vui lòng dùng tab Dán Token."

    def fetch_player_vn_price(self, spid, force_refresh=False):
        spid = int(spid)

        if not force_refresh:
            cached = self.db.get_vn_prices(spid, max_age_seconds=1800)
            if cached:
                cached["source"] = "Garena VN (Cache)"
                cached["server"] = "VN"
                return cached

        token = self.get_token()
        if not token:
            return None

        try:
            url = f"{self.api_base}/market/card_price?spid={spid}"
            headers = dict(DEFAULT_HEADERS)
            headers.update({
                'Authorization': f"Bearer {token}",
                'X-GARENA-UID': self.get_uid(),
                'Referer': 'https://fcom.garena.vn/',
                'Origin': 'https://fcom.garena.vn'
            })
            
            req = urllib.request.Request(url, headers=headers)
            with self.opener.open(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                if data.get("code") == 0 and "data" in data:
                    raw_prices = data["data"].get("prices", {})
                    formatted_prices = {}
                    for g in range(1, 11):
                        p_val = raw_prices.get(str(g), 0)
                        formatted_prices[g] = self.format_bp(p_val)
                    
                    self.db.save_vn_prices(spid, formatted_prices)
                    result = {f"vn{k}": v for k, v in formatted_prices.items()}
                    result["source"] = "Garena VN (Live)"
                    result["server"] = "VN"
                    result["updatetime"] = time.strftime("%Y-%m-%d %H:%M")
                    return result
        except Exception:
            pass

        return None

    @staticmethod
    def format_bp(amount):
        try:
            val = int(amount)
            if val >= 1_000_000_000:
                return f"{val / 1_000_000_000:.2f}B".replace(".00B", "B")
            elif val >= 1_000_000:
                return f"{val / 1_000_000:.1f}M".replace(".0M", "M")
            elif val >= 1_000:
                return f"{val / 1_000:.0f}K"
            elif val > 0:
                return f"{val:,}"
            return "-"
        except Exception:
            return str(amount)

if __name__ == "__main__":
    client = GarenaVNClient()
    print("[+] Garena Client initialized.")
