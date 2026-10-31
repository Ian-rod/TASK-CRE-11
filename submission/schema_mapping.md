# Source-to-Database Schema Mapping

**Project:** TASK-CRE-11 – Berlin Land Value Zone Ingestion  
**Target database:** Local PostgreSQL 16 with PostGIS 3.4  
**Target schema:** `iris_staging`  
**Target table:** `berlin_land_value_zones`  
**Target CRS:** EPSG:25832

| WFS source attribute | PostgreSQL column | Data type | Transformation |
|---|---|---|---|
| `id` (GeoJSON feature ID) | `source_feature_id` | TEXT | Preserved as source identifier |
| `brwid` | `zone_id` | TEXT | Trimmed string |
| `brw` | `land_value` | NUMERIC(14,2) | Parsed as Decimal |
| `stichtag` | `valuation_date` | DATE | Parsed as ISO date |
| `bezirk` | `district` | TEXT | Trimmed string |
| `nutzung` | `land_use` | TEXT | Trimmed string |
| `gfz` | `gfz` | NUMERIC(10,3) | Nullable Decimal |
| `beitragszustand` | `contribution_status` | TEXT | Preserved as string |
| `lumnum` | `source_reference_url` | TEXT | Nullable string |
| `anwert` | `anwert` | TEXT | Preserved as source categorical/string value |
| `verfahrensart` | `verfahrensart` | TEXT | Preserved as string |
| `geometry` | `geom` | geometry(MultiPolygon,25832) | Validated, repaired where possible, transformed from declared source CRS |

## Geometry processing

The source sample declares EPSG:25833. The ingestion process verifies this declaration and transforms geometries into EPSG:25832 using PyProj.

Shapely is used to parse geometries, detect invalid geometry, attempt repair with `make_valid()`, and normalize polygonal geometry into MultiPolygon.

Records with missing, empty or unusable geometry are rejected.

## Idempotency

The local staging table uses `source_feature_id` as its unique key. PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` prevents duplicate rows when the same source feature is ingested again.

This is a development assumption and should be confirmed against the authoritative source's identifier stability and the final target DDL.
