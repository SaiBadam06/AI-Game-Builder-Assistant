"""
generators/quests.py
Generates quests and storylines based on world and factions.
"""
import re
from model_loader import generate_text
from prompts import QUEST_PROMPT


def _clean(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_field(label: str, block: str) -> str:
    m = re.search(rf'{re.escape(label)}:\s*(.+?)(?=\n[A-Z]|\Z)', block, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ''


def _parse_quest(block: str) -> dict:
    return {
        'title':      _extract_field('TITLE', block),
        'type':       _extract_field('TYPE', block),
        'objective':  _extract_field('OBJECTIVE', block),
        'location':   _extract_field('LOCATION', block),
        'enemy':      _extract_field('ENEMY', block),
        'key_npc':    _extract_field('KEY NPC', block),
        'twist':      _extract_field('TWIST', block),
        'reward':     _extract_field('REWARD', block),
        'difficulty': _extract_field('DIFFICULTY', block),
    }


def generate_quests(world: dict, politics: dict) -> dict:
    world_desc    = world.get('raw', world.get('environment', ''))
    factions_desc = politics.get('raw', '')

    prompt = QUEST_PROMPT.format(
        factions_description=factions_desc,
        world_description=world_desc
    )
    raw = _clean(generate_text(prompt, temperature=0.9, max_tokens=1600))

    blocks = re.split(r'QUEST\s+\d+:', raw, flags=re.IGNORECASE)
    quests = [_parse_quest(b) for b in blocks[1:] if b.strip()]

    return {
        'quests': quests,
        'raw': raw,
    }
