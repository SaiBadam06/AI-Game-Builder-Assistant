"""
generators/game_code.py
Uses Groq (LLaMA) to generate a complete, playable HTML5 browser mini-game
based on the level design and world theme.
"""
import re
import os
import uuid
from model_loader import generate_text
import json
from prompts import GAME_PROMPT, GAME_MCP_PROMPT


def _clean_bold(text: str) -> str:
    return re.sub(r'\*{1,3}', '', text).strip()


def _extract_html(raw: str) -> str:
    """Extract the HTML content from the LLM response."""
    # Try to find <!DOCTYPE html> ... </html> block
    m = re.search(r'(<!DOCTYPE html>.*?</html>)', raw, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: strip markdown fences if present
    raw = re.sub(r'```(?:html)?\s*', '', raw)
    raw = re.sub(r'```\s*$', '', raw, flags=re.MULTILINE)
    return raw.strip()


def generate_game_code(world: dict, level: dict) -> dict:
    """
    Generate a complete HTML/JS mini-game and save it as a file.
    Returns dict with: game_html, file_path, file_name.
    """
    theme     = world.get('theme', 'fantasy')
    world_name= world.get('name', 'Unknown World')
    level_desc = (
        f"World: {world_name} ({theme})\n"
        f"Level: {level.get('level_name','')}\n"
        f"Environment: {level.get('environment','')}\n"
        f"Enemies: {', '.join(e.get('name','') for e in level.get('enemies',[]))}\n"
        f"Win Condition: {level.get('win_condition','')}\n"
        f"Time Limit: {level.get('time_limit','120')} seconds"
    )

    prompt = GAME_PROMPT.format(
        level_description=level_desc,
        theme=theme
    )

    raw = generate_text(prompt, temperature=0.7, max_tokens=4000)
    game_html = _extract_html(raw)

    # ── Generate MCP Architecture JSON ──
    mcp_prompt = GAME_MCP_PROMPT.format(level_description=level_desc)
    mcp_raw = generate_text(mcp_prompt, temperature=0.5, max_tokens=800)
    
    mcp_data = {
        "model": "Handles internal game state, logic, and component tracking.",
        "controller": "Processes user keyboard input.",
        "presenter": "Renders objects and dynamic UI to the HTML5 canvas."
    }
    try:
        # Aggressive JSON extraction: find first { and last }
        clean_json = re.sub(r'```(?:json)?', '', mcp_raw).replace('```', '').strip()
        start = clean_json.find('{')
        end = clean_json.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(clean_json[start:end])
            # Ensure the strict keys are present
            mcp_data['model'] = parsed.get('model', mcp_data['model'])
            mcp_data['controller'] = parsed.get('controller', mcp_data['controller'])
            mcp_data['presenter'] = parsed.get('presenter', mcp_data['presenter'])
    except Exception as e:
        print(f"MCP parse error (using defaults): {e}")

    # Save the generated game
    games_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'static', 'generated_games'
    )
    os.makedirs(games_dir, exist_ok=True)

    file_name = f"game_{uuid.uuid4().hex[:8]}.html"
    file_path = os.path.join(games_dir, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(game_html)

    return {
        'game_html': game_html,
        'file_name': file_name,
        'file_path': file_path,
        'mcp': mcp_data,
    }
