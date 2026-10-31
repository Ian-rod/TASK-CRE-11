#Spatial geometry processing 
#source data uses EPSG:25833 but we need EPSG:25832


import logging

from pyproj import CRS, Transformer
from shapely import make_valid
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import transform, unary_union

from app.config import settings

logger = logging.getLogger(__name__)


def extract_geojson_crs(data: dict) -> str:
    """
    Extract the declared CRS from a GeoJSON FeatureCollection.

    We fail if the CRS is missing rather than guessing.
    """

    crs_data = data.get("crs")

    if not isinstance(crs_data, dict):
        raise ValueError("GeoJSON response does not declare a CRS")

    properties = crs_data.get("properties", {})
    crs_name = properties.get("name")

    if not crs_name:
        raise ValueError("GeoJSON CRS name is missing")

    return crs_name


def extract_polygons(geometry) -> list[Polygon]:
    """
    Extract polygon components from Polygon, MultiPolygon,
    or GeometryCollection results.
    """

    if isinstance(geometry, Polygon):
        return [geometry]

    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)

    if hasattr(geometry, "geoms"):
        polygons = []

        for part in geometry.geoms:
            polygons.extend(extract_polygons(part))

        return polygons

    return []

#Validate and repair it.
def process_geometry(
    geometry_data: dict,
    declared_source_crs: str,
) -> MultiPolygon:
    """
    Validate, repair and transform a GeoJSON geometry.

    Output: MultiPolygon in the configured target CRS.
    """

    if not isinstance(geometry_data, dict):
        raise ValueError("Geometry must be a GeoJSON dictionary")

    # Verify the actual source CRS against our configuration.
    source_crs = CRS.from_user_input(declared_source_crs)
    expected_crs = CRS.from_user_input(settings.source_crs)

    if source_crs != expected_crs:
        raise ValueError(
            f"Unexpected source CRS: {source_crs}. "
            f"Expected {expected_crs}."
        )

    # Convert GeoJSON into a Shapely geometry.
    try:
        geom = shape(geometry_data)
    except Exception as exc:
        raise ValueError("Unable to parse GeoJSON geometry") from exc

    if geom.is_empty:
        raise ValueError("Geometry is empty")

    # Repair invalid geometries.
    if not geom.is_valid:
        logger.warning("Invalid geometry encountered. Attempting repair.")
        geom = make_valid(geom)

    if geom.is_empty:
        raise ValueError("Geometry became empty after repair")

    # Extract polygonal components.
    polygons = extract_polygons(geom)

    if not polygons:
        raise ValueError(
            "Geometry contains no polygonal components after repair"
        )

    if len(polygons) != len(
        getattr(geom, "geoms", [geom])
    ):
        logger.warning(
            "Non-polygonal geometry components were excluded during normalization"
        )

    # Combine components into a valid polygonal geometry.
    merged = unary_union(polygons)

    if merged.is_empty or not merged.is_valid:
        raise ValueError("Polygon geometry is invalid after normalization")

    # Ensure the final geometry is a MultiPolygon.
    if isinstance(merged, Polygon):
        geom = MultiPolygon([merged])
    elif isinstance(merged, MultiPolygon):
        geom = merged
    else:
        raise ValueError(
            f"Unexpected geometry type after normalization: "
            f"{merged.geom_type}"
        )

    # Transform coordinates to the target CRS.(EPSG:25833 -> EPSG:25832)
    transformer = Transformer.from_crs(
        source_crs,
        CRS.from_user_input(settings.target_crs),
        always_xy=True,
    )

    geom = transform(transformer.transform, geom)

    if geom.is_empty or not geom.is_valid:
        raise ValueError("Geometry is invalid after CRS transformation")

    logger.debug(
        "Geometry processed successfully: %s",
        geom.geom_type,
    )

    return geom
