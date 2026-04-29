import json
import gradio as gr
import mlx_whisper
import llms

from state import MODELS, EVAL_MODELS, settings, usage, settings_file


async def msg_submit(message, history, model='GPT 5 mini'):
    if message:
        model_name = MODELS[model]
        async for hist, usage_text in llms.stream_coach(model_name, message, history):
            yield hist, usage_text
    else:
        yield history, gr.update()


def msg_change(message):
    return gr.update(interactive=bool(message.strip()))


def transcribe(msg, audio):
    text = msg
    if audio:
        try:
            result = mlx_whisper.transcribe(
                audio,
                path_or_hf_repo="mlx-community/whisper-small-mlx"
            )
            text += result["text"]
        except Exception as e:
            gr.Warning(f"Transcription failed: {e}")
    return text, None


def sysprompt_update(prompt, key='COACH_PROMPT'):
    if key in settings:
        settings[key] = prompt
        with open(settings_file, 'r') as f:
            settings_obj = json.load(f)

        settings_obj[key] = prompt
        with open(settings_file, 'w') as f:
            json.dump(settings_obj, f, ensure_ascii=False)

        if key == 'COACH_PROMPT':
            gr.Info("Coach system prompt updated.")
        elif key == 'ENGLISH_PROMPT':
            gr.Info("English evaluation system prompt updated.")
    else:
        gr.Warning(f'Failed to update: unknown setting {key}.')
        return gr.update()

    return prompt


async def evaluate(message, history, model):
    if not message or model == 'no eval':
        print('Skip evaluation...')
        return "", history, gr.update()
        
    try:
        model_name = EVAL_MODELS[model]
        model_resp, usage_text = await llms.evaluate(model_name, message)
    except Exception as e:
        print(e)
        gr.Error('Failed to do evaluation.')
        return "", history, gr.update()

    evaluation = f"Message: `{message}`\n{model_resp}"
    new_text = f"{evaluation}\n---\n{history}" if history else evaluation

    return "", new_text, usage_text


def format_usage(key='coach'):
    def get(field):
        return usage[f"{key}_{field}"]

    return (
        f"input {get('input'):,} | "
        f"output {get('output'):,} | "
        f"total {get('total'):,}"
    )


def render_usages():
    return format_usage(), format_usage(key='ev')


def render_sys_prompts():
    return settings['COACH_PROMPT'], settings['ENGLISH_PROMPT']


def clear_coach_usage():
    usage["coach_input"] = 0
    usage["coach_output"] = 0
    usage["coach_total"] = 0
    usage["coach_$"] = 0
    return format_usage()


def clear_ev_usage():
    usage["ev_input"] = 0
    usage["ev_output"] = 0
    usage["ev_total"] = 0
    usage["ev_$"] = 0
    return format_usage(key='ev')
