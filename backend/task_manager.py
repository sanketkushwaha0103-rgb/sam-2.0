import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_FILE = os.path.join(BASE_DIR, "tasks.json")

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return {"tasks": []}
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("tasks"), list):
                return data
    except json.JSONDecodeError:
        pass
    return {"tasks": []}


def save_tasks(data):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _refresh_statuses(data):
    now = datetime.now()
    changed = False

    for task in data.get("tasks", []):
        task.setdefault("status", "pending")
        task.setdefault("when", "")
        task.setdefault("created_at", now.isoformat())

        due_at = task.get("due_at")
        if task["status"] == "pending" and due_at:
            try:
                due_dt = datetime.fromisoformat(due_at)
                if now - due_dt >= timedelta(hours=1):
                    task["status"] = "missed"
                    changed = True
            except ValueError:
                continue

    return changed


def add_task(what, when, due_at=None):
    data = load_tasks()
    task = {
        "what": what,
        "when": when,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    if due_at:
        task["due_at"] = due_at
    data["tasks"].append(task)
    save_tasks(data)
    return len(data["tasks"])


def complete_task(index):
    data = load_tasks()
    tasks = data.get("tasks", [])
    if index < 1 or index > len(tasks):
        return None

    task = tasks[index - 1]
    task["status"] = "done"
    task["completed_at"] = datetime.now().isoformat()
    save_tasks(data)
    return task


def delete_task(index):
    data = load_tasks()
    tasks = data.get("tasks", [])
    if index < 1 or index > len(tasks):
        return None

    removed = tasks.pop(index - 1)
    save_tasks(data)
    return removed


def reschedule_task(index, when, due_at=None):
    data = load_tasks()
    tasks = data.get("tasks", [])
    if index < 1 or index > len(tasks):
        return None

    task = tasks[index - 1]
    task["when"] = when
    task["status"] = "pending"
    task.pop("completed_at", None)
    task.pop("notified_at", None)
    if due_at:
        task["due_at"] = due_at
    else:
        task.pop("due_at", None)
    save_tasks(data)
    return task


def get_due_task_notifications(now=None):
    data = load_tasks()
    tasks = data.get("tasks", [])
    now = now or datetime.now()
    due_tasks = []

    for index, task in enumerate(tasks, start=1):
        if task.get("status") != "pending":
            continue
        due_at = task.get("due_at")
        if not due_at or task.get("notified_at"):
            continue
        try:
            due_dt = datetime.fromisoformat(due_at)
        except ValueError:
            continue
        if due_dt <= now:
            due_tasks.append((index, task))

    return due_tasks


def mark_task_notified(index, notified_at=None):
    data = load_tasks()
    tasks = data.get("tasks", [])
    if index < 1 or index > len(tasks):
        return None

    task = tasks[index - 1]
    task["notified_at"] = (notified_at or datetime.now()).isoformat()
    save_tasks(data)
    return task


def list_tasks():
    data = load_tasks()
    if _refresh_statuses(data):
        save_tasks(data)
    return data["tasks"]
