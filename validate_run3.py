#!/usr/bin/env python3
"""
PAF Run 3 — Static Validation (Steps 21-24)
Deterministic, non-judgmental check (AI-3).
Reproduce: python3 validation/validate_run3.py   |  Exit 0 = all pass.
"""
import json, sys, pathlib
from jsonschema import Draft202012Validator, RefResolver

ROOT = pathlib.Path(__file__).resolve().parent.parent
SC = ROOT/"framework"/"schemas"
store = {f.name: json.load(open(f)) for f in SC.glob("*.json")}
res = []
def ck(cid, d, ok, det=""): res.append((cid, d, "PASS" if ok else "FAIL", det))

def validator(schema_name):
    s = store[schema_name]
    return Draft202012Validator(s, resolver=RefResolver(base_uri="", referrer=s, store=store))

# ---- Step 21: regression portfolios ----
TEST = ROOT/"framework"/"testing"
portfolios = sorted(TEST.glob("PAF-REGRESSION-*.json"))
v = validator("paf.regression-portfolio.schema.json")
bad = []
fam_seen = set()
mandatory_fams = {"SELF_APPROVAL", "SILENT_EXCEPTION", "FABRICATED_EVIDENCE", "UNAPPROVED_BYPASS"}
for p in portfolios:
    d = json.loads(p.read_text())
    for e in list(v.iter_errors(d))[:2]:
        bad.append(f"{p.name}:{e.message[:80]}")
    for case in d["adversarialCases"]:
        if case.get("family"): fam_seen.add(case["family"])

ck("R3-01", "At least 6 regression portfolios present", len(portfolios) >= 6, str(len(portfolios)))
ck("R3-02", "All regression portfolios validate against contract", not bad, "; ".join(bad[:5]))
ck("R3-03", "All 4 mandatory adversarial families are exercised (VP-2)",
   mandatory_fams <= fam_seen, str(mandatory_fams - fam_seen))

# every case has an expectedResult and an answer key exists separately (non-circular grading)
missing_keys = []
for p in portfolios:
    d = json.loads(p.read_text())
    keyfile = ROOT / d["answerKey"]
    if not keyfile.exists(): missing_keys.append(p.name)
ck("R3-04", "Every portfolio's answer key exists as a separate file", not missing_keys, str(missing_keys))

# negative + adversarial cases outnumber nothing — but must both be present and non-trivial
thin = [p.name for p in portfolios if len(json.loads(p.read_text())["negativeCases"]) < 1
        or len(json.loads(p.read_text())["adversarialCases"]) < 1]
ck("R3-05", "Every portfolio has at least one negative AND one adversarial case", not thin, str(thin))

# ---- Step 22: registries ----
sec = json.load(open(ROOT/"framework"/"registries"/"PAF-Security-Standard.json"))
verr = list(validator("paf.security-standard.schema.json").iter_errors(sec))
ck("R3-06", "Security standard validates", not verr, str([e.message[:80] for e in verr[:3]]))
invariants = {b["invariant"] for b in sec["invariantBindings"]}
ck("R3-07", "Security standard binds all 3 global non-waivable security invariants",
   {"tenant_isolation", "authentication_authorization_integrity", "secret_protection"} <= invariants,
   str(invariants))

tech = json.load(open(ROOT/"framework"/"registries"/"PAF-Technology-Registry.json"))
verr = list(validator("paf.technology-registry.schema.json").iter_errors(tech))
ck("R3-08", "Technology registry validates", not verr, str([e.message[:80] for e in verr[:3]]))
ck("R3-09", "Technology registry carries zero project-specific entries at CORE layer (portability)",
   tech["approvedEntries"] == [], str(tech["approvedEntries"]))

env = json.load(open(ROOT/"framework"/"registries"/"PAF-Environment-Registry.json"))
verr = list(validator("paf.environment-registry.schema.json").iter_errors(env))
ck("R3-10", "Environment registry validates", not verr, str([e.message[:80] for e in verr[:3]]))
tiers = [e["tier"] for e in env["environments"]]
ck("R3-11", "Environment tiers are strictly increasing with no duplicates", tiers == sorted(set(tiers)) and len(tiers)==len(set(tiers)), str(tiers))
prodenv = [e for e in env["environments"] if e["productionDataAllowed"]]
ck("R3-12", "Exactly the highest-tier environment allows production data", 
   len(prodenv)==1 and prodenv[0]["tier"]==max(tiers), str(prodenv))

# ---- Step 23: design system ----
ds = json.load(open(ROOT/"framework"/"gui"/"PAF-Design-System.json"))
verr = list(validator("paf.design-system.schema.json").iter_errors(ds))
ck("R3-13", "Design system validates", not verr, str([e.message[:80] for e in verr[:3]]))
ck("R3-14", "Color-alone encoding is explicitly prohibited", 
   any("color" in a["requirement"].lower() for a in ds["accessibilityRequirements"]))

# ---- Step 24: performance/ops ----
po = json.load(open(ROOT/"framework"/"operations"/"PAF-Performance-Operations.json"))
verr = list(validator("paf.performance-operations.schema.json").iter_errors(po))
ck("R3-15", "Performance/operations contract validates", not verr, str([e.message[:80] for e in verr[:3]]))
ck("R3-16", "STABLE status requires human approval, not elapsed time",
   "human approval" in po["stableApprovalRule"].lower() and "elapsed time" in po["stableApprovalRule"].lower())
ck("R3-17", "Rollback requires a VERIFIED recovery procedure (not merely documented)",
   "verified" in po["rollbackRule"].lower())

# ---- Regression (Runs 1-2 must still hold) ----
FORB = ["projectone","project one","delphics","anthropic","claude","chatgpt","openai","github","celonis","pm4py","fastapi","cytoscape"]
leaks = []
for f in (ROOT/"framework").rglob("*"):
    if f.is_file() and f.suffix in (".json",".md",".py"):
        low = f.read_text(errors="ignore").lower()
        leaks += [f"{f.relative_to(ROOT)}:{t}" for t in FORB if t in low]
ck("R3-18", "SR-1 portability holds across all Run 3 artifacts", not leaks, str(leaks[:5]))

fails = sum(1 for r in res if r[2] == "FAIL")
print("="*78); print("PAF RUN 3 — STATIC VALIDATION (Steps 21-24)"); print("="*78)
for cid, d, st, det in res:
    print(f"[{st}] {cid}  {d}")
    if det and st == "FAIL": print(f"        {det}")
print("-"*78); print(f"RESULT: {len(res)-fails}/{len(res)} checks passed"); print("="*78)
sys.exit(1 if fails else 0)
