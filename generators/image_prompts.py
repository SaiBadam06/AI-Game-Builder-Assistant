"""
generators/image_prompts.py

Uses the LLM (Groq) to craft rich, detailed image prompts for every visual
element of the game world: character portraits, location art, faction emblems,
world scenes, villain portraits.

These prompts work directly in Kandinsky, Midjourney, DALL-E, Stable Diffusion.
"""

import re
from model_loader import generate_text


def _clean(text: str) -> str:
    text = re.sub(r'\*{1,3}', '', text)
    # Strip any preamble like "Here is the prompt:" or "Image prompt:"
    text = re.sub(r'^(?:here is|image prompt|prompt)[:\s]+', '', text, flags=re.IGNORECASE)
    return text.strip().strip('"')


def _ask(instruction: str) -> str:
    """Ask the LLM for a single image prompt (short, targeted call)."""
    return _clean(generate_text(instruction, temperature=0.75, max_tokens=200))


# ── CHARACTER PORTRAIT ──────────────────────────────────────────────────────

def character_portrait_prompt(world: dict) -> str:
    char = world.get('player_character', '')
    theme = world.get('theme', 'fantasy')
    world_name = world.get('name', '')
    return _ask(f"""
Write a single detailed image generation prompt (Midjourney / Stable Diffusion style)
for the player character of a {theme} game world called {world_name}.

Character description: {char}

Rules:
- Start with the character's physical appearance
- Include lighting, pose, art style, and quality tags
- Keep it under 80 words
- Return ONLY the prompt, no explanation, no quotes

Example format:
tall elven warrior with silver plate armor, glowing rune sword, long white hair,
standing on a cliff at sunset, dramatic rim lighting, digital painting, 8k, concept art,
highly detailed, cinematic
""")


# ── LOCATION / SCENE ─────────────────────────────────────────────────────────

def location_prompt(name: str, description: str, theme: str) -> str:
    return _ask(f"""
Write a single image generation prompt for this game world location.

Location name: {name}
Description: {description}
World theme: {theme}

Return ONLY the prompt (under 70 words), no explanation.
Include: environment, atmosphere, lighting, art style, quality tags.
""")


# ── FACTION EMBLEM ────────────────────────────────────────────────────────────

def faction_emblem_prompt(faction: dict, theme: str) -> str:
    return _ask(f"""
Write a single image generation prompt for a faction emblem or banner.

Faction: {faction.get('name', '')}
Type: {faction.get('type', '')}
Ideology: {faction.get('ideology', '')}
World theme: {theme}

Return ONLY the prompt (under 60 words), no explanation.
Include: symbol description, style (heraldic / neon / tribal / etc.), colors, mood.
""")


# ── VILLAIN PORTRAIT ──────────────────────────────────────────────────────────

def villain_portrait_prompt(villain_name: str, villain_desc: str, theme: str) -> str:
    return _ask(f"""
Write a single image generation prompt for a game villain portrait.

Villain: {villain_name}
Description: {villain_desc}
World theme: {theme}

Return ONLY the prompt (under 70 words), no explanation.
Include: dramatic appearance, sinister lighting, environment, art style, quality tags.
""")


# ── CIVILIZATION PORTRAIT ─────────────────────────────────────────────────────

def civilization_prompt(civ: dict, theme: str) -> str:
    return _ask(f"""
Write a single image generation prompt for a typical member of a game world civilization.

Civilization: {civ.get('name', '')}
Race: {civ.get('race', '')}
Culture: {civ.get('culture', '')}
Appearance: {civ.get('appearance', '')}
World theme: {theme}

Return ONLY the prompt (under 75 words), no explanation.
Include: character appearance, clothing/armor, environment, art style, quality tags.
""")


# ── WORLD ESTABLISHING SHOT ───────────────────────────────────────────────────

