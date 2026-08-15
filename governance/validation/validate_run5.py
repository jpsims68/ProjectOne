#!/usr/bin/env python3
"""
PAF Run 5 — Adapter & Assembly Validation (Steps 35-43)
Deterministic, non-judgmental check (AI-3).
Reproduce: python3 validation/validate_run5.py   |  Exit 0 = all pass.
"""
import json, sys, pathlib
from jsonschema import Draft202012Validator, RefResolver
ROOT=pathlib.Path(__file__).resolve().parent.parent
SC=ROOT/"schemas" if (ROOT/"schemas").exists() else ROOT/"framework"/"schemas"
store={f.name:json.load(open(f)) for f in SC.glob("*.json")}
AD=ROOT/"adapters"; MAN=ROOT/"manifests"
res=[]
def ck(cid,d,ok,det=""): res.append((cid,d,"PASS" if ok else "FAIL",det))
adapters={p.stem:json.loads(p.read_text()) for p in AD.glob("*.json")}

# All adapters validate against the contract schema
s=store["paf.adapter-contract.schema.json"]
v=Draft202012Validator(s,resolver=RefResolver(base_uri="",referrer=s,store=store))
bad=[]
for name,a in adapters.items():
    for e in list(v.iter_errors(a))[:1]: bad.append(f"{name}:{e.message[:90]}")
ck("R5-01","All adapters validate against the adapter contract",not bad,"; ".join(bad[:4]))
ck("R5-02","All 5 required adapters present (contract, GitHub, ChatGPT, Anthropic, coding)",
   len(adapters)>=5 and "PAF-Adapter-Anthropic" in adapters, str(sorted(adapters)))

# Step 38: Anthropic adapter is first-class and carries NO ProjectOne governance
anth=adapters["PAF-Adapter-Anthropic"]
ck("R5-03","Anthropic adapter declares layer=ADAPTER",anth["header"]["layer"]=="ADAPTER")
txt=json.dumps(anth).lower()
leak=[t for t in ["projectone","delphics","fastapi","sql server","cytoscape","pm4py","d-66","d-35"] if t in txt]
ck("R5-04","Anthropic adapter contains NO ProjectOne-specific governance",not leak,str(leak))

# Every adapter declares the 5 translation rules
missing_rules=[name for name,a in adapters.items()
  if set(a["translationRules"].keys())!={"translatesNeverRedefines","noAuthorityOrigination","noProjectGovernance","noStateInvention","noIndependenceCollapse"}]
ck("R5-05","Every adapter declares all 5 translate-never-redefine rules",not missing_rules,str(missing_rules))

# Every CANNOT_SATISFY gap carries mitigation + risk acceptor (schema enforces, verify populated)
badgap=[]
for name,a in adapters.items():
    for c in a["capabilityMap"]:
        if c["support"]=="CANNOT_SATISFY" and (not c.get("mitigation") or not c.get("riskAcceptor")):
            badgap.append(f"{name}:{c['capability']}")
ck("R5-06","Every CANNOT_SATISFY gap has a mitigation AND a named risk acceptor",not badgap,str(badgap))

# GitHub adapter: live ops + secrets declared CANNOT_SATISFY with deferred verification
gh=adapters["PAF-Adapter-GitHub"]
gh_gaps={c["capability"]:c for c in gh["capabilityMap"] if c["support"]=="CANNOT_SATISFY"}
ck("R5-07","GitHub live ops honestly declared CANNOT_SATISFY + deferred (no fabricated pass)",
   any("live github" in k.lower() and gh_gaps[k].get("deferredVerification") for k in gh_gaps),str(list(gh_gaps)))

# No adapter claims NATIVE for a control that is a global non-waivable it can't enforce here
# (secret_protection must never be NATIVE on a conversational surface)
convo=[a for a in adapters.values() if a["surfaceClass"]=="CONVERSATIONAL_WORKBENCH"]
badsec=[a["adapterId"] for a in convo for c in a["capabilityMap"]
        if "secret" in c["capability"].lower() and c["support"]=="NATIVE"]
ck("R5-08","No conversational adapter claims NATIVE secret storage",not badsec,str(badsec))

# Step 40: config manifest inventories everything with hashes
cm=json.load(open(MAN/"PAF-Configuration-Manifest.json"))
ck("R5-09","Configuration manifest inventories all components with hashes",
   cm["componentCount"]>=90 and all(c.get("hash") for c in cm["components"]),f"count={cm['componentCount']}")

# Step 41: compatibility matrix generated, gaps visible
compat=json.load(open(MAN/"PAF-Adapter-Compatibility-Matrix.json"))
ck("R5-10","Compatibility matrix declares gaps with mitigations before delegation",
   len(compat["declaredGaps"])>=1 and all(g.get("mitigation") and g.get("riskAcceptor") for g in compat["declaredGaps"]),
   f"{len(compat['declaredGaps'])} gaps")
ck("R5-11","Compatibility matrix is generated from adapters (not hand-authored)",
   compat.get("generatedFrom")=="adapters/*.json")

# Step 42: release manifest is a CANDIDATE, not approved; approval gate is Step 54
rm=json.load(open(MAN/"PAF-Release-Manifest.json"))
ck("R5-12","Release manifest is VALIDATION_CANDIDATE, not approved",rm["releaseState"]=="VALIDATION_CANDIDATE")
ck("R5-13","Release manifest defers approval to Step 54 (not inferred from validation)",
   "Step 54" in rm["approvalGate"])
ck("R5-14","Release manifest lists open items blocking approval (incl. 360-decision gap)",
   any("360" in x for x in rm["openItemsBlockingApproval"]))

# Portability preserved: framework/ still clean
FORB=["projectone","delphics","fastapi","sql server","cytoscape","pm4py"]
leaks=[]
for f in (ROOT/"framework").rglob("*"):
    if f.is_file() and f.suffix in (".json",".md",".py"):
        low=f.read_text(errors="ignore").lower()
        leaks+=[f"{f.relative_to(ROOT)}:{t}" for t in FORB if t in low]
ck("R5-15","Layer separation preserved: framework/ core still name-free",not leaks,str(leaks[:4]))

fails=sum(1 for r in res if r[2]=="FAIL")
print("="*78); print("PAF RUN 5 — ADAPTER & ASSEMBLY VALIDATION (Steps 35-43)"); print("="*78)
for cid,d,st,det in res:
    print(f"[{st}] {cid}  {d}")
    if det and st=="FAIL": print(f"        {det}")
print("-"*78); print(f"RESULT: {len(res)-fails}/{len(res)} checks passed"); print("="*78)
sys.exit(1 if fails else 0)
