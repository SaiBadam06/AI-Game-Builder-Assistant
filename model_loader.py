"""
model_loader.py
Groq API client wrapper.
"""
import os
import time
from groq import Groq
import groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is not set in .env")
        _client = Groq(api_key=api_key)
    return _client

def generate_text(prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
    """Submit a prompt to LLaMA 3.3 via Groq with rate-limit retries."""
    client = get_client()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except groq.RateLimitError as e:
            error_msg = str(e).lower()
            if "tokens per day" in error_msg or "tpd" in error_msg:
                # Daily limit reached! We cannot retry. 
                # Raise an error to prevent the entire pipeline from silently yielding empty data.
                raise RuntimeError("Groq API Daily Limit Reached. Please try again tomorrow or use a different key.")
            elif attempt < max_retries - 1:
                # Sleep for 4.5 seconds to let the generic TPM limit reset
                time.sleep(4.5)
            else:
                raise RuntimeError("Groq API Rate Limit Reached. Please try again later.")
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"API Error: {str(e)}")
