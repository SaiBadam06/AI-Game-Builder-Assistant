"""
generators/lore.py
Generates history, myths, legendary heroes, great villains, prophecies.
"""
import re
from model_loader import generate_text
from prompts import LORE_PROMPT


def _clean(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_field(label: str, text: str) -> str:
    m = re.search(rf'{re.escape(label)}:\s*(.+?)(?=\n[A-Z]|\Z)', text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''


def _extract_list(label: str, text: str) -> list:
    pattern = rf'{re.escape(label)}:\s*\n((?:- .+\n?)+)'
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return []
    results = []
    for line in m.group(1).splitlines():
        line = line.strip().lstrip('- ').strip()
        if not line:
            continue
        if ':' in line:
            name, desc = line.split(':', 1)
            results.append({'name': name.strip(), 'description': desc.strip()})
        else:
            results.append({'name': line, 'description': ''})
    return results


def generate_lore(world: dict, politics: dict) -> dict:
    world_desc = world.get('raw', world.get('environment', ''))
    factions_raw = politics.get('raw', '')
    combined = f"WORLD:\n{world_desc}\n\nFACTIONS:\n{factions_raw}"

    prompt = LORE_PROMPT.format(world_and_factions=combined)
    raw = _clean(generate_text(prompt, temperature=0.9, max_tokens=1400))

    return {
        'creation_myth':      _extract_field('CREATION MYTH', raw),
        'historical_eras':    _extract_list('HISTORICAL ERAS', raw),
        'legendary_heroes':   _extract_list('LEGENDARY HEROES', raw),
        'great_villains':     _extract_list('GREAT VILLAINS', raw),
        'prophecy':           _extract_field('ANCIENT PROPHECY', raw),
        'forbidden_knowledge':_extract_field('FORBIDDEN KNOWLEDGE', raw),
        'raw': raw,
    }
