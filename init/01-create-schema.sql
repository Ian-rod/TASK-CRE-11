
-- Enable PostGIS in our local development database.
CREATE EXTENSION IF NOT EXISTS postgis;

-- Candidate-owned staging schema.
CREATE SCHEMA IF NOT EXISTS iris_staging;

-- Berlin land value zones.
CREATE TABLE IF NOT EXISTS iris_staging.berlin_land_value_zones (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Source identifiers
    source_feature_id TEXT NOT NULL UNIQUE,
    zone_id TEXT NOT NULL,

    -- Land value attributes
    land_value NUMERIC(14, 2) NOT NULL
        CHECK (land_value >= 0),
    valuation_date DATE NOT NULL,
    district TEXT NOT NULL,
    land_use TEXT NOT NULL,

    -- Optional source attributes
    gfz NUMERIC(10, 3)
        CHECK (gfz IS NULL OR gfz >= 0),
    contribution_status TEXT,
    source_reference_url TEXT,
    anwert TEXT,
    verfahrensart TEXT,

    -- Spatial data: ETRS89 / UTM Zone 32N
    geom geometry(MultiPolygon, 25832) NOT NULL
        CHECK (ST_IsValid(geom)),

    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Useful indexes for spatial and attribute queries.
CREATE INDEX IF NOT EXISTS idx_brv_geom
    ON iris_staging.berlin_land_value_zones
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_brv_zone_date
    ON iris_staging.berlin_land_value_zones (zone_id, valuation_date);

CREATE INDEX IF NOT EXISTS idx_brv_district
    ON iris_staging.berlin_land_value_zones (district);
