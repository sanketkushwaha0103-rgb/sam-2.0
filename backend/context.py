# context.py

context = {
    "last_intent": None,
    "pending_task": None,
    "pending_action": None
}

def update_context(intent, text):
    context["last_intent"] = intent

    if intent == "TASK":
        context["pending_task"] = text

def clear_pending_task():
    context["pending_task"] = None

def set_pending_action(action):
    context["pending_action"] = action

def clear_pending_action():
    context["pending_action"] = None

def get_context():
    return context
    