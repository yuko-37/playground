import os
import json
from state import settings, settings_file


def set_sys_prompts():
    with open(settings_file, 'r') as f:
        settings_obj = json.load(f)

    settings['COACH_PROMPT'] = settings_obj.get('COACH_PROMPT',
                                                 settings_obj.get('DEFAULT_COACH_PROMPT'))
    settings['ENGLISH_PROMPT'] = settings_obj.get('ENGLISH_PROMPT',
                                                   settings_obj.get('DEFAULT_ENGLISH_PROMPT'))


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'interview_coach.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            return f.read()
    return ''
