import os
from openai import OpenAI
from dotenv import load_dotenv
from agents import AsyncOpenAI


load_dotenv()

openai = OpenAI()
ollama = OpenAI(api_key='ollama', base_url="http://localhost:11434/v1")
ollama_async_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)


MODELS = {
    'GPT 5 nano': 'gpt-5-nano',
    'GPT 4o mini': 'gpt-4o-mini',
    'GPT 5.4 mini': 'gpt-5.4-mini',
    'GPT 5.4 nano': 'gpt-5.4-nano',
    'GPT 5.4': 'gpt-5.4',
    'llama 3.2': 'llama3.2'
}
COACH_MODELS = {**MODELS, 'no coach': 'none'}
EVAL_MODELS = {**MODELS, 'no eval': 'none'}

settings = {}
usage = {
    'coach_input': 0, 'coach_output': 0, 'coach_total': 0, 'coach_$': 0,
    'ev_input': 0, 'ev_output': 0, 'ev_total': 0, 'ev_$': 0,
}

settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
