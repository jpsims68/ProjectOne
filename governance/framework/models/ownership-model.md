# Ownership Model (Step 4)

**Artifact ID:** `PAF-MODEL-OWNERSHIP` · **Version:** 0.1 · **Layer:** CORE
**Contract:** `paf.ownership-registry.schema.json`

## 1. Why this exists

Unowned work is unreviewed work. Every governed artifact and work type must resolve to an accountable owner and at least one review path *before* implementation, because ownership determines who reviews, who approves, and who is accountable when it fails.

## 2. Owned entity classes (generic)

The core defines the *kinds* of thing requiring ownership; a Profile maps its artifacts onto them.

| Class | Notes |
|---|---|
| `CAPABILITY_SLICE` | Independently testable vertical capability |
| `SHARED_PLATFORM_COMPONENT` | Protected: deliberately small, promotion-gated |
| `CANONICAL_DATA` | Protected: identity, keys, grain |
| `PUBLIC_CONTRACT` | Protected: versioned, directional, consumer-visible |
| `SCHEMA_OR_STRUCTURAL_DEFINITION` | Protected: structural change is not an ordinary change |
| `SEED_OR_REFERENCE_DATA` | |
| `SCHEDULED_JOB_OR_PIPELINE` | |
| `INGESTION_PATH` | |
| `MATERIALIZATION` | |
| `DOCUMENTATION_ARTIFACT` | |
| `GOVERNANCE_CONTROL` | Protected |
| `OPERATIONAL_ARTIFACT` | |
| `TEST_ASSET` | |
| `EVIDENCE_RECORD` | |

## 3. Rules

**No orphans.** Every governed entity resolves to exactly one accountable owner and at least one review path. An unmapped entity yields `OWNERSHIP_UNRESOLVED` — an interrupt state, not a warning.

**Accountability is singular.** Work may be shared; accountability is not. "The team owns it" is an unowned artifact.

**No self-approval.** An owner may not be the sole approver of a change they authored. This is structural, not cultural — the review path must name someone other than the author.

**Protected assets change differently.** Entities flagged `sharedAssetProtection` require explicit impact analysis, identification of affected consumers, and retesting of those consumers. The cost of changing shared things is the reason shared things stay small.

**Ownership is declared, not inferred from location.** An artifact's directory says nothing about who owns it (SR-4).
