#!/usr/bin/env python3
"""
PAF Matrix Generator (Steps 14-20)
Derives all seven matrices from the role contracts and workflow definitions.

Design decision C-R2-01: matrices are GENERATED, never hand-authored. A hand-authored
matrix is a second copy of the same facts and will silently drift from the contracts it
claims to summarize. Generation makes drift structurally impossible.

Reproduce: python3 framework/matrices/generate_matrices.py
"""
import json, pathlib, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CON  = ROOT / "framework" / "contracts"
WF   = ROOT / "framework" / "workflows"
OUT  = ROOT / "framework" / "matrices"
TS   = "2026-08-13T10:01:00-04:00"

roles = {p.stem: json.loads(p.read_text()) for p in sorted(CON.glob("*.json"))}
flows = {p.stem: json.loads(p.read_text()) for p in sorted(WF.glob("*.json"))}

def hdr(aid, desc):
    return {"artifactId": aid, "version": "0.1", "status": "DRAFT", "schemaVersion": "1.0",
            "layer": "CORE", "governedBy": ["PAF-SPEC"], "createdAt": TS,
            "generatedFrom": ["framework/contracts/*.json", "framework/workflows/*.json"],
            "note": desc}

# ---- Step 14: Gate Matrix ----
gates = []
for wid, w in flows.items():
    for g in w["gates"]:
        gates.append({
            "gateId": g["gateId"], "workflowId": wid, "afterStageClass": g["afterStageClass"],
            "requiredEvidenceClasses": g["requiredEvidenceClasses"],
            "closureAuthority": g["closureAuthority"],
            "independenceRequired": g.get("independenceRequired", False),
            "humanApprovalCategoryRef": g.get("humanApprovalCategoryRef"),
            "exceptionEligible": g.get("exceptionEligible", False),
            "stopConditions": w.get("stopConditions", [])})
json.dump({"header": hdr("PAF-MATRIX-GATE", "Every lifecycle gate with its evidence, closure authority, and stop conditions."),
           "gateCount": len(gates), "gates": gates}, open(OUT/"gate-matrix.json","w"), indent=2)

# ---- Step 15: Role-to-Workflow Matrix ----
r2w = collections.defaultdict(list)
for wid, w in flows.items():
    for st in w["stageSequence"]:
        r2w[st["owningRole"]].append({"workflowId": wid, "stageClass": st["stageClass"], "participation": "OWNS"})
        for r in st.get("participatingRoles", []):
            r2w[r].append({"workflowId": wid, "stageClass": st["stageClass"], "participation": "CONTRIBUTES"})
json.dump({"header": hdr("PAF-MATRIX-ROLE-WORKFLOW", "Which roles participate in which workflow stages."),
           "assignments": {k: v for k, v in sorted(r2w.items())}}, open(OUT/"role-workflow-matrix.json","w"), indent=2)

# ---- Step 16: Role-to-Source-Bundle Matrix ----
json.dump({"header": hdr("PAF-MATRIX-SOURCE-BUNDLE", "Generic source classes each role receives. Least-authority: concrete source IDs bind at Profile."),
           "bundles": {rid: r["sourceBundleClasses"] for rid, r in sorted(roles.items())}},
          open(OUT/"role-source-bundle-matrix.json","w"), indent=2)

# ---- Step 17: Role-to-Tool Permission Matrix ----
perms = sorted({p["permission"] for r in roles.values() for p in r["toolPermissions"]})
grid = {rid: {p["permission"]: p["grant"] for p in r["toolPermissions"]} for rid, r in roles.items()}
for rid in grid:
    for p in perms:
        grid[rid].setdefault(p, "DENIED")   # fail closed (CR-5)
json.dump({"header": hdr("PAF-MATRIX-TOOL-PERMISSION",
            "Least privilege by role. Unlisted permission defaults DENIED (CR-5). NOTE: this matrix is DECLARATIVE on conversational workbenches with no per-role sandboxing; enforcement arrives via the repository/CI adapter."),
           "permissions": perms, "defaultGrant": "DENIED",
           "grid": {k: dict(sorted(v.items())) for k, v in sorted(grid.items())}},
          open(OUT/"role-tool-permission-matrix.json","w"), indent=2)

# ---- Step 18: Evidence Matrix ----
ev_index = collections.defaultdict(lambda: {"requiredByGates": [], "declaredProducerRoles": [], "derivedProducerRoles": []})
for g in gates:
    for ec in g["requiredEvidenceClasses"]:
        ev_index[ec]["requiredByGates"].append(g["gateId"])
for rid, r in roles.items():
    for ob in r["evidenceObligations"]:
        ev_index[ob]["declaredProducerRoles"].append(rid)

# Derivation rule (documented, not arbitrary): the role that OWNS the stage a gate
# follows is the presumptive producer of that gate's required evidence. Declared
# obligations in role contracts remain authoritative; derivation only closes the
# traceability graph so no gate demands evidence nobody is accountable for.
stage_owner = {}
for wid, w in flows.items():
    for st in w["stageSequence"]:
        stage_owner[(wid, st["stageClass"])] = st["owningRole"]
