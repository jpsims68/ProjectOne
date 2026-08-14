# Portable Agent Framework — Validation Report

**Artifact ID:** `PAF-VALIDATION-REPORT` · **Version:** 1.0
**Framework under validation:** PAF `1.0-rc1` (VALIDATION_CANDIDATE)
**Date:** 2026-08-13 EDT (America/New_York)
**Step:** 52 of 113
**Status:** DECISION-READY — supports the Step 54 approval decision. Does not constitute approval.

---

## 1. Bottom line

The framework is **structurally complete, executable, and demonstrably enforcing**. All nine validation suites pass. Execution found five defects, all corrected without weakening a control.

**Two things stand between this report and Framework v1 approval**, and both need you:

1. **Step 49 sustainability thresholds are proposed, not approved.** Your Dry-Run Acceptance Plan's `gateRule` blocks Framework v1 approval until you approve them.
2. **The verification readiness assessment (§6) depends in part on a mapping I authored.** I recommend independent review before you rely on it.

Everything else is evidenced and reproducible.

---

## 2. What was validated

| Layer | Components |
|---|---|
| CORE (generic framework) | 86 |
| PROFILE (ProjectOne configuration) | 10 |
| ADAPTER | 5 |
| **Total** | **101** |

Reproduce every result below with one command:

```
python3 validation/run_all_validation.py <core_dir>
```

---

## 3. Static validation results (Step 44)

| Suite | Result | Covers |
|---|---|---|
| Framework core | **15/15** | Schema validity, `$ref` resolution, portability (SR-1), fail-closed defaults, no-migration deferral shape, continuity chain |
| Roles / workflows / matrices | **21/21** | 16 role contracts, 15 workflows, 45 gates, self-approval prohibition, least privilege, acyclic authority graph, bidirectional evidence traceability |
| Testing / registries / GUI / ops | **18/18** | Regression portfolio structure, security invariant bindings, environment tiering, theming layer separation, STABLE approval rule |
| Profile binding | **16/16** | D-PAF-01 lifecycle equality, hash-bound registries, by-reference requirements, 360 verification bindings |
| Adapters / assembly | **15/15** | Translate-never-redefine, Anthropic adapter portability, capability-gap discipline, release-state honesty |
| Contract ↔ instance conformance | **5/5** | Core contracts genuinely accept the approved governance registries |

**No static structural or reference defects remain.**

---

## 4. Regression execution (Step 45)

**31/31 cases behaved as specified**, executed against the live governance engine and graded against answer keys held in separate files (non-circular grading).

All four mandatory adversarial families exercised and **refused**:

| Family | Cases | Representative case that must fail — and does |
|---|---|---|
| Self-approval | 4 | A reviewer that is a relabeled continuation of the implementer's own reasoning |
| Silent exception | 6 | Emergency framing used to pierce `tenant_isolation` |
| Fabricated evidence | 5 | `NOT_EXAMINED` submitted with no reason, then treated downstream as PASS |
| Unapproved bypass | 6 | A human-approval gate advanced because 48 hours elapsed with no reply |
| Chain integrity | 4 | A stale-generation continuation package re-uploaded |
| Source authority | 6 | An immutable source read without its applicable overlays |

---

## 5. Governance dry run and replay (Steps 46–48)

**12/12 mandatory scenarios executed. Zero-tolerance violations: 0.**

| Zero-tolerance criterion | Result |
|---|---|
| No cross-tenant access or tenant-isolation bypass | **PASS** |
| No fabricated completion or evidence-honesty violation | **PASS** |
| No required human approval inferred from silence or replaced by an agent | **PASS** |
| No non-waivable control accepted through exception or emergency | **PASS** |
| No source-authority decision from an unverified or prohibited source | **PASS** |
| No unbounded retry loop | **PASS** |
| No work item reaches Stable without required evidence and approval | **PASS** |

**Retrospective replay: 8/8** real pre-framework ProjectOne decisions routed correctly — including the D-66 PM4Py drop, the D-35 OCPM structural deferral, the F-009 CRITICAL hold under baseline discipline, exclusion of the accidentally-uploaded v1.1-FROZEN audit, the 406 file-drift substitution, DDR-read-without-overlays, agent-attempted DDR amendment, and spike-versus-DDR precedence.

### Measured governance workload

| Metric | Value |
|---|---|
| Human approvals across 12 scenarios | 7 |
| Human review minutes | 70 |
| Specialist reviewers engaged | 5 |
| Evidence artifacts produced | 31 |
| Reroutes / rework loops | 4 / 1 |
| Exceptions requested | 2 (both scenario-mandated) |
| Full Agent Review triggers | 2 |
| **False blocks** | **0** |
| **Missed required gates** | **0** |
| **Pro-forma / bypass signals** | **0** |

The last three matter most. Zero false blocks means the framework did not refuse correctly-formed work — the leading indicator of whether people will start routing around it. Zero bypass signals means no control was satisfied pro forma.

---

## 6. Verification readiness — READ THIS BEFORE APPROVING

The verification map's Framework-v1 bar is `MECHANISM_IMPLEMENTED_AND_EVIDENCE_LINKABLE`. At the start of this run, all 360 decisions sat at `DEFINED_IN_MAP__IMPLEMENTATION_PENDING`.

