import json
import gradio as gr
import mlx_whisper
import llms

from state import COACH_MODELS, EVAL_MODELS, settings, usage, settings_file
from ui_formatter import format_usage, format_usage_with_tokens, format_evaluation


async def msg_submit(message, history, model='GPT 5 mini'):
    if model == 'no coach' or not message.strip():
        yield history, gr.update()
    else:
        model_name = COACH_MODELS[model]
        async for hist, usage_text in llms.stream_coach(model_name, message, history):
            yield hist, usage_text


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
    if model == 'no eval' or not message.strip():
        print('Skip evaluation...')
        return "", history, gr.update()
        
    try:
        model_name = EVAL_MODELS[model]
        evaluation_result, tokens = await llms.evaluate(model_name, message)
    except Exception as e:
        print(e)
        gr.Error('Failed to do evaluation.')
        return "", history, gr.update()

    evaluation_text = format_evaluation(message, history, evaluation_result)
    usage_text = format_usage_with_tokens(tokens)

    return "", evaluation_text, usage_text


def render_usages():
    return format_usage(), format_usage(key='ev')


def render_settings():
    return (settings['COACH_PROMPT'], settings['ENGLISH_PROMPT'],
            settings['COACH_SELECTED_MODEL'], settings['EVAL_SELECTED_MODEL'])


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


def clear_chat():
    return []


def model_update(model, prefix):
    key = f'{prefix}_SELECTED_MODEL'
    settings[key] = model
    with open(settings_file, 'r') as f:
        settings_obj = json.load(f)

    settings_obj[key] = model
    with open(settings_file, 'w') as f:
        json.dump(settings_obj, f, ensure_ascii=False)
