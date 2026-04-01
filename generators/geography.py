"""
generators/geography.py
Generates geography: climate zones, cities, wonders, dangerous regions, trade routes.
"""
import re
from model_loader import generate_text
from prompts import GEOGRAPHY_PROMPT


def _clean(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_list(label: str, text: str) -> list:
    """Extract a bullet list section into a list of dicts with name and description."""
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


def generate_geography(world: dict) -> dict:
    description = world.get('raw', world.get('environment', ''))
    prompt = GEOGRAPHY_PROMPT.format(world_description=description)
    raw = _clean(generate_text(prompt, temperature=0.85, max_tokens=1200))

    return {
        'climate_zones':    _extract_list('CLIMATE ZONES', raw),
        'major_cities':     _extract_list('MAJOR CITIES', raw),
        'natural_wonders':  _extract_list('NATURAL WONDERS', raw),
        'dangerous_regions':_extract_list('DANGEROUS REGIONS', raw),
        'trade_routes':     _extract_list('TRADE ROUTES', raw),
        'raw': raw,
    }
