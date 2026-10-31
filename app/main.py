
import logging

from app.config import settings
from app.ingestion.wfs_client import WFSClient
from app.ingestion.pagination import fetch_all_feature_collection
from app.transformation.field_mapper import map_feature
from app.transformation.geometry import (
    extract_geojson_crs,
    process_geometry,
)
from app.validation.validators import validate_records
from app.database.connection import (
    get_connection,
    verify_destination,
)
from app.database.repository import upsert_records


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_ingestion():
    logger.info("Starting TASK-CRE-11 land value ingestion.")

    # 1. Extract
    client = WFSClient()
    collection = fetch_all_feature_collection(client)
    features = collection["features"]

    logger.info("Extracted %s source features.", len(features))

    # 2. Verify the declared source CRS
    source_crs = extract_geojson_crs(collection)

    logger.info("Source CRS verified: %s", source_crs)

    # 3. Transform
    transformed_records = []
    transformation_failures = []

    for index, feature in enumerate(features):
        try:
            record = map_feature(feature)

            record["geometry"] = process_geometry(
                record["geometry"],
                source_crs,
            )

            transformed_records.append(record)

        except Exception as exc:
            logger.error(
                "Transformation failed for feature %s: %s",
                feature.get("id", index),
                exc,
            )

            transformation_failures.append({
                "feature_id": feature.get("id", str(index)),
                "error": str(exc),
            })

    # 4. Validate
    valid_records, rejected_records = validate_records(
        transformed_records
    )

    # 5. Load
    connection = get_connection()

    try:
        verify_destination(connection)

        # Commit the read-only verification transaction.
        # This ensures the repository starts its own transaction.
        connection.commit()

        result = upsert_records(
            connection,
            valid_records,
        )

    finally:
        connection.close()

    # 6. Report
    report = {
        "source_features": len(features),
        "transformation_failures": len(transformation_failures),
        "validation_rejections": len(rejected_records),
        "valid_records": len(valid_records),
        "processed_records": result["processed"],
        "failed_records": (
            len(transformation_failures)
            + len(rejected_records)
        ),
    }

    logger.info("INGESTION SUMMARY: %s", report)

    return report


if __name__ == "__main__":
    try:
        run_ingestion()
    except Exception:
        logger.exception("Ingestion pipeline failed.")
        raise
