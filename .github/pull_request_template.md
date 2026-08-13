## Work item

- **Work item ID:**
- **Work type:** <!-- FEATURE_SLICE | DEFECT | ARCHITECTURE_CHANGE | SECURITY_CHANGE | DOCUMENTATION_CHANGE | THEME_CHANGE | METHODOLOGY_CHANGE | COMMERCIAL_CHANGE | PERFORMANCE_CHANGE | DEPENDENCY_UPGRADE | SPIKE | EMERGENCY -->
- **Slice / area owned:**

## Risk classification

- **Risk class:** <!-- R1 | R2 | R3 | R4 -->
- **Triggers fired:** <!-- e.g. R4.1 — reference the class-qualified trigger index, not prose -->
- **Basis:** <!-- why this class, and which higher-class conditions were checked and did NOT fire -->

> Uncertainty routes **upward**. If impact cannot be bounded from available evidence, this is R4.

## Smallest coherent change (CPM-1)

<!-- What is the smallest change that achieves the outcome? If this PR does several things, say why they cannot be separated. -->

## Contract and behaviour preservation (CPM-2)

- [ ] No public contract changed
- [ ] Public contract changed — version bumped, consumers identified, compatibility path recorded below

## Design deferral declaration (no-migration / P-8)

- [ ] No deferral in this change
- [ ] Deferred **functionality only** — supporting design remains above the cut line
- [ ] Deferred **structural design** — REQUIRES architecture review and owner approval

> Deferring functionality is a scheduling decision. Deferring design that accumulated data will later require is not reversible without transforming live data.

## Evidence

<!-- Link the actual artifact. A description of a result is not evidence. -->

| Evidence class | Link | Reproduction command |
|---|---|---|
|  |  |  |

- [ ] Every criterion reported PASS was actually examined
- [ ] Anything not examined is marked NOT_EXAMINED with a reason
- [ ] No result is asserted without a linked, reproducible artifact

## Testing (CPM-4)

- [ ] Impact-based tests run
- [ ] Full portfolio run (required for R3/R4 or shared-asset change)
- [ ] Tenant isolation verified (required if any canonical data path touched)

## Recovery (CPM-3)

- **Recovery class:** <!-- ROLLBACK | ROLL_FORWARD | CONTAINMENT | NOT_RECOVERABLE_BY_DESIGN -->
- **Procedure:**
- [ ] Recovery procedure has been **tested**, not merely written

> An untested recovery is not a recovery.

## Independent review (CPM-5)

- **Mechanism used:** <!-- SEPARATE_INVOCATION_CLEAN_CONTEXT | DETERMINISTIC_NONJUDGMENTAL_CHECK | HUMAN_REVIEW | DIFFERENT_MODEL_OR_MODEL_FAMILY -->
- **Reviewer (distinct from implementer):**

> A different role label alone never qualifies. R4 requires a deterministic check **plus** independent judgment.

## Human approval

- **Approval class required:** <!-- or NONE -->
- **Approved by / date:**

> Never satisfied by silence, elapsed time, agent recommendation, or emergency status.

## Documentation

- [ ] Documentation updated in this PR, or
- [ ] No documentation impact (state why)

## Exceptions

- [ ] None
- [ ] Exception ID: ______  expiry: ______  compensating control: ______
