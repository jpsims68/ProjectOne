#!/usr/bin/env python3
"""
Governance check — VSA-3 slice boundary enforcement.
Cross-slice import is a BUILD FAILURE, not a review comment.

Rules enforced:
  1. A slice may not import another slice directly. Cross-slice dependency is permitted
     only through /contracts (explicit, versioned, directional, acyclic).
  2. /platform may not import a slice. Dependency direction is one-way.
  3. Every slice directory must contain a valid slice.manifest.json.
  4. Declared contract dependencies must resolve and must not form a cycle.

Exit 0 = clean. Exit 1 = violation.
"""

import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
SLICES, PLATFORM, CONTRACTS = ROOT / "slices", ROOT / "platform", ROOT / "contracts"
SRC = {".py", ".ts", ".tsx", ".js", ".jsx"}
viol = []


def sources(base):
    return [p for p in base.rglob("*") if p.is_file() and p.suffix in SRC] if base.exists() else []


slice_names = sorted(d.name for d in SLICES.iterdir() if d.is_dir()) if SLICES.exists() else []

# Rule 3 — every slice carries a manifest
manifests = {}
for name in slice_names:
    mf = SLICES / name / "slice.manifest.json"
    if not mf.exists():
        viol.append(
            f"[VSA-1] slices/{name}: missing slice.manifest.json — a slice without a manifest is ungoverned code"
        )
        continue
    try:
        m = json.loads(mf.read_text())
        manifests[name] = m
    except Exception as e:
        viol.append(f"[VSA-1] slices/{name}/slice.manifest.json is not valid JSON: {e}")
        continue
    for field in (
        "sliceId",
        "ownerRole",
        "consumedContracts",
        "producedContracts",
        "lifecycleState",
        "riskClass",
    ):
        if field not in m:
            viol.append(f"[VSA-1] slices/{name}: manifest missing required field '{field}'")

# Rule 1 — no direct cross-slice import
for name in slice_names:
    for f in sources(SLICES / name):
        text = f.read_text(errors="ignore")
        for other in slice_names:
            if other == name:
                continue
            if re.search(
                rf"(from|import|require\()\s*['\"]?[\w./]*slices[./]{re.escape(other)}\b", text
            ):
                viol.append(
                    f"[VSA-3] {f.relative_to(ROOT)} imports slice '{other}' directly — cross-slice dependency must go through /contracts"
                )

# Rule 2 — platform must not depend on a slice
for f in sources(PLATFORM):
    text = f.read_text(errors="ignore")
    for name in slice_names:
        if re.search(
            rf"(from|import|require\()\s*['\"]?[\w./]*slices[./]{re.escape(name)}\b", text
        ):
            viol.append(
                f"[VSA-3] {f.relative_to(ROOT)} imports slice '{name}' — platform may never depend on a slice (one-way direction)"
            )

# Rule 4 — declared contracts resolve, and the graph is acyclic
produced = {}
for name, m in manifests.items():
    for c in m.get("producedContracts", []):
        cid = c if isinstance(c, str) else c.get("contractId")
        produced.setdefault(cid, []).append(name)
graph = defaultdict(set)
for name, m in manifests.items():
    for c in m.get("consumedContracts", []):
        cid = c if isinstance(c, str) else c.get("contractId")
        if cid not in produced and CONTRACTS.exists() and not any(CONTRACTS.rglob(f"{cid}*")):
            viol.append(
                f"[VSA-3] slices/{name}: consumes contract '{cid}' which is not produced by any slice and has no definition in /contracts"
            )
        for owner in produced.get(cid, []):
            if owner != name:
                graph[name].add(owner)

WHITE, GREY, BLACK = 0, 1, 2
color = defaultdict(int)


def dfs(n, path):
    color[n] = GREY
    for m in graph[n]:
        if color[m] == GREY:
            viol.append(
                f"[VSA-3] contract dependency CYCLE: {' -> '.join([*path, n, m])} — dependencies must be acyclic"
            )
        elif color[m] == WHITE:
            dfs(m, [*path, n])
    color[n] = BLACK


for n in list(graph):
    if color[n] == WHITE:
        dfs(n, [])

print("=" * 72)
print("GOVERNANCE CHECK — slice boundaries (VSA-1 / VSA-3)")
print("=" * 72)
print(
    f"slices found: {len(slice_names)}  {slice_names if slice_names else '(none yet — scaffold stage)'}"
)
if viol:
    print(f"\n{len(viol)} VIOLATION(S):")
    for v in viol:
        print(f"  ! {v}")
    print("\nRESULT: FAIL")
    sys.exit(1)
print("\nRESULT: PASS — no boundary violations")
sys.exit(0)
