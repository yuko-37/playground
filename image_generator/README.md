## Image Prompt Designer

A Gradio app that turns a conversation into an AI-generated image.

- Chat with **Llama 3.2** (local) or **GPT** to refine your idea
- The assistant asks about subject, style, lighting, and mood
- Once ready, it extracts a polished prompt and sends it to image generation model

<img width="800" height="775" alt="Screenshot 2026-04-15 at 12 59 17" src="https://github.com/user-attachments/assets/67c48595-6682-4399-ab8e-14392b588a6a" />

### Run with Docker

```bash
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up --build
```

Open http://localhost:7860. Ollama pulls `llama3.2` (~2 GB) on first start.

### Run locally 

```bash
pip install openai gradio python-dotenv pillow
```
or 
```bash
uv sync
```
Install Ollama if it is not already installed, then run it and pull the llama 3.2 model.

```bash
ollama serve && ollama pull llama3.2
python gradio_app.py
```

### Environment variables
Provide environment variables via a .env file or any other method.

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Required. Used for GPT chat and image generation |
| `OLLAMA_BASE_URL` | Optional. Defaults to `http://localhost:11434/v1` |
