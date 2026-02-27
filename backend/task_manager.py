import json
import os
from datetime import datetime

TASK_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return {"tasks": []}
    with open(TASK_FILE, "r") as f:
        return json.load(f)

def save_tasks(data):
    with open(TASK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_task(what, when):
    data = load_tasks()
    task = {
        "what": what,
        "when": when,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    data["tasks"].append(task)
    save_tasks(data)

def list_tasks():
    data = load_tasks()
    return data["tasks"]