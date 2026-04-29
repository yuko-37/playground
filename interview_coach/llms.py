import gradio as gr
from state import settings, usage


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
