import json
import os

SESSIONS_FILE = "sessions.json"

def save_session(title, id_suffix):
    if not os.path.exists(SESSIONS_FILE):
        sessions = []
    else:
        with open(SESSIONS_FILE, "r") as f:
            try:
                sessions = json.load(f)
            except json.JSONDecodeError:
                sessions = []

    sessions.append({
        "title": title,
        "id_suffix": id_suffix
    })

    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=4)
