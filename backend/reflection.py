from datetime import datetime
from task_manager import list_tasks

def generate_reflection():
    tasks = list_tasks()

    if not tasks:
        return "You’ve had a quiet period. That’s okay."

    pending = [t for t in tasks if t["status"] == "pending"]

    if len(pending) == 0:
        return "You’ve been completing what you start. That’s good to see."

    if len(pending) <= 2:
        return "A few things are still pending. No rush."

    return "You’ve got several pending tasks. Want to talk about what’s getting in the way?"