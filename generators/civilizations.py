"""
generators/civilizations.py
Generates civilizations and cultures within the world.
"""
import re
from model_loader import generate_text
from prompts import CIVILIZATION_PROMPT


def _clean(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_field(label: str, block: str) -> str:
    m = re.search(rf'{re.escape(label)}:\s*(.+?)(?=\n[A-Z]|\Z)', block, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''


def _parse_civilization(block: str) -> dict:
    return {
        'name':              _extract_field('NAME', block),
        'race':              _extract_field('RACE', block),
        'homeland':          _extract_field('HOMELAND', block),
        'culture':           _extract_field('CULTURE', block),
        'traditions':        _extract_field('TRADITIONS', block),
        'social_structure':  _extract_field('SOCIAL STRUCTURE', block),
        'strengths':         _extract_field('STRENGTHS', block),
        'weaknesses':        _extract_field('WEAKNESSES', block),
        'signature_ability': _extract_field('SIGNATURE ABILITY', block),
        'appearance':        _extract_field('APPEARANCE', block),
    }


def generate_civilizations(world: dict) -> dict:
    description = world.get('raw', world.get('environment', ''))
    prompt = CIVILIZATION_PROMPT.format(world_description=description)
    raw = _clean(generate_text(prompt, temperature=0.9, max_tokens=1600))

    # Split on "CIVILIZATION N:"
    blocks = re.split(r'CIVILIZATION\s+\d+:', raw, flags=re.IGNORECASE)
    civilizations = [_parse_civilization(b) for b in blocks[1:] if b.strip()]

    return {
        'civilizations': civilizations,
        'raw': raw,
    }
