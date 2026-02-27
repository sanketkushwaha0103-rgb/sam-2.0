import json
import os

TRUST_FILE = "trust.json"
THRESHOLD = 3  # confirmations needed

def load_trust():
    if not os.path.exists(TRUST_FILE):
        return {"trusted_apps": {}}
    with open(TRUST_FILE, "r") as f:
        return json.load(f)

def save_trust(data):
    with open(TRUST_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_confirmation(app):
    data = load_trust()
    apps = data["trusted_apps"]

    apps[app] = apps.get(app, 0) + 1
    save_trust(data)

def is_trusted(app):
    data = load_trust()
    return data["trusted_apps"].get(app, 0) >= THRESHOLD