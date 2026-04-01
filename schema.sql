-- schema.sql
-- Create tables for AI Game World Generator persistence
-- WARNING: This will drop existing tables to ensure UUID compatibility

DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS levels CASCADE;
DROP TABLE IF EXISTS quests CASCADE;
DROP TABLE IF EXISTS lore CASCADE;
DROP TABLE IF EXISTS politics CASCADE;
DROP TABLE IF EXISTS civilizations CASCADE;
DROP TABLE IF EXISTS geography CASCADE;
DROP TABLE IF EXISTS worlds CASCADE;

-- 1. Worlds: Main entry for each generation
CREATE TABLE worlds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme TEXT NOT NULL,
    name TEXT,
    tagline TEXT,
    environment TEXT,
    magic_system TEXT,
    tone TEXT,
    player_character TEXT,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Geography: Climate zones, cities, wonders, routes
CREATE TABLE geography (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    climate_zones JSONB,
    major_cities JSONB,
    natural_wonders JSONB,
    dangerous_regions JSONB,
    trade_routes JSONB,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Civilizations
CREATE TABLE civilizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    civilizations_data JSONB,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Politics: Factions, alliances, wars
CREATE TABLE politics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    factions JSONB,
    major_alliance TEXT,
    major_war TEXT,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Lore: Historical events and legends
CREATE TABLE lore (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    history JSONB,
    legends JSONB,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Quests: Questlines and objectives
CREATE TABLE quests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    quests_data JSONB,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Levels: Level design and environmental details
CREATE TABLE levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    level_data JSONB,
    raw_output TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 8. Images: Storing generated image prompts and URLs
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    image_type TEXT, -- 'map', 'character', 'location', etc.
    prompt TEXT,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
