# Source Authority Model (Step 3)

**Artifact ID:** `PAF-MODEL-SOURCE-AUTHORITY` · **Version:** 0.2 · **Layer:** CORE
**Contract:** `paf.source-registry.schema.json` · **Authority interface:** AI-1

## 1. Why this exists

An agent with an incomplete or mis-ranked source bundle will produce confident, fluent, wrong work. Source resolution is therefore the first control in the framework, not a housekeeping detail.

## 2. Resolution algorithm

Resolution is deterministic. Given a subject and a candidate source set:

1. **Filter by scope.** Discard sources whose `governsSubjects` does not include the subject. Tier rank is irrelevant to a source that does not govern the subject at all.
2. **Filter by status.** Discard `SUPERSEDED`, `HISTORICAL`, and `PROHIBITED_FOR_CURRENT_USE`.
3. **Resolve versions.** Any source with `versionResolved: false` triggers `SOURCE_VERSION_UNRESOLVABLE` and halts resolution. An unresolved version is never treated as current.
4. **Apply overlays.** For each immutable source, the effective content is the source plus all applicable approved overlay entries. Reading the base alone is an incomplete read.
5. **Rank within subject.** Among survivors, lower tier number wins.
6. **Detect ties.** Two equal-tier sources governing the same subject with conflicting content trigger `EQUAL_AUTHORITY_CONFLICT` and halt.
7. **Attach use classification.** Every source handed to an agent carries its permission label.

## 3. The four rules that carry the weight

**Scope beats tier.** A tier-1 source does not control a subject it never claimed. Global precedence is a category error; precedence is always *per subject*.

**Recency is not authority.** A newer artifact never supersedes an older one merely by existing. Supersession is explicit, recorded, approved, and carries a `supersessionBasis`. The schema refuses a supersession without one.

**Effective source = base + overlays.** Where a source is immutable, corrections live in an overlay. An agent that reads only the base source has read a document that no longer means what it says.

**Evidence cannot promote itself.** Sources classified with `mayDetermineResult: false` may inform a finding or a proposal. They may never specify the outcome. Prototype output, pilot artifacts, spike findings, and observations are evidence — they describe what happened, not what should be.

## 4. Immutability and the correction path

Two document classes exist, and conflating them is a defect in both directions:

| Class | Change mechanism | Failure if confused |
|---|---|---|
| **Immutable source** | Overlay entry only — never edited in place | Editing destroys the provenance the overlay exists to preserve |
| **Framework-created artifact** | Maintained directly; edited and versioned in place | Routing it through the overlay clutters the correction record and implies an immutability that does not apply |

## 5. Absent sources

An absent source is not automatically a blocker. Availability is declared:

- `ABSENT_NON_BLOCKING` — derivative, superseded, or illustrative; work proceeds.
- `ABSENT_ACQUISITION_TRIGGER` — not needed now, but a named future condition requires acquiring the exact source before proceeding. The trigger is recorded as a field, not as a memory.
- `ABSENT_BLOCKING` — required now; escalate.

A source that is absent *and* load-bearing is never reconstructed, approximated, or substituted from a similar file. Near-identical copies from uncontrolled locations are not the source.