for g in gates:
    owner = stage_owner.get((g["workflowId"], g["afterStageClass"]))
    if owner:
        for ec in g["requiredEvidenceClasses"]:
            if owner not in ev_index[ec]["declaredProducerRoles"] and owner not in ev_index[ec]["derivedProducerRoles"]:
                ev_index[ec]["derivedProducerRoles"].append(owner)
for ec in ev_index:
    ev_index[ec]["producedByRoles"] = sorted(set(ev_index[ec]["declaredProducerRoles"] + ev_index[ec]["derivedProducerRoles"]))
json.dump({"header": hdr("PAF-MATRIX-EVIDENCE", "Bidirectional traceability: evidence class -> gates requiring it, roles producing it. Producers are DECLARED (from role contract obligations) or DERIVED (stage-owner rule); both are recorded separately so the basis is always visible."),
           "evidenceClassCount": len(ev_index),
           "evidence": {k: v for k, v in sorted(ev_index.items())}}, open(OUT/"evidence-matrix.json","w"), indent=2)

# ---- Step 19: Dependency Map ----
edges = []
for rid, r in roles.items():
    for t in r.get("handoffsTo", []):   edges.append({"from": rid, "to": t, "type": "HANDOFF"})
    for f in r.get("handoffsFrom", []): edges.append({"from": f, "to": rid, "type": "HANDOFF"})
    for t in r["independenceProfile"]["providesIndependentReviewFor"]:
        edges.append({"from": rid, "to": t, "type": "REVIEWS"})
layer_edges = [{"from": "PROFILE", "to": "CORE", "type": "BINDS_TO"}, {"from": "ADAPTER", "to": "CORE", "type": "TRANSLATES"}]

def has_cycle(es, kinds):
    adj = collections.defaultdict(set)
    for e in es:
        if e["type"] in kinds: adj[e["from"]].add(e["to"])
    WHITE, GREY, BLACK = 0, 1, 2
    color = collections.defaultdict(int); cyc = []
    def dfs(n, path):
        color[n] = GREY
        for m in adj[n]:
            if color[m] == GREY: cyc.append(path + [n, m])
            elif color[m] == WHITE: dfs(m, path + [n])
        color[n] = BLACK
    for n in list(adj): 
        if color[n] == WHITE: dfs(n, [])
    return cyc

authority_cycles = has_cycle(edges, {"REVIEWS"})
json.dump({"header": hdr("PAF-MATRIX-DEPENDENCY", "Role handoff and review edges, plus layer direction. Authority (REVIEWS) edges must be acyclic: a review cycle means mutual self-approval."),
           "layerEdges": layer_edges, "roleEdges": edges,
           "authorityCyclesDetected": authority_cycles,
           "acyclic": not authority_cycles}, open(OUT/"dependency-map.json","w"), indent=2)

# ---- Step 20: Framework Ownership Matrix ----
own = []
for rid, r in roles.items():
    own.append({"entityId": f"framework/contracts/{rid}.json", "entityClass": "GOVERNANCE_CONTROL",
                "steward": "ROLE_ORCHESTRATOR", "reviewPath": ["ROLE_QUALITY"], "changeAuthority": "HUMAN_OWNER"})
for wid in flows:
    own.append({"entityId": f"framework/workflows/{wid}.json", "entityClass": "GOVERNANCE_CONTROL",
                "steward": "ROLE_ORCHESTRATOR", "reviewPath": ["ROLE_QUALITY","ROLE_SECURITY_RELEASE"], "changeAuthority": "HUMAN_OWNER"})
for p in sorted((ROOT/"framework"/"schemas").glob("*.json")):
    own.append({"entityId": f"framework/schemas/{p.name}", "entityClass": "GOVERNANCE_CONTROL",
                "steward": "ROLE_ARCHITECTURE", "reviewPath": ["ROLE_QUALITY"], "changeAuthority": "HUMAN_OWNER"})
for p in sorted(OUT.glob("*.json")):
    own.append({"entityId": f"framework/matrices/{p.name}", "entityClass": "GOVERNANCE_CONTROL",
                "steward": "ROLE_ORCHESTRATOR", "reviewPath": ["ROLE_QUALITY"],
                "changeAuthority": "GENERATED - change the source contract, never the matrix"})
json.dump({"header": hdr("PAF-MATRIX-OWNERSHIP", "Steward, reviewers, and change authority for every framework artifact. No orphans."),
           "entityCount": len(own), "entities": own}, open(OUT/"ownership-matrix.json","w"), indent=2)

print(f"gates={len(gates)}  roles={len(roles)}  workflows={len(flows)}  evidenceClasses={len(ev_index)}  ownedEntities={len(own)}")
print(f"authority graph acyclic: {not authority_cycles}")
sys.exit(1 if authority_cycles else 0)
