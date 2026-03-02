import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

DEFAULT_MEMORY = {
    "identity": {},
    "boundaries": {}
}

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return DEFAULT_MEMORY.copy()

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except json.JSONDecodeError:
        return DEFAULT_MEMORY.copy()

    if not isinstance(memory, dict):
        return DEFAULT_MEMORY.copy()

    memory.setdefault("identity", {})
    memory.setdefault("boundaries", {})
    return memory

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def update_identity(key, value):
    memory = load_memory()
    memory.setdefault("identity", {})[key] = value
    save_memory(memory)

def get_identity():
    memory = load_memory()
    return memory.get("identity", {})

def recall_identity(key):
    memory = load_memory()
    return memory.get("identity", {}).get(key)

def get_boundaries():
    memory = load_memory()
    if isinstance(memory.get("boundaries"), dict):
        return memory["boundaries"]
    # Backward compatibility with older schema.
    return memory.get("identity", {}).get("boundaries", {})
