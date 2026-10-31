# Submission Documentation

This directory contains supporting documentation and evidence for **TASK-CRE-11 – Berlin BORIS Land Value Data Ingestion**.

The files in this directory describe the source-to-target data mapping, provide sample ingestion output, document validation results, and demonstrate how the ingestion process is restricted to the `iris_staging` schema.

## Contents

| File | Description |
|---|---|
| `output_sample.json` | Provides a representative example of a transformed land value zone record, showing the structure of the data prepared for storage. |
| `schema_mapping.md` | Documents how fields from the source WFS GeoJSON response are mapped to columns in the PostgreSQL staging table, including data type conversions and coordinate reference system transformation. |
| `validation_results.md` | Records the results of ingestion validation, including source feature counts, transformation failures, rejected records, database write results, and test outcomes. |
| `evidence.sql` | Contains SQL queries used to verify the staging table, stored record counts, geometry types, coordinate reference systems, data validity, and duplicate records. |
| `limitations.md` | Documents known limitations, assumptions, source availability issues, and decisions made during implementation. |

## Implementation Notes

- The ingestion process is designed to write only to the `iris_staging` schema.
- Spatial geometries are transformed to **EPSG:25832** before persistence.
- Source attributes are mapped and validated before database insertion.
- Records are inserted or updated using an idempotent upsert strategy.
- Supporting SQL queries are provided to independently verify the stored data.

## Verification

The evidence and validation documents should be reviewed alongside the application source code and test results. Reported ingestion counts and database results reflect actual execution results, rather than expected or estimated values.

