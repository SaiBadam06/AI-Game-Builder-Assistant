import os
import groq
try:
    import httpx
    print(f"httpx version: {httpx.__version__}")
except ImportError:
    print("httpx not found")

print(f"groq version: {groq.__version__}")

try:
    from groq import Groq
    # Try to initialize with a dummy key to see if __init__ fails
    client = Groq(api_key="gsk_test_key")
    print("Groq client initialized successfully (with dummy key)")
except Exception as e:
    print(f"Failed to initialize Groq client: {e}")
    import traceback
    traceback.print_exc()
