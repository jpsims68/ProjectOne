# Registry Binding Model (Steps 6–10)

**Artifact ID:** `PAF-BINDING-MODEL` · **Version:** 0.1 · **Layer:** CORE
**Implements ratified decision D-PAF-01.**

## 1. The problem this solves

Steps 6–10 require the framework to *integrate* five approved governance registries, and Step 6 requires framework state transitions to match the approved lifecycle registry **exactly**. But Layer 1 must remain project-independent (PR-2, SR-1). Embedding the registries in the core would produce a framework that governs one project and no other.

## 2. The resolution

**The core defines contracts. The profile supplies instances. A deterministic check proves they agree.**

```
CORE contract                    PROFILE instance              Proof
─────────────────────────────    ──────────────────────────    ────────────────────
paf.lifecycle-registry           <project> lifecycle           equality check
paf.risk-standard                <project> risk standard       conformance + equality
paf.exception-registry           <project> exception registry   conformance + coverage
paf.independence-standard        <project> independence std     conformance
paf.human-approval-registry      <project> approval registry    conformance + invariant
```

The contract states *what must be true of any such registry*. The instance states *what is true for this project*. Neither is redundant, and the core never learns the instance's content.

## 3. What "matches exactly" means, operationally

At Profile binding (Steps 29–33), a deterministic check asserts the framework's resolved transition table is **identical** to the bound registry's:

- every state present, none added;
- no state renamed, merged, split, or reordered;
- every `allowedNext` edge identical in both directions;
- every interrupt state present with its resume rule;
- auxiliary tracks mapped, never substituted for the primary state.

Any difference is a failure, not a variance. The check records the instance's `boundInstanceHash`, so a later silent edit to the registry breaks the binding rather than quietly changing behavior.

## 4. Binding states

| State | Meaning | Framework behavior |
|---|---|---|
| `BOUND` | Instance supplied, conformance check passed | Control operates per instance |
| `UNBOUND_STRICT_MODE` | No instance supplied | **Control is NOT disabled.** It runs in its most restrictive form (CR-5) and an `unconfiguredControlWarning` is raised with `ownerNotified` |

Per the owner's ratified amendment to D-PAF-02, strict mode is never silent.

## 5. Strict-mode behavior per contract

| Contract | Behavior while unbound |
|---|---|
| Lifecycle | No transition may be asserted; work holds at entry state |
| Risk | Every work item classified at the **highest** class |
| Exception | **No** exception may be granted |
| Independence | Every review requires a qualifying mechanism plus human review |
| Human approval | Every approval obligation is non-waivable and non-delegable |

## 6. Conformance evidence

`validation/conformance_probe.py` is the reproducible check behind this model. It validates each approved instance against its core contract without binding it, proving the contracts are neither too loose (accepting anything) nor too tight (rejecting the real registries).

**Run 1 result: 5/5 conform.** Two contract defects were found and corrected during this run — the lifecycle contract mis-named the authority block, and the risk contract wrongly assumed every class is trigger-defined when the residual lowest class is conjunctive. Both were defects in the contracts, not the instances. Corrected by modeling reality more precisely, not by loosening the assertion (VP-3).

## 7. Adapter prohibition

No adapter may invent, rename, merge, skip, or reorder a governed state or gate; nor collapse required independent steps into one invocation for convenience. An adapter that cannot express a control declares a capability gap with a compensating mechanism and a named risk acceptor. A gap that is merely noted is not mitigated.
