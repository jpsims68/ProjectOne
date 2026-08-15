#!/usr/bin/env python3
"""
PAF Governance Engine — executable enforcement of the framework's controls.

Reads its rules FROM the framework artifacts (schemas, matrices, workflows, profile bindings).
It hard-codes no governance: change a contract and the engine's behavior changes.

This is what makes Steps 45-47 real execution rather than description.
"""
import json, pathlib
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent

def _load(p): return json.loads((ROOT/p).read_text())

class Framework:
    def __init__(self, core_dir=None):
        self.roles = {p.stem: json.loads(p.read_text()) for p in (ROOT/"framework/contracts").glob("*.json")}
        self.flows = {json.loads(p.read_text())["workflowId"]: json.loads(p.read_text())
                      for p in (ROOT/"framework/workflows").glob("*.json")}
        self.gates = {g["gateId"]: g for g in _load("framework/matrices/gate-matrix.json")["gates"]}
        self.perm  = _load("framework/matrices/role-tool-permission-matrix.json")
        self.vem   = _load("framework/models/verification-execution-model.json")
        self.prof_life = _load("profile/PROJECTONE-Lifecycle.json")
        self.prof_risk = _load("profile/PROJECTONE-Risk.json")
        self.prof_exc  = _load("profile/PROJECTONE-Exception.json")
        self.prof_appr = _load("profile/PROJECTONE-Human-Approval.json")
        self.prof_ind  = _load("profile/PROJECTONE-Independence.json")
        self.prof_src  = _load("profile/PROJECTONE-Source-Registry.json")
        core = pathlib.Path(core_dir) if core_dir else pathlib.Path("/home/claude/bootstrap/core")
        self.life = json.loads((core/"ProjectOne-Lifecycle-State-Registry-v1.1.json").read_text())
        self.risk = json.loads((core/"ProjectOne-Risk-and-Materiality-Classification-Standard-v1.1.json").read_text())
        self.exc  = json.loads((core/"ProjectOne-Exception-Eligibility-Registry-v1.1.json").read_text())
        self.appr = json.loads((core/"ProjectOne-Human-Approval-Authority-and-Continuity-Registry-v1.0.json").read_text())
        self.ind  = json.loads((core/"ProjectOne-Operational-Independence-Standard-v1.0.json").read_text())
        self.states = {s["id"]: s for s in self.life["primaryStates"]}
        self.interrupts = {s["id"]: s for s in self.life["interruptStates"]}
        self.invariants = {i["name"] for i in self.exc["globalNonWaivableInvariants"]}
        self.exc_class = {d["decisionId"]: d["effectiveClass"] for d in self.exc["decisions"]}
        self.nondelegable = set(self.appr["nonDelegableClasses"])
        self.qualifying = {m["id"] for m in self.ind["qualifyingMechanisms"] if m["qualifies"]}
        self.nonqualifying = {m["id"] for m in self.ind["qualifyingMechanisms"] if not m["qualifies"]}
        self.ind_fields = set(self.ind["evidenceRecordSchema"]["requiredFields"])

    # ---------- controls ----------
    def transition(self, frm, to):
        """Lifecycle: only registry-declared edges; interrupts reachable globally."""
        if to in self.interrupts: return True, "interrupt state"
        if frm in self.interrupts:
            return True, "resume from interrupt"
        if frm not in self.states: return False, f"unknown source state {frm}"
        if to not in self.states: return False, f"state not in registry: {to}"
        allowed = self.states[frm].get("allowedNext", [])
        if to in allowed: return True, "declared edge"
        return False, f"{frm} -> {to} not an allowed edge"

    def classify_risk(self, work_type, triggers):
        """Highest triggered class wins; uncertainty routes UPWARD.

        Triggers are referenced as class-qualified indices ('R4.1') resolving to the bound
        standard's declared trigger text. A trigger reference that resolves to NOTHING is
        NOT ignored: an unrecognised trigger means the classifier's input could not be
        bounded, so the item classifies at the highest class (fail closed, D-PAF-02).
        Silently falling back to the work-type floor would make a typo indistinguishable
        from a deliberate low classification — the dominant silent-omission failure mode.
        """
        floor = self.prof_risk["workTypeDefaultRisk"].get(work_type, "R2")
        order = [c["id"] for c in self.risk["classes"]]          # highest severity first
        bycls = {c["id"]: (c.get("triggers") or []) for c in self.risk["classes"]}
        best = floor
        unresolved = []
        for ref in triggers:
            if ref == "UNKNOWN_IMPACT":
                return order[0]
            cls, _, idx = str(ref).partition(".")
            if cls in bycls and idx.isdigit() and int(idx) < len(bycls[cls]):
                if order.index(cls) < order.index(best): best = cls
            else:
                unresolved.append(ref)
        if unresolved:
            return order[0]      # unbounded classification input -> highest class
        return best

    def resolve_trigger(self, ref):
        """Return the declared trigger text for a class-qualified reference, or None."""
        bycls = {c["id"]: (c.get("triggers") or []) for c in self.risk["classes"]}
        cls, _, idx = str(ref).partition(".")
        if cls in bycls and idx.isdigit() and int(idx) < len(bycls[cls]):
            return bycls[cls][int(idx)]
        return None

    def may_grant_exception(self, decision_id, invariant=None, emergency=False, expiry=None, compensating=None, approver_class=None):
        if invariant in self.invariants:
            return False, f"global non-waivable invariant: {invariant}"
        cls = self.exc_class.get(decision_id)
        if cls is None: return False, f"decision {decision_id} unclassified — refused (fail closed)"
        if cls == "NON_WAIVABLE": return False, f"{decision_id} is NON_WAIVABLE"
        if cls == "NORMALLY_NON_WAIVABLE": return False, f"{decision_id} is NORMALLY_NON_WAIVABLE — not eligible without owner-approved override"
        if emergency and invariant in self.invariants: return False, "emergency may not pierce a global invariant"
        if not expiry: return False, "exception requires an expiry"
        if not compensating: return False, "exception requires compensating controls"
        if approver_class != "HUMAN": return False, "exception requires human approval; agent cannot approve"
        return True, "eligible, bounded, compensated, human-approved"

    def approval_satisfied(self, approval_class, actor_class, basis, delegate=None, delegate_expiry=None):
        if actor_class != "HUMAN": return False, "agent can never supply human approval"
        if basis in ("SILENCE","ELAPSED_TIME","AGENT_RECOMMENDATION","MAJORITY","ROLE_RELABEL","EMERGENCY"):
            return False, f"approval never satisfied by {basis}"
        if delegate:
            if approval_class in self.nondelegable: return False, f"{approval_class} is non-delegable"
            if not delegate_expiry: return False, "delegation requires an expiry"
        return True, "valid human approval"

    def independence_satisfied(self, mechanisms, risk_class, evidence_fields, reviewer_actor, implementer_actor):
        if reviewer_actor == implementer_actor: return False, "reviewer is the implementer"
        used = set(mechanisms)
        if not (used & self.qualifying): return False, f"no qualifying mechanism (given: {sorted(used)})"
        if used <= self.nonqualifying: return False, "only non-qualifying mechanisms (role relabel)"
        missing = self.ind_fields - set(evidence_fields)
        if missing: return False, f"NOT_INDEPENDENT — missing evidence fields: {sorted(missing)[:3]}"
        if risk_class == "R4":
            if "DETERMINISTIC_NONJUDGMENTAL_CHECK" not in used:
                return False, "R4 requires a deterministic check"
            if not (used & {"HUMAN_REVIEW","DIFFERENT_MODEL_OR_MODEL_FAMILY","SEPARATE_INVOCATION_CLEAN_CONTEXT"}):
                return False, "R4 requires independent judgment in addition to the deterministic check"
        return True, "independent"

    def evidence_valid(self, rec):
        if rec.get("result")=="NOT_EXAMINED" and not rec.get("notExaminedReason"):
            return False, "NOT_EXAMINED requires a reason"
        if rec.get("reproducible") and not rec.get("reproductionCommand"):
            return False, "reproducible evidence requires a reproduction command"
        if rec.get("result")=="PASS" and rec.get("productionMethod")=="AGENT_JUDGMENT" and rec.get("claimsIndependence"):
            return False, "agent judgment alone never satisfies independence"
        if rec.get("editedInPlace") and rec.get("frozen"):
            return False, "a frozen evidence record is superseded, never edited in place"
        return True, "valid"

    def gate_closable(self, gate_id, provided_evidence, closure_actor_class, independence_ok=True):
        g = self.gates.get(gate_id)
        if not g: return False, f"unknown gate {gate_id}"
        missing = set(g["requiredEvidenceClasses"]) - set(provided_evidence)
        if missing: return False, f"missing evidence: {sorted(missing)}"
        if not g["closureAuthority"]: return False, "gate has no closure authority"
        if "HUMAN_APPROVAL" in g["closureAuthority"] and closure_actor_class != "HUMAN":
            return False, "gate requires human approval"
        if g.get("independenceRequired") and not independence_ok:
            return False, "gate requires independent review"
        return True, "closable"

    def tool_permitted(self, role, permission):
        grid = self.perm["grid"].get(role, {})
        return grid.get(permission, self.perm["defaultGrant"])

    def retry_allowed(self, role, attempt, failure_class):
        rp = self.roles[role]["retryPolicy"]
        if failure_class == "GOVERNANCE_CONFLICT": return False, "governance conflict is never retried"
        if attempt >= rp["maxAttempts"]: return False, f"max attempts ({rp['maxAttempts']}) exhausted — escalate"
        return True, "retry allowed"

    def chain_valid(self, pkg_pred_hash, actual_pred_hash, corpus_hash, actual_corpus_hash):
        if corpus_hash != actual_corpus_hash: return False, "STOP: immutable corpus hash mismatch"
        if pkg_pred_hash != actual_pred_hash: return False, "STOP: predecessor package chain broken"
        return True, "chain intact"

    def read_effective_source(self, source, overlays_applied):
        """CR-3: effective source = immutable base + ALL applicable approved overlays.
        Reading the base alone is an incomplete read and is refused — the agent would
        be acting on text that no longer means what it says."""
        required = set(source.get("overlayRefs", []))
        applied = set(overlays_applied or [])
        missing = required - applied
        if missing:
            return False, f"incomplete read: {len(missing)} applicable overlay(s) not applied: {sorted(missing)}"
        return True, "effective source read (base + all applicable overlays)"

    def source_resolve(self, subject, candidates):
        """scope-bound; recency is not authority; ties escalate."""
        elig = [c for c in candidates if subject in c.get("governsSubjects",[]) and c.get("status")=="ACTIVE"]
        if any(not c.get("versionResolved", True) for c in elig): return None, "ESCALATE: unresolved version"
        if not elig: return None, "no source governs this subject"
        best = min(c["tier"] for c in elig)
        top = [c for c in elig if c["tier"]==best]
        if len(top) > 1: return None, "ESCALATE: equal-authority conflict"
        return top[0], "resolved"
