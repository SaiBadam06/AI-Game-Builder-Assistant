import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"Key set: {'Yes' if SUPABASE_KEY else 'No'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing credentials")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    test_data = {
        "theme": "Test Theme",
        "name": "Test World",
        "tagline": "A test tagline",
        "environment": "Test environment",
        "magic_system": "Test magic",
        "tone": "Test tone",
        "player_character": "Test hero",
        "raw": "Test raw output"
    }
    
    print("Attempting to insert into 'worlds'...")
    response = supabase.table("worlds").insert({
        "theme":            test_data.get("theme"),
        "name":             test_data.get("name"),
        "tagline":          test_data.get("tagline"),
        "environment":      test_data.get("environment"),
        "magic_system":     test_data.get("magic_system"),
        "tone":             test_data.get("tone"),
        "player_character": test_data.get("player_character"),
        "raw_output":       test_data.get("raw")
    }).execute()
    
    print("Response received:")
    print(response)
    
    if response.data:
        print(f"Success! Inserted world ID: {response.data[0]['id']}")
    else:
        print("Insert failed: No data returned. This might be due to RLS policies.")

except Exception as e:
    print(f"Error during test: {e}")
