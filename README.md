# ProjectOne

Process Intelligence as a Service (PIaaS) — multi-tenant, process- and industry-agnostic.

**Status:** Repository scaffold. Production application implementation is **NOT AUTHORIZED**
until the governed authorization gate is passed.

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
slices/      one directory per vertical slice; each owns its full stack
platform/    deliberately small approved shared platform
contracts/   versioned, directional, acyclic public contracts — the ONLY cross-slice path
data/        canonical shared data foundations (platform-owned)
ops/         migrations, jobs, ingestion, deployment artifacts
config/      configuration hierarchy; secret NAMES only, never values
tests/       cross-cutting suites; slice-owned tests live in the slice
docs/        documentation by audience, with update triggers
governance/  frozen framework baseline, profile, adapters, evidence
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
