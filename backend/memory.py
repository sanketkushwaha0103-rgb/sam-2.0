import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_identity(key, value):
    memory = load_memory()
    memory["identity"][key] = value
    save_memory(memory)

def get_identity():
    memory = load_memory()
    return memory.get("identity", {})

def recall_identity(key):
    memory = load_memory()
    return memory.get("identity", {}).get(key)

def get_boundaries():
    memory = load_memory()
    return memory.get("identity", {}).get("boundaries", {})