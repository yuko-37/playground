from agents import Agent, OpenAIChatCompletionsModel
from state import settings, ollama_async_client
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    corrected_phrase: str = Field(description="Corrected version of provided text.")
    notes: list[str] = Field(description="A list of notes.")


def evaluator_agent(model_name):
    if model_name.startswith('gpt'):
        agent = Agent(
            name='EvaluatorAgent',
            instructions=settings['ENGLISH_PROMPT'],
            model=model_name,
            output_type=EvaluationResult,
        )
    elif model_name.startswith('llama'):
        agent = Agent(
            name='EvaluatorAgent',
            instructions=settings['ENGLISH_PROMPT'],
            model=OpenAIChatCompletionsModel(
                model=model_name,
                openai_client=ollama_async_client,
            ),
            output_type=EvaluationResult,
        )
    else:
        raise ValueError(f'Unknown model: {model_name}')
    
    return agent
