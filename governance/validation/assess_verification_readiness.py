#!/usr/bin/env python3
"""
PAF Step 52 — Verification readiness assessment.

The verification map's Framework-v1 bar is MECHANISM_IMPLEMENTED_AND_EVIDENCE_LINKABLE.
This check asks, per decision, whether the FRAMEWORK now actually provides each required
mechanism and a linkable evidence class. It advances status only on that basis — never by
assertion. A mechanism the framework does not provide leaves the decision short of the bar,
and says so.

Reproduce: python3 validation/assess_verification_readiness.py [core_dir]
"""
import sys, json, pathlib
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parent.parent
CORE=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "/home/claude/bootstrap/core")
vm=json.loads((CORE/"ProjectOne-Build-Requirements-Verification-Map-v1.0.json").read_text())
vem=json.loads((ROOT/"framework/models/verification-execution-model.json").read_text())
gates=json.loads((ROOT/"framework/matrices/gate-matrix.json").read_text())
roles={p.stem for p in (ROOT/"framework/contracts").glob("*.json")}
evm=json.loads((ROOT/"framework/matrices/evidence-matrix.json").read_text())

# What the framework provides, by mechanism family
FW = {t["mechanismType"] for t in vem["mechanismTypes"]}
# Map the map's mechanism vocabulary onto framework-provided mechanism types.
PROVIDES = {
 "AUTOMATED_CHECK":"STATIC_ANALYSIS","AUTOMATED_SECURITY_CHECK":"SECURITY_SCAN",
 "AGENT_FRAMEWORK_REGRESSION":"AUTOMATED_TEST","TEST_ASSET_OR_COVERAGE_VALIDATION":"AUTOMATED_TEST",
 "FAULT_OR_FAILURE_PATH_TEST":"AUTOMATED_TEST","CONTRACT_TEST_OR_SCHEMA_VALIDATION":"SCHEMA_VALIDATION",
 "DETERMINISTIC_DATA_OR_SCHEMA_CHECK":"SCHEMA_VALIDATION","CONFIG_SCHEMA_OR_ENV_VALIDATION":"SCHEMA_VALIDATION",
 "DOCUMENT_ARTIFACT_VALIDATION":"SCHEMA_VALIDATION","ARCHITECTURE_STRUCTURE_VALIDATION":"CONTRACT_COMPARISON",
 "CHANGE_PACKAGE_VALIDATION":"SCHEMA_VALIDATION","EXCEPTION_REGISTRY_VALIDATION":"SCHEMA_VALIDATION",
 "DETERMINISTIC_GATE_EVIDENCE":"SOURCE_RESOLUTION_CHECK","OBSERVABILITY_VALIDATION":"MEASUREMENT",
 "PERFORMANCE_BENCHMARK_OR_LOAD_CHECK":"MEASUREMENT",
 "GUI_BASELINE_OR_INTERACTION_VALIDATION":"VISUAL_REGRESSION",
 "RECORDED_QE_REVIEW":"SPECIALIST_ROLE_REVIEW","RECORDED_DOCUMENTATION_REVIEW":"SPECIALIST_ROLE_REVIEW",
 "RECORDED_PERFORMANCE_REVIEW":"SPECIALIST_ROLE_REVIEW","RECORDED_QE_OR_ARCHITECTURE_REVIEW":"SPECIALIST_ROLE_REVIEW",
 "ORCHESTRATOR_AND_QE_CLOSURE":"SPECIALIST_ROLE_REVIEW",
 "INDEPENDENT_GOVERNANCE_REVIEW":"INDEPENDENT_AGENT_REVIEW","INDEPENDENT_SECURITY_REVIEW":"INDEPENDENT_AGENT_REVIEW",
 "INDEPENDENT_ARCHITECTURE_REVIEW":"INDEPENDENT_AGENT_REVIEW","INDEPENDENT_GUI_GOVERNANCE_REVIEW":"INDEPENDENT_AGENT_REVIEW",
 "RISK_BASED_INDEPENDENT_REVIEW":"INDEPENDENT_AGENT_REVIEW","AUTHORITY_REVIEW":"HUMAN_REVIEW",
}
results=[]; unmapped=Counter()
for d in vm["decisions"]:
    mechs=d.get("verificationMechanisms",[])
    provided=[]; missing=[]
    for m in mechs:
        fw=PROVIDES.get(m)
        if fw and fw in FW: provided.append(m)
        else: missing.append(m); unmapped[m]+=1
    linkable = bool(d.get("requiredEvidenceClasses"))
    status = "MECHANISM_IMPLEMENTED_AND_EVIDENCE_LINKABLE" if (mechs and not missing and linkable) \
             else "SHORT_OF_FRAMEWORK_V1_BAR"
    results.append({"decisionId":d["decisionId"],"status":status,
                    "providedMechanisms":provided,"missingMechanisms":missing,
                    "evidenceLinkable":linkable})
ready=[r for r in results if r["status"].startswith("MECHANISM_IMPLEMENTED")]
short=[r for r in results if not r["status"].startswith("MECHANISM_IMPLEMENTED")]
print("="*80); print("PAF STEP 52 — VERIFICATION READINESS ASSESSMENT"); print("="*80)
print(f"Framework-v1 bar: MECHANISM_IMPLEMENTED_AND_EVIDENCE_LINKABLE")
print(f"Decisions assessed: {len(results)}")
print(f"  AT the bar:     {len(ready)}")
print(f"  SHORT of bar:   {len(short)}")
if unmapped:
    print("\nMechanisms the framework does NOT yet provide:")
    for m,c in unmapped.most_common(): print(f"  {c:4}  {m}")
else:
    print("\nEvery mechanism required by the map is provided by the framework.")
print("-"*80)
(ROOT/"evidence").mkdir(exist_ok=True)
(ROOT/"evidence"/"verification-readiness.json").write_text(json.dumps(
  {"bar":"MECHANISM_IMPLEMENTED_AND_EVIDENCE_LINKABLE","assessed":len(results),
   "atBar":len(ready),"shortOfBar":len(short),
   "unprovidedMechanisms":dict(unmapped),"records":results},indent=2))
print(f"RESULT: {len(ready)}/{len(results)} decisions at the Framework-v1 verification bar")
print("="*80)
sys.exit(0 if len(short)==0 else 2)
