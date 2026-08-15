#!/usr/bin/env python3
"""
PAF Run 1 — Framework Static Validation
Deterministic, non-judgmental check (independence mechanism AI-3).
Reproduce: python3 validate_framework.py
Exit 0 = all pass.
"""
import json, sys, pathlib, re
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "framework" / "schemas"
results = []

def check(cid, desc, ok, detail=""):
    results.append((cid, desc, "PASS" if ok else "FAIL", detail))

# V1 — every schema is valid JSON Schema
bad = []
for f in sorted(SCHEMAS.glob("*.json")):
    try:
        Draft202012Validator.check_schema(json.load(open(f)))
    except Exception as e:
        bad.append(f"{f.name}: {str(e)[:80]}")
check("V1-01", "All core schemas are valid JSON Schema 2020-12", not bad, "; ".join(bad))
# Schema count grows as runs add contracts. Assert the foundation set is present by NAME
# rather than by count: a count assertion silently becomes stale and then fails for the
# wrong reason, which is worse than not checking at all.
FOUNDATION = {
  "paf.common.schema.json", "paf.source-registry.schema.json", "paf.ownership-registry.schema.json",
  "paf.work-item.schema.json", "paf.handoff.schema.json", "paf.decision.schema.json",
  "paf.escalation.schema.json", "paf.exception.schema.json", "paf.recovery.schema.json",
  "paf.continuity-snapshot.schema.json", "paf.evidence.schema.json",
  "paf.lifecycle-registry.schema.json", "paf.risk-standard.schema.json",
  "paf.exception-registry.schema.json", "paf.independence-standard.schema.json",
  "paf.human-approval-registry.schema.json"}
present = {f.name for f in SCHEMAS.glob("*.json")}
check("V1-02", "All 16 foundation schemas present by name", FOUNDATION <= present,
      f"missing: {sorted(FOUNDATION - present)}")

# V2 — every $ref target resolves
names = {f.name for f in SCHEMAS.glob("*.json")}
unresolved = []
for f in SCHEMAS.glob("*.json"):
    for ref in re.findall(r'"\$ref"\s*:\s*"([^"]+)"', f.read_text()):
        tgt = ref.split("#")[0]
        if tgt and tgt not in names:
            unresolved.append(f"{f.name} -> {ref}")
check("V2-01", "All $ref targets resolve to a present schema", not unresolved, "; ".join(unresolved))

# V3 — PORTABILITY (SR-1). The load-bearing check behind D-PAF-01.
# No file under framework/ may name a project, vendor, or product.
FORBIDDEN = ["projectone", "project one", "delphics", "anthropic", "claude", "chatgpt",
             "openai", "github", "celonis", "pm4py", "fastapi", "cytoscape"]
leaks = []
for f in (ROOT / "framework").rglob("*"):
    if not f.is_file():
        continue
    low = f.read_text(errors="ignore").lower()
    for term in FORBIDDEN:
        if term in low:
            leaks.append(f"{f.relative_to(ROOT)}: '{term}'")
check("V3-01", "SR-1 no project/vendor/product name appears anywhere in framework/", not leaks,
      "; ".join(leaks[:8]))

# V3-02 — core schemas declare CORE layer only, never PROFILE/ADAPTER content
common = json.load(open(SCHEMAS / "paf.common.schema.json"))
layers = common["$defs"]["artifactHeader"]["properties"]["layer"]["enum"]
check("V3-02", "artifactHeader enforces three-layer declaration (PR-1/PR-2)",
      set(layers) == {"CORE", "PROFILE", "ADAPTER"}, str(layers))

# V4 — control integrity assertions
hr = json.load(open(SCHEMAS / "paf.human-approval-registry.schema.json"))
check("V4-01", "Human approval contract structurally forbids agent approval",
      hr["properties"]["validation"]["properties"]["agentCanApprove"].get("const") is False)

ind = json.load(open(SCHEMAS / "paf.independence-standard.schema.json"))
check("V4-02", "Independence contract requires a non-qualifying mechanism to exist",
      ind["properties"]["qualifyingMechanisms"]["minItems"] >= 2)

exc = json.load(open(SCHEMAS / "paf.exception-registry.schema.json"))
check("V4-03", "Exception contract requires at least one global non-waivable invariant",
      exc["properties"]["globalNonWaivableInvariants"]["minItems"] >= 1)

life = json.load(open(SCHEMAS / "paf.lifecycle-registry.schema.json"))
check("V4-04", "Lifecycle contract requires every interrupt state to declare a resume rule",
      "resumeRule" in life["properties"]["interruptStates"]["items"]["required"])

src = json.load(open(SCHEMAS / "paf.source-registry.schema.json"))
check("V4-05", "Source contract fixes recency-is-not-authority as a constant (CR-2)",
      "recencyIsNotAuthority" in src["properties"]["resolutionRules"]["properties"])
check("V4-06", "Source contract fails closed on unbound configuration (CR-5)",
      src["properties"]["resolutionRules"]["properties"]["unboundBehavior"]["const"]
      == "MOST_RESTRICTIVE_PLUS_WARNING")

# V4-07 — D-PAF-02 ratified amendment: unconfigured control must warn
check("V4-07", "D-PAF-02 amendment: unconfiguredControlWarning requires ownerNotified",
      "ownerNotified" in common["$defs"]["unconfiguredControlWarning"]["required"])

# V4-08 — no-migration shape (spec 4.3)
wi = json.load(open(SCHEMAS / "paf.work-item.schema.json"))
dc = wi["properties"]["deferralRecords"]["items"]["properties"]["deferralClass"]["enum"]
check("V4-08", "Deferral records distinguish functionality from structural design",
      set(dc) == {"FUNCTIONALITY_ONLY", "STRUCTURAL_DESIGN", "UNDECLARED"}, str(dc))

# V4-09 — evidence honesty
ev = json.load(open(SCHEMAS / "paf.evidence.schema.json"))
check("V4-09", "Evidence contract can express NOT_EXAMINED and demands a reason",
      "NOT_EXAMINED" in ev["properties"]["result"]["enum"])

# V4-10 — continuity chain
cs = json.load(open(SCHEMAS / "paf.continuity-snapshot.schema.json"))
check("V4-10", "Continuity snapshot requires a verifiable predecessor/corpus hash chain",
      set(cs["properties"]["packageChain"]["required"]) ==
      {"thisPackageId", "immutableCorpusHash", "predecessorPackageHash"})

fails = sum(1 for r in results if r[2] == "FAIL")
print("=" * 78)
print("PAF RUN 1 — FRAMEWORK STATIC VALIDATION")
print("=" * 78)
for cid, desc, st, detail in results:
    print(f"[{st}] {cid}  {desc}")
    if detail and st == "FAIL":
        print(f"        {detail}")
print("-" * 78)
print(f"RESULT: {len(results)-fails}/{len(results)} checks passed")
print("=" * 78)
sys.exit(1 if fails else 0)
