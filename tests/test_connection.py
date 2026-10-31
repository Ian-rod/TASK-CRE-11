
import pytest

from app.database.connection import get_connection


def test_database_uri_is_required(monkeypatch):
    monkeypatch.setattr(
        "app.database.connection.settings.db_uri",
        "",
    )

    with pytest.raises(ValueError, match="DB_URI is missing"):
        get_connection()


def test_only_staging_schema_is_allowed(monkeypatch):
    monkeypatch.setattr(
        "app.database.connection.settings.db_uri",
        "postgresql://iris_user:iris_password@localhost:5433/iris_dev",
    )

    monkeypatch.setattr(
        "app.database.connection.settings.db_schema",
        "iris_core",
    )

    with pytest.raises(ValueError, match="Only iris_staging"):
        get_connection()
