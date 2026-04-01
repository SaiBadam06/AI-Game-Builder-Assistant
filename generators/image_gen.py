"""
generators/image_gen.py

Image generation using NVIDIA NIM (Stable Diffusion 3 Medium).
Requires: requests, Pillow.
"""

import os
import uuid
import logging
import base64
import requests
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'static', 'generated_images'
)
os.makedirs(IMAGES_DIR, exist_ok=True)

# NVIDIA NIM Configuration
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
    except ImportError:
        pass

API_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"


def is_available() -> bool:
    """Check if the NVIDIA API key is configured."""
    return bool(NVIDIA_API_KEY)


def generate_image(prompt: str, prefix: str = "img",
                   aspect_ratio: str = "1:1") -> dict:
    """
    Generate an image using NVIDIA NIM Stable Diffusion 3 Medium API.

    Returns:
        {
            'success': bool,
            'image_url': str | None,
            'prompt': str,
            'error': str | None,
        }
    """
    if not NVIDIA_API_KEY:
        return {
            'success': False,
            'image_url': None,
            'prompt': prompt,
            'error': "NVIDIA_API_KEY not found in environment.",
        }

    try:
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Accept": "application/json",
        }

        # SD3 Medium on NIM typically supports various aspect ratios
        payload = {
            "prompt": prompt,
            "cfg_scale": 7,
            "aspect_ratio": aspect_ratio,
            "mode": "text-to-image",
        }

        logger.info(f"Requesting image from NVIDIA NIM: {API_URL}")
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"NVIDIA API Error: {response.status_code} - {response.text}")
            return {
                'success': False,
                'image_url': None,
                'prompt': prompt,
                'error': f"API Error {response.status_code}: {response.text[:100]}",
            }

        data = response.json()
        
        # NIM response format usually contains "artifacts" or "image" as base64
        # Adjusting based on standard NIM SD3 response structure
        image_b64 = None
        if "artifacts" in data:
            image_b64 = data["artifacts"][0].get("base64")
        elif "image" in data:
            image_b64 = data["image"]
        
        if not image_b64:
            return {
                'success': False,
                'image_url': None,
                'prompt': prompt,
                'error': "No image data found in API response.",
            }

        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data))

        fname = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        fpath = os.path.join(IMAGES_DIR, fname)
        image.save(fpath, format='PNG')

        return {
            'success': True,
            'image_url': f'/static/generated_images/{fname}',
            'prompt': prompt,
            'error': None,
        }

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {
            'success': False,
            'image_url': None,
            'prompt': prompt,
            'error': str(e),
        }

