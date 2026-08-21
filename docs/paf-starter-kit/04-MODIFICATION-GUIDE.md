# Modification Guide

Organized by **what you want to change**, not by which file it lives in.

---

## The one rule that governs all of this

**Never edit a frozen artifact in place.** Anything under `framework/`, and any baseline manifest, is frozen. Changes happen by governed change package plus a new version. The prior version is retained immutably.

This is not ceremony. A frozen artifact is the thing every later claim is measured against. Edit it silently and every prior verification becomes unfalsifiable — you can no longer tell whether something passed because it was correct or because the standard moved.

---

## "I want to use a different technology"

**Change:** `profile/YOURPROJECT-Technology-Registry.json`

The registry is **allowlist-based** — anything not listed ACTIVE is denied by default. Add an entry with name, category, version range, role, approver, and date. Adding an entry is a governed change: it needs a change package and a human approver, not just an edit.

**When a version range must change** — a security advisory, a needed feature — amend the range, record the reason, and append to `changeHistory`. On the originating project a CVE in a test framework forced exactly this; the amendment recorded the advisory ID, the fix version, and evidence the suite still passed.

---

## "I'm not on GitHub" / "I use a different AI platform"

**Change:** `adapters/` and `adapter-config/ACTIVE-ADAPTERS.md`

The adapter layer is how the framework binds to your tools. Five ship: GitHub, Anthropic, ChatGPT, a coding workbench, and the adapter contract itself.

Write a new adapter conforming to `PAF-Adapter-Contract.json`, then list it as active. **Do not** modify the core to accommodate a tool — that's what the adapter layer is for, and the moment you do it the framework stops being portable.

> **Known gap:** the adapter layer carries no negative-test requirement, while the core carries the principle in seven places. Every gate failure on the originating project happened in the adapter layer. If you write an adapter, write its fixture matrix first.

---

## "The risk classification is wrong for my project"

**Change:** `profile/YOURPROJECT-Risk.json`

Everything landing in R4 means nobody will use the framework. Everything in R1 means it does nothing. Expect to revise after a month of real use — plan for that rather than trying to be right first time.

Keep the escalation rule intact: **uncertainty routes upward.** If impact cannot be bounded from available evidence, it is the higher class. That rule is what makes the classification honest under pressure.

---

## "I need to change who approves what"

**Change:** `profile/YOURPROJECT-Human-Approval.json`

Define approval classes and which are non-delegable. The framework's position is absolute and worth preserving: **approval is never satisfied by silence, elapsed time, an agent's recommendation, or urgency.**

Solo projects usually run required approvals at 0, because GitHub forbids approving your own PR. Record that human-review independence is *attested, not enforced* — claiming a control you don't have is worse than admitting the gap.

---

## "I want to add a check"

**Change:** add to `scripts/`, wire into `.github/workflows/governance.yml`, add to required checks.

**Build the fixture matrix first.** Not after. Include:

- one fixture per violation the check should catch
- **a clean control that would trip a naive implementation** — for a text scanner, name the forbidden constructs inside comments and string literals

The clean control matters as much as the violations. A check that produces false positives gets disregarded, and a disregarded check is no check at all.

Then make the check **assert it examined something** — "files scanned: 1" — not merely that it exited zero.

> On the originating project, a newly written check passed all ten of its violation fixtures on the first run because it scanned nothing when given a file argument. The harness caught it immediately. Without the harness it would have shipped as a required check that could never fail.

---

## "I need to change something in framework/"

You almost certainly don't. Work through this in order:

1. **Is it really project-specific?** Then it belongs in `profile/`, not the core.
2. **Is it tool-specific?** Then it belongs in `adapters/`.
3. **Is it a genuine defect in the generic framework?** Rare, but real.

For (3): create a change package documenting the defect and the fix, get explicit approval, apply the change, regenerate `framework/SHA256SUMS.txt`, create a **new** baseline version, and retain the old one. Never edit in place, never regenerate a baseline silently.

If you find yourself doing this often, the layer separation has broken down and that is the real problem.

---

## "I want to change an immutable source document"

**Use an overlay.** Never edit the source.

An immutable source is evidence of what was provided and when. Editing it destroys the ability to distinguish an original requirement from a later reinterpretation. Instead, record the modification in an overlay register: what changed, why, who decided, and when.

Two properties make overlays work:

- **The source must be read together with its active overlays.** Reading it alone gives a stale answer.
- **Record the source's hash at overlay time.** If the source later changes, the mismatch is visible rather than silent — the overlay must then be re-read against the newer source.

Overlays can also be **pending**: recorded now, applied when a stated trigger fires. That is the correct handling for a change that is decided but not yet due, and it prevents the obligation living only in memory.

---

## "The PR template is too heavy"

**Change:** `.github/pull_request_template.md`

Legitimate — but before cutting, know what each section buys you:

| Section | Buys you |
|---|---|
| Risk classification | Proportional scrutiny instead of uniform ceremony |
| Evidence | Claims tied to reproducible artifacts, not assertions |
| Recovery | A rollback plan written before it's needed |
| Independent review | Someone or something other than the author checked |
| Human approval | A named person, not implied consent |

**Do not cut Evidence.** It's the section that makes everything else more than paperwork. If you must trim, start with Testing and Documentation, which are often covered by CI anyway.

---

## "How do I get framework improvements from another project?"

**There is no upstream mechanism, deliberately.**

Each project forks the framework at install time and diverges. There is no channel by which project two's improvements reach project one. If you want that, you build it — a shared repository, a version policy, a migration path.

Stated plainly so it's a decision rather than a surprise. For most solo and small-team situations, independent forks are the right answer: they're simpler, and they let each project's profile evolve without coordination.
