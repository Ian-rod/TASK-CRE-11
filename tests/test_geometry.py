
from shapely.geometry import Polygon, mapping
from pyproj import CRS

from app.transformation.geometry import process_geometry


# A small square in the source CRS (EPSG:25833).
polygon = Polygon([
    (378000, 5825000),
    (378100, 5825000),
    (378100, 5825100),
    (378000, 5825100),
    (378000, 5825000),
])

geojson_geometry = mapping(polygon)

result = process_geometry(
    geometry_data=geojson_geometry,
    declared_source_crs="urn:ogc:def:crs:EPSG::25833",
)

print("GEOMETRY PROCESSING SUCCESSFUL")
print("--------------------------------")

print("Geometry type:", result.geom_type)
print("Is valid:", result.is_valid)
print("Is empty:", result.is_empty)
print("Number of polygons:", len(result.geoms))

assert result.geom_type == "MultiPolygon"
assert result.is_valid
assert not result.is_empty
assert len(result.geoms) == 1

print("\nAll geometry checks passed!")
