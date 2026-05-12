import gradio as gr
from functools import partial
from state import COACH_MODELS, EVAL_MODELS
from ui_event_handlers import (
    msg_submit, msg_change, transcribe, sysprompt_update,
    render_usages, render_settings,
    clear_coach_usage, clear_ev_usage, clear_chat,
    evaluate, model_update
)
from utils import load_settings, load_css

load_settings()
css = load_css()


with gr.Blocks() as ui:
    active_tab = gr.State("coach")
    with gr.Tabs():
        with gr.Tab("Interview coach") as coach_tab:
            with gr.Row():
                with gr.Sidebar(open=False):
                    gr.Markdown("### Settings")
                    sysprompt_inp = gr.Textbox(label='System Prompt')
                    sysprompt_update_btn = gr.Button(value='Update')
                with gr.Column():
                    with gr.Row():
                        coach_usage = gr.Markdown()
                        clear_coach_usage_btn = gr.Button(value='Clear', elem_classes='gr_btn')
                    chatbot = gr.Chatbot(elem_classes='chatbot')

        with gr.Tab("English evaluation") as eval_tab:
            with gr.Row():
                with gr.Sidebar(open=False):
                    gr.Markdown("### Settings")
                    ev_sysprompt_inp = gr.Textbox(label='System Prompt')
                    ev_sysprompt_update_btn = gr.Button(value='Update')
                with gr.Column():
                    with gr.Row():
                        ev_usage = gr.Markdown()
                        clear_ev_usage_btn = gr.Button(value='Clear', elem_classes='gr_btn')
                    ev_mrk = gr.Markdown('', elem_classes='chatbot')
    with gr.Row():
        audio_msg = gr.Audio(sources="microphone", type="filepath",
                             container=True, recording=False,
                             waveform_options=gr.WaveformOptions(
                                 show_recording_waveform=False,
                             ), scale=2)
        with gr.Column(scale=1, min_width=80):
            coach_model = gr.Dropdown(choices=COACH_MODELS,
                                      show_label=False, container=False,
                                      interactive=True)
            eval_model = gr.Dropdown(choices=EVAL_MODELS,
                                     show_label=False, container=False,
                                     interactive=True)
        clear_btn = gr.Button(value='Clear', elem_classes='gr_btn')
    with gr.Row():
        send_btn = gr.Button(value='Send', interactive=False, elem_classes='gr_btn')
        msg = gr.Textbox(elem_id='msg',
                         show_label=False, container=False)

    load_settings()
    ui.load(render_usages, outputs=[coach_usage, ev_usage])
    ui.load(render_settings, outputs=[sysprompt_inp, ev_sysprompt_inp, coach_model, eval_model])

    msg.change(msg_change, [msg], [send_btn])

    msg.submit(msg_submit, [msg, chatbot, coach_model], [msg, chatbot, coach_usage]
              ).then(evaluate, [ev_mrk, eval_model], [ev_mrk, ev_usage])

    send_btn.click(msg_submit, [msg, chatbot, coach_model], [msg, chatbot, coach_usage]
              ).then(evaluate, [ev_mrk, eval_model], [ev_mrk, ev_usage])

    audio_msg.input(transcribe, inputs=[msg, audio_msg], outputs=[msg, audio_msg]
                   ).then(fn=None, js="() => document.querySelector('#msg textarea')?.focus()")

    sysprompt_inp.submit(fn=sysprompt_update, inputs=[sysprompt_inp], outputs=sysprompt_inp)
    sysprompt_update_btn.click(fn=sysprompt_update, inputs=[sysprompt_inp], outputs=sysprompt_inp)

    ev_sysprompt_inp.submit(fn=partial(sysprompt_update, key='ENGLISH_PROMPT'), inputs=[ev_sysprompt_inp], outputs=ev_sysprompt_inp)
    ev_sysprompt_update_btn.click(fn=partial(sysprompt_update, key='ENGLISH_PROMPT'), inputs=[ev_sysprompt_inp], outputs=ev_sysprompt_inp)

    coach_tab.select(fn=lambda: "coach", outputs=active_tab)
    eval_tab.select(fn=lambda: "evaluation", outputs=active_tab)

    clear_btn.click(clear_chat, inputs=active_tab, outputs=[chatbot, ev_mrk], queue=False)
    clear_coach_usage_btn.click(clear_coach_usage, inputs=None, outputs=coach_usage, queue=False)
    clear_ev_usage_btn.click(clear_ev_usage, inputs=None, outputs=ev_usage, queue=False)

    coach_model.input(fn=partial(model_update, prefix='COACH'), inputs=coach_model, outputs=None)
    eval_model.input(fn=partial(model_update, prefix='EVAL'), inputs=eval_model, outputs=None)

if __name__ == '__main__':
    ui.launch(inbrowser=False, css=css)
