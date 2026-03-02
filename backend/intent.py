import re

ACTION_VERBS = ("open", "run", "start", "launch")
TASK_HINTS = ("remind", "reminder", "schedule", "todo", "task")
REFLECT_HINTS = ("feel", "tired", "lazy", "stressed", "overwhelmed")
ASK_HINTS = ("what", "why", "how", "explain")


def _extract_action_target(text_lower):
    for verb in ACTION_VERBS:
        prefix = f"{verb} "
        if text_lower.startswith(prefix):
            return text_lower[len(prefix):].strip()
    return ""


def _extract_task_slots(text_lower):
    slots = {}

    match = re.search(r"(?:remind me to|add a task to|add task to|schedule)\s+(.+)", text_lower)
    if not match:
        match = re.search(r"task\s+(.+)", text_lower)

    if not match:
        return slots

    remainder = match.group(1).strip()

    time_marker = re.search(r"\b(at|on|by|tomorrow|today|in)\b", remainder)
    if time_marker:
        split_at = time_marker.start()
        task_text = remainder[:split_at].strip()
        time_text = remainder[split_at:].strip()
        if task_text:
            slots["task_text"] = task_text
        if time_text:
            slots["time_text"] = time_text
    else:
        if remainder:
            slots["task_text"] = remainder

    return slots


def parse_intent(text):
    text_lower = text.lower().strip()
    if not text_lower:
        return {"intent": "UNKNOWN", "slots": {}, "confidence": 0.0}

    slots = {}

    task_list_match = re.fullmatch(r"(show|list)\s+(my\s+)?tasks?", text_lower)
    if task_list_match:
        return {"intent": "TASK_LIST", "slots": slots, "confidence": 0.95}

    complete_match = re.search(
        r"(?:mark\s+task|complete\s+task|task)\s+(\d+)\s*(?:as\s+)?(?:done|complete|completed)?",
        text_lower,
    )
    if complete_match and any(word in text_lower for word in ("done", "complete", "completed", "mark")):
        slots["task_index"] = int(complete_match.group(1))
        return {"intent": "TASK_COMPLETE", "slots": slots, "confidence": 0.95}

    delete_match = re.search(r"(?:delete|remove)\s+(?:task\s+)?(\d+)", text_lower)
    if delete_match:
        slots["task_index"] = int(delete_match.group(1))
        return {"intent": "TASK_DELETE", "slots": slots, "confidence": 0.95}

    reschedule_match = re.search(
        r"(?:reschedule|move|change)\s+task\s+(\d+)\s+(?:to|at|for)\s+(.+)",
        text_lower,
    )
    if reschedule_match:
        slots["task_index"] = int(reschedule_match.group(1))
        slots["time_text"] = reschedule_match.group(2).strip()
        return {"intent": "TASK_RESCHEDULE", "slots": slots, "confidence": 0.9}

    followup_reschedule_match = re.fullmatch(
        r"(?:actually\s+)?(?:make it|set it|change it|change it to|move it|move it to|reschedule it|reschedule it to)\s+(.+)",
        text_lower,
    )
    if followup_reschedule_match:
        slots["time_text"] = followup_reschedule_match.group(1).strip()
        return {"intent": "TASK_RESCHEDULE_FOLLOWUP", "slots": slots, "confidence": 0.9}

    short_followup_match = re.fullmatch(r"(?:actually\s+)?at\s+(.+)", text_lower)
    if short_followup_match:
        slots["time_text"] = f"at {short_followup_match.group(1).strip()}"
        return {"intent": "TASK_RESCHEDULE_FOLLOWUP", "slots": slots, "confidence": 0.8}

    action_target = _extract_action_target(text_lower)
    if action_target:
        slots["action_target"] = action_target
        return {"intent": "ACTION", "slots": slots, "confidence": 0.95}

    if any(hint in text_lower for hint in TASK_HINTS):
        slots.update(_extract_task_slots(text_lower))
        confidence = 0.85 if slots.get("task_text") else 0.6
        return {"intent": "TASK", "slots": slots, "confidence": confidence}

    if any(hint in text_lower for hint in REFLECT_HINTS):
        return {"intent": "REFLECT", "slots": slots, "confidence": 0.7}

    if text_lower.endswith("?") or any(text_lower.startswith(f"{hint} ") for hint in ASK_HINTS):
        return {"intent": "ASK", "slots": slots, "confidence": 0.65}

    if any(verb in text_lower for verb in ACTION_VERBS):
        return {"intent": "ACTION", "slots": slots, "confidence": 0.5}

    return {"intent": "UNKNOWN", "slots": {}, "confidence": 0.2}


def detect_intent(text):
    return parse_intent(text)["intent"]
