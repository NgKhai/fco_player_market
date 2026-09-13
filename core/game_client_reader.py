"""Read-only checks for the installed FC Online client assets."""

from pathlib import Path

from config import GAME_DB_PATH, GAME_DIR, GAME_VI_ARCHIVE_PATH


def inspect_game_client() -> dict:
    root = Path(GAME_DIR)
    files = {
        "game_db": Path(GAME_DB_PATH),
        "vietnamese_archive": Path(GAME_VI_ARCHIVE_PATH),
    }
    return {
        "path": str(root),
        "exists": root.is_dir(),
        "files": {
            name: {
                "path": str(path),
                "exists": path.is_file(),
                "size": path.stat().st_size if path.is_file() else 0,
            }
            for name, path in files.items()
        },
        # ponytail: keep this inspect-only until a supported client extractor/key exists.
        "localized_names_available": False,
        "reason": "Game assets are proprietary binary files; a supported extractor/key is required.",
    }


if __name__ == "__main__":
    result = inspect_game_client()
    assert result["exists"], f"Không tìm thấy thư mục game: {GAME_DIR}"
    for name, info in result["files"].items():
        status = f"OK ({info['size']:,} bytes)" if info["exists"] else "MISSING"
        print(f"{name}: {status}")
    print(f"localized_names_available: {result['localized_names_available']}")
    print(result["reason"])
