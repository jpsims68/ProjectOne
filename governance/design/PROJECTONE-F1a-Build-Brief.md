# ProjectOne — F1a Build Brief

**Status:** ACTIVE — the production build entry for F1a
**Supersedes for production use:** `406-ProjectOne-DDL-Build-Kickoff-Brief.md`, which is explicitly **PILOT ONLY** (fictional ITSM client, obsolete fabricated dataset). §1–§10 of 406 remain a valid standing reference and are cited here rather than restated.
**Authority:** derived. The DDR and Profile are canonical. Where this brief and a canonical source disagree, the canonical source wins and this brief is the defect.
**Created:** 2026-08-24 — closes B2.12 PRE-3

---

## 0. Read this first

**F1a is the least reversible thing in this build.** It is the schema everything else sits on. Once data exists in it, changing its shape means transforming live data — the migration DDR **P-8** exists to prevent.

Three things follow:

1. **Design-ahead is not optional here.** F1b immediately follows and is marked **IMMOVABLE** in the roadmap precisely so stopping later defers *functionality*, never *design*.
2. **Read the effective DDR, not the DDR file.** Three approved decisions exist only as overlays and appear nowhere in `201`: D-67, D-68, and the event-order field name. See §2.
3. **You cannot verify this by running it and looking at the output.** Expected answers must be derived independently. See §6.

---

## 1. Scope

**In F1a** — from the roadmap: *core spine — event model, base dims, Tier-1 serving, closure ancestry (D-43)*. Mapped onto 406 §5:

| Cluster | Contents |
|---|---|
| **A** Core event-log spine | `event`, `case_master`, `event_case_assignment` |
| **B** Dimensional backbone | 4 universal dims, `entity_dim_1..4`, surrogate-keyed, SCD-2-upgradeable |
| **F** Serving layer | **Tier-1 only.** Tier-2 is F7 and builds no tables |
| **D-43** | Closure ancestry for subtree filtering |
| **M** Ingestion load-run spine | `ingestion_run`, `mapping_version` — **owner decision 2026-08-24** |

**On cluster M.** The roadmap places design-ahead reservations in F1b, but the `event` fact carries `load_run_key` and an FK pointing at a table that does not exist is unenforceable. Adding the constraint later means altering a populated fact — the migration P-8 forbids. Two small tables now; the boundary moved deliberately.

**Not in F1a:**

| | Where | Note |
|---|---|---|
| OCPM D-35, baseline D-53, script-catalog D-60, access model D-61 | **F1b — IMMOVABLE** | Reserved-but-dormant. Tables built, unpopulated |
| C activity grouping (D-38) | Later | **Blocked by OD-06** — `603-Activities_Groupings_for_Mapping.md` not yet acquired |
| E identity/tenancy, G, H, I, J, K, L, N | Later units | `tenant_key` still appears on every tenant-scoped table (D-16) |

---

## 2. Read the effective DDR, not the file

**The DDR file is wrong about itself in two ways**, both settled by AB-CM-029 and AB-CM-030:

- Header reads **v1.35**. Current authoritative version is **v1.37**.
- Stated range D-01…D-66. **Effective range is D-01…D-69.**

**Three decisions appear nowhere in the file.** Searching `201` returns zero occurrences of each:

| Decision | Overlay | Why it matters to F1a |
|---|---|---|
| Event-order field name **`event_sequence_num`** | AB-CM-021 | **A column name in the first table you write.** Not `sequence_num` |
| **D-68** business-unit assignment precedence | AB-CM-022 | Determines how `event.business_unit_key` resolves |
| **D-67** data-driven theming | AB-CM-011 | Frontend; not F1a, but part of the effective range |

The total sort is `(from_ts, event_sequence_num, event_key)`. D-62 controls the field name and the source/synthesis cascade; D-47 controls ordering semantics.

**All 29 overlays are in** `governance/overlays/PROJECTONE-999-Overlay-Register.json`. `governance/profile/PROJECTONE-Source-Registry.json` records which sources carry overlays and warns that reading a base file alone yields a stale answer.

---

## 3. Constraints that bind this build

Read **Build Constraints Guide §1–§9** in full. The ones that bite hardest here:

**§2 — the OQ-13 design tax.** OQ-13 is open between Azure SQL Database and Managed Instance, so nothing may depend on an MI-only capability. `check_cloud_target_compatibility.py` is a **required status check** and will fail the build on SQL Agent objects, cross-database three- and four-part names, linked servers, CLR, `USE`, file placement, backup/restore, instance configuration and more.

> **This check has never run against real DDL.** F1a is its first live exercise. Expect it to fire; that is the control working.

**A trap in the other direction (CF-006).** `REGEXP_LIKE` and family need compatibility level 170 — SQL Server 2025. Your local instance is 2022, max 160. **They work on Azure and fail locally.** The compatibility check does not cover this direction and correctly should not. Needing one is a decision to raise, not a workaround to code around.

