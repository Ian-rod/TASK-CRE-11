# To check required fields such as zone_id, land_value and valuation_date
#Valid numeric values,dates,
# Non-empty district and land-use values,Valid non-empty MultiPolygon geometry,
# Duplicate zone identifiers within the same valuation date


from datetime import date
from decimal import Decimal
from shapely.geometry import MultiPolygon

from app.config import settings


def validate_record(record: dict) -> list[str]:
    """
    Validate one transformed BORIS record.

    Returns a list of validation errors.
    An empty list means the record passed validation.
    """

    errors = []

    # Check required attributes.
    required_fields = [
        "zone_id",
        "land_value",
        "valuation_date",
        "district",
        "land_use",
    ]

    for field in required_fields:
        value = record.get(field)

        if value is None or value == "":
            errors.append(f"Missing required field: {field}")

    # Validate land value.
    land_value = record.get("land_value")

    if land_value is not None:
        if not isinstance(land_value, Decimal):
            errors.append("Land value must be a Decimal")
        elif not land_value.is_finite() or land_value < 0:
            errors.append("Land value must be finite and non-negative")

    # Validate valuation date.
    valuation_date = record.get("valuation_date")

    if valuation_date is not None:
        if not isinstance(valuation_date, date):
            errors.append("Valuation date must be a date object")

    # Validate GFZ when supplied.
    gfz = record.get("gfz")

    if gfz is not None:
        if not isinstance(gfz, Decimal):
            errors.append("GFZ must be a Decimal")
        elif not gfz.is_finite() or gfz < 0:
            errors.append("GFZ must be finite and non-negative")

    # Validate geometry.
    geometry = record.get("geometry")

    if geometry is None:
        errors.append("Geometry is missing")

    elif not isinstance(geometry, MultiPolygon):
        errors.append("Geometry must be a MultiPolygon")

    else:
        if geometry.is_empty:
            errors.append("Geometry is empty")

        if not geometry.is_valid:
            errors.append("Geometry is invalid")

    return errors


def validate_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Validate multiple records and detect duplicate zone/date keys.

    Returns:
        valid_records: Records accepted for loading.
        rejected_records: Records rejected with their error messages.
    """

    valid_records = []
    rejected_records = []

    seen_keys = set()

    for record in records:
        errors = validate_record(record)

        # Check the proposed composite key.
        zone_id = record.get("zone_id")
        valuation_date = record.get("valuation_date")

        if zone_id is not None and valuation_date is not None:
            record_key = (zone_id, valuation_date)

            if record_key in seen_keys:
                errors.append(
                    f"Duplicate zone/date key: {record_key}"
                )
            else:
                seen_keys.add(record_key)

        if errors:
            rejected_records.append({
                "record": record,
                "errors": errors,
            })
        else:
            valid_records.append(record)

    return valid_records, rejected_records
