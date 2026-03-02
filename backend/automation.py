import os
import re
import shutil
import subprocess
import webbrowser

SAFE_APP_NAME = re.compile(r"^[a-zA-Z0-9_. -]{1,64}$")


def open_app(app_name):
    app_name = app_name.strip()
    if not SAFE_APP_NAME.fullmatch(app_name):
        return "I can't open that app name safely."

    candidates = [app_name]
    if "." not in app_name:
        candidates.append(f"{app_name}.exe")

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            try:
                subprocess.Popen([resolved])
                return f"Opening {app_name}"
            except OSError:
                continue

    try:
        os.startfile(app_name)
        return f"Opening {app_name}"
    except OSError:
        return f"I couldn't open {app_name}"


def open_folder(path):
    if os.path.exists(path):
        os.startfile(path)
        return "Folder opened."
    return "I couldn't find that folder."


def open_website(url):
    webbrowser.open(url)
    return f"Opening {url}"
