# Release and Tag Conventions (Step 72)

## Version identity

```
v<MAJOR>.<MINOR>.<PATCH>
```

| Increment | When |
|---|---|
| MAJOR | Backward-incompatible public contract change (an R4 trigger) |
| MINOR | New capability, backward compatible |
| PATCH | Defect correction, no contract change |

## Tag rules

1. **Tags are immutable.** Once pushed, a tag is never moved or deleted. A mistake gets a new tag.
2. **A tag is created only from `main`** at a commit whose required checks passed.
3. **A tag is not a release.** Tagging records identity; releasing requires the `PRODUCTION_RELEASE` human approval.
4. Every tag maps to exactly one framework release record in `docs/release/`.

## Release record — required contents

A GitHub Release without these is incomplete:

- Work items included, by ID
- Risk class of the release (highest of its constituents)
- Evidence bundle reference and content hashes
- Recovery/rollback procedure, **verified**
- `PRODUCTION_RELEASE` approval — approver and date
- Residual risk record, and any open exception with its expiry
- Deployment record: artifact version and target environment

## Lifecycle mapping

| Repository event | Lifecycle state | Not the same as |
|---|---|---|
| PR merged to `main` | `VERIFIED` (if gate evidence complete) | acceptance |
| Tag pushed | `RELEASE_CANDIDATE` | released |
| Release published + owner approval | `PRODUCTION` | Stable |
| Observation period complete + `STABLE_STATUS` approval | `STABLE` | — |

**STABLE is never inferred from elapsed time without incident.** It requires explicit human approval after a recorded observation period.
