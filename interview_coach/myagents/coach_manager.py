from agents import Agent, OpenAIChatCompletionsModel
from state import settings, ollama_async_client
from myagents.search_manager_agent import search_manager_agent


COACH_MANAGER_PROMPT = """
Always give short answers and whenever asked please ask one question at a time.
Do not guess or predict beyond your knowledge cutoff. 
If asked about anything after your cutoff or outside your verified knowledge, 
ask the user whether to proceed with a search tool.
Only delegate to search manager agent if the user explicitly agrees.
"""


def coach_manager(model_name):
    if model_name.startswith('gpt'):
        agent = Agent(
            name='CoachAgent',
            instructions=f"{settings['COACH_PROMPT']}\n{COACH_MANAGER_PROMPT}",
            model=model_name,
            handoffs=[search_manager_agent],
        )
    elif model_name.startswith('llama'):
        agent = Agent(
            name='CoachAgent',
            instructions=settings['COACH_PROMPT'],
            model=OpenAIChatCompletionsModel(
                model=model_name,
                openai_client=ollama_async_client,
            ),
        )
    else:
        raise ValueError(f'Unknown model: {model_name}')

    return agent