import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "personality.json")

DEFAULT_PERSONALITY = {
    "tone": "calm",
    "verbosity": "low",
    "default_state": "listening",
    "interruptions": False,
    "confirmation_style": "soft",
    "reflection_style": "gentle"
}

def load_personality():
    if not os.path.exists(FILE):
        return DEFAULT_PERSONALITY.copy()

    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return DEFAULT_PERSONALITY.copy()

    if not isinstance(data, dict):
        return DEFAULT_PERSONALITY.copy()

    personality = DEFAULT_PERSONALITY.copy()
    personality.update(data)
    return personality

def save_personality(personality):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(personality, f, indent=2)
