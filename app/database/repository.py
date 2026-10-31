#Insert new land-value zones.
#Update existing zones when the same source_feature_id is received again.
#Commit successful batches or roll them back if an error occurs.


import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Fixed destination: never accept a table name from external input.
DESTINATION = "iris_staging.berlin_land_value_zones"

#If the source feature ID does not exist, PostgreSQL inserts a new row.
#If it already exists, PostgreSQL updates the existing row.
def upsert_records(connection, records: list[dict]) -> dict:
    """
    Insert new records or update existing records.

    Uses source_feature_id as the conflict key.
    All operations are performed in one transaction.
    """

    if settings.db_schema != "iris_staging":
        raise ValueError("Database writes are restricted to iris_staging.")

    if settings.db_table != "berlin_land_value_zones":
        raise ValueError(
            "DB_TABLE must be berlin_land_value_zones."
        )

    if not records:
        logger.info("No records to insert.")
        return {"processed": 0, "failed": 0}

    insert_sql = """
        INSERT INTO iris_staging.berlin_land_value_zones (
            source_feature_id,
            zone_id,
            land_value,
            valuation_date,
            district,
            land_use,
            gfz,
            contribution_status,
            source_reference_url,
            anwert,
            verfahrensart,
            geom
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            ST_GeomFromWKB(%s, 25832)
        )
        ON CONFLICT (source_feature_id)
        DO UPDATE SET
            zone_id = EXCLUDED.zone_id,
            land_value = EXCLUDED.land_value,
            valuation_date = EXCLUDED.valuation_date,
            district = EXCLUDED.district,
            land_use = EXCLUDED.land_use,
            gfz = EXCLUDED.gfz,
            contribution_status = EXCLUDED.contribution_status,
            source_reference_url = EXCLUDED.source_reference_url,
            anwert = EXCLUDED.anwert,
            verfahrensart = EXCLUDED.verfahrensart,
            geom = EXCLUDED.geom,
            updated_at = CURRENT_TIMESTAMP;
    """

    processed = 0

    try:
        with connection.transaction():
            with connection.cursor() as cursor:
                for record in records:
                    geometry = record["geometry"]

                    if geometry is None or geometry.is_empty:
                        raise ValueError(
                            "Cannot insert a record with empty geometry."
                        )

                    if not geometry.is_valid:
                        raise ValueError(
                            "Cannot insert a record with invalid geometry."
                        )

                    if geometry.geom_type != "MultiPolygon":
                        raise ValueError(
                            "Expected MultiPolygon geometry."
                        )

                    cursor.execute(
                        insert_sql,
                        (
                            record["source_feature_id"],
                            record["zone_id"],
                            record["land_value"],
                            record["valuation_date"],
                            record["district"],
                            record["land_use"],
                            record["gfz"],
                            record["contribution_status"],
                            record["source_reference_url"],
                            record["anwert"],
                            record["verfahrensart"],
                            bytes(geometry.wkb),
                        ),
                    )

                    processed += 1

        logger.info(
            "Database insert completed. Processed: %s",
            processed,
        )

        return {
            "processed": processed,
            "failed": 0,
        }

    except Exception:
        logger.exception(
            "Database upsert failed. Transaction rolled back."
        )
        raise
