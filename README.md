# AI Game World Generator

This is a Flask application with SSE streaming, image generation, and world export features for building an AI Game World.

## How to Run Locally

### 1. Requirements

Ensure you have Python installed on your system.

Install all the required dependencies by running:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file based on the `.env.example` file and populate it with your respective API keys:
- Groq API Key
- NVIDIA API Key
- Supabase Credentials

### 3. Run the Application

You can start the server by executing:
```bash
python app.py
```

The app will become accessible locally at `http://localhost:5000` (or `http://127.0.0.1:5000`).
