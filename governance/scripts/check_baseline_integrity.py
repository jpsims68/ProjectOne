#!/usr/bin/env python3
"""
Governance check — framework baseline integrity. FAIL-CLOSED.

DEFECT HISTORY (F-R9-01): the previous version of this check was inline shell:

    if [ -f governance/framework/SHA256SUMS.txt ]; then verify; else echo "skipping"; fi

That fails OPEN. When 137 framework files were committed to the repository ROOT instead
of governance/framework/, the manifest was not at the expected path, the check silently
skipped, and reported SUCCESS while verifying nothing. A green tick asserted the approved
baseline was intact when the check had not looked at a single file.

A control that reports PASS without examining anything is worse than no control: it
manufactures false assurance. This version distinguishes three states explicitly.

States:
  ABSENT_EXPECTED   - baseline dir absent AND repo has no framework content  -> PASS (genuine scaffold stage)
  ABSENT_UNEXPECTED - framework content exists somewhere but not at the expected path -> FAIL
  PRESENT           - verify every hash -> PASS only if all match

Exit 0 = clean. Exit 1 = violation.
"""

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "governance" / "framework"
SUMS = BASE / "SHA256SUMS.txt"

# Fingerprints of framework content. If these exist ANYWHERE in the repo, the framework
# has been committed and MUST be verifiable at the expected path.
FINGERPRINTS = [
    "paf.common.schema.json",
    "PAF-Framework-Specification-*.md",
    "ROLE_ORCHESTRATOR.json",
    "PAF-Frozen-Baseline-*.json",
]

print("=" * 72)
print("GOVERNANCE CHECK — framework baseline integrity (fail-closed)")
print("=" * 72)

found_anywhere = []
for pat in FINGERPRINTS:
    for p in ROOT.rglob(pat):
        if ".git" in p.parts:
            continue
        found_anywhere.append(p.relative_to(ROOT))

if not SUMS.exists():
    if found_anywhere:
        print("\nSTATE: ABSENT_UNEXPECTED")
        print(
            f"\nFramework content IS present in this repository ({len(found_anywhere)} matching files),"
        )
        print(
            "but the baseline manifest is NOT at the expected path:\n  governance/framework/SHA256SUMS.txt"
        )
        print("\nExamples of misplaced framework files:")
        for p in sorted(found_anywhere)[:8]:
            print(f"  ! {p}")
        print("\nThis is the signature of a flattened or misplaced upload. The baseline cannot")
        print("be verified, so this check FAILS rather than skipping. Refusing to report PASS")
        print("on an unexamined baseline.")
        print("\nRESULT: FAIL")
        sys.exit(1)
    print("\nSTATE: ABSENT_EXPECTED")
    print("\nNo framework content committed yet and no baseline manifest. Genuine scaffold stage.")
    print("\nRESULT: PASS")
    sys.exit(0)

print("\nSTATE: PRESENT — verifying every hash in the manifest")

# Hashing is done in-process with hashlib rather than by shelling out to
# `sha256sum`. That external tool does not exist on Windows, so the previous
# implementation raised an unhandled FileNotFoundError on the owner's machine:
# a check that is supposed to be the fail-closed guard on the frozen framework
# produced a stack trace instead of a verdict. It exited non-zero, so it failed
# closed by accident rather than by design. Verified identical results on both
# platforms: 87/87 files, same PASS/FAIL behaviour on a tampered manifest.
expected = 0
ok = 0
bad: list[str] = []
for line in SUMS.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    expected += 1
    digest, _, name = line.partition("  ")
    name = name.strip()
    if not name:
        bad.append(f"{line} — unparseable manifest line")
        continue
    target = BASE / name
    if not target.is_file():
        bad.append(f"{name}: MISSING")
        continue
    h = hashlib.sha256()
    with target.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    if h.hexdigest() == digest.strip():
        ok += 1
    else:
        bad.append(f"{name}: FAILED — content does not match the approved hash")

print(f"\nfiles in manifest: {expected}")
print(f"verified OK:       {ok}")

if bad or ok != expected:
    print(f"\n{len(bad)} PROBLEM(S):")
    for line in bad[:15]:
        print(f"  ! {line}")
    print("\nThe approved frozen baseline has been altered, or files are missing.")
    print("Any change to the baseline requires a governed change package and a new version.")
    print("\nRESULT: FAIL")
    sys.exit(1)

print("\nRESULT: PASS — approved baseline intact, all hashes match")
sys.exit(0)
