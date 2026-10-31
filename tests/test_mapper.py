
from datetime import date
from decimal import Decimal

from app.transformation.field_mapper import map_feature


sample_feature = {
    "type": "Feature",
    "id": "brw2026_vector.1002",
    "properties": {
        "brwid": "1002",
        "brw": 400,
        "bezirk": "Spandau",
        "nutzung": "W - Wohngebiet",
        "stichtag": "2026-01-01",
        "gfz": 0.7,
        "beitragszustand": "Beitragsfrei nach BauGB",
        "lumnum": None,
        "anwert": None,
        "verfahrensart": None
    },
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": []
    }
}


mapped = map_feature(sample_feature)

print("MAPPING SUCCESSFUL")
print("-------------------")

for key, value in mapped.items():
    print(f"{key}: {value}")

# Basic assertions
assert mapped["zone_id"] == "1002"
assert mapped["land_value"] == Decimal("400")
assert mapped["valuation_date"] == date(2026, 1, 1)
assert mapped["district"] == "Spandau"
assert mapped["gfz"] == Decimal("0.7")
assert mapped["anwert"] is None

print("\nAll mapping checks passed!")
