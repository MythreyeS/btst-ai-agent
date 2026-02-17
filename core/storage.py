import os
import json
import csv
from datetime import datetime

DATA_DIR = "data"

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path: str, default):
    ensure_data_dir()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, data):
    ensure_data_dir()
    with open(path, "w") as f:
        json.dump(data, f)

def append_csv(path: str, row: dict, fieldnames: list[str]):
    ensure_data_dir()
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def today_str():
    return datetime.now().date().isoformat()
