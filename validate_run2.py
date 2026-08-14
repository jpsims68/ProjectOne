#!/usr/bin/env python3
"""
PAF Run 2 — Static Validation (Steps 11-20)
Deterministic, non-judgmental check (AI-3).
Reproduce: python3 validation/validate_run2.py   |  Exit 0 = all pass.
"""
import json, sys, pathlib, collections
from jsonschema import Draft202012Validator, RefResolver

ROOT = pathlib.Path(__file__).resolve().parent.parent
SC = ROOT/"framework"/"schemas"; CON = ROOT/"framework"/"contracts"
WF = ROOT/"framework"/"workflows"; MX = ROOT/"framework"/"matrices"
store = {f.name: json.load(open(f)) for f in SC.glob("*.json")}
roles = {p.stem: json.loads(p.read_text()) for p in CON.glob("*.json")}
flows = {p.stem: json.loads(p.read_text()) for p in WF.glob("*.json")}
res = []
def ck(cid, d, ok, det=""): res.append((cid, d, "PASS" if ok else "FAIL", det))

def val(schema_name, objs):
    s = store[schema_name]
    v = Draft202012Validator(s, resolver=RefResolver(base_uri="", referrer=s, store=store))
    bad = []
    for name, o in objs.items():
        for e in list(v.iter_errors(o))[:1]:
            bad.append(f"{name}:{'/'.join(str(p) for p in e.path)}")
    return bad

ck("R2-01", "All 16 role contracts present", len(roles) == 16, f"found {len(roles)}")
ck("R2-02", "All role contracts validate", not val("paf.role-contract.schema.json", roles), "; ".join(val("paf.role-contract.schema.json", roles)[:4]))
ck("R2-03", "All workflows validate", not val("paf.workflow.schema.json", flows), "; ".join(val("paf.workflow.schema.json", flows)[:4]))

# No role may review its own work
ck("R2-04", "No role contract permits reviewing its own work",
   all(r["independenceProfile"]["mayReviewOwnWork"] is False for r in roles.values()))
selfrev = [rid for rid, r in roles.items() if rid in r["independenceProfile"]["providesIndependentReviewFor"]]
ck("R2-05", "No role lists itself as its own independent reviewer", not selfrev, str(selfrev))

# Implementation roles must not hold merge/release/admin
IMPL = [rid for rid, r in roles.items() if "IMPLEMENTATION" in r.get("roleClass", [])]
viol = []
for rid in IMPL:
    g = {p["permission"]: p["grant"] for p in roles[rid]["toolPermissions"]}
    for perm in ("VCS_MERGE", "VCS_ADMIN", "RELEASE_EXECUTE"):
        if g.get(perm) == "ALLOWED": viol.append(f"{rid}:{perm}")
ck("R2-06", "No implementation role holds merge/admin/release privilege", not viol, str(viol))

# Production data + secrets denied to every role
pv = []
for rid, r in roles.items():
    g = {p["permission"]: p["grant"] for p in r["toolPermissions"]}
    for perm in ("DB_PRODUCTION_ACCESS", "SECRET_READ", "EVIDENCE_AMEND"):
        if g.get(perm) != "DENIED": pv.append(f"{rid}:{perm}={g.get(perm)}")
ck("R2-07", "Production data, secrets, and evidence amendment denied to ALL roles", not pv, str(pv))

# Every role declares an independence mechanism for its review scopes
nomech = [rid for rid, r in roles.items() if not r["independenceProfile"]["requiredMechanisms"]]
ck("R2-08", "Every role declares required independence mechanism(s)", not nomech, str(nomech))

# Agent judgment alone never satisfies independence
vem = json.load(open(ROOT/"framework"/"models"/"verification-execution-model.json"))
bad = [m["mechanismType"] for m in vem["mechanismTypes"] if not m["isDeterministic"] and m["satisfiesIndependenceAlone"]]
ck("R2-09", "No non-deterministic mechanism claims to satisfy independence alone", not bad, str(bad))

