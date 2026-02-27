import speech_recognition as sr
import pyttsx3

from intent import detect_intent
from context import (
    update_context,
    get_context,
    clear_pending_task,
    set_pending_action,
    clear_pending_action
)
from memory import (
    update_identity,
    recall_identity,
    get_boundaries
)
from task_manager import add_task, list_tasks
from reflection import generate_reflection
from automation import open_app, open_folder, open_website
from shortcuts import FOLDER_SHORTCUTS, WEBSITE_SHORTCUTS
from trust_manager import record_confirmation, is_trusted
from personality import load_personality
from daily_state import load_state, save_state


# ------------------ VOICE ENGINE ------------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()


# ------------------ CORE BRAIN ------------------
def sam_reply(text):
    intent = detect_intent(text)
    text_lower = text.lower()
    boundaries = get_boundaries()
    ctx = get_context()
    personality = load_personality()
    daily = load_state()

    # ------------------------------------------------
    # 🔁 AUTOMATION CONFIRMATION (MUST COME FIRST)
    # ------------------------------------------------
    CONFIRM_WORDS = ["yes", "yeah", "yep", "ok", "okay", "do it", "go ahead", "haan", "kar de"]

    if any(word in text_lower for word in CONFIRM_WORDS):
        pending_action = ctx.get("pending_action")
        if pending_action:
            daily["actions_used"] += 1
            save_state(daily)

            clear_pending_action()
            return open_app(pending_action)
        else:
            return "There’s nothing pending to do."
    if text_lower in ["be quiet", "stay silent", "silent mode"]:
        personality["default_state"] = "silent"
        return "Alright. I’ll stay quiet."

    if text_lower in ["talk again", "you can speak", "resume"]:
        personality["default_state"] = "listening"
        return "I’m back."
    # ---- TASK CONTINUATION ----
    if ctx["last_intent"] == "TASK" and intent == "UNKNOWN":
        task_text = ctx["pending_task"]
        add_task(task_text, text)

        daily["tasks_created"] += 1
        save_state(daily)

        clear_pending_task()
        return f"Task saved: {task_text} at {text}"

    # ------------------------------------------------
    # 🧾 IDENTITY STORAGE
    # ------------------------------------------------
    if "my name is" in text_lower:
        name = text.split("is")[-1].strip()
        update_identity("name", name)
        return f"Got it. I’ll remember your name as {name}."

    if "my goal is" in text_lower:
        update_identity("goal", text.split("is")[-1].strip())
        return "I’ve saved your goal."

    if "i usually" in text_lower:
        update_identity("habit", text)
        return "I’ll keep that habit in mind."

    if "i prefer" in text_lower:
        update_identity("preference", text)
        return "Noted. I’ll respect that preference."

    if "i struggle with" in text_lower:
        update_identity("thinking_style", text)
        return "Thank you for trusting me with that."

    # ------------------------------------------------
    # 🔍 MEMORY RECALL
    # ------------------------------------------------
    if "what is my name" in text_lower:
        name = recall_identity("name")
        return f"Your name is {name}." if name else "You haven’t told me your name yet."

    if "what is my goal" in text_lower:
        goal = recall_identity("goal")
        return goal if goal else "You haven’t shared a goal yet."

    if "do you know my habit" in text_lower:
        habit = recall_identity("habit")
        return habit if habit else "You haven’t shared a habit yet."

    # ------------------------------------------------
    # 🆕 NEW TASK REQUEST
    # ------------------------------------------------
    if intent == "TASK":
        update_context("TASK", text)
        return "When should I remind you?"

    # ------------------------------------------------
    # 📋 SHOW TASKS
    # ------------------------------------------------
    if "show my tasks" in text_lower:
        tasks = list_tasks()
        if not tasks:
            return "You don’t have any tasks right now."

        reply = "Here are your tasks:\n"
        for i, task in enumerate(tasks, start=1):
            reply += f"{i}. {task['what']} at {task['when']} ({task['status']})\n"
        return reply

    # ------------------------------------------------
    # 🌿 REFLECTION
    # ------------------------------------------------
    if "reflect" in text_lower or "how am i doing" in text_lower:
        return generate_reflection()

    # ------------------------------------------------
    # ⚙️ AUTOMATION (NEW REQUEST)
    # ------------------------------------------------
    if intent == "ACTION":

        for key in FOLDER_SHORTCUTS:
            if key in text_lower:
                return open_folder(FOLDER_SHORTCUTS[key])

        for key in WEBSITE_SHORTCUTS:
            if key in text_lower:
                return open_website(WEBSITE_SHORTCUTS[key])

        app_name = text_lower.replace("open", "").strip()
        if app_name:
            if is_trusted(app_name):
                return open_app(app_name)
            set_pending_action(app_name)
            return f"Do you want me to open {app_name}?"

    return "I’m here. Tell me what you want to do next."


# ------------------ VOICE INPUT ------------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("You (voice):", text)
        return text
    except:
        return ""


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    print("\nSAM 2.0 is awake.\n")
    print("Modes:")
    print("  text  → keyboard input")
    print("  voice → voice-only mode")
    print("  exit  → quit\n")

    start_mode = input("Choose start mode (text / voice): ").lower()

    # ---------------- TEXT MODE ----------------
    if start_mode == "text":
        print("Text mode enabled. Type 'exit' to quit.\n")
        while True:
            user_input = input("You: ")

            if not user_input:
                continue

            if user_input.lower() == "exit":
                speak("Going silent.")
                break

            response = sam_reply(user_input)
            print("SAM:", response)
            speak(response)

    # ---------------- VOICE MODE ----------------
    elif start_mode == "voice":
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
                break

            response = sam_reply(user_input)
            print("SAM:", response)
            speak(response)

    else:
        print("Invalid mode. Exiting.")