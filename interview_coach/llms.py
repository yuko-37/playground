import gradio as gr

from state import settings, usage
from evaluator_agent import evaluator_agent
from coach_agent import coach_agent
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent, ResponseCompletedEvent


async def evaluate(model, message):
    evaluator = evaluator_agent(model)
    result = await Runner.run(evaluator, message)
    evaluation = result.final_output

    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    for response in result.raw_responses:
        u = response.usage
        input_tokens += u.input_tokens
        output_tokens += u.output_tokens
        total_tokens += u.total_tokens

    usage['ev_input'] += input_tokens
    usage['ev_output'] += output_tokens
    usage['ev_total'] += total_tokens
    
    usage_text = (f"inputs + {input_tokens}: {usage['ev_input']:,} | "
                  f"output + {output_tokens}: {usage['ev_output']:,} | "
                  f"total + {total_tokens}: {usage['ev_total']:,}")
    
    return evaluation, usage_text


def ask_openai(client, model, message):
    messages = [{"role": 'user', "content": f"{settings['ENGLISH_PROMPT']}{message}"}]
    completion = client.chat.completions.create(
        model=model,
        messages=messages
    )

    u = completion.usage
    usage['ev_input'] += u.prompt_tokens
    usage['ev_output'] += u.completion_tokens
    usage['ev_total'] += u.total_tokens
    usage_text = (f"inputs + {u.prompt_tokens}: {usage['ev_input']:,} | "
                  f"output + {u.completion_tokens}: {usage['ev_output']:,} | "
                  f"total + {u.total_tokens}: {usage['ev_total']:,}")

    return completion.choices[0].message.content, usage_text


async def stream_coach(model, message, history):
    messages = [{"role": record["role"], "content": record["content"][0]["text"]}
                for record in history]
    messages.append({"role": "user", "content": message})

    coach = coach_agent(model)
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
                    yield gr.update(), usage_text


def stream_openai(client, model, message, history):
    messages = [{"role": "system", "content": settings['COACH_PROMPT']}]

    for record in history:
        messages.append({"role": record["role"], "content": record["content"][0]["text"]})

    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True}
    )

    partial_reply = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            partial_reply += chunk.choices[0].delta.content
            history_chunk = [
                {"role": "user", "content": [{"text": message, "type": "text"}]},
                {"role": "assistant", "content": [{"text": partial_reply, "type": "text"}]},
            ]
            yield history + history_chunk, gr.update()
        elif chunk.usage is not None:
            u = chunk.usage
            usage['coach_input'] += u.prompt_tokens
            usage['coach_output'] += u.completion_tokens
            usage['coach_total'] += u.total_tokens
            usage_text = (f"inputs + {u.prompt_tokens}: {usage['coach_input']:,} | "
                          f"output + {u.completion_tokens}: {usage['coach_output']:,} | "
                          f"total + {u.total_tokens}: {usage['coach_total']:,}")
            yield gr.update(), usage_text
