#!/usr/bin/env python3
"""
Governance check — secret_protection (global non-waivable invariant).
Refuses committed secret VALUES. Configuration may reference secret NAMES only.
Exit 0 = clean. Exit 1 = violation.
"""
import re, sys, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATTERNS = [
    (r"(?i)\b(aws_secret_access_key|aws_access_key_id)\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{16,}", "AWS credential"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained token"),
    (r"sk-[A-Za-z0-9]{20,}", "API secret key"),
    (r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----", "private key"),
    (r"(?i)\b(password|passwd|secret|api_key|apikey|token)\b\s*[:=]\s*['\"][^'\"$\{\s]{8,}['\"]", "hardcoded credential"),
    (r"(?i)(Server|Data Source)=.+;\s*(Password|Pwd)=[^;'\"]{4,}", "connection string with password"),
]
ALLOW = re.compile(r"(\$\{|\$\(|process\.env|os\.environ|<[A-Z_]+>|CHANGEME|EXAMPLE|placeholder|\bREPLACE_ME\b)", re.I)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "governance"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2"}

hits = []
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