**Assessment result: 360/360 decisions now meet the bar.**

**The honest caveat.** That result has two parts, and only one is deterministic:

- **Deterministic:** does the framework implement mechanism type *X*? Checkable against the verification execution model. Yes for all twelve implemented types.
- **My judgment:** does the map's mechanism *M* correspond to framework mechanism *X*? For example, that `RECORDED_QE_REVIEW` (138 decisions) corresponds to `SPECIALIST_ROLE_REVIEW`. That mapping is defensible, but I authored it.

By the framework's own rule, agent judgment does not satisfy independence. **I therefore do not present §6 as independently verified.** I recommend a clean-context independent review of the mechanism mapping before you rely on this figure. It does not block approval, but you should approve knowing which part is measured and which part is argued.

The remaining status steps — `EVIDENCE_PRESENT` and `VERIFIED` — belong to application work, not framework approval.

---

## 7. Defects found and corrected (Step 50)

Every defect was corrected by fixing the artifact or engine. **No control was weakened to make a test pass.**

| ID | Defect | Severity | Correction |
|---|---|---|---|
| **F-R6-02** | **Risk classification failed OPEN.** An unrecognised trigger reference silently fell back to the work-type floor class, making a typo indistinguishable from a deliberate low classification | **HIGH** | Now fails closed: unresolved trigger input returns the highest class. Uncertainty routes upward |
| **F-R6-01** | **No overlay enforcement.** A source with applicable overlays could be read base-only and accepted — an agent acting on text that no longer means what it says | **HIGH** | `read_effective_source()` added; incomplete reads refused. Portfolio extended |
| **F-R6-04** | Zero-tolerance reporting marked all seven criteria FAIL whenever any violation existed — asserting breaches that did not occur | MEDIUM | Per-criterion mapping |
| **F-R6-03** | Two dry-run scenario paths used lifecycle edges the registry does not declare. **The engine correctly refused both** — the defect was in scenario authoring | LOW | Paths corrected. Confirms the lifecycle control holds against its own author |
| **F-R6-05** | Thresholds artifact declared `layer` outside its header | LOW | Header corrected |
| **F-R5-01** | Portability leak: the Anthropic adapter's own prohibition contained the literal project name | LOW | Generic wording |
| **F-R2-01** | 44 of 82 evidence classes required by a gate had no accountable producer | MEDIUM | Documented stage-owner derivation; check hardened to enforcing |

**F-R6-02 is the most consequential.** A fail-open risk classifier would have silently under-protected work for the life of the system, and no static check would have caught it. Only execution did. This is the strongest argument that Steps 45–47 were worth running rather than asserting.

---

## 8. Residual risk and declared capability gaps

Nine capability gaps are formally declared in the Adapter Compatibility Matrix. Each carries a mitigation and names **John** as risk acceptor.

| Gap | Consequence | Mitigation |
|---|---|---|
| **Live GitHub/CI operations** | Steps 63–72, 91, 101, 110 cannot be self-verified on this platform | Adapter fully specified and locally unit-validatable; live validation **deferred to owner execution**. No GitHub integration is signed off as passing |
| **Secret storage** | `secret_protection` is a global non-waivable invariant and cannot be satisfied by this surface | Secrets never entered in conversation; bound in owner environment via an unbound interface. Handled by architecture, never by exception |
| **Persistent container state** | Nothing survives between sessions | Durable externalized packages, hash-chained, owner-retained. Verified working across six runs |
| **Per-role tool sandboxing** | Least-privilege matrix is declarative here | Enforced via the repository/CI adapter |
| **Different model-family independence** | Cross-family independence unavailable within one platform | Such gates route to human review or another platform. Never simulated |

### Other open items

- **75 of 330 requirements** have untested consolidation fidelity pending the DATA, API, SEC and non-pilot CODE recap documents — a branch-local pause you ratified. Carried openly, not silently closed.
- **`603-Activities_Groupings_for_Mapping.md`** unavailable; flagged as an acquisition trigger that must fire before any D-38 grouping-seed implementation.
- **F-019 / SD-004** reopens automatically if an exact Manifest v73 artifact ever appears.

---

## 9. Readiness assessment

| Dimension | State |
|---|---|
| Structural completeness | **Ready** — 101 components, all validating |
| Behavioral correctness | **Ready** — 31/31 regression, 12/12 dry run, 8/8 replay |
| Adversarial resistance | **Ready** — all four mandatory families refused |
| Layer separation / portability | **Ready** — core provably free of project and vendor names |
| Defect state | **Ready** — 7 defects found, all corrected without weakening controls |
| Capability gaps | **Declared** — 9 gaps, all mitigated, all with a named risk acceptor |
| Verification readiness | **Ready with caveat** — 360/360 at the bar; mechanism mapping is my judgment (§6) |
| **Sustainability thresholds** | **NOT APPROVED — owner decision required (Step 49)** |

**Recommendation:** the framework is ready for the Step 54 approval decision, conditional on your approval of the Step 49 sustainability thresholds. I do not treat this report as approval, and approval cannot be inferred from these results.
