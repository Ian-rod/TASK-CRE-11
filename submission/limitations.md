# Limitations, Assumptions and Data Considerations

## 1. Source endpoint availability

The originally specified endpoint:

`https://gdi.berlin.de/services/wfs/boris`

was not successfully accessed during development.

An alternative endpoint was used for development:

`https://gdi.berlin.de/services/wfs/brw2026`

Layer:

`brw2026:brw2026_vector`

This endpoint returned a GeoJSON FeatureCollection containing 1,623 features in the observed run. It is an alternative dataset and has not been confirmed as an approved replacement for the originally specified BORIS endpoint.

The use of this alternative endpoint should therefore be treated as a development assumption pending confirmation.

## 2. Coordinate reference systems

The observed source response declared EPSG:25833. The application verifies the declared CRS and transforms geometries into the required EPSG:25832.

The application does not assume that all future source responses will use the same CRS.

## 3. Attribute assumptions

The source attributes were mapped according to their observed values and names.

The `anwert` attribute initially appeared to be numeric based on limited sample observations. A larger extraction revealed categorical values including `EU`, `N` and `SU`. The implementation was changed to preserve this field as text.

The semantic meaning and complete value domain of some source attributes should be confirmed against authoritative service documentation.

## 4. Database assumptions

A local PostgreSQL 16 / PostGIS 3.4 database was created for development.

The table `iris_staging.berlin_land_value_zones` and its constraints are candidate-defined. They are not represented as the client's confirmed production or shared staging DDL.

The source feature ID is used as the unique upsert key. Its stability across future dataset releases should be verified.

No production database credentials or client portfolio data are included.

## 5. Data licensing and usage

The applicable licence and redistribution conditions for the Berlin land value data were not independently verified during implementation.

The data is used for this technical ingestion exercise. Redistribution or commercial reuse should be checked against the source provider's applicable licence and terms.

## 6. Valuation limitations

Land value zone figures are official valuation-related data, not guaranteed transaction prices or individual property valuations.

The imported values should not be interpreted as a substitute for a property-specific valuation, professional advice or current market assessment.

The valuation date (`stichtag`) is retained to distinguish the applicable valuation period.

## 7. External service dependencies

The ingestion depends on the availability, response format, pagination behaviour and rate limits of the external WFS service.

The alternative `/brw2026` endpoint was accessible during development, but future availability and service behaviour have not been guaranteed.

Network failures, unexpected response formats and incomplete pagination are treated as ingestion errors rather than silently accepted as complete imports.
