import base64
import gradio as gr
import os

from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


load_dotenv()
gpt = OpenAI()
llama = OpenAI(base_url=os.getenv('OLLAMA_BASE_URL'), api_key="ollama")

MODELS = {
    "llama 3.2": "llama3.2",
    "GPT 5 mini": "gpt-5-mini",
}

PROMPT_HEADER = "FINAL PROMPT:"
SYSTEM_PROMPT = f"""
You are an assistant that helps users create high-quality image generation prompts.

Your job:
- Ask clarifying questions step by step
- Do NOT generate the final prompt too early
- Gather details like:
  - subject
  - style
  - composition
  - lighting
  - mood
  - camera / perspective

When you have enough information, output:

{PROMPT_HEADER}
<well-written detailed prompt>

Keep responses short and conversational.
"""


def stream_chat(client: OpenAI, model: str, message: str, history: list):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for record in history:
        messages.append({"role": record["role"], "content": record["content"][0]["text"]})

    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    partial_reply = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            partial_reply += chunk.choices[0].delta.content
            history_chunk = [
                {"role": "user", "content": [{"text": message, "type": "text"}]},
                {"role": "assistant", "content": [{"text": partial_reply, "type": "text"}]},
            ]
            _, _, prompt_chunk = partial_reply.partition(PROMPT_HEADER)
            yield history + history_chunk, "", prompt_chunk.strip()


def msg_submit(message: str, history: list, model: str):
    model_id = MODELS[model]
    if model_id == 'llama3.2':
        client = llama
    elif model_id == 'gpt-5-mini':
        client = gpt
    else:
        raise ValueError(f'Unknown model name: {model_id}')
        
    yield from stream_chat(client, model_id, message, history)


def artist(prompt: str):
    if not prompt:
        return None
    response = gpt.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
        response_format="b64_json",
    )
    image_data = base64.b64decode(response.data[0].b64_json)
    img = Image.open(BytesIO(image_data))
    return img


with gr.Blocks(title="Image Prompt Designer") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Image Prompt Designer")
            model = gr.Dropdown(label="Model", choices=list(MODELS.keys()), value="llama 3.2")
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(value="draw a goat", label="Message")
            clear = gr.Button("Clear chat")

        with gr.Column(scale=1):
            gr.Markdown("## Image Panel")
            prompt_box = gr.Textbox(label="Prompt", lines=5)
            run_btn = gr.Button("Generate Image", variant="primary")
            output_box = gr.Image(label="Result")

    msg.submit(msg_submit, [msg, chatbot, model], [chatbot, msg, prompt_box])
    clear.click(lambda: [], None, chatbot)
    run_btn.click(artist, inputs=prompt_box, outputs=output_box)

if __name__ == "__main__":
    demo.launch(inbrowser=True)

