# Portable Agent Framework — Framework Specification

**Artifact ID:** `PAF-SPEC`
**Version:** 0.2 (DRAFT — construction baseline; becomes v1.0 only at Step 55 freeze)
**Created:** 2026-08-13 10:01 EDT (America/New_York)
**Step:** 1 of 113 (Run 1 — Framework Foundation)
**Status:** ACTIVE — foundation decisions ratified by owner 2026-08-13
**Document class:** Assistant-created artifact — maintained directly, never via 999 overlay (999 §1.2)

---

## 0. What this document is

This is the constitution of the Portable Agent Framework (PAF). Every framework artifact built in Steps 2–53 must conform to it. It defines *what the framework is*, *what it may never contain*, *how it is configured*, *how it is extended*, *how authority enters it*, and *how it is validated*.

It deliberately contains **no project rules and no vendor names**. The project enters at Steps 25–34 as a Profile; execution surfaces enter at Steps 35–39 as Adapters. This document describes those relationships structurally; naming a specific project or vendor here would itself be a portability defect, and a validation check enforces that.

---

## 1. Purpose

The PAF exists to make AI-assisted software development **governable, auditable, portable, and resistant to context loss**.

It does five things:

1. **Classifies work** — every unit of work receives a type, a risk class, an owner, and a lifecycle position before implementation begins.
2. **Routes work** — classification deterministically determines which roles participate, which reviews are required, which evidence must exist, and which human approvals gate progress.
3. **Constrains agents** — each role holds bounded authority, cannot exceed it, and cannot approve its own work.
4. **Produces evidence** — completion is a function of recorded evidence, never of assertion, elapsed time, or fluent narration.
5. **Survives discontinuity** — state lives in durable externalized artifacts, so work resumes across context windows, sessions, workbenches, and AI platforms without loss of authority or history.

### 1.1 The problem it solves

AI agents are fluent. Fluency is indistinguishable from correctness at a glance, and an agent that has lost its context will confidently produce work that looks finished. Left ungoverned, this failure mode compounds silently: an unverified assumption becomes a design premise, becomes a schema, becomes production data.

The PAF's answer is to make **authority explicit, review independent, evidence mandatory, and state external**. No control in this framework may be satisfied by an agent's own claim that it was satisfied.

---

## 2. Boundaries

### 2.1 The framework IS

- A set of versioned, machine-readable schemas and registries.
- A lifecycle, risk, exception, independence, and approval control system.
- A set of portable role contracts with bounded authority.
- A set of workflow, gate, permission, and evidence matrices.
- A configuration loader with deterministic resolution rules.
- A validation suite that can prove its own structural integrity.

### 2.2 The framework IS NOT

- **Not a project.** It contains no product requirements, no domain vocabulary, no schema design, no feature scope.
- **Not a workbench.** It does not assume a chat interface, an IDE, a container, a filesystem layout, or a specific AI vendor.
- **Not an authority on project content.** It governs *how* decisions are made and recorded; it never makes them.
- **Not a runtime.** It is specification plus configuration plus deterministic checks. Enforcement surfaces (CI, branch protection, repository controls) are adapters, not the framework.
- **Not self-approving.** The framework cannot ratify itself, and no framework artifact may weaken a control in order to pass its own validation.

### 2.3 The portability test

> **A rule belongs in the framework core if, and only if, it would remain true and useful for a completely different project, in a different domain, on a different workbench.**

If removing the project entirely would leave a rule meaningless, that rule belongs in the Profile. If removing the workbench would leave it meaningless, it belongs in an Adapter. This test is applied at every step from 2 through 53 and is a validation check, not a matter of taste.

---

## 3. Portability model

The framework is a **three-layer system with strictly downward authority**.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1 — FRAMEWORK CORE                                   │
│  Generic. Project-independent. Workbench-independent.       │
│  Schemas · lifecycle contract · risk machinery ·            │
│  exception machinery · independence machinery ·             │
│  approval machinery · role contracts · workflows ·          │
│  matrices · validation suite                                │
│                                                             │
│  Knows: control semantics                                   │
│  Never knows: project content, vendor behavior              │
└──────────────────────────┬──────────────────────────────────┘
                           │ binds ▼            (never ▲)
