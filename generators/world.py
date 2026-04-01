"""
generators/world.py
Generates the core game world theme and description.
"""
import re
from model_loader import generate_text
from prompts import WORLD_PROMPT


def _clean(text: str) -> str:
    """Remove markdown bold/italic markers."""
    text = re.sub(r'\*{1,3}', '', text)
    return text.strip()


def generate_world(theme: str) -> dict:
    prompt = WORLD_PROMPT.format(theme=theme)
    raw = _clean(generate_text(prompt, temperature=0.9, max_tokens=1200))

    def extract(label: str, text: str, multiline: bool = False) -> str:
        if multiline:
            pattern = rf'{label}:\s*\n((?:- .+\n?)+)'
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                lines = [l.strip().lstrip('- ').strip() for l in m.group(1).splitlines() if l.strip()]
                return lines
            return []
        else:
            pattern = rf'{label}:\s*(.+?)(?=\n[A-Z]|\Z)'
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return m.group(1).strip() if m else ''

    continents_raw = extract('CONTINENTS', raw, multiline=True)
    landmarks_raw  = extract('NOTABLE LANDMARKS', raw, multiline=True)

    # Parse continent name:desc pairs
    continents = []
    for item in continents_raw:
        if ':' in item:
            name, desc = item.split(':', 1)
            continents.append({'name': name.strip(), 'description': desc.strip()})
        else:
            continents.append({'name': item, 'description': ''})

    landmarks = []
    for item in landmarks_raw:
        if ':' in item:
            name, desc = item.split(':', 1)
            landmarks.append({'name': name.strip(), 'description': desc.strip()})
        else:
            landmarks.append({'name': item, 'description': ''})

    return {
        'theme': theme,
        'name': extract('WORLD NAME', raw),
        'tagline': extract('TAGLINE', raw),
        'environment': extract('ENVIRONMENT', raw),
        'continents': continents,
        'magic_system': extract('MAGIC OR TECHNOLOGY SYSTEM', raw),
        'landmarks': landmarks,
        'tone': extract('TONE AND ATMOSPHERE', raw),
        'player_character': extract('PLAYER CHARACTER CONCEPT', raw),
        'raw': raw,
    }
