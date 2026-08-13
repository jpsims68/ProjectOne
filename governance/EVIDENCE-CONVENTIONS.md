# Evidence and Governance Artifact Storage (Step 71)

## The problem this solves

Evidence trapped in a chat window or a CI log is evidence you will not have in six months.
CI logs expire. Conversations are not addressable. Neither is a durable record.

## Durable locations

| Artifact | Location | Retention |
|---|---|---|
| Framework frozen baseline | `governance/framework/` | Permanent. Immutable — superseded, never edited |
| ProjectOne Profile | `governance/profile/` | Permanent, versioned |
| Adapters | `governance/adapters/` | Permanent, versioned |
| Owner approval records | `governance/approvals/` | **Permanent. Never deleted, never edited.** |
| Change packages | `governance/changes/` | Permanent |
| Exception records | `governance/exceptions/` | Permanent, including after expiry — an expired exception is history, not garbage |
| Gate evidence | `docs/evidence/<work-item-id>/` | Permanent for R3/R4; minimum 2 years for R1/R2 |
| Test/CI results referenced by a gate | `docs/evidence/<work-item-id>/` — **copied out of CI**, not linked to a log | Same as gate evidence |
| Production observation records | `docs/evidence/observation/` | Permanent |
| Continuity snapshots | `governance/continuity/` | Permanent — the platform-transfer record |
| Release records | `docs/release/` | Permanent |

## Rules

1. **A CI log link is not evidence.** CI logs expire. The artifact must be copied into the repository, or attached to a release, with its content hash recorded.
2. **Evidence is addressable by work item.** Given a work item ID, every piece of evidence for it must be findable without searching chat history.
3. **Evidence is never edited.** A superseding record is added; the original stays. A frozen record rewritten to match later findings is an evidence-honesty violation — non-waivable.
4. **Every reproducible evidence record carries its reproduction command.** A result nobody can re-run is an assertion.
5. **Approvals are never deleted.** Including rejected ones. A rejection is part of the record.

## Naming

```
docs/evidence/<work-item-id>/<evidence-class>-<yyyymmdd-hhmm>-<short>.<ext>
docs/evidence/<work-item-id>/SHA256SUMS.txt
```

Timestamps are local Eastern (America/New_York), to the minute.
