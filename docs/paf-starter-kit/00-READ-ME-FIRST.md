# READ ME FIRST

**Portable Agent Framework (PAF) — Starter Kit v1.0**
Generated 2026-08-21 from a repository where this framework governs a live build.

---

## What you're holding

A governance framework for building software **with AI agents**, packaged so you can drop it into a new project on day one.

It answers a specific question: *when an AI agent does most of the work, how do you know the work is actually sound?* Not by trusting the agent, and not by reading everything it produces. By making the important claims **mechanically checkable**, and by making the agent's authority explicit and bounded.

Three things it gives you:

1. **16 role contracts** — definitions of what each kind of agent may do, may not do, what evidence it owes, and who it hands off to. A coding agent may not approve its own implementation. A spike agent may not edit canonical documents. These are enforced by structure, not politeness.
2. **A governed change process** — every change carries a risk classification, an evidence record, a recovery plan, and a named approver. Nothing merges on assertion alone.
3. **Repository gates that actually run** — CI checks that block a merge when the frozen framework is altered, a secret is committed, or a file lands in the wrong place.

## What it is not

- Not a CI/CD pipeline, though it uses one
- Not a project management system
- Not a methodology for deciding **what** to build — only for governing **how** it gets built once decided
- Not a substitute for knowing your own domain

If you want a framework that makes you go faster, this isn't it. Read `07-WHAT-THIS-COSTS-YOU.md` before committing — it's the honest version, and it includes when *not* to use this.

---

## Where to start

**If you want to be running in an hour:** read this document, then open `02-AI-KICKOFF-PROMPT.md`, paste it into your AI assistant along with the files it names, and work through it together. That's the intended path.

**If you want to understand before you install:** read this document, then `07-WHAT-THIS-COSTS-YOU.md`, then `08-EXAMPLE-inventory-tracker.md` to see it applied to something small and concrete. Then come back to the kickoff prompt.

**If you're evaluating whether this is worth it at all:** read `07` and `01-ESTIMATION-GUIDE.md`. Those two will tell you more than the rest combined.

---

## How this is meant to be used

**With an AI assistant, cooperatively.** The framework was built by an AI agent working with a human owner, and it is designed to be installed the same way. You are not expected to hand-write thirteen JSON profile documents. You are expected to paste a prompt, answer questions about your project, and review what comes back.

Your job in that loop is the part an agent cannot do: **decide.** Which sources are immutable. Who approves what. What counts as high risk. The agent can draft, check, and verify. It cannot tell you what you care about.

---

## Contents

### Documents — read in this order

| File | What it's for |
|---|---|
| **00-READ-ME-FIRST.md** | This document. Orientation and starting point. |
| **01-ESTIMATION-GUIDE.md** | How long setup actually takes, by task, with honest ranges. |
| **02-AI-KICKOFF-PROMPT.md** | The prompt you paste into your AI assistant to begin. |
| **03-BOOTSTRAP-INSTRUCTIONS.md** | Creating your own frozen baseline and approval record. **Required** — the kit deliberately does not include one. |
| **04-MODIFICATION-GUIDE.md** | How to change things, organized by what you want to change. |
| **05-DECISIONS-YOU-MUST-MAKE.md** | The choices that are empty by design and only you can fill. |
| **06-LESSONS-ALREADY-PAID-FOR.md** | Failures already suffered on your behalf. Inherit them free. |
| **07-WHAT-THIS-COSTS-YOU.md** | Overhead, friction, and when not to use this framework. |
| **08-EXAMPLE-inventory-tracker.md** | **Optional.** A fictional worked example. Illustrative only — not a template, not part of the framework. |

### Files — the framework itself

| Path | Contents | Modify? |
|---|---|---|
| `framework/` | 87 files. The frozen core: spec, 16 role contracts, schemas, workflows, models, matrices. | **Never in place.** See `04`. |
| `framework/SHA256SUMS.txt` | Integrity manifest covering all 87. | No |
| `adapters/` | 5 workbench adapters — GitHub, Anthropic, ChatGPT, coding workbench, adapter contract. | Only via governed change |
| `adapter-config/` | Which adapters are active; workspace extension policy. | Yes, per project |
| `scripts/` | 5 governance checks + the bootstrap self-test. | Yes, carefully |
| `profile-template/` | 13 blank profile documents. **This is your main work.** | Yes — this is the point |
| `.github/workflows/` | CI and governance workflows. Python/uv reference implementation. | Yes, per your stack |
| `.github/pull_request_template.md` | The governance metadata every PR must carry. | Yes, carefully |
| `tooling/` | Reference `pyproject.toml` and `.gitignore`. | Yes |

---

## The 16 role contracts

These are the "agents." Each is a frozen contract in `framework/contracts/` specifying authority, prohibitions, tool permissions, evidence obligations, independence profile, handoffs, and stop-work authority.

