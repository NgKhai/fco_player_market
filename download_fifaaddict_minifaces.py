"""Download imported FIFAAddict minifaces once for local-only web serving."""

import concurrent.futures
import os
import sqlite3
import urllib.request

from config import DEFAULT_HEADERS, MINIFACES_DIR, SQLITE_DB_PATH


TARGET_DIR = os.path.join(MINIFACES_DIR, "fifaaddict")


def download(uid):
    path = os.path.join(TARGET_DIR, f"{uid}.png")
    if os.path.isfile(path) and os.path.getsize(path) > 500:
        return True, "exists"
    try:
        req = urllib.request.Request(f"https://s1.fifaaddict.com/fo4/players/{uid}.png", headers=DEFAULT_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
        if len(data) <= 500 or not data.startswith(b"\x89PNG"):
            return False, "invalid"
        with open(path, "wb") as output:
            output.write(data)
        return True, "downloaded"
    except Exception:
        return False, "failed"


def main(workers=12):
    os.makedirs(TARGET_DIR, exist_ok=True)
    with sqlite3.connect(SQLITE_DB_PATH) as db:
        uids = [row[0] for row in db.execute("SELECT uid FROM fifaaddict_players ORDER BY uid")]
    done = failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for ok, status in pool.map(download, uids):
            done += ok
            failed += not ok
            if (done + failed) % 100 == 0:
                print(f"{done + failed}/{len(uids)} | downloaded/existing={done} failed={failed}")
    print(f"Finished: {done} local images, {failed} failed")


if __name__ == "__main__":
    main()
