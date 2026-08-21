# Estimation Guide

**Purpose: set realistic expectations.** Not to make setup look fast.

---

## Read this before any number below

Every estimate is marked **OBSERVED** or **INFERRED**.

- **OBSERVED** — measured on a real project that ran this framework through 100+ build steps.
- **INFERRED** — reasoned from adjacent observed work. Less reliable. Treat the upper end as more likely than the lower.

Most setup estimates are INFERRED, for an honest reason: the framework was **built incrementally over many sessions**, not installed from a kit. Nobody has yet installed it from this kit start to finish. You may be the first. Where a number is a guess, it says so.

## Assumptions behind every figure

These matter more than the numbers:

| Assumption | If false |
|---|---|
| Working **with an AI assistant**, not by hand | Multiply by **3–5×**. The profile documents alone are a day of typing. |
| Comfortable with git: branch, commit, push, PR | Add 2–4 hours, and expect friction at Step 9 |
| Using GitHub | Adapter work; the GitHub adapter is the only one exercised in production |
| Solo, or with a single approver | Multi-approver flows add coordination, not build time |
| You know your project's domain | The profile asks questions only you can answer |

**The largest variance driver is not skill — it's whether you actually fill in the profile or defer it.** Deferring feels faster and produces machinery attached to nothing. Every hour saved there comes back multiplied.

---

## Session 1 — Install and prove the gates
**Total: 2–4 hours.** Natural stopping point: after the self-test passes.

| # | Task | Est. | Basis |
|---|---|---|---|
| 1.1 | Read `00`, `07`, skim `01` | 30–45 min | INFERRED |
| 1.2 | Create empty repo, clone locally | 10–15 min | OBSERVED |
| 1.3 | Copy kit into the layout in `03` | 15–20 min | OBSERVED |
| 1.4 | Run bootstrap self-test, confirm all gates go red | 10–30 min | OBSERVED — 10 min if clean; 30 if a path needs fixing |
| 1.5 | First commit and push | 10 min | OBSERVED |
| 1.6 | Read `05-DECISIONS-YOU-MUST-MAKE.md` without answering yet | 30–45 min | INFERRED |

**Stop here.** Don't start the profile at the end of a session — it's the part that rewards a fresh head, and half-answered decisions are worse than unanswered ones.

---

## Session 2 — The profile, part one
**Total: 3–5 hours.** The heaviest session. Natural stopping point: after the technology registry.

| # | Task | Est. | Basis |
|---|---|---|---|
| 2.1 | `Profile.json` — identity, terminology, bound framework version | 20–30 min | INFERRED |
| 2.2 | `Source-Registry.json` — which documents are authoritative, which immutable | 45–90 min | OBSERVED — genuinely hard, and consequential |
| 2.3 | `Technology-Registry.json` — every approved tool with version ranges | 60–120 min | OBSERVED |
| 2.4 | `Ownership.json` — who owns what | 20–40 min | INFERRED |
| 2.5 | Commit, PR, merge | 20–30 min | OBSERVED |

**On 2.3:** the registry is **allowlist-based** — anything unlisted is denied. That is the point, and it is also why it takes longer than expected. Budget the upper end if your stack is at all unusual.

**On 2.2:** deciding what is immutable is the decision people most regret rushing. An immutable source can never be edited in place, only overlaid. Choose deliberately.

---

## Session 3 — The profile, part two
**Total: 3–4 hours.** Stopping point: after human-approval classes.

| # | Task | Est. | Basis |
|---|---|---|---|
| 3.1 | `Risk.json` — risk classes and escalation triggers | 45–75 min | OBSERVED |
| 3.2 | `Human-Approval.json` — who approves what, what is non-delegable | 30–60 min | OBSERVED |
| 3.3 | `Verification.json` — how claims get proven | 45–75 min | INFERRED |
| 3.4 | `Independence.json` — what independent review means here | 20–40 min | OBSERVED |
| 3.5 | `Lifecycle.json`, `Exception.json` | 30–45 min | INFERRED |
| 3.6 | Commit, PR, merge | 20–30 min | OBSERVED |

