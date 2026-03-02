# context.py

context = {
    "last_intent": None,
    "pending_task": None,
    "pending_action": None,
    "last_task_index": None,
    "conversation_history": []
}

def update_context(intent, text):
    context["last_intent"] = intent

    if intent == "TASK":
        context["pending_task"] = text

def add_turn(role, text, max_turns=10):
    context["conversation_history"].append({
        "role": role,
        "text": text
    })
    if len(context["conversation_history"]) > max_turns:
        context["conversation_history"] = context["conversation_history"][-max_turns:]

def get_history():
    return context["conversation_history"]

def clear_pending_task():
    context["pending_task"] = None

def set_pending_action(action):
    context["pending_action"] = action

def clear_pending_action():
    context["pending_action"] = None

def set_last_task_index(index):
    context["last_task_index"] = index

def get_last_task_index():
    return context.get("last_task_index")

def clear_last_task_index():
    context["last_task_index"] = None

def get_context():
    return context
    
