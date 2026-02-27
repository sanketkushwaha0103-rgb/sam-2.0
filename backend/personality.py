import json
import os

FILE = "personality.json"

def load_personality():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)