**§8 — computation placement.** Two questions, in order: does the input grow with tenant data volume — if yes, set-based SQL, no exception. Can SQL express the operation — if yes, SQL anyway.

**§4 — no migration framework.** Schema is numbered, forward-only SQL scripts under the db-build-sop. A schema change requiring data transformation is a **design failure**, not a migration task.

---

## 4. Modeling principles

From 406 §6, unchanged and still binding:

- **Surrogate keys everywhere** (D-11); facts carry surrogate FKs (D-34) — enables SCD-2 upgrade without touching facts
- **SCD-2-upgradeable** dims (D-34); `resource_dim` is SCD-2 from day one (D-29)
- **`tenant_key`** on every tenant-scoped table (D-16)
- **Nullable reservations** for dormant items — present in schema, unpopulated
- **3NF** per db-build-sop

**Resolved, build concretely — no stubs:** slot count and type split (55 event: 30/15/10; 20 `case_master`: 10/6/4); fixed-front dim list plus `entity_dim_1..4`; event natural-key cascade (D-62, Tier A `tenant+process+source_event_id`, else Tier B).

---

## 5. Open items to surface, not invent

From 406 §7. **Propose options; do not decide silently.**

1. **Tier-1 base-metric materialization shape** — grain of the pre-digest rows. Not in the DDR.
2. **Closure table versus materialized path** for hierarchy ancestry — required for G-15 subtree filtering.
3. **Tier-1 serving strategy — build to D-49 (DIRECTIONAL).** Do **not** build a general cube layer.
4. **Successor stamping — four hazards (D-50).** Not write-once, so open cases carry a null successor until a later batch extends them. Chains are per-scenario. Changing `df_tiebreak` invalidates every chain. Variants are not derivable from successors.
5. **CR-5 not fully satisfied** — D-48 stores items 1–2 on `process`; item 3 remains.
6. **Registry must support "do not import this field"** — an explicit ignore placement.
7. **Resolver / tenant-registry placement** — separate control DB versus in-line.
8. **Default-scenario `case_key` denormalization onto `event`** — build-time tuning choice.

---

## 6. Verification

**Dataset:** `data/pilot/` — 3,411 events, 400 cases, equipment maintenance across three depots. Generated by `tools/generate_pilot_log.py`, deterministic, reproducible, and enforced by a required check.

**Conforms to 504**, not to a schema — the schema is F1a's output.

**The rule that makes this meaningful (Guide §9b):**

| Practice | Status |
|---|---|
| Expected values derived from the generator or independently | **Required** |
| Expected values captured from a system run and frozen | **PROHIBITED for correctness** |

Capturing output is legitimate for *regression*. It is not legitimate for *correctness* — it proves behaviour is stable, **including stably wrong**.

**Three questions F1a testing must answer (Guide §9a):**

1. Does the schema accept the contract? *If loading the pilot log requires editing the pilot log, the schema is wrong — not the data.*
2. Do dimension resolutions produce the right answer? **32 cases span a technician depot change**, so a join on the resource's *current* row returns a plausible wrong answer and is detectable.
3. Are Tier-1 results correct — not merely produced?

**Edge cases the dataset deliberately carries:** 23 duplicate timestamps (forces `event_sequence_num` to matter) · 32 depot-change-spanning cases (D-68 as-of) · 3 depots / 9 areas (D-43) · 68 rework cases, 18 self-transitions (variants) · 10 cases open at the boundary (proves reopening is not *forbidden*) · 2,195 Tier A / 1,216 Tier B rows (both D-62 key tiers).

**CI cannot verify most of this.** No SQL Server, and none before OQ-13. Two of three test classes are **owner-executed**, as canonical Steps 108 and 109 were. Results are evidence only when the owner runs them and returns output.

---

## 7. Standing frame

**Process- and industry-agnostic** (406 §1). Naming is slot-generic: `business_unit_dim`, never `corporate_bu_dim`; `entity_dim_N`, never `vendor_dim`. The pilot dataset is equipment maintenance because that is nobody's target market — it is **not** a vertical.

**No later migrations** (406 §2, DDR P-8). Reserved-but-dormant structures are built now, unpopulated.

**Technology registry is an allowlist.** Anything not listed ACTIVE is DENIED by default.

**Process discipline** (406 §8): timestamps to the minute in America/New_York; read the current version before editing a cumulative artifact and state which version you are building from; DDR / PRD / Manifest / Continuity Brief are Tier-1 canonical, edited surgically.

---

## 8. Definition of done

F1a is complete when:

- Every cluster A, B, F(Tier-1), M table exists, with D-43 ancestry
- The pilot log loads with **no edit to the pilot log**
- Dimension resolutions verified, including at least one as-of case spanning a change
- Tier-1 results verified against **independently derived** expected answers
- All required status checks pass, including cloud-target compatibility against real DDL for the first time
- Open items in §5 are **surfaced and decided**, not silently resolved
- Owner-executed test results returned and recorded as evidence

**F1a is not complete because it runs.** It is complete when its output has been verified against answers derived without it.