┌──────────────────────────┴──────────────────────────────────┐
│  LAYER 2 — PROJECT PROFILE                                  │
│  One per project. Configuration, not code.                  │
│  Source registry · ownership map · terminology ·            │
│  risk triggers · gate bindings · verification bindings ·     │
│  project constraints                                         │
│                                                             │
│  Knows: this project's content and authority                │
│  Never knows: vendor behavior                               │
│  May NOT: invent states, weaken controls, add authority     │
└──────────────────────────┬──────────────────────────────────┘
                           │ executed on ▼      (never ▲)
┌──────────────────────────┴──────────────────────────────────┐
│  LAYER 3 — WORKBENCH ADAPTER                                │
│  One per execution surface. Thin translation only.          │
│  Repository/VCS hosting · conversational workbenches ·      │
│  coding workbenches                                         │
│                                                             │
│  Knows: how to express framework behavior on this surface   │
│  Never knows: why a control exists                          │
│  May NOT: rename/merge/skip/reorder states or gates,        │
│           collapse required independent steps,               │
│           originate authority of any kind                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 The three inviolable directional rules

**PR-1 — Authority flows down, never up.** A Profile may bind a control; it may not create, relax, or override one. An Adapter may express a control; it may not reinterpret one. A capability absent from an Adapter is a *declared gap requiring mitigation*, never a licence to skip the control.

**PR-2 — Layers are separable.** The Core must remain coherent with the Profile removed. The Core plus Profile must remain coherent with the Adapter removed. Validation asserts this by construction, not by inspection.

**PR-3 — Substitution is lossless.** Replacing the Adapter changes *how* work is executed and *what evidence looks like*. It never changes which controls apply, which reviews are required, or who approves. Platform migration must never be a governance event.

### 3.2 Why this matters more than it appears

The framework is being built on one AI platform, for a project that has already migrated between platforms once. The migration that has already happened is the proof of the requirement. Any convenience of the current workbench that leaks into Layer 1 becomes a hidden dependency that will surface as a governance failure at the next transfer — at which point it will be indistinguishable from a genuine control.

---

## 4. Configuration model

### 4.1 Contract-and-instance

The Core defines **contracts** (schemas + semantics). The Profile supplies **instances** conforming to them. The Core never embeds instance content.

| Core defines (contract) | Profile supplies (instance) |
|---|---|
| What a lifecycle registry must contain and how transitions resolve | This project's states and transitions |
| How risk classes rank, escalate, and bind controls | This project's risk triggers |
| What makes an exception valid and what can never be waived | This project's decision-level classifications |
| What qualifies as independent review | Which of this project's gates require it |
| How human approval authority resolves | This project's approval classes and approvers |
| What a source registry must express | This project's sources, tiers, versions, overlays |

**Consequence, stated plainly:** the Core carries *no* state names, *no* risk trigger text, *no* decision IDs, *no* approver names. Those live in Layer 2. A Core that has memorised the Profile has failed PR-2 whether or not it behaves correctly today.

### 4.2 Resolution rules

**CR-1 — Authority is scope-bound, never global.** Every source declares the subjects it governs. Precedence is evaluated per subject. A high-tier source does not control subjects outside its declared scope.

**CR-2 — Recency is not authority.** A newer artifact does not supersede an older one by virtue of being newer. Supersession is explicit, recorded, and approved.

**CR-3 — Effective source = immutable source + approved overlays.** Where a source is immutable, its effective content is the source plus every applicable approved overlay entry. Reading the source alone is an incomplete read.

**CR-4 — Unresolvable is a stop, not a default.** If two equal-authority sources conflict on a material subject, or a version cannot be resolved, the framework enters an interrupt state and escalates. It never picks, never averages, never infers from context.

**CR-5 — Absent configuration fails closed.** A control with no Profile binding is *not* disabled. It defaults to its most restrictive form until bound.

**CR-6 — Unknown keys ignored, missing keys defaulted, version declared.** Every configuration artifact carries a schema version. Forward compatibility is achieved by graceful defaulting, never by silent migration of stored records.

### 4.3 Design-ahead (no-migration) as a framework property

The Core does not know any project's no-migration rules. It does enforce the *shape* of the principle:

> Deferring **functionality** is a scheduling decision. Deferring **design that accumulated state will later require** is a structural decision that cannot be reversed without transforming existing data.

The framework therefore requires that any deferral record explicitly declare which of the two it is, and treats an undeclared deferral as the structural kind — the restrictive default, per CR-5. A Profile may bind stricter project rules on top. It may not relax this.

---

## 5. Directory and package structure

