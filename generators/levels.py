"""
generators/levels.py
Converts a quest into a detailed, playable level design.
"""
import re
from model_loader import generate_text
from prompts import LEVEL_PROMPT


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


def generate_level(world: dict, quests: dict) -> dict:
    quest_list = quests.get('quests', [])
    # Use the first quest (main quest) for level generation
    if quest_list:
        q = quest_list[0]
        quest_desc = (
            f"Title: {q.get('title','')}\n"
            f"Objective: {q.get('objective','')}\n"
            f"Location: {q.get('location','')}\n"
            f"Enemy: {q.get('enemy','')}\n"
            f"Twist: {q.get('twist','')}\n"
            f"Win Condition: defeat the enemy and reach the objective"
        )
    else:
        quest_desc = quests.get('raw', 'Generic adventure quest')

    world_desc = world.get('raw', world.get('environment', ''))

    prompt = LEVEL_PROMPT.format(
        quest_description=quest_desc,
        world_description=world_desc
    )
    raw = _clean(generate_text(prompt, temperature=0.85, max_tokens=1200))

    return {
        'level_name':    _extract_field('LEVEL NAME', raw),
        'environment':   _extract_field('ENVIRONMENT', raw),
        'layout':        _extract_list('LAYOUT', raw),
        'enemies':       _extract_list('ENEMIES', raw),
        'obstacles':     _extract_list('OBSTACLES', raw),
        'collectibles':  _extract_list('COLLECTIBLES', raw),
        'win_condition': _extract_field('WIN CONDITION', raw),
        'lose_condition':_extract_field('LOSE CONDITION', raw),
        'time_limit':    _extract_field('TIME LIMIT', raw),
        'raw': raw,
    }
