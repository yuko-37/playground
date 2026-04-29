import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI()
ollama = OpenAI(api_key='ollama', base_url="http://localhost:11434/v1")

MODELS = {
    'GPT 5.4 mini': 'gpt-5.4-mini',
    'GPT 5 mini': 'gpt-5-mini',
    'llama 3.2': 'llama3.2',
}
EVAL_MODELS = {**MODELS, 'no eval': 'none'}

settings = {}
usage = {
    'coach_input': 0, 'coach_output': 0, 'coach_total': 0, 'coach_$': 0,
    'ev_input': 0, 'ev_output': 0, 'ev_total': 0, 'ev_$': 0,
}

settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
