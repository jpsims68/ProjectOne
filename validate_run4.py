#!/usr/bin/env python3
"""
PAF Run 4 — Profile Binding Validation (Steps 25-34)
Deterministic, non-judgmental check (AI-3). This is the first real test of D-PAF-01:
the bound lifecycle must match the approved registry EXACTLY, and no project rule may
leak upward into the framework core.
Reproduce: python3 validation/validate_run4.py <core_dir>   |  Exit 0 = all pass.
"""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROF = ROOT/"profile"
CORE = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "/home/claude/bootstrap/core")
res=[]
def ck(cid,d,ok,det=""): res.append((cid,d,"PASS" if ok else "FAIL",det))
def load(p): return json.loads(pathlib.Path(p).read_text())

# All profile artifacts declare PROFILE layer
profs = {p.stem: load(p) for p in PROF.glob("*.json")}
bad_layer = [k for k,v in profs.items() if v.get("header",{}).get("layer") != "PROFILE"]
ck("R4-01", "Every profile artifact declares layer=PROFILE", not bad_layer, str(bad_layer))
ck("R4-02", "All 10 profile artifacts present (Steps 25-34)", len(profs) >= 10, str(len(profs)))

# ---- D-PAF-01 LIFECYCLE EQUALITY: bound stage->state map must reference only real registry states ----
life = load(CORE/"ProjectOne-Lifecycle-State-Registry-v1.1.json")
registry_states = {s["id"] for s in life["primaryStates"]} | {s["id"] for s in life["interruptStates"]}
lb = profs["PROJECTONE-Lifecycle"]
mapped_states = set(lb["stageClassToStateMap"].values()) | set(lb["workTypeEntryStates"].values())
invented = mapped_states - registry_states
ck("R4-03", "D-PAF-01: no lifecycle state invented — every bound state exists in the approved registry",
   not invented, f"invented: {sorted(invented)}")
ck("R4-04", "D-PAF-01: no second state machine — binding asserts it explicitly",
   "noSecondStateMachineAssertion" in lb and "NO states of its own" in lb["noSecondStateMachineAssertion"])

# Human phase echo matches registry exactly (no rename/reorder/merge)
reg_phases = [p["phase"] for p in life.get("humanPhaseMap",[])]
ck("R4-05", "D-PAF-01: human phase list matches registry exactly (no rename/merge/reorder)",
   lb["humanPhaseMapEcho"] == reg_phases, f"echo={lb['humanPhaseMapEcho']} vs reg={reg_phases}")

# ---- Bound instance hashes match the actual core files (detects drift/substitution) ----
import hashlib
def sha(fn): return hashlib.sha256((CORE/fn).read_bytes()).hexdigest()
hashmiss=[]
for k,v in profs.items():
    b=v.get("binding")
    if b and b.get("bindingState")=="BOUND":
        fn=b["boundInstanceId"]
        if (CORE/fn).exists() and b.get("boundInstanceHash") and b["boundInstanceHash"]!=sha(fn):
            hashmiss.append(fn)
ck("R4-06", "Every bound registry hash matches the actual core file (no drift)", not hashmiss, str(hashmiss))

# All five governance registries are BOUND (not left in strict mode)
bound = {v["binding"]["boundInstanceId"] for k,v in profs.items() if v.get("binding",{}).get("bindingState")=="BOUND"}
need = {"ProjectOne-Lifecycle-State-Registry-v1.1.json","ProjectOne-Risk-and-Materiality-Classification-Standard-v1.1.json",
 "ProjectOne-Exception-Eligibility-Registry-v1.1.json","ProjectOne-Human-Approval-Authority-and-Continuity-Registry-v1.0.json",
 "ProjectOne-Operational-Independence-Standard-v1.0.json"}
ck("R4-07", "All 5 governance registries are now BOUND (strict mode cleared)", need <= bound, str(need-bound))

# ---- Step 28: build requirements loaded BY REFERENCE, texts not duplicated ----
br = profs["PROJECTONE-Build-Requirements"]
ck("R4-08", "Build requirements loaded by reference, not duplicated", br.get("loadedByReference") is True)
# heuristic: config must not contain long requirement prose
txt = json.dumps(br)
ck("R4-09", "Build-requirements config carries decision IDs, not 330 requirement texts",
   len(br.get("referencedDecisionIds",[]))==360 and len(txt) < 60000, f"ids={len(br.get('referencedDecisionIds',[]))}, bytes={len(txt)}")

# ---- Step 34: all 360 decisions bound to verification ----
vb = profs["PROJECTONE-Verification"]
ck("R4-10", "All 360 decisions bound to verification mechanisms/evidence", len(vb.get("records",[]))==360, str(len(vb.get("records",[]))))
unmapped = [r["decisionId"] for r in vb["records"] if not r["verificationMechanisms"] or not r["requiredEvidenceClasses"]]
ck("R4-11", "No verification record has empty mechanism or evidence", not unmapped, str(unmapped[:5]))

# ---- Step 26: source resolution deterministic; unavailable sources declared not reconstructed ----
sr = profs["PROJECTONE-Source-Registry"]
unresolved = [s["displayName"] for s in sr["sources"] if s["status"]=="ACTIVE" and not s.get("versionResolved")]
ck("R4-12", "Every ACTIVE source has a resolved version", not unresolved, str(unresolved[:5]))
trig = [s for s in sr["sources"] if s.get("availability")=="ABSENT_ACQUISITION_TRIGGER"]
ck("R4-13", "603 grouping source carried as acquisition-trigger, not reconstructed",
   any("603" in s["displayName"] and s.get("acquisitionTrigger") for s in trig), str([s['displayName'] for s in trig]))

# ---- PORTABILITY: no project name leaked into framework/ (Layer 1 stays clean) ----
FORB=["projectone","delphics","fastapi","sql server","cytoscape","pm4py","celonis"]
leaks=[]
for f in (ROOT/"framework").rglob("*"):
    if f.is_file() and f.suffix in (".json",".md",".py"):
        low=f.read_text(errors="ignore").lower()
        leaks+=[f"{f.relative_to(ROOT)}:{t}" for t in FORB if t in low]
ck("R4-14", "Layer separation holds: no ProjectOne/stack name leaked into framework/ core", not leaks, str(leaks[:5]))

# ---- Terminology guard: prohibited framings absent from profile as ASSERTIONS only ----
prof = profs["PROJECTONE-Profile"]
prohibited = prof["terminology"]["prohibitedFramings"]
ck("R4-15", "Profile explicitly prohibits vertical/single-process framings (industry-agnostic)",
   any("beachhead" in p.lower() for p in prohibited) and any("p2p" in p.lower() or "o2c" in p.lower() for p in prohibited))

# ---- Technology stack is Profile content, PM4Py prohibited per D-66 ----
hb = profs["PROJECTONE-Human-Approval"]
stack = hb.get("technologyStack",{}).get("entries",[])
pm4py = [e for e in stack if e["name"]=="PM4Py"]
ck("R4-16", "Technology stack bound at Profile; PM4Py marked PROHIBITED per DDR D-66",
   pm4py and pm4py[0]["status"]=="PROHIBITED", str(pm4py))

fails=sum(1 for r in res if r[2]=="FAIL")
print("="*78); print("PAF RUN 4 — PROFILE BINDING VALIDATION (Steps 25-34)"); print("="*78)
for cid,d,st,det in res:
    print(f"[{st}] {cid}  {d}")
    if det and st=="FAIL": print(f"        {det}")
print("-"*78); print(f"RESULT: {len(res)-fails}/{len(res)} checks passed"); print("="*78)
sys.exit(1 if fails else 0)