```
paf/
├── framework/                        # LAYER 1 — generic core
│   ├── spec/
│   │   └── PAF-Framework-Specification.md          # this document
│   ├── schemas/                                     # Steps 2, 5
│   │   ├── paf.common.schema.json                   # shared primitives
│   │   ├── paf.source-registry.schema.json          # Step 3
│   │   ├── paf.ownership-registry.schema.json       # Step 4
│   │   ├── paf.work-item.schema.json                # Step 5
│   │   ├── paf.handoff.schema.json
│   │   ├── paf.decision.schema.json
│   │   ├── paf.escalation.schema.json
│   │   ├── paf.exception.schema.json
│   │   ├── paf.recovery.schema.json
│   │   ├── paf.continuity-snapshot.schema.json
│   │   ├── paf.evidence.schema.json
│   │   ├── paf.lifecycle-registry.schema.json       # Step 6
│   │   ├── paf.risk-standard.schema.json            # Step 7
│   │   ├── paf.exception-registry.schema.json       # Step 8
│   │   ├── paf.independence-standard.schema.json    # Step 9
│   │   └── paf.human-approval-registry.schema.json  # Step 10
│   ├── models/                                      # normative semantics
│   │   ├── source-authority-model.md                # Step 3
│   │   └── ownership-model.md                       # Step 4
│   ├── binding/                                     # contract→instance rules
│   │   ├── lifecycle-binding.md                     # Step 6
│   │   ├── risk-binding.md                          # Step 7
│   │   ├── exception-binding.md                     # Step 8
│   │   ├── independence-binding.md                  # Step 9
│   │   └── human-approval-binding.md                # Step 10
│   ├── contracts/                                   # Step 11 — 16 role contracts
│   ├── workflows/                                   # Step 12
│   ├── matrices/                                    # Steps 14–20
│   ├── testing/                                     # Step 21
│   ├── registries/                                  # Step 22
│   ├── gui/                                         # Step 23
│   └── operations/                                  # Step 24
├── profile/                          # LAYER 2 — one per project (Steps 25–34)
├── adapters/                         # LAYER 3 — one per surface (Steps 35–39)
├── validation/                       # deterministic checks (Steps 44–45)
├── evidence/                         # evidence records
├── state/                            # continuity snapshots
└── manifests/                        # Steps 40, 42
```

### 5.1 Structural rules

- **SR-1** — No file under `framework/` may name a project, a vendor, or a product. Enforced by a validation check, not by review discipline.
- **SR-2** — No file under `profile/` or `adapters/` may redefine a Core schema. They reference and instantiate.
- **SR-3** — Every artifact declares `artifactId`, `version`, `status`, `schemaVersion`, and `governedBy`.
- **SR-4** — Directory position is not authority. An artifact's authority comes from its declaration and the Source Registry, never from where it sits.

---

## 6. Extension points

Extension is **declared and validated**, never ad hoc. Five extension points exist; nothing else is extensible without a governed framework change.

| # | Extension point | Extends by | Bounded by |
|---|---|---|---|
| **EP-1** | **Project Profile** | Supplying registry instances, bindings, terminology, constraints | May not create states, weaken controls, or add authority |
| **EP-2** | **Workbench Adapter** | Mapping framework behavior to a surface; declaring capability gaps | May not rename/merge/skip/reorder states or gates, collapse independent steps, or originate authority |
| **EP-3** | **Role contract set** | Adding or specialising roles within the approved roster | May not grant self-approval or exceed the role's declared authority |
| **EP-4** | **Workflow definitions** | Adding governed work paths | Must use the canonical lifecycle and existing role contracts |
| **EP-5** | **Verification mechanisms** | Adding deterministic checks and evidence classes | May not reduce an existing requirement's verification obligation |

**EP-0 — the meta-rule.** Any extension that would weaken a non-waivable control is not an extension. It is a governance change requiring the owner's explicit approval, and the framework must refuse it structurally rather than accept it and log a warning.

### 6.1 Capability gaps are first-class

When an Adapter cannot satisfy a control, the framework requires four things recorded together: the control, the reason, the compensating mechanism, and who accepted the residual risk. A gap that is merely noted is not mitigated. This is what makes platform limitations visible *before* work is delegated to a platform that cannot govern it (the Step 41 compatibility matrix is the consolidated view).

---

## 7. Authority interfaces

Authority enters the framework through exactly **four** interfaces. There is no fifth, and nothing may originate authority internally.

