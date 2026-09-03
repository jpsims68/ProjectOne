# ProjectOne

Process Intelligence as a Service (PIaaS) — multi-tenant, process- and industry-agnostic.

**Status:** Repository scaffold. Production application implementation is **NOT AUTHORIZED**
until the governed authorization gate is passed.

## Start here

**If you are picking this up cold — human or agent — read these four, in order:**

| Read | Why |
|---|---|
| [`governance/state/PAF-Continuity-Snapshot-FrameworkV1.json`](governance/state/PAF-Continuity-Snapshot-FrameworkV1.json) | Where the build actually is. Current step, open decisions, open risks, exceptions, corrections, and `carriedForward` — work that exists outside this repository and would otherwise be lost. |
| [`governance/baselines/`](governance/baselines/) | The last known-stable baseline: versions, hashes, environment, test and security results, recovery point — and an explicit `whatIsNOTProven` section. |
| `canonicalStepCrosswalk` (inside the snapshot) | What each build step required and what actually satisfies it. Do not assume a step is complete because a number appears somewhere. |
| `201-ProjectOne-Design-Decision-Record.md` — **not in this repository** | The design canon. Every locked decision and its reasoning. It lives in the Claude Project, not here — ask the owner for it. Nothing in this repository is a substitute, and no version is quoted here on purpose: the Project Manifest records the current one. |

Also here: [`docs/paf-starter-kit/`](docs/paf-starter-kit/) — the portable governance framework extracted for use on a **different** project. Nine documents covering orientation, realistic time estimates, an AI kickoff prompt, bootstrap instructions, and the failures already paid for on this build. Not needed to work on ProjectOne; kept here because these documents cannot be rebuilt from anything else in this repository.

**The repository is the system of record for build state** — what exists, what passed, what is proven. It wins any disagreement about state with a summary, a branch, a working copy, or anyone's recollection, including the owner's. Clone fresh and read state from here.

**The DDR is the source of truth for design** — what was decided and why. It is not in this repository. Neither overrides the other, because they do not overlap: this repository does not decide design, and the DDR does not record build state. If they appear to conflict, you have crossed a subject boundary — stop and ask the owner.

**Two things a successor must not do:**

- Do not trust a green check that has never been proven capable of going red. Run `governance/scripts/bootstrap_selftest.py` first.
- Do not begin application implementation. It is NOT AUTHORIZED until the explicit owner authorization gate is passed.

## Governance

This repository is governed by the Portable Agent Framework v1.0 (frozen baseline).

| Document | Purpose |
|---|---|
| [`governance/BRANCH-STRATEGY.md`](governance/BRANCH-STRATEGY.md) | Branch model and what a merge does and does not mean |
| [`governance/OWNERSHIP-MAP.md`](governance/OWNERSHIP-MAP.md) | Path → framework role ownership, and the solo-owner limitation |
| [`governance/EVIDENCE-CONVENTIONS.md`](governance/EVIDENCE-CONVENTIONS.md) | Where evidence lives and why CI logs are not evidence |
| [`governance/RELEASE-CONVENTIONS.md`](governance/RELEASE-CONVENTIONS.md) | Version, tag, and release identity |

## Structure

```
PRESENT TODAY
  app/         baseline shell only — one health endpoint, no features
  tests/       cross-cutting suites; slice-owned tests will live in the slice
  docs/        documentation by audience, with update triggers
  governance/  frozen framework baseline, profile, adapters, evidence, state

PLANNED — these directories DO NOT EXIST YET
  slices/      one directory per vertical slice; each owns its full stack
  platform/    deliberately small approved shared platform
  contracts/   versioned, directional, acyclic public contracts — the ONLY cross-slice path
  data/        canonical shared data foundations (platform-owned)
  ops/         migrations, jobs, ingestion, deployment artifacts
  config/      configuration hierarchy; secret NAMES only, never values

They appear when the first vertical slice is authorized. The split is stated
explicitly because a reader looking for a directory that does not exist wastes
time deciding whether something is broken.
```

## Checks

Every pull request runs:

- **Slice boundaries** — cross-slice imports are a build failure, not a review comment
- **Secret protection** — refuses committed secret values
- **PR governance metadata** — risk class, evidence, recovery, deferral declaration
- **Build / lint / test**, **dependency and static security scan**

Run them locally before pushing:

```bash
python3 governance/scripts/check_slice_boundaries.py
python3 governance/scripts/check_no_secrets.py
```
