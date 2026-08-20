"""Fixture matrix for the FR-010 Azure SQL Database compatibility check.

FR-010's acceptance test requires the check to fail "on a fixture containing each
prohibited pattern". These tests are that fixture matrix, executed on every run so
the check cannot silently stop working — the failure mode that let two required CI
checks pass without doing anything (Step 102).

The clean-control test matters as much as the violation tests: a check that flags
legitimate SQL gets disregarded, and a disregarded check is no check at all.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "governance" / "scripts" / "check_cloud_target_compatibility.py"
FIXTURES = ROOT / "tests" / "fixtures" / "cloud_compat"
VIOLATIONS = sorted((FIXTURES / "violations").glob("*.sql"))


def run_check(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECK), str(target)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def test_fixture_set_is_present() -> None:
    """Absent fixtures must fail loudly rather than vacuously passing the matrix.

    Without this, deleting the fixtures would leave the parametrised test with an
    empty argument list and a green run.
    """
    assert VIOLATIONS, "violation fixtures are missing — the matrix would pass vacuously"
    assert (FIXTURES / "clean_azure_safe.sql").is_file()


@pytest.mark.parametrize("fixture", VIOLATIONS, ids=lambda p: p.stem)
def test_violation_fixture_fails(fixture: Path) -> None:
    r = run_check(fixture)
    assert r.returncode == 1, f"{fixture.name} should FAIL but exited {r.returncode}\n{r.stdout}"
    assert "RESULT: FAIL" in r.stdout
    assert "SQL files scanned: 1" in r.stdout, "the file must actually be read, not skipped"


def test_clean_fixture_passes() -> None:
    """Blocked constructs named in comments and string literals must not trip it."""
    r = run_check(FIXTURES / "clean_azure_safe.sql")
    assert r.returncode == 0, f"clean fixture produced false positives:\n{r.stdout}"
    assert "SQL files scanned: 1" in r.stdout


def test_same_database_and_tempdb_three_part_names_allowed() -> None:
    """Microsoft: three-part names for the current database and tempdb are supported.

    Flagging every three-part name would be the false-positive that makes a check
    get ignored.
    """
    r = run_check(FIXTURES / "clean_azure_safe.sql")
    assert "CROSS-DATABASE" not in r.stdout


def test_absent_scope_is_declared_not_assumed() -> None:
    """An empty scope must announce itself as absent-expected, not pass silently."""
    r = run_check(ROOT / "tests" / "fixtures" / "cloud_compat" / "does_not_exist")
    assert r.returncode == 0
    assert "ABSENT-EXPECTED" in r.stdout
