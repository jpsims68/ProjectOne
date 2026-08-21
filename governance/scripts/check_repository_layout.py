#!/usr/bin/env python3
"""
Governance check — repository layout. Refuses flattened or misplaced uploads.

DEFECT HISTORY (F-R9-02): a browser folder-upload silently discarded directory paths and
committed 137 governance files to the repository root. Nothing detected it; the baseline
check skipped and reported green. Detection depended entirely on the owner asking for a
manual comparison.

This check makes that failure mode structurally detectable.

Rules:
  1. Only an allowlisted set of files may sit at the repository root.
  2. Files whose names identify them as governance/framework artifacts must live under
     governance/ — never at the root, never in an unexpected directory.

Exit 0 = clean. Exit 1 = violation.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

ALLOWED_ROOT = {
    "README.md",
    ".gitignore",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    ".ruff.toml",
    "package.json",
    "package-lock.json",
    ".editorconfig",
    ".gitattributes",
    # Added Steps 92-100: environment variable TEMPLATE — carries NAMES only.
    # ".env" itself is deliberately NOT allowed here and is refused outright by
    # check_no_secrets.py, because it carries VALUES.
    ".env.example",
    "uv.lock",
    "vite.config.ts",
    "tsconfig.json",
    "index.html",
}

# Names that identify governance/framework artifacts wherever they appear.
GOVERNED_PATTERNS = [
    r"^paf\..*\.json$",
    r"^PAF-.*\.(json|md)$",
    r"^ROLE_.*\.json$",
    r"^WF_.*\.json$",
    r"^PROJECTONE-.*\.json$",
    r"^SHA256SUMS\.txt$",
    r"^CP-\d+.*\.json$",
    r".*-matrix\.json$",
    r"^paf_engine\.py$",
    r"^validate_run\d\.py$",
    r"^run_(all_validation|dryrun|regression|replay)\.py$",
    r"^(conformance_probe|activation_checkpoint|assess_verification_readiness)\.py$",
]

viol = []


def tracked_by_git(rel: str) -> bool:
    """Is this path actually in the repository?

    This check exists to catch files COMMITTED to the wrong place — the signature
    of an upload that lost its directory structure. An untracked local file is not
    that. A developer's .env is required to run the application and the
    local-environment tests, and it is correctly git-ignored; flagging it made the
    check fail permanently on the owner's machine for a legitimate state.

    Fail-closed: if git cannot answer, treat the file as tracked and flag it.
    """
    try:
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return True


for p in sorted(ROOT.iterdir()):
    if p.is_file() and p.name not in ALLOWED_ROOT and tracked_by_git(p.name):
        viol.append(f"[LAYOUT] '{p.name}' is at the repository root — not an allowed root file")

for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or ".git" in p.parts:
        continue
    rel = p.relative_to(ROOT)
    if any(re.match(pat, p.name) for pat in GOVERNED_PATTERNS) and rel.parts[0] != "governance":
        viol.append(f"[LAYOUT] governance artifact outside governance/: {rel}")

print("=" * 72)
print("GOVERNANCE CHECK — repository layout")
print("=" * 72)
root_files = [p.name for p in ROOT.iterdir() if p.is_file()]
print(f"files at repository root: {len(root_files)}")

if viol:
    uniq = sorted(set(viol))
    print(f"\n{len(uniq)} VIOLATION(S) (showing up to 20):")
    for v in uniq[:20]:
        print(f"  ! {v}")
    if len(uniq) > 20:
        print(f"  ... and {len(uniq) - 20} more")
    print("\nThis is the signature of an upload that lost its directory structure.")
    print("Fix the upload; do not commit files to the root to make the check pass.")
    print("\nRESULT: FAIL")
    sys.exit(1)

print("\nRESULT: PASS — layout correct")
sys.exit(0)
