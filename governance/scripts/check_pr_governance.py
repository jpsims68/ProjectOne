#!/usr/bin/env python3
"""
Governance check — PR carries required governance metadata (Step 67).
Reads the PR body and refuses a merge that omits classification, evidence honesty,
recovery, or deferral declaration.

Usage: python3 check_pr_governance.py <pr_body_file>
Exit 0 = clean. Exit 1 = violation.
"""
import re, sys, pathlib

body = pathlib.Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else ""
low = body.lower()
viol = []

m = re.search(r"\*\*risk class:\*\*\s*(R[1-4])", body, re.I)
if not m:
    viol.append("Risk class missing or not one of R1..R4 — classification precedes implementation")
risk = m.group(1).upper() if m else None

if not re.search(r"\*\*basis:\*\*\s*\S", body, re.I):
    viol.append("Risk basis empty — which triggers fired, and which higher-class conditions were checked?")

if not re.search(r"\|\s*\S+.*\|.*http|\|\s*\S+.*\|\s*\S+\s*\|", body):
    if "no evidence" not in low:
        viol.append("Evidence table appears empty — a description of a result is not evidence")

if "[x] every criterion reported pass was actually examined" not in low:
    viol.append("Evidence-honesty attestation not checked (non-waivable invariant)")

if not re.search(r"\*\*recovery class:\*\*\s*(ROLLBACK|ROLL_FORWARD|CONTAINMENT|NOT_RECOVERABLE_BY_DESIGN)", body, re.I):
    viol.append("Recovery class missing — recovery is part of completion, not a postscript")

if not re.search(r"\[x\].*deferral|\[x\].*deferred", low):
    viol.append("Design deferral declaration missing — an undeclared deferral is treated as structural")

if risk in ("R3", "R4"):
    if not re.search(r"\*\*mechanism used:\*\*\s*(SEPARATE_INVOCATION_CLEAN_CONTEXT|DETERMINISTIC_NONJUDGMENTAL_CHECK|HUMAN_REVIEW|DIFFERENT_MODEL_OR_MODEL_FAMILY)", body, re.I):
        viol.append(f"{risk} requires a declared independence mechanism — a role label alone never qualifies")
if risk == "R4":
    if not re.search(r"DETERMINISTIC_NONJUDGMENTAL_CHECK", body, re.I):
        viol.append("R4 requires a deterministic check in addition to independent judgment")
    if not re.search(r"\*\*approved by / date:\*\*\s*\S", body, re.I):
        viol.append("R4 requires recorded human approval — never inferred from silence or elapsed time")

print("=" * 72)
print("GOVERNANCE CHECK — pull request metadata")
print("=" * 72)
print(f"declared risk class: {risk or 'MISSING'}")
if viol:
    print(f"\n{len(viol)} VIOLATION(S):")
    for v in viol:
        print(f"  ! {v}")
    print("\nRESULT: FAIL")
    sys.exit(1)
print("\nRESULT: PASS — required governance metadata present")
sys.exit(0)
