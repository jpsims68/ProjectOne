#!/usr/bin/env python3
"""
Repository bootstrap — canonical Step 103.

Brings a local environment to the intended baseline state and reports evidence.
Canonical Step 103 says "execute approved bootstrap only; record failures and
evidence." Until now no bootstrap script existed, so the step was performed by
hand with nothing to point at afterwards. This is the thing to run.

WHAT IT DOES
  1. Verifies the interpreter against pyproject requires-python
  2. Verifies every tool the build depends on is present and reports its version
  3. Reports local environment readiness (.env present, and correctly untracked)
  4. Runs every governance check and reports the result

WHAT IT DOES NOT DO
It changes nothing. It installs nothing, writes nothing, and touches no
database. It reports. If something needs fixing, it tells you and exits
non-zero; it does not fix it for you, because a bootstrap that silently repairs
its own preconditions hides the fact that they were wrong.

USAGE
    uv run python governance/scripts/bootstrap.py
"""

import pathlib
import shutil
import subprocess
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]

CHECKS = [
    "check_repository_layout.py",
    "check_baseline_integrity.py",
    "check_no_secrets.py",
    "check_slice_boundaries.py",
    "check_cloud_target_compatibility.py",
    "check_overlay_reachability.py",
]

# Tools the build depends on. Version ranges are governed by the technology
# registry; this reports what is present so a mismatch is visible, and does not
# duplicate the registry's ranges here — two sources of truth would drift.
TOOLS = [
    ("python", [sys.executable, "--version"]),
    ("uv", ["uv", "--version"]),
    ("git", ["git", "--version"]),
    ("node", ["node", "--version"]),
    ("ruff", ["ruff", "--version"]),
    ("mypy", ["mypy", "--version"]),
    ("pytest", ["pytest", "--version"]),
]


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "not found"
    except subprocess.SubprocessError as exc:
        return 1, str(exc)


def main() -> int:
    print("=" * 72)
    print("REPOSITORY BOOTSTRAP — canonical Step 103")
    print("=" * 72)
    failures: list[str] = []

    # --- 1. Interpreter -----------------------------------------------------
    print("\n[1] Interpreter")
    pyproject = tomllib.load((ROOT / "pyproject.toml").open("rb"))
    required = pyproject["project"]["requires-python"]
    actual = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"    requires-python : {required}")
    print(f"    running         : {actual}")
    if sys.version_info[:2] != (3, 13):
        failures.append(f"interpreter is {actual}; pyproject requires {required}")
        print("    MISMATCH — the declared range is not what is running")
    else:
        print("    OK")

    # --- 2. Toolchain -------------------------------------------------------
    print("\n[2] Toolchain")
    for name, cmd in TOOLS:
        if cmd[0] != sys.executable and shutil.which(cmd[0]) is None:
            print(f"    {name:<8} NOT FOUND")
            failures.append(f"{name} not on PATH")
            continue
        code, out = run(cmd)
        first = out.splitlines()[0] if out else "(no output)"
        print(f"    {name:<8} {first[:58]}")
        if code != 0:
            failures.append(f"{name} did not report a version")

    # --- 3. Local environment ----------------------------------------------
    print("\n[3] Local environment")
    env_file = ROOT / ".env"
    if env_file.exists():
        code, out = run(["git", "ls-files", "--error-unmatch", "--", ".env"])
        if code == 0:
            print("    .env  PRESENT but TRACKED IN GIT — this is a secret-protection failure")
            failures.append(".env is tracked in git")
        else:
            print("    .env  present and correctly untracked")
    else:
        # Absent-expected, stated rather than assumed. CI never has one.
        print("    .env  ABSENT — expected in CI; required locally for Step 108")
        print("          copy .env.example to .env and fill in local values")

    # --- 4. Governance checks ----------------------------------------------
    print("\n[4] Governance checks")
    for c in CHECKS:
        path = ROOT / "governance" / "scripts" / c
        if not path.exists():
            print(f"    {c:<38} MISSING")
            failures.append(f"{c} is missing")
            continue
        code, out = run([sys.executable, str(path)])
        verdict = "PASS" if code == 0 else "FAIL"
        print(f"    {c:<38} {verdict}")
        if code != 0:
            failures.append(f"{c} failed")

    # --- Summary ------------------------------------------------------------
    print("\n" + "=" * 72)
    if failures:
        print(f"RESULT: FAIL — {len(failures)} problem(s)\n")
        for f in failures:
            print(f"  ! {f}")
        print("\nFix these before treating the local environment as baseline.")
        return 1

    print("RESULT: PASS — local environment is at the intended baseline state")
    print("\nThis says the environment is READY. It does not say the gates WORK —")
    print("run bootstrap_selftest.py to prove each gate can go red.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
