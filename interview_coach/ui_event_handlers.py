import gradio as gr
import mlx_whisper
import llms

from state import COACH_MODELS, EVAL_MODELS, settings, usage, state
from ui_formatter import format_usage, format_usage_with_tokens, format_evaluation
from utils import update_user_settings_file


async def msg_submit(message, history, model='GPT 5 mini'):
    state['MSG_FOR_EVALUATION'] = message
    if model == 'no coach' or not message.strip():
        yield "", history, gr.update()
    else:
        model_name = COACH_MODELS[model][0]
        async for hist, tokens in llms.stream_coach(model_name, message, history):
            yield "", hist, format_usage_with_tokens(tokens, model)


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
        update_user_settings_file()
        info_str = "Coach system prompt updated." if key == 'COACH_PROMPT' else \
            "English evaluation system prompt updated."
        gr.Info(info_str)
    else:
        gr.Warning(f'Failed to update: unknown setting {key}.')
        return gr.update()

    return prompt


async def evaluate(history, model):
    message = state.get('MSG_FOR_EVALUATION', '')
    if model == 'no eval' or not message.strip():
        print('Skip evaluation...')
        return history, gr.update()

    model_name = EVAL_MODELS[model][0]
    try:
        evaluation_result, tokens = await llms.evaluate(model_name, message)
    except Exception as e:
        print(e)
        gr.Error('Failed to do evaluation.')
        return history, gr.update()

    evaluation_text = format_evaluation(message, history, evaluation_result)
    usage_text = format_usage_with_tokens(tokens, model, prefix='ev')

    return evaluation_text, usage_text


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


def clear_chat(active_tab):
    if active_tab == 'coach':
        return [], gr.update()
    if active_tab == 'evaluation':
        return gr.update(), ""
    gr.Warning(f"Unknown tab: {active_tab}")
    return gr.update(), gr.update()


def model_update(model, prefix):
    key = f'{prefix}_SELECTED_MODEL'
    settings[key] = model
    update_user_settings_file()
