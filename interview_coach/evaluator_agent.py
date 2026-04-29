from agents import Agent, OpenAIChatCompletionsModel
from state import settings, ollama_async_client


def evaluator_agent(model_name):
    if model_name.startswith('gpt'):
        agent = Agent(
            name='EvaluatorAgent',
            instructions=settings['ENGLISH_PROMPT'],
            model=model_name
        )
    elif model_name.startswith('llama'):
        agent = Agent(
            name='EvaluatorAgent',
            instructions=settings['ENGLISH_PROMPT'],
            model=OpenAIChatCompletionsModel(
                model=model_name,
                openai_client=ollama_async_client,
            )
        )
    else:
        raise ValueError(f'Unknown model: {model_name}')
    
    return agent
