import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "daily_state.json")

def load_state():
    today = date.today().isoformat()

    if not os.path.exists(FILE):
        return reset_state(today)

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return reset_state(today)

    if data.get("date") != today:
        return reset_state(today)

    return data

def save_state(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def reset_state(today):
    data = {
        "date": today,
        "tasks_created": 0,
        "actions_used": 0,
        "reflection_shown": False
    }
    save_state(data)
    return data
