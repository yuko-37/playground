import gradio as gr

from state import usage
from myagents.evaluator_agent import evaluator_agent, EvaluationResult
# from myagents.coach_agent import coach_agent
from myagents.coach_manager import coach_manager
from agents import Runner, trace, gen_trace_id
from openai.types.responses import ResponseTextDeltaEvent, ResponseCompletedEvent


async def evaluate(model, message):
    evaluator = evaluator_agent(model)
    result = await Runner.run(evaluator, message)
    evaluation = result.final_output_as(EvaluationResult)
    tokens = _parse_evaluation_result(result)
    _update_global_usage(tokens, 'ev')
    return evaluation, tokens


def _parse_evaluation_result(result):
    tokens = {
        'input_tokens':0,
        'output_tokens': 0,
        'total_tokens': 0,
    }

    for response in result.raw_responses:
        u = response.usage
        tokens['input_tokens'] += u.input_tokens
        tokens['output_tokens'] += u.output_tokens
        tokens['total_tokens'] += u.total_tokens

    return tokens


def _update_global_usage(tokens, prefix):
    usage[f'{prefix}_input'] += tokens['input_tokens']
    usage[f'{prefix}_output'] += tokens['output_tokens']
    usage[f'{prefix}_total'] += tokens['total_tokens']


async def stream_coach(model, message, history):
    messages = [{"role": record["role"], "content": record["content"][0]["text"]}
                for record in history]
    messages.append({"role": "user", "content": message})
    history.append({"role": "user", "content": [{"text": message, "type": "text"}]})

    coach = coach_manager(model)
    trace_id = gen_trace_id()
    with trace('Coach manager', trace_id=trace_id):
        result = Runner.run_streamed(coach, messages)
    async for hist, tokens in _parse_coach_result(result, history):
        yield hist, tokens


async def _parse_coach_result(result, history):
    partial_reply = ""
    async for event in result.stream_events():

        tokens = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
        }

        if event.type == "raw_response_event":
            if isinstance(event.data, ResponseTextDeltaEvent):
                partial_reply += event.data.delta
                history_chunk = [{"role": "assistant", "content": [{"text": partial_reply, "type": "text"}]}]
                yield history + history_chunk, tokens

            elif isinstance(event.data, ResponseCompletedEvent) and hasattr(event.data.response, 'usage'):
                u = event.data.response.usage

                if u:
                    tokens['input_tokens'] += u.input_tokens
                    tokens['output_tokens'] += u.output_tokens
                    tokens['total_tokens'] += u.total_tokens

                    _update_global_usage(tokens, 'coach')

                    yield gr.update(), tokens