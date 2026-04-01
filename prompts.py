"""
prompts.py
All LLM prompt templates for the generation pipeline.
"""

WORLD_PROMPT = """You are a creative game world designer.

Create a detailed fictional game world based on this theme: {theme}

Provide a structured response with EXACTLY these sections:

WORLD NAME: [single name]
TAGLINE: [one exciting sentence]
ENVIRONMENT: [2-3 sentences describing the overall world feel]
CONTINENTS:
- [name]: [brief description]
(list as many continents as make sense for this world)
MAGIC OR TECHNOLOGY SYSTEM: [2-3 sentences]
NOTABLE LANDMARKS:
- [name]: [description]
(list notable landmarks that define the world)
TONE AND ATMOSPHERE: [2-3 sentences describing the mood, vibe, and emotional atmosphere of the game world]
PLAYER CHARACTER CONCEPT: [name, race, role, appearance, abilities, personality — 4-5 sentences]

Do not use markdown bold markers. Keep each section clear and concise."""


GEOGRAPHY_PROMPT = """You are a fictional cartographer and world-builder.

Based on this game world:
{world_description}

Generate detailed geography for the world.

Provide a structured response with EXACTLY these sections:

CLIMATE ZONES:
- [zone name]: [description]
(list the core climate zones)

MAJOR CITIES:
- [city name] ([continent]): [description, population culture]
(list the most prominent cities in the world)

NATURAL WONDERS:
- [name]: [description]
(list natural wonders)

DANGEROUS REGIONS:
- [name]: [why it is dangerous]
(list dangerous or forbidden areas)

TRADE ROUTES:
- [route name]: [connects what, what goods]
(list the major trade arteries)

Do not use markdown bold markers."""


CIVILIZATION_PROMPT = """You are a cultural anthropologist for fictional worlds.

Based on this game world:
{world_description}

Generate unique civilizations or races that inhabit this world.
Do not restrict yourself to a specific number; generate as many as are relevant to the theme.

For each civilization provide EXACTLY this format:

CIVILIZATION [N]:
NAME: [civilization name]
RACE: [species or people]
HOMELAND: [where they live]
CULTURE: [2-3 sentences about their way of life]
TRADITIONS: [2 key traditions]
SOCIAL STRUCTURE: [how society is organized]
STRENGTHS: [what they excel at]
WEAKNESSES: [their vulnerability]
SIGNATURE ABILITY: [a unique power or skill]
APPEARANCE: [physical description of a typical member]

Do not use markdown bold markers."""


POLITICS_PROMPT = """You are a political strategist for fictional kingdoms.

Based on this game world:
{world_description}

Generate the major factions with political tensions between them.
Do not restrict yourself to a specific number; generate as many factions as are necessary for a rich political landscape.

For each faction provide EXACTLY this format:

FACTION [N]:
NAME: [faction name]
TYPE: [empire / republic / cult / tribe / corporation / etc.]
LEADER: [name and title]
IDEOLOGY: [core belief or goal]
TERRITORY: [where they control]
MILITARY STRENGTH: [weak / moderate / strong / overwhelming]
ALLY: [allied faction name]
ENEMY: [rival faction name]
CURRENT CONFLICT: [one sentence about their active struggle]

End with:
MAJOR ALLIANCE: [describe the main power alliance between factions]
MAJOR WAR: [describe the central conflict threatening the world]

Do not use markdown bold markers."""


LORE_PROMPT = """You are a lore master and historian of fictional worlds.

Based on this game world and its factions:
{world_and_factions}

Generate the world's history and mythology.

Provide EXACTLY these sections:

CREATION MYTH: [3-4 sentences on how the world was created]

HISTORICAL ERAS:
- [Era name] ([time period]): [key events, 2 sentences]
(list the major eras of history)

LEGENDARY HEROES:
- [Hero name]: [race, power, legendary deed — 2 sentences]
(list legendary heroes)

GREAT VILLAINS:
- [Villain name]: [origin, evil act, current status — 2 sentences]
(list the most notorious villains)

ANCIENT PROPHECY: [a foreboding prophecy about the world's fate — 3-4 sentences]

FORBIDDEN KNOWLEDGE: [a dangerous secret or taboo — 2-3 sentences]

Do not use markdown bold markers."""


QUEST_PROMPT = """You are a game quest designer.

Based on these factions:
{factions_description}

And this world:
{world_description}

Generate unique quests.
Do not limit yourself to a specific number; provide a dynamic set of quests that span from early game to late game.

For each quest provide EXACTLY this format:

QUEST [N]:
TITLE: [quest name]
TYPE: [main story / side quest / faction war / mystery / dungeon raid]
OBJECTIVE: [what the player must do — 2 sentences]
LOCATION: [specific area in the world]
ENEMY: [who or what opposes the player]
KEY NPC: [important character who gives or assists the quest]
TWIST: [unexpected plot twist mid-quest]
REWARD: [items, abilities, or story unlocks]
DIFFICULTY: [Easy / Medium / Hard / Legendary]

Do not use markdown bold markers."""


LEVEL_PROMPT = """You are a game level designer.

Convert this quest into a detailed playable level:
{quest_description}

World context:
{world_description}

Provide EXACTLY these sections:

LEVEL NAME: [name]
ENVIRONMENT: [detailed visual description of the level setting]
LAYOUT:
- Area 1: [name and description]
(list the sequence of sub-areas in the level, ending with a boss area)

ENEMIES:
- [enemy type]: [behavior and attack pattern]
(list enemies found in this level)
- [boss]: [special abilities and defeat conditions]

OBSTACLES:
- [obstacle name]: [how it challenges the player]
(list environmental hazards)

COLLECTIBLES:
- [item]: [what it does]
(list items to find)

WIN CONDITION: [exactly how the player wins]
LOSE CONDITION: [exactly how the player loses]
TIME LIMIT: [in seconds, number only]

Do not use markdown bold markers."""


GAME_PROMPT = """You are an expert HTML5 game developer.

Create a complete, playable browser game using HTML, CSS, and JavaScript.

Game Level Details:
{level_description}

World Theme: {theme}

REQUIREMENTS (all mandatory):
- Use an HTML5 canvas element with id="gameCanvas"
- Player character that moves with WASD or Arrow Keys
- At least 2 different enemy types that move toward the player
- A score system that increases when enemies are defeated
- Health bar for the player (starts at 100)
- Win condition (reach score target) and Lose condition (health = 0)
- Atmospheric background matching the world theme (draw with canvas shapes/gradients)
- Game Over screen AND Victory screen with restart button
- Display: score, health, timer, and level name on screen
- Clean, complete, self-contained single HTML file

IMPORTANT:
- Return ONLY the complete HTML code starting with <!DOCTYPE html>
- No explanations, no markdown fences, no commentary
- The game must work immediately when opened in a browser
- Use vibrant colors matching the world theme"""

GAME_MCP_PROMPT = """You are a technical game architect. 
Analyze this game level description:
{level_description}

Provide a short, user-friendly Model-Controller-Presenter (MCP) architecture breakdown for the HTML5 canvas mini-game being generated.
Format the response as a valid JSON object with exactly these three keys:
"model": A 1-2 sentence description of the game state, data, and core logic (e.g., "Tracks player health, score, and enemy coordinates.").
"controller": A 1-2 sentence description of how the player interacts with the game (e.g., "Listens for WASD/Arrow keys to move the player and spacebar to attack.").
"presenter": A 1-2 sentence description of the visual rendering (e.g., "Renders the player, enemies, and dynamic score using an HTML5 Canvas loop.").

Return ONLY valid JSON. No markdown fences.
"""