**On 3.1:** getting risk triggers wrong in either direction is costly. Too loose and the framework does nothing. Too tight and everything is R4 and you stop using it. Expect to revise after a month of real use — plan for that rather than trying to be right first time.

---

## Session 4 — Baseline, freeze, and CI
**Total: 2–4 hours.** Stopping point: after all checks pass on a real PR.

| # | Task | Est. | Basis |
|---|---|---|---|
| 4.1 | Generate your own frozen baseline (`03`) | 20–40 min | OBSERVED |
| 4.2 | Create your approval record | 20–30 min | OBSERVED |
| 4.3 | Adapt CI workflows to your stack | 30–120 min | OBSERVED — 30 min if Python; up to 2 hrs otherwise |
| 4.4 | Push and watch the workflows run | 20–60 min | OBSERVED — **expect 2–3 failed runs.** Normal. |
| 4.5 | Configure branch protection and required checks | 30–45 min | OBSERVED — **least-proven step in this kit** |
| 4.6 | Re-run the self-test against the configured repo | 10 min | OBSERVED |

**On 4.4:** on the originating project, the CI harness took **three pushes** to go green — a build-backend failure, then a real CVE surfaced by a check that had never worked, then a regression caused by removing a line that turned out to be load-bearing. Every one was a genuine finding. If your first run fails, that is the system working.

---

## Session 5 — One governed change, end to end
**Total: 1–2 hours.** The most valuable session in the list.

| # | Task | Est. | Basis |
|---|---|---|---|
| 5.1 | Make a trivial change (one line of documentation) | 5 min | OBSERVED |
| 5.2 | Fill in the PR template properly, first time | 30–60 min | OBSERVED — genuinely takes this long initially |
| 5.3 | Watch all checks, merge, verify | 20–30 min | OBSERVED |
| 5.4 | Re-read what you wrote; decide what to simplify | 20 min | INFERRED |

**On 5.2:** the first governance PR body takes 30–60 minutes. The fifth takes 5–10. That curve is steep and reliable. Do not judge the framework's overhead by your first PR.

---

## Totals

| | Hours |
|---|---|
| **Fast path** — Python stack, AI-assisted, decisive | **11** |
| **Typical** | **14–17** |
| **Slow path** — unfamiliar stack, careful deliberation | **19–22** |
| **Without an AI assistant** | **40–70** (INFERRED, wide) |

Spread across five sessions of 2–5 hours. Not a single sitting, and it shouldn't be — sessions 2 and 3 are decision work, and decision quality falls off sharply after about four hours.

---

## Ongoing cost, after setup

| Activity | Cost | Basis |
|---|---|---|
| Governance PR body, once fluent | 5–15 min per PR | OBSERVED |
| Governed change package (new tech, changed constraint) | 30–90 min | OBSERVED |
| Adding a new check with a fixture matrix | 2–4 hours | OBSERVED |
| Continuity snapshot update at session end | 15–30 min | OBSERVED |
| Reviewing an agent's work against role prohibitions | 10–20 min per handoff | INFERRED |

**The steady-state overhead is roughly 10–20% on top of the work itself.** Whether that is worth it depends entirely on what a silent failure would cost you. See `07`.

---

## Where estimates most often go wrong

1. **The profile is decision work, not typing.** The hours are spent thinking. An AI assistant makes the writing near-free and the deciding no faster.
2. **CI adaptation depends on your stack, not this framework.** A Python project reuses the workflows nearly as-is. Anything else means rewriting the commands while keeping the gate discipline.
3. **The first PR body is an outlier.** Don't extrapolate from it.
4. **Expect failed CI runs during setup and treat them as findings.** Budget the time; don't budget for a clean first run.
5. **Deferring the profile does not save time.** It moves the cost somewhere less convenient and adds rework.
