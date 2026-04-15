FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    "openai>=2.31.0" \
    "gradio>=6.11.0" \
    python-dotenv \
    pillow

COPY gradio_app.py .

EXPOSE 7860

ENV GRADIO_SERVER_NAME=0.0.0.0

ENTRYPOINT ["python3", "gradio_app.py"]
