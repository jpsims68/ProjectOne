"""Application shell tests — canonical Step 109.

Step 109 requires that "the local application shell starts without bypassing
gates." These tests prove the shell is importable and its one endpoint responds,
without needing a running server or a configured machine.

Deliberately NOT tested here: that the shell serves over HTTP. That is proven by
the owner running uvicorn locally, which is what Step 109 actually asks for. A
test that spawns a server would add a dependency and a flake source to prove
something a single command already demonstrates.
"""

from pathlib import Path

import pytest

from app import __version__
from app.main import app, health


def test_shell_imports_without_configuration() -> None:
    """Importing the app must not require a populated .env.

    If it did, the linter, the type checker and every test would fail on a
    machine that has not been configured yet — and CI, which correctly has no
    .env, could never import the application at all.
    """
    assert app.title == "ProjectOne"
    assert app.version == __version__


def test_health_route_is_registered() -> None:
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    assert "/health" in paths


def test_health_reports_honestly_when_unconfigured() -> None:
    """Without configuration the shell must say so, not claim to be healthy.

    A health endpoint reporting "ok" while configuration is broken is worse than
    one reporting the problem — it converts a loud failure into a silent one.
    """
    if Path(".env").exists():
        pytest.skip(".env present — the unconfigured path cannot be exercised here")

    r = health()
    assert r["status"] == "degraded"
    assert r["configurationLoaded"] is False
    assert "error" in r["environment"].lower()


@pytest.mark.local_env
def test_health_reports_ok_when_configured() -> None:
    """With a local .env the shell reports ok and the environment name resolves."""
    if not Path(".env").exists():
        pytest.skip(".env not present — copy .env.example to .env and fill in local values")

    r = health()
    assert r["status"] == "ok"
    assert r["configurationLoaded"] is True
    assert r["environment"]


def test_shell_declares_it_is_not_a_feature_surface() -> None:
    """Guard against scope creep.

    Step 109 says explicitly: do not treat this as feature acceptance. If this
    assertion is ever removed to accommodate new routes, that is the moment
    someone should ask whether Step 112 authorization has been obtained.
    """
    r = health()
    assert "no feature surface" in r["note"].lower()

    paths = {r.path for r in app.routes if hasattr(r, "path")}
    non_doc = {p for p in paths if not p.startswith(("/docs", "/redoc", "/openapi"))}
    assert non_doc == {"/health"}, f"shell has grown beyond a health endpoint: {non_doc}"
