"""Step 99-100 — toolchain smoke test.

Proves the local environment is genuinely wired up: the interpreter is the expected
version, dependencies resolve, configuration validates, and the database is reachable.

Deliberately narrow. This verifies the TOOLCHAIN, not the product. No product code
exists; production application implementation is NOT AUTHORIZED.
"""

import os
import sys
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_python_version_matches_approved_range() -> None:
    """Approved range is >=3.13,<3.14 (technology registry, CP-005)."""
    assert sys.version_info[:2] == (3, 13), (
        f"Expected Python 3.13.x, found {sys.version.split()[0]}. "
        "The technology registry pins >=3.13,<3.14."
    )


@pytest.mark.smoke
def test_approved_dependencies_import() -> None:
    """Every runtime dependency in the registry must actually import."""
    import fastapi  # noqa: F401
    import pydantic  # noqa: F401
    import pyodbc  # noqa: F401
    import uvicorn  # noqa: F401


@pytest.mark.smoke
def test_odbc_driver_18_present() -> None:
    """ODBC Driver 18 is the approved driver (technology registry)."""
    import pyodbc

    drivers = pyodbc.drivers()
    assert any("ODBC Driver 18 for SQL Server" in d for d in drivers), (
        f"ODBC Driver 18 for SQL Server not found. Available: {drivers}"
    )


@pytest.mark.smoke
def test_configuration_loads_and_validates() -> None:
    """Configuration must validate at startup, or fail loudly.

    Skips when .env is absent so a fresh clone does not fail before setup.
    """
    if not Path(".env").exists():
        pytest.skip(".env not present — copy .env.example to .env and fill in local values")

    from app.config import Settings

    settings = Settings()  # type: ignore[call-arg]
    assert settings.db_connection_string, "Connection string must not be empty"
    assert settings.db_name, "Database name must not be empty"


@pytest.mark.smoke
def test_database_reachable() -> None:
    """The local instance must be reachable using the configured connection.

    Uses Windows Integrated Authentication locally — no credential is stored anywhere.
    """
    if not Path(".env").exists():
        pytest.skip(".env not present — copy .env.example to .env and fill in local values")

    import pyodbc

    from app.config import Settings

    settings = Settings()  # type: ignore[call-arg]
    with pyodbc.connect(settings.db_connection_string, timeout=10) as conn:
        row = conn.cursor().execute("SELECT @@VERSION;").fetchone()
    assert row is not None
    assert "SQL Server" in row[0]


@pytest.mark.smoke
def test_no_product_implementation_exists() -> None:
    """Guard: production application implementation is NOT AUTHORIZED.

    This test is expected to be REMOVED at the authorized implementation step. Its
    presence is a standing reminder that the authorization gate has not been passed.
    """
    assert not Path("slices").is_dir() or not any(
        f.endswith(".py") for _, _, files in os.walk("slices") for f in files
    ), "Product code found under slices/ — implementation is not yet authorized"