### AI-1 — Source Authority Interface *(built at Step 3)*
Governing content enters via registered sources carrying identity, provenance, version, status, immutability, scope, and use classification. Resolution is per-subject (CR-1), explicit about supersession (CR-2), overlay-aware (CR-3), and fails to a stop rather than a guess (CR-4).

### AI-2 — Human Authority Interface *(built at Step 10)*
Certain decisions require a named human. The framework holds work in a safe state until that decision is recorded. Silence, elapsed time, agent recommendation, majority, role relabeling, and emergency status are **never** approval. An agent may never be a delegated human authority. Delegation and pre-authorization, where permitted at all, require a named human, explicit scope, explicit criteria, and an expiry.

### AI-3 — Deterministic Verification Interface *(built at Step 13)*
Reproducible non-judgmental checks — tests, schema validation, static analysis, contract comparison, hashing, scanning. This is the only interface that produces conclusions without judgment, and it is therefore the backbone of independence on platforms where model diversity is unavailable.

### AI-4 — Independent Review Interface *(built at Step 9)*
Judgment produced under conditions that make it genuinely independent of the work being reviewed. Independence is a property of the **execution boundary**, not of the label attached to the reviewer. A continuation of the same reasoning pass, relabeled, never qualifies — it carries forward the implementer's assumptions and cannot reconstruct a conclusion it never left.

### 7.1 The closure rule

> Every gate must close through at least one authority interface. A gate that closes because an agent said it was closed is not a gate.

---

## 8. Validation approach

Validation is layered, and each layer answers a different question.

| Layer | Question | Method | Step |
|---|---|---|---|
| **V1 — Structural** | Do artifacts conform to their schemas? | Automated schema validation | 44 |
| **V2 — Referential** | Do all IDs, versions, and source links resolve? | Automated graph checks | 44 |
| **V3 — Directional** | Is authority acyclic and downward-only? | Automated dependency analysis | 19, 44 |
| **V4 — Coverage** | Does every requirement, gate, and role have a verification path and an owner? | Automated set comparison | 13, 18, 44 |
| **V5 — Behavioral** | Do controls behave correctly, including adversarially? | Regression portfolio with negative and adversarial cases | 45 |
| **V6 — Operational** | Does the whole system work end-to-end on representative work? | Controlled governance dry run | 46 |
| **V7 — Retrospective** | Would it have routed past real decisions correctly? | Governance replay | 47 |
| **V8 — Sustainability** | Is the control load survivable in practice? | Measured metrics against owner-approved thresholds | 48–49 |

### 8.1 Validation principles

- **VP-1 — Deterministic or it is not validation.** A check that depends on model judgment is a review, not a validation. Both are legitimate; they are not interchangeable, and evidence must record which was used.
- **VP-2 — Negative cases are mandatory.** A framework that only proves it permits correct work has proven nothing. It must demonstrably *refuse* self-approval, silent exception, fabricated evidence, and unapproved bypass.
- **VP-3 — Failures are never resolved by weakening the control.** A failing check is fixed by correcting the artifact or by a governed, approved change — never by relaxing the assertion to make it pass. This is itself a validated property.
- **VP-4 — Evidence honesty is absolute.** A criterion is never reported PASS if the branch was not examined. Unknown remains unknown until resolved. A frozen record is never rewritten to match later evidence; later evidence is a separate record.
- **VP-5 — Self-validation is insufficient alone.** The framework's own validation cannot be the sole basis for its approval. Step 54 requires the human owner.

---

## 9. Framework lifecycle and status

| Stage | Version | Meaning |
|---|---|---|
| Construction | `0.x` DRAFT | Steps 1–51. Artifacts exist and evolve; nothing is baselined |
| Validation candidate | `1.0-rc` | Step 43–52. Complete and under validation |
| Approved | `1.0` | Step 54. Explicit owner approval recorded |
| Frozen baseline | `1.0-FROZEN` | Step 55. Versions, hashes, manifests, evidence immutably fixed |

The framework is **not** authoritative over project work until Step 54. Until then it is under construction, and the governing execution layer remains the project's existing approved policy, responsibility model, registries, transfer package, and explicit owner direction.

---

## 10. Load-bearing decisions requiring owner ratification

Four decisions in this specification propagate into every artifact built in Steps 2–53. Reversing any of them later means rebuilding, not editing. They are presented for explicit ratification.

### D-PAF-01 — Contract-and-instance binding for Steps 6–10

