import gradio as gr
from functools import partial
from state import MODELS, EVAL_MODELS
from ui_event_handlers import (
    msg_submit, msg_change, transcribe, sysprompt_update,
    evaluate, render_usages, render_sys_prompts,
    clear_coach_usage, clear_ev_usage,
)
from utils import set_sys_prompts, load_css

set_sys_prompts()
css = load_css()

with gr.Blocks() as ui:
    with gr.Tabs():
        with gr.Tab("Interview coach"):
            with gr.Row():
                with gr.Sidebar(open=False):
                    gr.Markdown("### Settings")
                    sysprompt_inp = gr.Textbox(label='System Prompt')
                    sysprompt_update_btn = gr.Button(value='Update')
                with gr.Column():
                    with gr.Row():
                        coach_usage = gr.Markdown()
                        clear_coach_usage_btn = gr.Button(value='Clear', elem_classes='gr_btn')
                    chatbot = gr.Chatbot(layout='panel', elem_classes='chatbot')
                    with gr.Row():
                        audio_msg = gr.Audio(sources="microphone", type="filepath",
                                        container=True, recording=False,
                                        waveform_options=gr.WaveformOptions(
                                            show_recording_waveform=False,
                                        ), scale=2)
                        with gr.Column(scale=1, min_width=80):
                            coach_model = gr.Dropdown(choices=MODELS, value='GPT 5.4 mini', show_label=False, container=False,
                                                interactive=True)
                            eval_model = gr.Dropdown(choices=EVAL_MODELS, value='llama 3.2', show_label=False, container=False,
                                                interactive=True)
                        clear_btn = gr.Button(value='Clear', elem_classes='gr_btn')
                    with gr.Row():
                        send_btn = gr.Button(value='Send', interactive=False, elem_classes='gr_btn')
                        msg = gr.Textbox(elem_id='msg', show_label=False, container=False)

        with gr.Tab("English evaluation"):
            with gr.Row():
                with gr.Sidebar(open=False):
                    gr.Markdown("### Settings")
                    ev_sysprompt_inp = gr.Textbox(label='System Prompt')
                    ev_sysprompt_update_btn = gr.Button(value='Update')
                with gr.Column():
                    with gr.Row():
                        ev_usage = gr.Markdown()
                        clear_ev_usage_btn = gr.Button(value='Clear', elem_classes='gr_btn')
                    ev_mrk = gr.Markdown('')

    ui.load(render_usages, outputs=[coach_usage, ev_usage])
    ui.load(render_sys_prompts, outputs=[sysprompt_inp, ev_sysprompt_inp])

    msg.change(msg_change, [msg], [send_btn])
    msg.submit(msg_submit, [msg, chatbot, coach_model], [chatbot, coach_usage]
              ).then(evaluate, [msg, ev_mrk, eval_model], [msg, ev_mrk, ev_usage])

    send_btn.click(msg_submit, [msg, chatbot, coach_model], [chatbot, coach_usage]
              ).then(evaluate, [msg, ev_mrk, eval_model], [msg, ev_mrk, ev_usage])

    audio_msg.input(transcribe, inputs=[msg, audio_msg], outputs=[msg, audio_msg]
                   ).then(fn=None, js="() => document.querySelector('#msg textarea')?.focus()")

    sysprompt_inp.submit(fn=sysprompt_update, inputs=[sysprompt_inp], outputs=sysprompt_inp)
    sysprompt_update_btn.click(fn=sysprompt_update, inputs=[sysprompt_inp], outputs=sysprompt_inp)

    ev_sysprompt_inp.submit(fn=partial(sysprompt_update, key='ENGLISH_PROMPT'), inputs=[ev_sysprompt_inp], outputs=ev_sysprompt_inp)
    ev_sysprompt_update_btn.click(fn=partial(sysprompt_update, key='ENGLISH_PROMPT'), inputs=[ev_sysprompt_inp], outputs=ev_sysprompt_inp)

    clear_btn.click(lambda: None, inputs=None, outputs=chatbot, queue=False)
    clear_coach_usage_btn.click(clear_coach_usage, inputs=None, outputs=coach_usage, queue=False)
    clear_ev_usage_btn.click(clear_ev_usage, inputs=None, outputs=ev_usage, queue=False)

if __name__ == '__main__':
    ui.launch(inbrowser=False, css=css)
