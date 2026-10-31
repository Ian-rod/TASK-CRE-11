
-- 1. Confirm database and schema
SELECT current_database(), current_schema();

-- 2. Confirm PostGIS is installed
SELECT PostGIS_Full_Version();

-- 3. Confirm the destination table
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'iris_staging'
  AND table_name = 'berlin_land_value_zones';

-- 4. Confirm row count
SELECT COUNT(*) AS total_records
FROM iris_staging.berlin_land_value_zones;

-- 5. Verify geometry types and CRS
SELECT
    ST_GeometryType(geom) AS geometry_type,
    ST_SRID(geom) AS srid,
    COUNT(*) AS total
FROM iris_staging.berlin_land_value_zones
GROUP BY ST_GeometryType(geom), ST_SRID(geom);

-- 6. Check invalid geometries count
SELECT COUNT(*) AS invalid_geometries
FROM iris_staging.berlin_land_value_zones
WHERE NOT ST_IsValid(geom);

-- 7. Check duplicate source IDs
SELECT source_feature_id, COUNT(*)
FROM iris_staging.berlin_land_value_zones
GROUP BY source_feature_id
HAVING COUNT(*) > 1;

-- 8. Inspect representative rows
SELECT
    source_feature_id,
    zone_id,
    land_value,
    valuation_date,
    district,
    land_use,
    ST_SRID(geom) AS srid
FROM iris_staging.berlin_land_value_zones
LIMIT 10;

-- 9. Verify no records were written to iris_core
SELECT COUNT(*) AS core_table_count
FROM information_schema.tables
WHERE table_schema = 'iris_core'
  AND table_type = 'BASE TABLE';
