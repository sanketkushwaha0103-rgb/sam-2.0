import threading

import pyttsx3
import speech_recognition as sr

from automation import open_app, open_folder, open_website
from brain import answer_from_brain, seed_identity, teach_knowledge
from context import (
    add_turn,
    clear_last_task_index,
    clear_pending_action,
    clear_pending_task,
    get_context,
    get_history,
    get_last_task_index,
    set_last_task_index,
    set_pending_action,
    update_context,
)
from daily_state import load_state, save_state
from intent import parse_intent
from memory import get_boundaries, get_identity, recall_identity, update_identity
from personality import load_personality, save_personality
from reflection import generate_reflection
from shortcuts import APP_SHORTCUTS, FOLDER_SHORTCUTS, WEBSITE_SHORTCUTS
from task_manager import (
    add_task,
    complete_task,
    delete_task,
    get_due_task_notifications,
    list_tasks,
    mark_task_notified,
    reschedule_task,
)
from time_parser import format_when, parse_time_text
from trust_manager import is_trusted, record_confirmation


# ------------------ VOICE ENGINE ------------------
engine = pyttsx3.init()
SPEAK_LOCK = threading.Lock()


def speak(text):
    with SPEAK_LOCK:
        engine.say(text)
        engine.runAndWait()


def is_confirmation(text):
    return text.strip().lower() in {
        "yes",
        "yeah",
        "yep",
        "ok",
        "okay",
        "do it",
        "go ahead",
        "haan",
        "kar de",
    }


def extract_action_target(text_lower):
    for trigger in ("open", "run", "start", "launch"):
        prefix = f"{trigger} "
        if text_lower.startswith(prefix):
            return text_lower[len(prefix) :].strip()
    return text_lower.strip()


def check_due_reminders():
    due_tasks = get_due_task_notifications()
    for index, task in due_tasks:
        reminder_text = f"Reminder: {task['what']}."
        print("SAM (reminder):", reminder_text)
        speak(reminder_text)
        mark_task_notified(index)


def reminder_watcher(stop_event, interval_seconds=20):
    while not stop_event.is_set():
        check_due_reminders()
        stop_event.wait(interval_seconds)


