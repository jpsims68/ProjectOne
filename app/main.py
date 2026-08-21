"""Minimal application shell — canonical Step 109.

WHAT THIS IS
The smallest thing that can be said to start. It exposes one health endpoint and
nothing else: no database access, no business logic, no models, no mining.

WHAT THIS IS NOT
This is NOT F1a and NOT the first vertical slice. Production application
implementation remains NOT AUTHORIZED until explicit owner authorization at
canonical Step 112. Step 109 sits in the Baseline Validation block and says
plainly: "do not treat this as feature acceptance."

WHY A SHELL EARNS ITS PLACE
Until now nothing outside a test had ever imported app.config. A shell that
starts proves three things a passing test suite does not: the package imports,
configuration resolves from the environment, and the approved web framework is
wired correctly. If any of those is broken, better to find out here than inside
the first real feature.

DELIBERATELY NO DATABASE ACCESS
Canonical Step 108 validates database connectivity separately. Combining them
would make a failure ambiguous — you would not know whether the shell or the
database was at fault. Health reports that the application started, not that its
dependencies are reachable.

RUNNING IT
    uv run uvicorn app.main:app --reload
    curl http://127.0.0.1:8000/health
"""

from typing import Any

from fastapi import FastAPI

from app import __version__

app = FastAPI(
    title="ProjectOne",
    version=__version__,
    description="Baseline shell. Not a feature surface.",
)


@app.get("/health")
def health() -> dict[str, Any]:
    """Report that the application started and configuration resolved.

    Settings are constructed HERE rather than at import time. Importing this
    module must not require a populated .env — otherwise the test suite, the
    linter and any tooling that merely imports the app would fail on a machine
    that has not been configured yet. Configuration failure should surface when
    configuration is actually needed, and it should say so plainly.

    The handler is deliberately synchronous. It performs no I/O, and a sync
    handler can be called directly in a test without an event loop.
    """
    status = "ok"
    env = "unconfigured"
    config_loaded = False

    try:
        from app.config import Settings

        settings = Settings()  # type: ignore[call-arg]
        env = settings.env
        config_loaded = True
    except Exception as exc:
        # Startup does not fail here, but the response says so honestly. A health
        # endpoint that reports "ok" while configuration is broken is worse than
        # one that reports the problem.
        status = "degraded"
        env = f"configuration error: {type(exc).__name__}"

    return {
        "status": status,
        "version": __version__,
        "environment": env,
        "configurationLoaded": config_loaded,
        "note": "Baseline shell only. No feature surface is implemented.",
    }