def world_establishing_prompt(world: dict) -> str:
    env = world.get('environment', '')
    name = world.get('name', '')
    theme = world.get('theme', 'fantasy')
    return _ask(f"""
Write a single image generation prompt for an establishing shot of a game world.

World name: {name}
Environment: {env}
Theme: {theme}

Return ONLY the prompt (under 75 words), no explanation.
This should be a sweeping panoramic shot showing the world's most iconic landscape.
Include: environment, light, mood, art style, quality.
""")


# ── WORLD MAP ─────────────────────────────────────────────────────────────────

def world_map_prompt(world: dict, geography: dict) -> str:
    name = world.get('name', '')
    theme = world.get('theme', 'fantasy')
    continents = ", ".join([c.get('name', '') for c in world.get('continents', [])])
    cities = ", ".join([c.get('name', '') for c in geography.get('major_cities', [])])
    
    return _ask(f"""
Write a single image generation prompt for a highly detailed, professional cartography world map.

World Name: {name}
Theme: {theme}
Continents: {continents}
Key Cities: {cities}

Rules:
- Style: Academic fantasy map / sci-fi tactical hologram map / ancient parchment depending on theme.
- Labels: Continent and city names must be written in EXTREMELY CLEAR, BOLD, HIGH-CONTRAST TYPOGRAPHY.
- Legibility: Focus on sharp, readable text for '{name}' and other locations. No messy AI gibberish.
- Perspective: Top-down 2D or slightly angled orthographic map view.
- Features: Coastlines, mountains, forests, compass rose, ornate borders.
- Quality: Masterpiece, ultra-detailed, sharp focus, 8k resolution.
- Under 80 words. Return ONLY the prompt.
""")


# ── MASTER GENERATOR ─────────────────────────────────────────────────────────

def generate_all_image_prompts(world: dict, politics: dict,
                                lore: dict, geography: dict,
                                civilizations: dict) -> dict:
    """
    Generate image prompts for all major visual elements.
    Returns a structured dict keyed by category.
    """
    theme = world.get('theme', 'fantasy')

    prompts = {}

    # 1. Player character portrait
    prompts['character'] = {
        'label': f"Player Character — {world.get('name', '')}",
        'prompt': character_portrait_prompt(world),
        'icon': '🧙',
    }

    # 2. World establishing shot
    prompts['world_shot'] = {
        'label': f"World Establishing Shot — {world.get('name', '')}",
        'prompt': world_establishing_prompt(world),
        'icon': '🌍',
    }

    # 2b. AI World Map
    prompts['ai_map'] = {
        'label': f"AI-Generated World Map — {world.get('name', '')}",
        'prompt': world_map_prompt(world, geography),
        'icon': '🗺️',
    }

    # 3. First 3 cities as location art
    cities = geography.get('major_cities', [])[:3]
    prompts['locations'] = []
    for city in cities:
        prompts['locations'].append({
            'label': city.get('name', 'Location'),
            'prompt': location_prompt(city.get('name', ''), city.get('description', ''), theme),
            'icon': '🏙️',
        })

    # 4. Civilizations (up to 4)
    civs = civilizations.get('civilizations', [])[:4]
    prompts['civilizations'] = []
    for c in civs:
        prompts['civilizations'].append({
            'label': f"Civ: {c.get('name', '')}",
            'prompt': civilization_prompt(c, theme),
            'icon': '🏛️',
        })

    # 5. Faction emblems (up to 4)
    factions = politics.get('factions', [])[:4]
    prompts['factions'] = []
    for f in factions:
        prompts['factions'].append({
            'label': f"Faction: {f.get('name', '')}",
            'prompt': faction_emblem_prompt(f, theme),
            'icon': '⚔️',
        })

    # 6. First villain portrait
    villains = lore.get('great_villains', [])
    if villains:
        v = villains[0]
        prompts['villain'] = {
            'label': f"Villain — {v.get('name', '')}",
            'prompt': villain_portrait_prompt(v.get('name', ''), v.get('description', ''), theme),
            'icon': '☠️',
        }

    return prompts
