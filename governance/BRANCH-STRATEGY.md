# Branch Strategy (Step 64)

## Model

```
main ──────────────────────────────────────────►  protected, always releasable
  ▲
  └── work/<work-item-id>-<short-desc>            one branch per governed work item
```

**Deliberately simple.** No develop branch, no release branches, no gitflow. With one
human and a governed work-item model, extra long-lived branches add merge surface without
adding control. Branch complexity is not governance.

## Rules

| Rule | Basis |
|---|---|
| `main` is protected. No direct pushes. | CPM-6 controlled promotion |
| One branch per work item, named `work/<id>-<desc>` | CPM-1 smallest coherent change |
| Branch is short-lived — opened when the work item enters IMPLEMENTING, deleted on merge | CPM-1 |
| Every change reaches `main` through a pull request | CPM-5, CPM-6 |
| `main` must always be releasable — a merged PR is not a release, but a broken `main` is a defect | CPM-3 stable baseline |
| Tags are protected and immutable once pushed | CPM-6, Step 72 |

## What a merge to `main` does and does not mean

**Does mean:** required status checks passed, governance metadata present, the owner reviewed and merged.

**Does NOT mean:** the work item is accepted, released, or Stable. Merge is a repository event. Acceptance is a framework gate closure with evidence; release requires the `PRODUCTION_RELEASE` human approval; Stable requires `STABLE_STATUS` approval after production observation.

Conflating merge with acceptance is the most common way a governed process quietly becomes an ungoverned one.
