# intent.py

def detect_intent(text):
    text = text.lower()

    if any(word in text for word in ["what", "why", "how", "explain"]):
        return "ASK"

    if any(word in text for word in ["remind", "schedule", "todo", "task"]):
        return "TASK"

    if any(word in text for word in ["open", "run", "start", "launch"]):
        return "ACTION"

    if any(word in text for word in ["feel", "tired", "lazy", "stressed"]):
        return "REFLECT"

    return "UNKNOWN"