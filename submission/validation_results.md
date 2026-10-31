# Validation and Test Results

**Project:** TASK-CRE-11 – Berlin Land Value Zone Ingestion

## Test coverage

| Test | Purpose | Result |
|---|---|---|
| WFS extraction | Retrieve GeoJSON features from the configured WFS endpoint | Pending final recorded run |
| Pagination | Retrieve features across multiple pages | 1,623 features observed in one run |
| CRS validation | Verify the declared source CRS | EPSG:25833 observed |
| CRS transformation | Convert geometries to EPSG:25832 | Implemented; final test evidence pending |
| Geometry validation | Reject empty or invalid geometries after repair attempts | Implemented; final test evidence pending |
| Field mapping | Map source properties to internal records | Initial issue found with `anwert`; corrected to preserve string values |
| Database connection | Connect to local PostgreSQL/PostGIS | Connection established in application logs |
| Idempotency | Update an existing record instead of duplicating it | Test implemented; retain actual pytest output |
| Transaction rollback | Roll back a batch after an invalid record | Test implemented; retain actual pytest output |
| Staging isolation | Restrict database operations to `iris_staging` | Implemented; verify configuration and SQL destination |

## Observed extraction and transformation run

One application run reported:

- Source features retrieved: 1,623
- Transformation failures: 64
- Valid records: 1,559
- Validation rejections: 0
- Database records processed: 1,559

The 64 transformation failures were caused by treating the source `anwert` attribute as numeric when the source returned categorical values such as `EU`, `N` and `SU`.

The field mapping was subsequently changed to preserve `anwert` as text.

## Final database results

Complete this section after a successful ingestion and SQL verification:

- Final source feature count: [actual count]
- Transformation failures: [actual count]
- Validation rejections: [actual count]
- Database row count: [actual count]
- Invalid geometries in database: [actual count]
- Duplicate source identifiers: [actual count]
- Idempotency test: [PASS/FAIL]
- Transaction rollback test: [PASS/FAIL]

Attach the actual pytest output and SQL verification output when submitting.