| Role | Purpose |
|---|---|
| `ROLE_ORCHESTRATOR` | Sequences work, routes to roles, holds the plan |
| `ROLE_ARCHITECTURE` | Designs structure; owns architectural decisions |
| `ROLE_CODING` | Implements approved designs within slice boundaries |
| `ROLE_TEST_DEBUG` | Writes and runs tests; diagnoses failures |
| `ROLE_QUALITY` | Independent verification; evidence review |
| `ROLE_SECURITY_RELEASE` | Security review and release gating |
| `ROLE_SPIKE` | Time-boxed throwaway prototypes; proposes only |
| `ROLE_METHODOLOGY` | Owns the process itself |
| `ROLE_GUI_GOVERNANCE` | Governs UI surface decisions |
| `ROLE_UX_DESIGN` | Interaction and experience design |
| `ROLE_CONSULTING` | Domain advice into the build |
| `ROLE_ONBOARDING` | Bringing new participants in |
| `ROLE_TECH_DOC` | Technical documentation |
| `ROLE_BUSINESS_DOC` | Business-facing documentation |
| `ROLE_ENDUSER_DOC` | End-user documentation |
| `ROLE_ADMIN_DOC` | Administrative documentation |

You will not use all sixteen. Most small projects live in Orchestrator, Architecture, Coding, Test/Debug, and Quality. The rest exist so that when you need one, the boundaries are already defined.

**The important property:** a role's prohibitions are as load-bearing as its authority. `ROLE_CODING` may not approve its own implementation, may not alter an approved design without a governed change, may not use unapproved technology, and may not weaken a test to make it pass. That last one matters more than it sounds.

---

## What the gates actually check

Five checks ship with the kit. Four are generic; all five run in CI and block merges.

| Check | Blocks |
|---|---|
| `check_baseline_integrity.py` | Any alteration to the frozen framework core |
| `check_no_secrets.py` | Credentials committed to the repository |
| `check_repository_layout.py` | Governance artifacts in the wrong location |
| `check_slice_boundaries.py` | Cross-slice dependency violations |
| `check_pr_governance.py` | PRs missing required governance metadata |

Plus `bootstrap_selftest.py`, which is not a gate — it **proves the gates work** by deliberately breaking each one and confirming it goes red. Run it at setup and after any change to a check. See `06` for why this exists; it is the single most valuable thing in the kit.

---

## Step by step

**Step 1 — Read `07-WHAT-THIS-COSTS-YOU.md`.** Ten minutes. Decide whether to continue. There is no shame in stopping here; this framework is wrong for plenty of projects.

**Step 2 — Skim `01-ESTIMATION-GUIDE.md`.** Know what you're signing up for, and where the natural stopping points are.

**Step 3 — Create an empty repository** on GitHub (or your host). Don't configure anything yet.

**Step 4 — Copy the kit in.** `framework/`, `adapters/`, `adapter-config/`, `scripts/` go under `governance/`. `.github/` goes at the root. Exact layout is in `03-BOOTSTRAP-INSTRUCTIONS.md`.

**Step 5 — Run the bootstrap self-test.** Before anything else works, prove the gates can fail:
```
python3 governance/scripts/bootstrap_selftest.py
```
Expect: every gate proved it can go red. If not, stop and fix — see `03`.

**Step 6 — Open `02-AI-KICKOFF-PROMPT.md`** and paste it into your AI assistant with the files it names. From here you're working with the agent.

**Step 7 — Fill in the profile.** Thirteen documents, driven by `05-DECISIONS-YOU-MUST-MAKE.md`. This is the bulk of the work and the part only you can do.

**Step 8 — Create your own frozen baseline and approval record.** `03-BOOTSTRAP-INSTRUCTIONS.md`. Do not skip this: the kit deliberately ships without one, because a baseline records **your** approval of **your** project.

**Step 9 — Configure branch protection and required checks.** `03`, final section.

**Step 10 — Make one trivial governed change end to end.** Branch, PR with a filled-in body, watch the checks, merge. `03` walks it. Do this before real work — an hour spent here saves a week of misunderstanding.

---

## Two things worth knowing before you start

**The framework core is verifiably project-agnostic.** All 87 files were checked for references to the originating project: zero. The three-layer separation (generic Core / project Profile / workbench Adapters) held under 100+ steps of real use. What you're inheriting is not a cleaned-up copy of someone's project — it's the layer that was always meant to travel.

**This kit has been dry-run, not fully proven.** A fresh project was assembled from these exact files and every check was executed against it, including the self-test, all passing. What could **not** be tested from the authoring environment: creating a real repository, configuring branch protection, and running the workflows on real CI. Those instructions come from direct experience on a live repository, but they have not been re-validated on a fresh one. Treat Step 9 as the least-proven part of this kit and read its output carefully.

---

## If something goes wrong

- **A check fails on a clean tree** → misconfigured, not a real finding. `03`, troubleshooting.
- **A check passes when it shouldn't** → the serious case. Run the self-test. See `06`.
- **You need to change something in `framework/`** → you almost certainly don't. `04`.
- **The overhead feels wrong for what you're building** → it may well be. `07` names when to stop.
