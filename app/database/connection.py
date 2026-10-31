#connect the Python application to PostgreSQL/PostGIS


import logging

import psycopg

from app.config import settings

logger = logging.getLogger(__name__)


def get_connection():
    """
    Establish a connection to PostgreSQL.

    No database writes are performed by this function.
    """

    if not settings.db_uri:
        raise ValueError(
            "DB_URI is missing. Configure it in your .env file."
        )

    # Enforce the assignment's staging-only restriction.
    if settings.db_schema != "iris_staging":
        raise ValueError(
            "Database operations are restricted to iris_staging."
        )

    logger.info("Connecting to PostgreSQL...")

    try:
        connection = psycopg.connect(
            settings.db_uri,
            connect_timeout=10,
            application_name="TASK-CRE-11-BORIS-Ingestion",
        )

        logger.info("PostgreSQL connection established.")

        return connection

    except psycopg.Error as exc:
        logger.error("Database connection failed: %s", exc)
        raise RuntimeError(
            "Unable to connect to PostgreSQL."
        ) from exc


def verify_destination(connection):
    """
    Verify that the configured staging schema and target table exist.

    This function performs read-only queries.
    """

    if settings.db_schema != "iris_staging":
        raise ValueError("Only iris_staging is permitted.")

    if not settings.db_table:
        raise ValueError(
            "DB_TABLE is missing. Confirm the target table name first."
        )

    with connection.cursor() as cursor:

        # Verify the staging schema.
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.schemata
                WHERE schema_name = %s
            );
            """,
            (settings.db_schema,),
        )

        schema_exists = cursor.fetchone()[0]

        if not schema_exists:
            raise RuntimeError(
                f"Schema {settings.db_schema} does not exist."
            )

        # Verify the destination table.
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name = %s
                  AND table_type = 'BASE TABLE'
            );
            """,
            (settings.db_schema, settings.db_table),
        )

        table_exists = cursor.fetchone()[0]

        if not table_exists:
            raise RuntimeError(
                f"Table {settings.db_schema}.{settings.db_table} "
                "does not exist."
            )

    logger.info(
        "Destination verified: %s.%s",
        settings.db_schema,
        settings.db_table,
    )
