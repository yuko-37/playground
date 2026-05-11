import os
import json
from state import settings, settings_file


def load_settings():
    with open(settings_file, 'r') as f:
        settings_obj = json.load(f)
    settings.update(settings_obj)


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'interview_coach.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            return f.read()
    return ''
