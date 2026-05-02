# persistence.py — Load/save leaderboard and settings

import json
import os
from config import LEADERBOARD_FILE, SETTINGS_FILE

# ── Default values ─────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "sound":       False,
    "car_color":   [220, 50, 50],
    "difficulty":  1,          # index into DIFFICULTIES list
}


# ── Settings ───────────────────────────────────────────────────

def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[persistence] save_settings error: {e}")


# ── Leaderboard ────────────────────────────────────────────────

def load_leaderboard() -> list[dict]:
    """Return list of dicts: {name, score, distance, coins}. Sorted desc by score."""
    try:
        with open(LEADERBOARD_FILE) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_leaderboard(entries: list[dict]):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=4)
    except Exception as e:
        print(f"[persistence] save_leaderboard error: {e}")


def add_entry(name: str, score: int, distance: int, coins: int, top_n: int = 10):
    """Insert a new result and keep only the top *top_n* entries."""
    entries = load_leaderboard()
    entries.append({"name": name, "score": score, "distance": distance, "coins": coins})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:top_n]
    save_leaderboard(entries)