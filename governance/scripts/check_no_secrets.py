#!/usr/bin/env python3
"""
Governance check — secret_protection (global non-waivable invariant).
Refuses committed secret VALUES. Configuration may reference secret NAMES only.
Exit 0 = clean. Exit 1 = violation.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATTERNS = [
    (
        r"(?i)\b(aws_secret_access_key|aws_access_key_id)\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{16,}",
        "AWS credential",
    ),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained token"),
    (r"sk-[A-Za-z0-9]{20,}", "API secret key"),
    (r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "private key"),
    (
        r"(?i)\b(password|passwd|secret|api_key|apikey|token)\b\s*[:=]\s*['\"][^'\"$\{\s]{8,}['\"]",
        "hardcoded credential",
    ),
    # DEFECT F-R10-01: the quoted-value pattern above misses UNQUOTED assignments,
    # which is exactly the .env / dotenv format — the single most likely place a real
    # secret would appear. Found when a test .env containing a password passed cleanly.
    (
        r"(?i)^\s*[A-Z0-9_]*(PASSWORD|PASSWD|SECRET|API_KEY|APIKEY|TOKEN|PRIVATE_KEY)[A-Z0-9_]*\s*=\s*[^\s$\{<#\n][^\s]{5,}",
        "unquoted credential assignment",
    ),
    (
        r"(?i)(Server|Data Source)=.+;\s*(Password|Pwd)=[^;'\"]{4,}",
        "connection string with password",
    ),
]
ALLOW = re.compile(
    r"(\$\{|\$\(|process\.env|os\.environ|<[A-Z_]+>|CHANGEME|EXAMPLE|placeholder|\bREPLACE_ME\b)",
    re.I,
)
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "governance",
    # Tool caches are gitignored build artefacts, not repository content. Scanning
    # them produced false positives locally after any mypy/pytest/ruff run, which
    # trains the reader to disregard a real finding. CI never sees them (fresh
    # checkout), so this only ever misfired on the owner's machine.
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    ".tox",
    "dist",
    "build",
}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2"}

hits = []

# A committed .env is a violation regardless of contents. .env.example is the template
# and carries NAMES only; every other file in that family holds VALUES.
for p in ROOT.rglob(".env*"):
    if p.is_file() and ".git" not in p.parts and p.name != ".env.example":
        hits.append(
            f"{p.relative_to(ROOT)} — .env file committed; only .env.example may be tracked"
        )

for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix in SKIP_SUFFIX:
        continue
    if any(d in p.parts for d in SKIP_DIRS):
        continue
    try:
        text = p.read_text(errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if ALLOW.search(line):
            continue
        for pat, label in PATTERNS:
            if re.search(pat, line):
                hits.append(f"{p.relative_to(ROOT)}:{i} — possible {label}")
                break

print("=" * 72)
print("GOVERNANCE CHECK — secret protection (global non-waivable invariant)")
print("=" * 72)
if hits:
    print(f"\n{len(hits)} POSSIBLE SECRET(S) COMMITTED:")
    for h in hits[:25]:
        print(f"  ! {h}")
    print("\nSecrets are never committed, never logged, never placed in a configuration surface.")
    print("Configuration carries secret NAMES; values arrive at runtime through injection.")
    print("\nRESULT: FAIL")
    sys.exit(1)
print("\nRESULT: PASS — no committed secret values detected")
sys.exit(0)