# Every gate closes through an authority interface, never agent assertion
gm = json.load(open(MX/"gate-matrix.json"))
badg = [g["gateId"] for g in gm["gates"] if not g["closureAuthority"]]
ck("R2-10", "Every gate declares at least one closure authority", not badg, str(badg))
ck("R2-11", "Gate matrix is non-empty and covers every workflow",
   {g["workflowId"] for g in gm["gates"]} == set(flows), "")

# Independence-required gates must not be exception-eligible
conflict = [g["gateId"] for g in gm["gates"] if g["independenceRequired"] and g["exceptionEligible"]]
ck("R2-12", "No gate is both independence-required and exception-eligible", not conflict, str(conflict))

# Human-approval gates must name an approval category
noappr = [g["gateId"] for g in gm["gates"] if "HUMAN_APPROVAL" in g["closureAuthority"] and not g.get("humanApprovalCategoryRef")]
ck("R2-13", "Every human-approval gate names an approval category", not noappr, str(noappr))

# Authority graph acyclic
dm = json.load(open(MX/"dependency-map.json"))
ck("R2-14", "Role review/authority graph is acyclic (no mutual self-approval)", dm["acyclic"], str(dm["authorityCyclesDetected"]))

# Tool permission matrix fails closed
tm = json.load(open(MX/"role-tool-permission-matrix.json"))
ck("R2-15", "Tool permission matrix default is DENIED (CR-5)", tm["defaultGrant"] == "DENIED")
ck("R2-16", "Tool matrix covers every role", set(tm["grid"]) == set(roles))

# Evidence traceability both directions
em = json.load(open(MX/"evidence-matrix.json"))
orphan = [k for k, v in em["evidence"].items() if not v["requiredByGates"] and not v["producedByRoles"]]
ck("R2-17", "No evidence class is fully orphaned", not orphan, str(orphan[:5]))
unproduced = [k for k, v in em["evidence"].items() if v["requiredByGates"] and not v["producedByRoles"]]
ck("R2-18", "Bidirectional traceability closed: every gate-required evidence class has a producer",
   not unproduced, str(unproduced[:6]))
declared = sum(1 for v in em["evidence"].values() if v.get("declaredProducerRoles"))
ck("R2-21", "Producer basis is visible (declared vs derived recorded separately)",
   all("declaredProducerRoles" in v and "derivedProducerRoles" in v for v in em["evidence"].values()),
   f"{declared} declared in role contracts, {len(em['evidence'])-declared} derived by stage-owner rule")

# Ownership: no orphans
om = json.load(open(MX/"ownership-matrix.json"))
noown = [e["entityId"] for e in om["entities"] if not e.get("steward") or not e.get("reviewPath")]
ck("R2-19", "Every framework artifact has a steward and review path", not noown, str(noown[:4]))

# SR-1 portability holds after Run 2
FORB = ["projectone","project one","delphics","anthropic","claude","chatgpt","openai","github","celonis","pm4py","fastapi","cytoscape"]
leaks = []
for f in (ROOT/"framework").rglob("*"):
    if f.is_file():
        low = f.read_text(errors="ignore").lower()
        leaks += [f"{f.relative_to(ROOT)}:{t}" for t in FORB if t in low]
ck("R2-20", "SR-1 portability holds across all Run 2 artifacts", not leaks, str(leaks[:5]))

fails = sum(1 for r in res if r[2] == "FAIL")
print("="*78); print("PAF RUN 2 — STATIC VALIDATION (Steps 11-20)"); print("="*78)
for cid, d, st, det in res:
    print(f"[{st}] {cid}  {d}")
    if det and (st == "FAIL" or cid == "R2-21"): print(f"        {det}")
print("-"*78); print(f"RESULT: {len(res)-fails}/{len(res)} checks passed"); print("="*78)
sys.exit(1 if fails else 0)
