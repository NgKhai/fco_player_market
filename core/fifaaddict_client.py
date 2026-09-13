import urllib.request
import urllib.parse
import http.cookiejar
import uuid
import json
import time
import sys
from config import DEFAULT_HEADERS
from core.db_builder import DatabaseManager

sys.stdout.reconfigure(encoding='utf-8')

class FIFAAddictClient:
    def __init__(self, db_manager: DatabaseManager = None, locale="vn"):
        self.db = db_manager or DatabaseManager()
        self.locale = locale
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPCookieProcessor(self.cj),
        )
        self.token = None
        self._init_session()

    def _init_session(self):
        try:
            main_url = f"https://{self.locale}.fifaaddict.com/fo4db"
            req0 = urllib.request.Request(main_url, headers=DEFAULT_HEADERS)
            self.opener.open(req0, timeout=15)

            token_id = uuid.uuid4().hex
            handshake_url = f"https://{self.locale}.fifaaddict.com/api2?rq=araiwa&t={token_id}"
            headers_hs = dict(DEFAULT_HEADERS)
            headers_hs['Referer'] = main_url
            headers_hs['X-Requested-With'] = 'XMLHttpRequest'
            headers_hs['Cache-Control'] = 'no-store'

            resp = self.opener.open(urllib.request.Request(handshake_url, headers=headers_hs), timeout=15)
            self.token = resp.read().decode('utf-8').strip('"')
            return True
        except Exception as e:
            print(f"[-] Session handshake failed: {e}")
            return False

    def _get_api(self, query_str):
        if not self.token:
            self._init_session()
        url = f"https://{self.locale}.fifaaddict.com/api2?{query_str}&locale={self.locale}"
        headers = dict(DEFAULT_HEADERS)
        headers['Referer'] = f"https://{self.locale}.fifaaddict.com/fo4db"
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['X-ARAIWA'] = self.token
        headers['Accept'] = 'application/json, text/plain, */*'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = self.opener.open(req, timeout=15)
            return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                self._init_session()
                headers['X-ARAIWA'] = self.token
                req = urllib.request.Request(url, headers=headers)
                resp = self.opener.open(req, timeout=15)
                return json.loads(resp.read().decode('utf-8'))
            raise e

    def search_players_by_name(self, player_name):
        """
        Search players by name keyword (e.g. 'ronaldo', 'messi', 'son heung min')
        """
        encoded_name = urllib.parse.quote(player_name)
        query = f"q=fo4db&playername={encoded_name}"
        data = self._get_api(query)
        return data.get("db", [])

    def get_season_players(self, season_short_name):
        """
        Fetch all players of a specific season (e.g. 'icontm', '24toty', 'icon', 'ln', etc.)
        """
        query = f"q=fo4db&class={season_short_name}"
        data = self._get_api(query)
        return data.get("db", [])

    def get_player_full_detail(self, uid):
        """
        Fetch full player profile, attributes, traits, and live market price by UID.
        """
        if not uid.startswith("pid"):
            uid = f"pid{uid}"
        query = f"fo4pid={uid}"
        return self._get_api(query)

if __name__ == "__main__":
    client = FIFAAddictClient(locale="vn")
    results = client.search_players_by_name("ronaldo")
    print(f"[+] Tìm thấy {len(results)} kết quả cho 'ronaldo':")
    for p in results[:5]:
        print(f"    - {p.get('name')} | Mùa: {p.get('year_short') or p.get('year')} | OVR: {p.get('pos1val')} | Lương: {p.get('attrA')} | UID: {p.get('uid')}")
