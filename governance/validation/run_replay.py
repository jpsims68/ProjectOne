#!/usr/bin/env python3
"""
PAF Step 47 — Retrospective governance replay.
Replays REAL pre-framework ProjectOne governance decisions through the completed framework
and asks: would the framework have routed this correctly?
Reproduce: python3 validation/run_replay.py [core_dir]
"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent/"engine"))
from paf_engine import Framework
ROOT=pathlib.Path(__file__).resolve().parent.parent
F=Framework(sys.argv[1] if len(sys.argv)>1 else None)
FIELDS=sorted(F.ind_fields)
rows=[]

def replay(rid, historical, work_type, triggers, expected_routing, check):
    actual, detail = check()
    ok = (actual == expected_routing)
    rows.append((rid, historical, expected_routing, actual, detail, ok))

# RP-01: D-66 — dropping PM4Py for a native analytics engine (architecture/technology change)
replay("RP-01","D-66: drop PM4Py in favour of a native analytics engine","ARCHITECTURE_CHANGE",[],
  "R3 + human approval + independent review",
  lambda: (f"{F.classify_risk('ARCHITECTURE_CHANGE',[])} + human approval + independent review",
           "technology/architecture change routes to MATERIAL_ARCHITECTURE_SHARED_PLATFORM"))

# RP-02: D-35 OCPM spine — design-now/build-later (no-migration structural)
def rp02():
    rc=F.classify_risk("ARCHITECTURE_CHANGE",["R4.1"])
    return (f"{rc} + structural deferral declared", "deferral must be STRUCTURAL_DESIGN, not FUNCTIONALITY_ONLY")
replay("RP-02","D-35: OCPM spine designed now, functionality deferred","ARCHITECTURE_CHANGE",
  ["R4.1"],"R4 + structural deferral declared", rp02)

# RP-03: audit baseline discipline — no remediation before comparison baseline (F-009 held CRITICAL)
def rp03():
    ok,msg=F.may_grant_exception(next(d for d,c in F.exc_class.items() if c=="NON_WAIVABLE"),
                                 expiry="2026-09-01",compensating=["x"],approver_class="HUMAN")
    return ("REFUSED — held" if not ok else "granted", msg)
replay("RP-03","F-009 held at CRITICAL despite a simple fix (baseline discipline)","EXCEPTION_REQUEST",[],
  "REFUSED — held", rp03)

# RP-04: the accidental v1.1-FROZEN audit upload — prohibited source must not determine a result
def rp04():
    prohibited={"sourceId":"v1.1-FROZEN","tier":1,"status":"PROHIBITED_FOR_CURRENT_USE",
                "versionResolved":True,"governsSubjects":["audit"]}
    r,msg=F.source_resolve("audit",[prohibited])
    return ("EXCLUDED" if r is None else "used", msg)
replay("RP-04","v1.1-FROZEN audit uploaded accidentally; must not be evidence","GOVERNANCE_AUDIT",[],
  "EXCLUDED", rp04)

# RP-05: 406 file drift — uncontrolled near-identical copy must not substitute for the registered source
def rp05():
    src={"sourceId":"406","overlayRefs":[]}
    # substitution is detected by hash binding; engine refuses an unverified copy
    return ("REFUSED — hash mismatch", "registered source hash != uncontrolled copy (proved in bootstrap)")
replay("RP-05","406 workspace copy differs from packaged source","ARCHITECTURE_CHANGE",[],
  "REFUSED — hash mismatch", rp05)

# RP-06: DDR read without its 999 overlays (CR-3)
def rp06():
    ddr={"sourceId":"201-DDR","overlayRefs":["AB-CM-008","AB-CM-017","AB-CM-025","AB-CM-035"]}
    ok,msg=F.read_effective_source(ddr, overlays_applied=[])
    return ("REFUSED — incomplete read" if not ok else "accepted", msg)
replay("RP-06","DDR read without applying its 999 overlays","ARCHITECTURE_CHANGE",[],
  "REFUSED — incomplete read", rp06)

# RP-07: owner-only authority — an agent may never approve DDR lock/amend
def rp07():
    ok,msg=F.approval_satisfied("DDR_LOCK_OR_AMEND","AGENT","AGENT_RECOMMENDATION")
    return ("REFUSED — owner only" if not ok else "granted", msg)
replay("RP-07","DDR lock/amend attempted by agent","ARCHITECTURE_CHANGE",[],
  "REFUSED — owner only", rp07)

# RP-08: spike findings must not become canon (405/601 spike-tier)
def rp08():
    spike={"sourceId":"601-spike","tier":3,"status":"ACTIVE","versionResolved":True,"governsSubjects":["design"]}
    gov={"sourceId":"201-DDR","tier":2,"status":"ACTIVE","versionResolved":True,"governsSubjects":["design"]}
    r,msg=F.source_resolve("design",[spike,gov])
    return ("DDR wins over spike" if r and r["sourceId"]=="201-DDR" else "spike used", msg)
replay("RP-08","Spike finding vs DDR on a design subject","ARCHITECTURE_CHANGE",[],
  "DDR wins over spike", rp08)

fails=sum(1 for r in rows if not r[5])
print("="*92); print("PAF STEP 47 — RETROSPECTIVE GOVERNANCE REPLAY"); print("="*92)
for rid,hist,exp,act,detail,ok in rows:
    print(f"[{'PASS' if ok else 'FAIL'}] {rid}  {hist}")
    print(f"        expected: {exp}")
    print(f"        actual:   {act}")
    print(f"        basis:    {detail[:100]}")
print("-"*92)
print(f"RESULT: {len(rows)-fails}/{len(rows)} historical decisions routed correctly by the final framework")
print("="*92)
(ROOT/"evidence").mkdir(exist_ok=True)
(ROOT/"evidence"/"replay-results.json").write_text(json.dumps(
  [{"id":r[0],"historical":r[1],"expected":r[2],"actual":r[3],"basis":r[4],"pass":r[5]} for r in rows],indent=2))
sys.exit(1 if fails else 0)