**The tension:** Steps 6–10 direct me to *integrate* the five approved governance registries, and Step 6 says framework state transitions must "match the approved registry exactly." But those registries are project-named artifacts, and Layer 1 must be project-independent. Taken literally, integrating them into the Core violates portability. Taken loosely, "match exactly" loses its force.

**Proposed resolution:** the Core defines the *contract* each registry must satisfy — schema, semantics, transition rules, resolution behavior. The project's registries are bound as **instances** in the Profile (Steps 29–33). "Matches the approved registry exactly" is satisfied and machine-verified *when the Profile is loaded*: a deterministic check asserts that the framework's resolved transition table is identical to the bound registry's, with zero additions, removals, or renames.

**Why this way:** it satisfies both requirements without weakening either. The alternative — embedding the registry content in the Core — would produce a framework that governs this project and no other, failing the Step 1 portability mandate and PR-2.

**What ratifying this costs you:** a small indirection. Reading the Core will not tell you what the states *are*; you read the Profile for that. The deterministic equality check is what guarantees they agree.

### D-PAF-02 — Fail-closed defaults (CR-5)

Unbound or unmapped controls default to their **most restrictive** form rather than being inactive. An unmapped human-approval obligation is non-waivable until classified. An unclassified risk is treated at the higher class. An undeclared deferral is treated as structural.

**Why:** the opposite default makes an omission indistinguishable from a decision, and omissions are the dominant failure mode in AI-assisted work. Cost: early construction will surface controls in their strictest form and require deliberate relaxation. That friction is the point.

**Owner amendment (ratified 2026-08-13):** strict mode must never be silent. Whenever a control is unbound, the framework raises an `unconfiguredControlWarning` naming the control, stating the strict-mode behavior it is running under, and requiring owner notification. Records the framework produces and the operator's own reporting must both carry it. Enforced by check `V4-07`; the warning record's `ownerNotified` field is mandatory.

### D-PAF-03 — Step 1 approval interpretation

Step 1's completion criterion reads "**Approved** framework specification." This is ambiguous, and the ambiguity reaches the build. It could mean (a) formal owner approval, or (b) approval through the framework's own review process — which cannot exist at Step 1, since the framework is what Step 1 begins building. Meanwhile the human-approval registry's default rule says any explicit approval obligation not matched to an approval class is non-waivable and non-delegable until classified.

Read strictly, that would place a formal owner gate on Step 1 — and by the same logic on every step whose criterion says "approved," which is most of them. Fifty-plus formal gates before Step 54 would fail the sustainability test that Framework v1 approval itself depends on.

**Proposed resolution:** Step 1 requires your **explicit ratification of the load-bearing decisions in this section** — because Steps 2–53 inherit them — but is not a formal non-waivable approval gate. The formal framework approval remains **Step 54**, where the execution plan puts it. Intermediate steps proceed on construction authority, with owner ratification requested only where a decision is load-bearing or genuinely ambiguous.

**This is a governance interpretation, not a drafting choice.** I am surfacing it rather than resolving it silently. If you prefer the strict reading, say so and I will gate every "approved" criterion — it will be considerably slower, and I would expect it to fail Step 48's sustainability measurement, which is itself useful information.

### D-PAF-04 — Independence rests on deterministic checks plus clean-context invocation

Given that cross-model-family review is unavailable within a single AI platform, the framework's independence backbone is **AI-3** (deterministic checks) reinforced by **clean-context separate invocation** and **human review**. This shapes Steps 9, 13, 21, and 45: wherever a meaningful deterministic check can exist, the framework will require one rather than accepting judgment alone.

**Consequence:** more of the framework is expressed as executable checks than a purely document-driven design would produce. That is deliberate, and it is what makes independence real on this platform rather than asserted.

---

## 11. Step 1 completion status

| Required element | Section | Status |
|---|---|---|
| Generic framework purpose | §1 | Complete |
| Boundaries | §2 | Complete |
| Portability model | §3 | Complete |
| Configuration model | §4 | Complete |
| Directory/package structure | §5 | Complete |
| Extension points | §6 | Complete |
| Authority interfaces | §7 | Complete |
| Validation approach | §8 | Complete |

**Complete when:** approved framework specification suitable to govern all later framework artifacts.
**Current state:** drafted; awaiting ratification of D-PAF-01 through D-PAF-04 (§10).

**Not done, deliberately:** no schema written, no registry bound, no project content imported, no Step 2 artifact created. Steps 2–10 proceed on ratification.
