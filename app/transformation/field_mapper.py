# Covert the raw GeoJSON to python dictionary


from datetime import date

#Decimal provides better precision when representing decimal values
from decimal import Decimal, InvalidOperation 

from typing import Any


def parse_decimal(value: Any, field_name: str) -> Decimal | None:
    """Convert a source value into Decimal, preserving null values."""

    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError(f"{field_name} cannot be a boolean")

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid numeric value for {field_name}: {value}"
        ) from exc


def parse_date(value: Any, field_name: str) -> date | None:
    """Convert an ISO date string into a Python date."""

    if value is None:
        return None

    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid date for {field_name}: {value}"
        ) from exc


def clean_string(value: Any) -> str | None:
    """Remove surrounding whitespace while preserving null values."""

    if value is None:
        return None

    return str(value).strip() or None


def map_feature(feature: dict) -> dict:
    """
    Transform a raw BORIS GeoJSON feature into our internal data model.
    """

    if not isinstance(feature, dict):
        raise ValueError("Feature must be a dictionary")

    if feature.get("type") != "Feature":
        raise ValueError("Expected a GeoJSON Feature")

    properties = feature.get("properties")

    if not isinstance(properties, dict):
        raise ValueError("Feature properties must be a dictionary")

    return {
        # Source identifiers
        "source_feature_id": clean_string(feature.get("id")),
        "zone_id": clean_string(properties.get("brwid")),

        # Land valuation information
        "land_value": parse_decimal(
            properties.get("brw"), "brw"
        ),
        "valuation_date": parse_date(
            properties.get("stichtag"), "stichtag"
        ),

        # Location and land use
        "district": clean_string(properties.get("bezirk")),
        "land_use": clean_string(properties.get("nutzung")),

        # Additional valuation attributes
        "gfz": parse_decimal(
            properties.get("gfz"), "gfz"
        ),
        "contribution_status": clean_string(
            properties.get("beitragszustand")
        ),

        # Optional source information
        "source_reference_url": clean_string(
            properties.get("lumnum")
        ),
        "anwert": parse_decimal(
            properties.get("anwert"), "anwert"
        ),
        "verfahrensart": clean_string(
            properties.get("verfahrensart")
        ),

        # Geometry is processed separately
        "geometry": feature.get("geometry"),
    }
