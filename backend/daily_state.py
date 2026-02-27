import json
import os
from datetime import date

FILE = "daily_state.json"

def load_state():
    today = date.today().isoformat()

    if not os.path.exists(FILE):
        return reset_state(today)

    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return reset_state(today)

    if data["date"] != today:
        return reset_state(today)

    return data

def save_state(data):
    with open(FILE, "w") as f:
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