
from datetime import date
from decimal import Decimal

from shapely.geometry import Polygon, MultiPolygon

from app.validation.validators import (
    validate_record,
    validate_records,
)


def create_valid_record(zone_id="1002"):
    polygon = Polygon([
        (378000, 5825000),
        (378100, 5825000),
        (378100, 5825100),
        (378000, 5825100),
        (378000, 5825000),
    ])

    return {
        "zone_id": zone_id,
        "land_value": Decimal("400"),
        "valuation_date": date(2026, 1, 1),
        "district": "Spandau",
        "land_use": "W - Wohngebiet",
        "gfz": Decimal("0.7"),
        "geometry": MultiPolygon([polygon]),
    }


def test_valid_record():
    record = create_valid_record()

    errors = validate_record(record)

    assert errors == []


def test_missing_zone_id():
    record = create_valid_record()
    record["zone_id"] = None

    errors = validate_record(record)

    assert "Missing required field: zone_id" in errors


def test_negative_land_value():
    record = create_valid_record()
    record["land_value"] = Decimal("-400")

    errors = validate_record(record)

    assert "Land value must be finite and non-negative" in errors


def test_missing_geometry():
    record = create_valid_record()
    record["geometry"] = None

    errors = validate_record(record)

    assert "Geometry is missing" in errors


def test_duplicate_zone_date():
    records = [
        create_valid_record("1002"),
        create_valid_record("1002"),
    ]

    valid, rejected = validate_records(records)

    assert len(valid) == 1
    assert len(rejected) == 1
    assert any(
        "Duplicate zone/date key" in error
        for error in rejected[0]["errors"]
    )
