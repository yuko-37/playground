# AI Toolbox

**ai-toolbox** is a collection of independent Python and AI tools:

### 1. Image Prompt Designer (`image_generator/`)
A Gradio-based web app that uses conversational AI (local Llama 3.2 via Ollama, or OpenAI GPT) to guide users through refining an image idea.  
Once the concept is finalized, it extracts a polished prompt and generates the image via OpenAI's image generation API.

### 2. VK Video Scraper (`vkvideo_scrapper/`)
A Streamlit app that monitors predefined VK video playlists containing episodic shows and automatically surfaces the most recently published episodes.  
This allows users to check for new content without manually browsing playlists.

---

Both tools can be run locally or via Docker and are bundled together in a single **uv-managed Python project**.
