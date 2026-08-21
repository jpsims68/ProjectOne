#!/usr/bin/env python3
"""
BOOTSTRAP SELF-TEST — prove every gate can actually fail.

Run this once at setup, and again any time you change a check.

WHY THIS EXISTS
A governance check that has never failed is not known to work. In the project
this framework came from, three separate checks were found passing while
examining nothing:

  * a test gate globbing `tests/**/*.py` — bash has no globstar by default, so
    it matched nothing, printed "no tests yet", and passed
  * pip-audit pointed at a requirements file that did not exist
  * bandit pointed at directories that did not exist

All three were green for weeks. Green CI meant nothing, and nobody knew.

WHAT THIS DOES
For each check, it deliberately breaks the thing that check is supposed to
catch, confirms the check FAILS, then restores the original state and confirms
the check PASSES again. A check that passes while its target is broken is
reported as DEFECTIVE.

It writes only into a temporary sandbox copy. Your repository is not modified.

USAGE
    python3 scripts/bootstrap_selftest.py

Exit 0 = every gate proved it can go red. Exit 1 = at least one cannot.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Installed layout is governance/scripts/, so the repository root is two levels up.
# This matches the assumption every other check makes; keep them aligned.
ROOT = Path(__file__).resolve().parents[2]

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def run_check(sandbox: Path, script: str) -> int:
    """Run a governance check inside the sandbox and return its exit code."""
    return subprocess.run(
        [sys.executable, str(sandbox / "governance" / "scripts" / script)],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
    ).returncode


# --- Breakage functions -----------------------------------------------------
# Each returns a short description of the damage it did.


def break_baseline(sandbox: Path) -> str:
    target = sandbox / "governance" / "framework" / "SHA256SUMS.txt"
    first = next(
        line.split("  ", 1)[1].strip()
        for line in target.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    victim = sandbox / "governance" / "framework" / first
    victim.write_bytes(victim.read_bytes() + b"\n# tampered\n")
    return f"appended a byte to frozen file {first}"


def break_secrets(sandbox: Path) -> str:
    (sandbox / "leaked_config.py").write_text("password = supersecretvalue123\n", encoding="utf-8")
    return "committed an unquoted credential assignment"


def break_layout(sandbox: Path) -> str:
    (sandbox / "PROJECTONE-Profile.json").write_text("{}", encoding="utf-8")
    return "placed a governance artifact loose at the repository root"


def break_cloud_compat(sandbox: Path) -> str:
    d = sandbox / "db"
    d.mkdir(exist_ok=True)
    (d / "tampered.sql").write_text(
        "USE [mvp];\nEXEC msdb.dbo.sp_add_job @job_name = N'X';\n", encoding="utf-8"
    )
    return "added SQL using USE and SQL Server Agent, neither of which exists on Azure SQL Database"


CHECKS = [
    ("check_baseline_integrity.py", break_baseline, "frozen framework is intact"),
    ("check_no_secrets.py", break_secrets, "no credentials are committed"),
    ("check_repository_layout.py", break_layout, "governance artifacts are placed correctly"),
    ("check_cloud_target_compatibility.py", break_cloud_compat, "SQL runs on Azure SQL Database"),
]


def main() -> int:
    print("=" * 72)
    print("BOOTSTRAP SELF-TEST — proving each gate can go red")
    print("=" * 72)
    print(f"{DIM}Working in a temporary copy. Your repository is not modified.{RESET}\n")

    failures: list[str] = []

    for script, breaker, guards in CHECKS:
        print(f"{script}")
        print(f"{DIM}  guards: {guards}{RESET}")

        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp) / "repo"
            shutil.copytree(
                ROOT,
                sandbox,
                ignore=shutil.ignore_patterns(
                    ".git", ".venv", "__pycache__", "*.pyc", ".mypy_cache", ".pytest_cache"
                ),
            )

            # 1. Clean state must PASS. If it does not, the check is
            #    misconfigured and the negative test below proves nothing.
            clean = run_check(sandbox, script)
            if clean != 0:
                print(f"  {RED}MISCONFIGURED{RESET} — fails on a clean tree (exit {clean})")
                print(f"{DIM}    Fix this first. A check that fails on clean input cannot")
                print(f"    tell you anything about broken input.{RESET}\n")
                failures.append(f"{script}: fails on clean tree")
                continue
            print(f"  {GREEN}PASS{RESET} on clean tree")

            # 2. Broken state must FAIL. This is the part that matters.
            damage = breaker(sandbox)
            broken = run_check(sandbox, script)
            print(f"{DIM}  broke it: {damage}{RESET}")

            if broken == 0:
                print(f"  {RED}DEFECTIVE{RESET} — PASSED while its target was broken\n")
                failures.append(f"{script}: passes while broken")
            else:
                print(f"  {GREEN}FAIL{RESET} on broken tree (exit {broken}) — gate proved\n")

    print("=" * 72)
    if failures:
        print(f"{RED}RESULT: {len(failures)} gate(s) NOT PROVEN{RESET}\n")
        for f in failures:
            print(f"  ! {f}")
        print("\nA gate that cannot go red is not protecting you. Do not rely on")
        print("green CI until every gate here passes this test.")
        return 1

    print(f"{GREEN}RESULT: every gate proved it can go red{RESET}")
    print("\nThis says the gates WORK. It does not say they are SUFFICIENT —")
    print("that depends on whether you have written checks for the things that")
    print("actually matter on your project.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
