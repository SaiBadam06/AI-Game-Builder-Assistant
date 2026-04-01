"""
app.py  —  AI Game World Builder
Flask application with SSE streaming + image generation + world export.
"""

import json
import os
import traceback
from flask import (Flask, render_template, request, Response,
                   jsonify, send_from_directory)
from flask_cors import CORS

from generators.world import generate_world
from generators.geography import generate_geography
from generators.civilizations import generate_civilizations
from generators.politics import generate_politics
from generators.lore import generate_lore
from generators.quests import generate_quests
from generators.levels import generate_level
from generators.image_prompts import generate_all_image_prompts, world_map_prompt
from generators.world_map import generate_svg_map
from generators.image_gen import generate_image, is_available as gpu_available

# Supabase database integration
from database import (
    create_world, update_geography, update_civilizations,
    update_politics, update_lore, update_quests, update_levels, save_image
)

app = Flask(__name__, 
            static_folder='frontend', 
            static_url_path='', 
            template_folder='frontend')
CORS(app)

GAMES_DIR  = os.path.join(os.path.dirname(__file__), 'static', 'generated_games')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'generated_images')
os.makedirs(GAMES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


def _sse(event: str, data: dict | str) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = json.dumps(data)
    return f"event: {event}\ndata: {payload}\n\n"


# ════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game/<filename>')
def serve_game(filename):
    return send_from_directory(GAMES_DIR, filename)


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


# ════════════════════════════════════════════════════════
#  WORLD MAP  (returns SVG)
# ════════════════════════════════════════════════════════

@app.route('/world-map', methods=['POST'])
def world_map():
    # Allow CORS from Vercel (or any other domain)
    # The frontend needs to point to this backend URL
    data = request.get_json(silent=True) or {}
    world_data = data.get('world', {})
    geo_data   = data.get('geography', {})
    svg = generate_svg_map(world_data, geo_data)
    return Response(svg, mimetype='image/svg+xml')


# ════════════════════════════════════════════════════════
#  IMAGE GENERATION  (SDXL-Turbo or fallback)
# ════════════════════════════════════════════════════════

@app.route('/gpu-status', methods=['GET'])
def gpu_status():
    return jsonify({'gpu': gpu_available()})


@app.route('/generate-image', methods=['POST'])
def gen_single_image():
    """Generate one image from a given prompt. Called per prompt card."""
    data   = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '').strip()
    prefix = data.get('prefix', 'img')
    if not prompt:
        return jsonify({'error': 'prompt required'}), 400
    result = generate_image(prompt, prefix=prefix)
    
    # If a world_id is provided, save image metadata to Supabase
    world_id = data.get('world_id')
    if result.get('success') and world_id:
        save_image(world_id, prefix, prompt, result.get('image_url'))
        
    return jsonify(result)


# ════════════════════════════════════════════════════════
#  WORLD EXPORT
# ════════════════════════════════════════════════════════

@app.route('/export-world', methods=['POST'])
def export_world():
    """Return the full generated world as JSON for download."""
    data = request.get_json(silent=True) or {}
    # Strip raw blobs to keep export clean
    clean = {}
    for k, v in data.items():
        if isinstance(v, dict):
            clean[k] = {kk: vv for kk, vv in v.items() if kk != 'raw'}
        else:
            clean[k] = v
    return jsonify(clean)


# ════════════════════════════════════════════════════════
#  SSE STREAMING PIPELINE
# ════════════════════════════════════════════════════════

@app.route('/stream', methods=['GET'])
def stream():
    theme = request.args.get('theme', '').strip()
    if not theme:
        return jsonify({'error': 'theme is required'}), 400

    def generate():
        pipeline_data = {}
        try:
            # ── 1: World ────────────────────────────────────────────────
            yield _sse('progress', {'step': 'world', 'label': '🌍 Generating world theme…'})
            world = generate_world(theme)
            pipeline_data['world'] = world
            
            # Initialize world in Supabase and get world_id
            world_id = create_world(world)
            world['id'] = world_id # Add ID to payload sent to frontend
            
            yield _sse('world', world)

            # ── 2: Geography ─────────────────────────────────────────────
            yield _sse('progress', {'step': 'geography', 'label': '🗺️  Mapping geography…'})
            geography = generate_geography(world)
            pipeline_data['geography'] = geography
            
            # Save to Supabase
            if world_id:
                update_geography(world_id, geography)
                
            yield _sse('geography', geography)

            # ── 2b: AI World Map (NVIDIA NIM) ─────────────────────────────
            yield _sse('progress', {'step': 'geography', 'label': '🎨 Drawing AI World Map…'})
            map_prompt = world_map_prompt(world, geography)
            map_result = generate_image(map_prompt, prefix="map", aspect_ratio="16:9")
            
            if map_result['success']:
                if world_id:
                    save_image(world_id, 'map', map_prompt, map_result['image_url'])
                yield _sse('world_map', {'image_url': map_result['image_url']})
            else:
                # Fallback to SVG if NIM fails
                svg = generate_svg_map(world, geography)
                yield _sse('world_map', {'svg': svg})

            # ── 3: Civilizations ─────────────────────────────────────────
            yield _sse('progress', {'step': 'civilizations', 'label': '🏛️  Building civilizations…'})
            civilizations = generate_civilizations(world)
            pipeline_data['civilizations'] = civilizations
            
            if world_id:
                update_civilizations(world_id, civilizations)
                
            yield _sse('civilizations', civilizations)

            # ── 4: Politics ───────────────────────────────────────────────
            yield _sse('progress', {'step': 'politics', 'label': '⚔️  Designing factions…'})
            politics = generate_politics(world)
            pipeline_data['politics'] = politics
            
            if world_id:
                update_politics(world_id, politics)
                
            yield _sse('politics', politics)

            # ── 5: Lore ───────────────────────────────────────────────────
            yield _sse('progress', {'step': 'lore', 'label': '📜 Writing lore & history…'})
            lore = generate_lore(world, politics)
            pipeline_data['lore'] = lore
            
            if world_id:
                update_lore(world_id, lore)
                
            yield _sse('lore', lore)

            # ── 6: Quests ─────────────────────────────────────────────────
            yield _sse('progress', {'step': 'quests', 'label': '📋 Creating quests…'})
            quests = generate_quests(world, politics)
            pipeline_data['quests'] = quests
            
            if world_id:
                update_quests(world_id, quests)
                
            yield _sse('quests', quests)

            # ── 7: Level ──────────────────────────────────────────────────
            yield _sse('progress', {'step': 'level', 'label': '🎮 Designing level…'})
            level = generate_level(world, quests)
            pipeline_data['level'] = level
            
            if world_id:
                update_levels(world_id, level)
                
            yield _sse('level', level)

            # ── 7b: Image Prompts ─────────────────────────────────────────
            yield _sse('progress', {'step': 'image_prompts', 'label': '🎨 Crafting image prompts…'})
            img_prompts = generate_all_image_prompts(world, politics, lore, geography, civilizations)
            pipeline_data['image_prompts'] = img_prompts
            yield _sse('image_prompts', {
                'prompts': img_prompts,
                'gpu_available': gpu_available(),
            })



            # ── Done ─────────────────────────────────────────────────────
            yield _sse('done', {
                'message': 'Generation complete!',
                'world_data': {k: {kk: vv for kk, vv in v.items() if kk != 'raw'}
                               if isinstance(v, dict) else v
                               for k, v in pipeline_data.items()},
            })

        except Exception as e:
            tb = traceback.format_exc()
            yield _sse('error', {'message': str(e), 'traceback': tb})

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
