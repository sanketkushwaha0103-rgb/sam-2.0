import os
import webbrowser
import subprocess

def open_app(app_name):
    try:
        subprocess.Popen(f'start "" "{app_name}"', shell=True)
        return f"Opening {app_name}"
    except:
        return f"I couldn’t open {app_name}"

def open_folder(path):
    if os.path.exists(path):
        os.startfile(path)
        return "Folder opened."
    return "I couldn’t find that folder."

def open_website(url):
    webbrowser.open(url)
    return f"Opening {url}"