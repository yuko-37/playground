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
    evaluation_result = result.final_output_as(EvaluationResult)

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

    usage['ev_input'] += tokens['input_tokens']
    usage['ev_output'] += tokens['output_tokens']
    usage['ev_total'] += tokens['total_tokens']

    return evaluation_result, tokens


async def stream_coach(model, message, history):
    messages = [{"role": record["role"], "content": record["content"][0]["text"]}
                for record in history]
    messages.append({"role": "user", "content": message})

    coach = coach_manager(model)
    trace_id = gen_trace_id()
    with trace('Coach manager', trace_id=trace_id):
        result = Runner.run_streamed(coach, messages)

    partial_reply = ""

    async for event in result.stream_events():

        if event.type == "raw_response_event":
            if isinstance(event.data, ResponseTextDeltaEvent):
                partial_reply += event.data.delta
                history_chunk = [
                    {"role": "user", "content": [{"text": message, "type": "text"}]},
                    {"role": "assistant", "content": [{"text": partial_reply, "type": "text"}]},
                ]
                yield history + history_chunk, gr.update()

            elif isinstance(event.data, ResponseCompletedEvent) and hasattr(event.data.response, 'usage'):
                u = event.data.response.usage
                if u:
                    usage['coach_input'] += u.input_tokens
                    usage['coach_output'] += u.output_tokens
                    usage['coach_total'] += u.total_tokens
                    usage_text = (f"inputs + {u.input_tokens}: {usage['coach_input']:,} | "
                                  f"output + {u.output_tokens}: {usage['coach_output']:,} | "
                                  f"total + {u.total_tokens}: {usage['coach_total']:,}")
                    yield history, usage_text
