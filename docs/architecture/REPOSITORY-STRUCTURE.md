# Repository Structure (Steps 57–62 design, Step 73 scaffold)

Directories are created when real content lands in them. Git does not track empty
directories, so this document — not a set of placeholder files — is the record of intended
structure.

**Production application implementation is NOT AUTHORIZED.** No product code exists yet.

## Top level

| Path | Owner role | Rule | Traces to |
|---|---|---|---|
| `slices/` | slice owner | One directory per vertical slice — the smallest independently testable capability spanning all layers. Each slice owns its full stack. | VSA-1, VSA-6 |
| `platform/` | ROLE_ARCHITECTURE | Approved shared platform only. Deliberately small; every addition is a governed promotion. **Protected.** | VSA-2, VSA-5 |
| `contracts/` | ROLE_ARCHITECTURE | Versioned, directional, acyclic public contracts. The **only** permitted cross-slice dependency path. **Protected.** | VSA-3 |
| `data/` | ROLE_ARCHITECTURE | Canonical shared data foundations — migrations, seeds, field catalog. **Protected.** | VSA-4 |
| `ops/` | ROLE_SECURITY_RELEASE | Jobs, ingestion, materializations, deployment artifacts. Every artifact version-controlled with named ownership. | VSA-8 |
| `config/` | ROLE_CODING (+ security review) | Configuration hierarchy and environment overrides. Contains secret **names** only, never values. | CONFIG, SEC |
| `tests/` | ROLE_QUALITY | Cross-cutting suites. Slice-owned tests live inside the slice. | VSA-7, CPM-4 |
| `docs/` | ROLE_TECH_DOC | Documentation by audience, with explicit update triggers. | DOC |
| `governance/` | ROLE_ORCHESTRATOR | Frozen Framework v1 baseline, profile, adapters, evidence. **Protected.** | AGENT, DOD |
| `.github/` | ROLE_SECURITY_RELEASE | CODEOWNERS, workflows, templates. The enforcement surface. **Protected.** | CPM-5, CPM-6 |

## Dependency direction
slices → contracts → platform → data
One way only. A slice never imports another slice. Platform never imports a slice.
**Enforced by the Slice boundaries check — a violation fails the build, not the review.**

## Slice layout
slices/<slice-name>/
api/ slice-owned HTTP surface
domain/ slice-owned business logic and feature policy
data/ slice-owned data objects only (canonical data is platform-owned)
ui/ slice-owned components; consumes the design system, never forks it
tests/ unit/ integration/ contract/ — runnable in isolation
docs/ slice-level documentation
slice.manifest.json REQUIRED

A slice without a valid `slice.manifest.json` is not a slice — it is ungoverned code.
The manifest declares slice id, owner role, consumed and produced contracts with versions,
platform extension points used, lifecycle state, and risk class.

## Platform sub-areas
`tenancy/` `auth/` `persistence/` `observability/` `theming/` `extension-points/`
Moving code into `platform/` is a governed promotion requiring architecture review, impact
analysis, consumer identification, retest of affected consumers, and human approval.
**Convenience is never a promotion basis.**

## Configuration hierarchy
config/defaults/ safe defaults, committed
config/environments/<env>/ per-environment overrides, committed, no secrets
runtime injection secret values only — never committed, never logged
Defaults fail closed: absent configuration yields the most restrictive behaviour.

## Test areas
`contract/` `security/` `tenant/` `gui/` `performance/` `e2e/` `fixtures/` `governance/`
Test locations map to the 360-decision verification map, so evidence is linkable by
decision ID.

## Documentation areas
`developer/` `architecture/` `api/` `data/` `operations/` `user/` `admin/` `onboarding/`
