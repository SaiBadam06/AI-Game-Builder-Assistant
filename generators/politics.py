"""
generators/politics.py
Generates factions, rulers, alliances, and political conflicts.
"""
import re
from model_loader import generate_text
from prompts import POLITICS_PROMPT


def _clean(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_field(label: str, block: str) -> str:
    m = re.search(rf'{re.escape(label)}:\s*(.+?)(?=\n[A-Z]|\Z)', block, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''


def _parse_faction(block: str) -> dict:
    return {
        'name':             _extract_field('NAME', block),
        'type':             _extract_field('TYPE', block),
        'leader':           _extract_field('LEADER', block),
        'ideology':         _extract_field('IDEOLOGY', block),
        'territory':        _extract_field('TERRITORY', block),
        'military_strength':_extract_field('MILITARY STRENGTH', block),
        'ally':             _extract_field('ALLY', block),
        'enemy':            _extract_field('ENEMY', block),
        'current_conflict': _extract_field('CURRENT CONFLICT', block),
    }


def generate_politics(world: dict) -> dict:
    description = world.get('raw', world.get('environment', ''))
    prompt = POLITICS_PROMPT.format(world_description=description)
    raw = _clean(generate_text(prompt, temperature=0.85, max_tokens=1400))

    # Split on FACTION N:
    blocks = re.split(r'FACTION\s+\d+:', raw, flags=re.IGNORECASE)
    factions = [_parse_faction(b) for b in blocks[1:] if b.strip()]

    # Extract global summaries
    major_alliance = _extract_field('MAJOR ALLIANCE', raw)
    major_war      = _extract_field('MAJOR WAR', raw)

    return {
        'factions': factions,
        'major_alliance': major_alliance,
        'major_war': major_war,
        'raw': raw,
    }
