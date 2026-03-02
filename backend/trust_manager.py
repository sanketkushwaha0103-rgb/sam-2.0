import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRUST_FILE = os.path.join(BASE_DIR, "trust.json")
THRESHOLD = 3  # confirmations needed

def load_trust():
    if not os.path.exists(TRUST_FILE):
        return {"trusted_apps": {}}
    try:
        with open(TRUST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("trusted_apps", {})
                return data
    except json.JSONDecodeError:
        pass
    return {"trusted_apps": {}}

def save_trust(data):
    with open(TRUST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record_confirmation(app):
    app = app.strip().lower()
    data = load_trust()
    apps = data.setdefault("trusted_apps", {})

    apps[app] = apps.get(app, 0) + 1
    save_trust(data)

def is_trusted(app):
    app = app.strip().lower()
    data = load_trust()
    return data.get("trusted_apps", {}).get(app, 0) >= THRESHOLD
