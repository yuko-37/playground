import os
import json
from state import settings, settings_file, user_settings_file


def load_settings():
    file_path = user_settings_file if os.path.exists(user_settings_file) else settings_file
    with open(file_path, 'r') as f:
        settings_obj = json.load(f)
    settings.update(settings_obj)


def update_user_settings_file():
    with open(user_settings_file, 'w') as f:
        json.dump(settings, f, ensure_ascii=False)


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'interview_coach.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            return f.read()
    return ''