# ------------------ CORE BRAIN ------------------
def sam_reply(text):
    add_turn("user", text)

    def respond(message):
        add_turn("assistant", message)
        return message

    parsed = parse_intent(text)
    intent = parsed["intent"]
    slots = parsed["slots"]
    confidence = parsed["confidence"]
    text_lower = text.lower()
    get_boundaries()  # reserved for future response policy controls
    ctx = get_context()
    personality = load_personality()
    daily = load_state()
    seed_identity(get_identity())

    if text_lower.startswith("learn:"):
        fact = text.split(":", 1)[1].strip()
        if not fact:
            return respond("Tell me the fact after 'learn:'.")
        added = teach_knowledge(fact, source="manual_learn")
        if added:
            return respond("Learned. I will use this in future answers.")
        return respond("I already know that.")

    if text_lower.startswith("remember that "):
        fact = text[13:].strip()
        if not fact:
            return respond("Tell me what to remember.")
        added = teach_knowledge(fact, source="manual_remember")
        if added:
            return respond("Saved in my brain.")
        return respond("I already have that in my brain.")

    # ------------------ AUTOMATION CONFIRMATION ------------------
    if is_confirmation(text_lower):
        pending_action = ctx.get("pending_action")
        if pending_action:
            record_confirmation(pending_action)
            daily["actions_used"] += 1
            save_state(daily)

            clear_pending_action()
            return respond(open_app(pending_action))
        return respond("There's nothing pending to do.")

    if text_lower in ["be quiet", "stay silent", "silent mode"]:
        personality["default_state"] = "silent"
        save_personality(personality)
        return respond("Alright. I'll stay quiet.")

    if text_lower in ["talk again", "you can speak", "resume"]:
        personality["default_state"] = "listening"
        save_personality(personality)
        return respond("I'm back.")

    # ------------------ TASK CONTINUATION ------------------
    if ctx["last_intent"] == "TASK" and intent == "UNKNOWN":
        task_text = ctx["pending_task"]
        due_dt, parse_error = parse_time_text(text)
        if parse_error:
            return respond(parse_error)

        task_index = add_task(task_text, format_when(due_dt), due_dt.isoformat())
        set_last_task_index(task_index)

        daily["tasks_created"] += 1
        save_state(daily)

        clear_pending_task()
        return respond(f"Task saved: {task_text} at {format_when(due_dt)}")

    # ------------------ IDENTITY STORAGE ------------------
    if "my name is" in text_lower:
        name = text.split("is")[-1].strip()
        update_identity("name", name)
        return respond(f"Got it. I'll remember your name as {name}.")

    if "my goal is" in text_lower:
        update_identity("goal", text.split("is")[-1].strip())
        return respond("I've saved your goal.")

    if "i usually" in text_lower:
        update_identity("habit", text)
        return respond("I'll keep that habit in mind.")

    if "i prefer" in text_lower:
        update_identity("preference", text)
        return respond("Noted. I'll respect that preference.")

    if "i struggle with" in text_lower:
        update_identity("thinking_style", text)
        return respond("Thank you for trusting me with that.")

    # ------------------ MEMORY RECALL ------------------
    if "what is my name" in text_lower:
        name = recall_identity("name")
        if name:
            return respond(f"Your name is {name}.")
        return respond("You haven't told me your name yet.")

    if "what is my goal" in text_lower:
        goal = recall_identity("goal")
        if goal:
            return respond(goal)
        return respond("You haven't shared a goal yet.")

    if "do you know my habit" in text_lower:
        habit = recall_identity("habit")
        if habit:
            return respond(habit)
        return respond("You haven't shared a habit yet.")

    # ------------------ TASK COMMANDS ------------------
    if intent == "TASK_COMPLETE":
        task_index = slots["task_index"]
        task = complete_task(task_index)
        if not task:
            return respond("I couldn't find that task number.")
        set_last_task_index(task_index)
        return respond(f"Marked done: {task['what']}.")

    if intent == "TASK_DELETE":
        task = delete_task(slots["task_index"])
        if not task:
            return respond("I couldn't find that task number.")
        clear_last_task_index()
        return respond(f"Deleted task: {task['what']}.")

    if intent == "TASK_RESCHEDULE":
        due_dt, parse_error = parse_time_text(slots["time_text"])
        if parse_error:
            return respond(parse_error)
        task_index = slots["task_index"]
        task = reschedule_task(task_index, format_when(due_dt), due_dt.isoformat())
        if not task:
            return respond("I couldn't find that task number.")
        set_last_task_index(task_index)
        return respond(f"Rescheduled task {task_index} to {format_when(due_dt)}.")

    if intent == "TASK_RESCHEDULE_FOLLOWUP":
        task_index = get_last_task_index()
        if not task_index:
            return respond("Tell me which task number to reschedule, like: reschedule task 2 to 10 pm.")

        due_dt, parse_error = parse_time_text(slots["time_text"])
        if parse_error:
            return respond(parse_error)

        task = reschedule_task(task_index, format_when(due_dt), due_dt.isoformat())
        if not task:
            return respond("I couldn't find your recent task anymore. Say: show my tasks.")

        return respond(f"Updated task {task_index} to {format_when(due_dt)}.")

    # ------------------ NEW TASK REQUEST ------------------
    if intent == "TASK":
        if confidence < 0.5:
            return respond("I am not fully sure. Tell me like: remind me to <task> at <time>.")

        task_text = slots.get("task_text")
        time_text = slots.get("time_text")

        if task_text and time_text:
            due_dt, parse_error = parse_time_text(time_text)
            if parse_error:
                return respond(parse_error)

            task_index = add_task(task_text, format_when(due_dt), due_dt.isoformat())
            set_last_task_index(task_index)
            daily["tasks_created"] += 1
            save_state(daily)
            return respond(f"Task saved: {task_text} at {format_when(due_dt)}")

        if task_text:
            update_context("TASK", task_text)
            return respond("When should I remind you?")

        update_context("TASK", text)
        return respond("When should I remind you?")

    # ------------------ SHOW TASKS ------------------
    if intent == "TASK_LIST" or "show my tasks" in text_lower:
        tasks = list_tasks()
        if not tasks:
            return respond("You don't have any tasks right now.")

        reply = "Here are your tasks:\n"
        for i, task in enumerate(tasks, start=1):
            reply += f"{i}. {task['what']} at {task['when']} ({task['status']})\n"
        return respond(reply)

    # ------------------ REFLECTION ------------------
    if intent == "REFLECT" or "reflect" in text_lower or "how am i doing" in text_lower:
        return respond(generate_reflection())

    # ------------------ AUTOMATION (NEW REQUEST) ------------------
    if intent == "ACTION":
        if confidence < 0.5:
            return respond("I am not sure what to open. Say: open <app name>.")

        for key, path in FOLDER_SHORTCUTS.items():
            if key in text_lower:
                return respond(open_folder(path))

        for key, url in WEBSITE_SHORTCUTS.items():
            if key in text_lower:
                return respond(open_website(url))

        app_name = slots.get("action_target") or extract_action_target(text_lower)
        app_name = APP_SHORTCUTS.get(app_name, app_name)

        if app_name:
            if confidence < 0.75:
                return respond(f"I think you want to open {app_name}. Please say: open {app_name}.")

            if is_trusted(app_name):
                daily["actions_used"] += 1
                save_state(daily)
                return respond(open_app(app_name))

            set_pending_action(app_name)
            return respond(f"Do you want me to open {app_name}?")

    if intent in {"ASK", "UNKNOWN"}:
        brain_answer = answer_from_brain(text, history=get_history())
        if brain_answer:
            return respond(brain_answer)

    return respond("I'm here. Tell me what you want to do next.")


# ------------------ VOICE INPUT ------------------
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You (voice):", text)
        return text
    except Exception:
        return ""


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    print("\nSAM 2.0 is awake.\n")
    print("Modes:")
    print("  text  -> keyboard input")
    print("  voice -> voice-only mode")
    print("  exit  -> quit\n")

    start_mode = input("Choose start mode (text / voice): ").lower()
    stop_event = threading.Event()
    watcher = threading.Thread(target=reminder_watcher, args=(stop_event,), daemon=True)

    # ---------------- TEXT MODE ----------------
    if start_mode == "text":
        watcher.start()
        print("Text mode enabled. Type 'exit' to quit.\n")
        while True:
            user_input = input("You: ")

            if not user_input:
                continue

            if user_input.lower() == "exit":
                speak("Going silent.")
                stop_event.set()
                watcher.join(timeout=1)
                break

            response = sam_reply(user_input)
            print("SAM:", response)
            speak(response)

    # ---------------- VOICE MODE ----------------
    elif start_mode == "voice":
        watcher.start()
        print("Voice mode enabled. Say 'stop listening' or 'exit' to quit.\n")
        speak("Voice mode enabled. I am listening.")

        while True:
            user_input = listen()

            if not user_input:
                continue

            print("You:", user_input)

            lower = user_input.lower()

            if "stop listening" in lower or "exit" in lower:
                speak("Going silent.")
                stop_event.set()
                watcher.join(timeout=1)
                break

            response = sam_reply(user_input)
            print("SAM:", response)
            speak(response)

    else:
        print("Invalid mode. Exiting.")
