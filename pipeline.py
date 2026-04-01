"""
pipeline.py
Orchestrates the full world → factions → lore → quests → level → game pipeline.
Designed to be called step-by-step so Flask can stream progress via SSE.
"""

from generators.world import generate_world
from generators.geography import generate_geography
from generators.civilizations import generate_civilizations
from generators.politics import generate_politics
from generators.lore import generate_lore
from generators.quests import generate_quests
from generators.levels import generate_level
from generators.game_code import generate_game_code


PIPELINE_STEPS = [
    'world',
    'geography',
    'civilizations',
    'politics',
    'lore',
    'quests',
    'level',
    'game',
]

STEP_LABELS = {
    'world':         '🌍 Generating world theme...',
    'geography':     '🗺️  Mapping geography...',
    'civilizations': '🏛️  Building civilizations...',
    'politics':      '⚔️  Designing factions...',
    'lore':          '📜 Writing lore & history...',
    'quests':        '📋 Creating quests...',
    'level':         '🎮 Designing level...',
    'game':          '💻 Generating mini-game...',
}


def run_full_pipeline(theme: str) -> dict:
    """
    Execute the entire pipeline in sequence.
    Returns a dict with all generated data.
    """
    results = {}

    results['world']         = generate_world(theme)
    results['geography']     = generate_geography(results['world'])
    results['civilizations'] = generate_civilizations(results['world'])
    results['politics']      = generate_politics(results['world'])
    results['lore']          = generate_lore(results['world'], results['politics'])
    results['quests']        = generate_quests(results['world'], results['politics'])
    results['level']         = generate_level(results['world'], results['quests'])
    results['game']          = generate_game_code(results['world'], results['level'])

    return results
