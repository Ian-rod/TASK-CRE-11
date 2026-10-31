
from datetime import date
from decimal import Decimal

import pytest
from shapely.geometry import MultiPolygon, Polygon

from app.config import settings
from app.database.connection import get_connection
from app.database.repository import upsert_records


@pytest.fixture
def db_connection():
    if settings.db_schema != "iris_staging":
        pytest.fail("Tests must only use iris_staging.")

    if settings.db_table != "berlin_land_value_zones":
        pytest.fail("Unexpected database table.")

    connection = get_connection()

    try:
        yield connection
    finally:
        connection.close()


def make_record(source_feature_id, land_value):
    polygon = Polygon([
        (390000, 5810000),
        (390100, 5810000),
        (390100, 5810100),
        (390000, 5810100),
        (390000, 5810000),
    ])

    return {
        "source_feature_id": source_feature_id,
        "zone_id": "TEST-001",
        "land_value": Decimal(str(land_value)),
        "valuation_date": date(2026, 1, 1),
        "district": "Test District",
        "land_use": "W - Wohngebiet",
        "gfz": Decimal("0.7"),
        "contribution_status": None,
        "source_reference_url": None,
        "anwert": None,
        "verfahrensart": None,
        "geometry": MultiPolygon([polygon]),
    }


def delete_test_record(connection, source_feature_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM iris_staging.berlin_land_value_zones
            WHERE source_feature_id = %s;
            """,
            (source_feature_id,),
        )
    connection.commit()


def test_insert_and_update_are_idempotent(db_connection):
    source_id = "TEST-REPOSITORY-001"

    try:
        first_record = make_record(source_id, 400)

        result = upsert_records(db_connection, [first_record])

        assert result["processed"] == 1

        # Re-ingest the same source feature with an updated value.
        updated_record = make_record(source_id, 650)

        result = upsert_records(db_connection, [updated_record])

        assert result["processed"] == 1

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*), MAX(land_value)
                FROM iris_staging.berlin_land_value_zones
                WHERE source_feature_id = %s;
                """,
                (source_id,),
            )

            count, land_value = cursor.fetchone()

        assert count == 1
        assert land_value == Decimal("650.00")

    finally:
        delete_test_record(db_connection, source_id)


def test_failed_batch_is_rolled_back(db_connection):
    source_id = "TEST-REPOSITORY-002"

    valid_record = make_record(source_id, 400)

    invalid_record = make_record(
        "TEST-REPOSITORY-003",
        500,
    )
    invalid_record["geometry"] = None

    try:
        with pytest.raises(ValueError, match="empty geometry"):
            upsert_records(
                db_connection,
                [valid_record, invalid_record],
            )

        with db_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM iris_staging.berlin_land_value_zones
                WHERE source_feature_id IN (%s, %s);
                """,
                (source_id, "TEST-REPOSITORY-003"),
            )

            count = cursor.fetchone()[0]

        assert count == 0

    finally:
        delete_test_record(db_connection, source_id)
        delete_test_record(db_connection, "TEST-REPOSITORY-003")
