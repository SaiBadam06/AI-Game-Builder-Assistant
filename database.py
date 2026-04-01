import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_supabase: Client = None

def get_supabase() -> Client:
    """Lazy initialize Supabase client to catch late .env updates."""
    global _supabase
    if _supabase:
        return _supabase
    
    # Reload env in case it changed
    load_dotenv(override=True)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key or "your-project-id" in url:
        return None
        
    try:
        _supabase = create_client(url, key)
        return _supabase
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
        return None

def create_world(data: dict) -> str:
    """Initialize a world entry and return its ID."""
    sb = get_supabase()
    if not sb: return None
    try:
        response = sb.table("worlds").insert({
            "theme":            data.get("theme"),
            "name":             data.get("name"),
            "tagline":          data.get("tagline"),
            "environment":      data.get("environment"),
            "magic_system":     data.get("magic_system"),
            "tone":             data.get("tone"),
            "player_character": data.get("player_character"),
            "raw_output":       data.get("raw")
        }).execute()
        
        if response.data:
            return response.data[0]['id']
    except Exception as e:
        print(f"Error creating world in Supabase: {e}")
    return None

def update_geography(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("geography").insert({
            "world_id":          world_id,
            "climate_zones":     data.get("climate_zones"),
            "major_cities":      data.get("major_cities"),
            "natural_wonders":   data.get("natural_wonders"),
            "dangerous_regions": data.get("dangerous_regions"),
            "trade_routes":      data.get("trade_routes"),
            "raw_output":        data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating geography in Supabase: {e}")

def update_civilizations(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("civilizations").insert({
            "world_id":           world_id,
            "civilizations_data": data.get("civilizations"),
            "raw_output":         data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating civilizations in Supabase: {e}")

def update_politics(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("politics").insert({
            "world_id":       world_id,
            "factions":       data.get("factions"),
            "major_alliance": data.get("major_alliance"),
            "major_war":      data.get("major_war"),
            "raw_output":     data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating politics in Supabase: {e}")

def update_lore(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        # Safer list merging
        heroes = data.get("legendary_heroes") or []
        villains = data.get("great_villains") or []
        sb.table("lore").insert({
            "world_id":   world_id,
            "history":   data.get("historical_eras"),
            "legends":   heroes + villains,
            "raw_output": data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating lore in Supabase: {e}")

def update_quests(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("quests").insert({
            "world_id":    world_id,
            "quests_data": data.get("quests"),
            "raw_output":  data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating quests in Supabase: {e}")

def update_levels(world_id: str, data: dict):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("levels").insert({
            "world_id":   world_id,
            "level_data": data,
            "raw_output": data.get("raw")
        }).execute()
    except Exception as e:
        print(f"Error updating levels in Supabase: {e}")

def save_image(world_id: str, image_type: str, prompt: str, image_url: str):
    sb = get_supabase()
    if not sb or not world_id: return
    try:
        sb.table("images").insert({
            "world_id":   world_id,
            "image_type": image_type,
            "prompt":     prompt,
            "image_url":  image_url
        }).execute()
    except Exception as e:
        print(f"Error saving image in Supabase: {e}")
