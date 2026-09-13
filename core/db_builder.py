import sqlite3
import json
import os
import time
from config import SQLITE_DB_PATH, JSON_DB_PATH

class DatabaseManager:
    def __init__(self, db_path=SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Seasons Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seasons (
                season_id INTEGER PRIMARY KEY,
                class_name TEXT NOT NULL,
                season_img TEXT,
                display_name TEXT
            )
            """)

            # Positions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                pos_id INTEGER PRIMARY KEY,
                desc TEXT NOT NULL
            )
            """)

            # Players Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                spid INTEGER PRIMARY KEY,
                season_id INTEGER,
                pid INTEGER,
                name_kr TEXT,
                name_en TEXT,
                name_vi TEXT,
                main_pos TEXT,
                ovr INTEGER DEFAULT 0,
                salary INTEGER DEFAULT 0,
                height INTEGER DEFAULT 0,
                weight INTEGER DEFAULT 0,
                foot_pref TEXT,
                foot_left INTEGER DEFAULT 5,
                foot_right INTEGER DEFAULT 5,
                skill_moves INTEGER DEFAULT 1,
                team_name TEXT,
                nation_name TEXT,
                birthdate TEXT,
                attributes_json TEXT,
                traits_json TEXT,
                has_action_img INTEGER DEFAULT 0,
                has_base_img INTEGER DEFAULT 0,
                FOREIGN KEY (season_id) REFERENCES seasons(season_id)
            )
            """)

            # Vietnam Market Prices Table (Server Garena VN Cache)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_prices_vn (
                spid INTEGER,
                grade INTEGER,
                price_vn INTEGER,
                price_formatted TEXT,
                updated_at INTEGER,
                PRIMARY KEY (spid, grade)
            )
            """)

            # App Settings Table (Garena Token, configs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at INTEGER
            )
            """)

            # Indexes for ultra-fast lookup
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_name_kr ON players(name_kr)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_name_en ON players(name_en)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_season ON players(season_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_pid ON players(pid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_ovr ON players(ovr)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_vn_spid ON market_prices_vn(spid)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fifaaddict_players (
                uid TEXT PRIMARY KEY,
                season_code TEXT NOT NULL,
                name_vi TEXT,
                data_json TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fifaaddict_name ON fifaaddict_players(name_vi)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fifaaddict_season ON fifaaddict_players(season_code)")

            conn.commit()

    def save_fifaaddict_players(self, season_code, players):
        now = int(time.time())
        records = []
        for player in players:
            uid = str(player.get("uid", "")).strip()
            if uid:
                records.append((uid, season_code, player.get("name"), json.dumps(player, ensure_ascii=False), now))
        with self.get_connection() as conn:
            conn.executemany("""
            INSERT OR REPLACE INTO fifaaddict_players (uid, season_code, name_vi, data_json, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, records)
            conn.commit()
        return len(records)

    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            """, (key, value, int(time.time())))
            conn.commit()

    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return row["value"]
            return default

    def save_seasons(self, seasons_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for s in seasons_data:
                cursor.execute("""
                INSERT OR REPLACE INTO seasons (season_id, class_name, season_img, display_name)
                VALUES (?, ?, ?, ?)
                """, (s.get("seasonId"), s.get("className"), s.get("seasonImg"), s.get("className")))
            conn.commit()

    def save_positions(self, positions_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for p in positions_data:
                cursor.execute("""
                INSERT OR REPLACE INTO positions (pos_id, desc)
                VALUES (?, ?)
                """, (p.get("spposition"), p.get("desc")))
            conn.commit()

    def batch_insert_players_meta(self, players_meta):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            records = []
            for p in players_meta:
                spid = int(p.get("id"))
                season_id = spid // 1000000
                pid = spid % 1000000
                name_kr = p.get("name")
                records.append((spid, season_id, pid, name_kr))

            cursor.executemany("""
            INSERT OR IGNORE INTO players (spid, season_id, pid, name_kr)
            VALUES (?, ?, ?, ?)
            """, records)
            conn.commit()

    def save_vn_prices(self, spid, prices_dict):
        """
        prices_dict: {1: 12500000, 2: 45000000, ...} or { "1": "12.5M", ... }
        """
        now = int(time.time())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            records = []
            for grade, price_val in prices_dict.items():
                if str(grade).isdigit():
                    g = int(grade)
                    p_formatted = str(price_val)
                    p_int = 0
                    if isinstance(price_val, int):
                        p_int = price_val
                    records.append((int(spid), g, p_int, p_formatted, now))
            cursor.executemany("""
            INSERT OR REPLACE INTO market_prices_vn (spid, grade, price_vn, price_formatted, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, records)
            conn.commit()

    def get_vn_prices(self, spid, max_age_seconds=1800):
        """
        Get cached VN prices for a spid. Returns dict or None if expired/not found.
        """
        now = int(time.time())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT grade, price_formatted, updated_at 
            FROM market_prices_vn 
            WHERE spid = ? 
            ORDER BY grade ASC
            """, (int(spid),))
            rows = cursor.fetchall()
            if not rows:
                return None
            
            # Check age of newest row
            if now - rows[0]["updated_at"] > max_age_seconds:
                return None # Expired

            result = {}
            for r in rows:
                result[f"vn{r['grade']}"] = r["price_formatted"]
            return result

    def export_to_json(self, output_path=JSON_DB_PATH, limit=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            SELECT p.*, s.class_name as season_name, s.season_img
            FROM players p
            LEFT JOIN seasons s ON p.season_id = s.season_id
            ORDER BY p.ovr DESC, p.spid ASC
            """
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                item = dict(row)
                if item.get("attributes_json"):
                    item["attributes"] = json.loads(item["attributes_json"])
                if item.get("traits_json"):
                    item["traits"] = json.loads(item["traits_json"])
                result.append(item)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return len(result)

    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM seasons")
            total_seasons = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT spid) FROM market_prices_vn")
            vn_prices_count = cursor.fetchone()[0]
            return {
                "total_players": total_players,
                "total_seasons": total_seasons,
                "vn_prices_count": vn_prices_count
            }
