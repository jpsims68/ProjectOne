# PAF Foundation Decision Record

**Artifact ID:** `PAF-FDR` · **Version:** 1.0 · **Layer:** PROFILE (project-scoped governance record)
**Created:** 2026-08-13 EDT · **Run:** 1 (Steps 1–10)

Held outside `framework/` deliberately: this is a project decision record, and framework/ must remain name-free (SR-1).

| ID | Decision | Status | Ratified |
|---|---|---|---|
| D-PAF-01 | Registries integrate by contract-and-instance binding, with a deterministic equality check at Profile binding | **RATIFIED** | Owner, 2026-08-13 |
| D-PAF-02 | Unbound controls fail closed to most-restrictive form | **RATIFIED WITH AMENDMENT** | Owner, 2026-08-13 |
| D-PAF-02a | *Amendment:* strict mode must never be silent — every unconfigured control raises a warning naming the control and its strict-mode behavior, with owner notification mandatory | **RATIFIED** | Owner, 2026-08-13 |
| D-PAF-03 | Owner ratification at load-bearing/ambiguous decisions only; formal framework approval remains Step 54 | **RATIFIED** | Owner, 2026-08-13 |
| D-PAF-04 | Independence rests on deterministic checks + clean-context separate invocation + human review; role labels alone never qualify | **RATIFIED** | Owner, 2026-08-13 |

## Owner clarification recorded during ratification (D-PAF-04)

The owner asked whether adversarial role design — a QA agent distinct from a tester agent, an orchestrator overseeing independent agents — supplies independence on its own.

**It does not, and this distinction is load-bearing for Steps 11–15.** Roles determine *who reviews what, with what authority*. Independence determines *whether the review is genuine*. A reviewer role occupied by a continuation of the same reasoning pass carries the implementer's assumptions forward and cannot reconstruct a conclusion it never left.

Both are required. Role separation without an execution boundary produces the appearance of independence without the substance. The 16 role contracts (Step 11) must therefore state, per role, which independence mechanism its reviews require — not merely that the role is "independent."

## Run 1 construction decisions (not owner-gated, per D-PAF-03)

| ID | Decision | Reversal cost |
|---|---|---|
| C-R1-01 | JSON Schema 2020-12 as the schema language | Low — mechanical translation |
| C-R1-02 | `layer` (CORE/PROFILE/ADAPTER) declared on every artifact header, making PR-1/PR-2 machine-checkable | Low |
| C-R1-03 | SR-1 portability enforced by automated name-scan over `framework/`, not by review discipline | Low |
| C-R1-04 | Project decision records held outside `framework/` so the core stays name-free | Low |
| C-R1-05 | `deferralClass` with `UNDECLARED` defaulting to `STRUCTURAL_DESIGN` — encodes the no-migration principle in the record shape | Moderate — schema change |
| C-R1-06 | Continuity snapshot carries `predecessorPackageHash` + `immutableCorpusHash`, making the externalized-state chain verifiable | Low |
| C-R1-07 | Timestamps require an explicit UTC offset; bare local time rejected | Low |

C-R1-05 is the one worth a second look at Step 25 — flagging it now rather than at Step 54.

---

# Run 2 (Steps 11–20) — Construction Decisions

Recorded per D-PAF-03: construction authority, surfaced at the run boundary for owner review.

| ID | Decision | Reversal cost |
|---|---|---|
| C-R2-01 | **Matrices are generated from role contracts and workflows, never hand-authored.** A hand-authored matrix is a second copy of the same facts and will silently drift from the contracts it claims to summarize. Generation makes drift structurally impossible. | Low |
| C-R2-02 | Role contracts reference normative policy by identifier and never restate it — restated policy becomes a second, unowned authority that drifts from its source | Low |
| C-R2-03 | Role contracts use generic lifecycle **stage classes**, not state names. Concrete states bind at Profile (implements D-PAF-01) | Moderate — would require re-authoring all 16 contracts |
| C-R2-04 | Every role denies `DB_PRODUCTION_ACCESS`, `SECRET_READ`, and `EVIDENCE_AMEND` by construction, not by policy statement | Low |
| C-R2-05 | Tool permissions fail closed: any permission not listed for a role is `DENIED` (CR-5) | Low |
| C-R2-06 | **Evidence producers are DECLARED or DERIVED, recorded separately.** Where a gate required evidence no role explicitly claimed, the producer is derived by a documented rule — the role owning the stage the gate follows. The basis is always visible, so derived coverage is never mistaken for a declared obligation | Low |
| C-R2-07 | Each role contract declares which independence *mechanism* its reviews require — implements the owner's D-PAF-04 clarification that role separation alone is insufficient | Low |

## Finding closed during Run 2

**F-R2-01 — Evidence traceability gap.** Initial generation left 44 of 82 evidence classes required by a gate with no accountable producer. Step 18's completion criterion is bidirectional traceability, so this was a real hole, not a cosmetic one. Closed by C-R2-06. The check was hardened from informational to enforcing so it cannot silently reopen.

## Note carried to Step 17 / Step 41

The Role-to-Tool Permission Matrix is **declarative on conversational workbenches** — there is no per-role sandboxing on this platform, and all tools are available in every invocation. Least privilege here is a specification that the repository and CI adapters enforce later. Recorded in the matrix header and due for consolidation in the Step 41 adapter compatibility matrix.

---

# Run 3 (Steps 21–24) — Construction Decisions

| ID | Decision | Reversal cost |
|---|---|---|
| C-R3-01 | Regression portfolios test the framework's own controls, independent of any project's application code — 6 portfolios, 29 cases, covering all 4 mandatory adversarial families (self-approval, silent exception, fabricated evidence, unapproved bypass) per VP-2 | Low |
| C-R3-02 | Each portfolio's answer key is a **separate file** from its fixture, so grading cannot be circular (an agent grading its own fixture against its own expectations proves nothing) | Low |
| C-R3-03 | Technology Registry ships at CORE with **zero approved entries**. The registry's shape (categories, fail-closed rule) is portable; the actual approved stack is Profile content — binds at Step 32 or the coding-workbench adapter (Step 39) | Low |
| C-R3-04 | Environment Registry hard-codes exactly one production-data-allowed tier at the top of a strictly increasing sequence — makes "which environment can see real tenant data" a structural fact, not a per-deployment judgment call | Moderate |
| C-R3-05 | Design system layer-separation rules are written as JSON Schema `const` values, not prose — an instance literally cannot state a different rule and still validate | Low |
| C-R3-06 | STABLE approval and rollback-verification rules are similarly load-bearing `const` values, closing off the "elapsed time = stable" and "documented = recovered" failure modes at the schema level | Low |

## Regression discipline established this run

Every run's static validator is re-run alongside the current run's, and the reproduction commands are listed in the continuity snapshot. Run 3 confirms **Runs 1 and 2 both still pass unmodified** (15/15, 21/21) after Run 3's additions — no later run may silently weaken an earlier one's guarantees.

---

# Run 4 (Steps 25–34) — ProjectOne Profile Construction

This run built Layer 2 — the ProjectOne Profile — and is the first real test of D-PAF-01.

| ID | Decision | Reversal cost |
|---|---|---|
| C-R4-01 | **The 5 governance registries bind by hash reference, not by copy.** Each Profile binding records the exact SHA-256 of the registry it binds; a later silent edit to a registry breaks the binding rather than changing behavior unnoticed | Low |
| C-R4-02 | **Lifecycle binds to the 27+13 registry states with zero invention** — validated by R4-03. The framework's generic stage classes map onto real registry states; ProjectOne creates no states of its own. D-PAF-01 confirmed under load | Moderate |
| C-R4-03 | **Build requirements loaded by reference only** — decision IDs and versions, never the 330 requirement texts or 30 architecture decisions. The Build Policy stays the sole normative home (D4-GOV-01). Duplicating would create a second, drifting copy | Low |
| C-R4-04 | Technology stack (FastAPI, SQL Server, Cytoscape.js) binds at Profile, not framework. PM4Py marked PROHIBITED per DDR D-66 | Low |
| C-R4-05 | 8 unavailable sources carried as **declared absences**, never reconstructed. 603 grouping source flagged `ABSENT_ACQUISITION_TRIGGER` — a live tripwire before any D-38 grouping-seed work | Low |
| C-R4-06 | Industry-agnostic terminology guard written into the Profile as explicit prohibited framings (no SMB-wholesale beachhead, no P2P/O2C primary focus). Mid-market/SMB size positioning retained | Low |

## The 7 strict-mode controls are now CLEARED

Runs 1–3 ended with 7 controls in strict mode (lifecycle, risk, exception, independence, human approval, source, ownership) because nothing was configured. **Run 4 binds all 7.** R4-07 confirms the five governance registries are BOUND; source and ownership are configured via Steps 26–27. No control remains in unconfigured strict mode.

## Open items carried forward (unchanged, still open)

- **75 of 330 requirements** have untested consolidation fidelity pending DATA/API/SEC + non-pilot CODE recap docs. Recorded in the build-requirements config as an open verification item, not a silent gap.
- **All 360 decisions** sit at DEFINED_IN_MAP; framework-v1 minimum is EVIDENCE_LINKABLE. This 360-wide delta is the substance of framework activation (Steps 44–56), not a satisfied requirement.
- **603 acquisition trigger** — must request the exact immutable source before D-38 grouping-seed implementation.

---

# Run 5 (Steps 35–43) — Adapters & Framework Assembly

Built Layer 3 (adapters) and assembled the complete three-layer validation candidate.

| ID | Decision | Reversal cost |
|---|---|---|
| C-R5-01 | **Step 38 Anthropic adapter is first-class and carries zero project governance** — validated by R5-04. It encodes the clean-context independence protocol, the durable-externalized-state protocol, and honest CANNOT_SATISFY declarations for GitHub/CI/secrets/persistence | Moderate |
| C-R5-02 | **Every capability gap is first-class: mitigation + named risk acceptor required by schema.** A gap that is merely noted fails validation. 9 gaps declared across adapters, all with John as risk acceptor | Low |
| C-R5-03 | **GitHub live operations declared CANNOT_SATISFY with deferredVerification=true** — no GitHub integration is signed off as passing without real execution. The adapter is fully specified and locally unit-validatable; live validation routes to owner (Steps 63-72/91/101/110) | Low |
| C-R5-04 | The Adapter Compatibility Matrix is **generated from the adapters**, not hand-authored — same anti-drift discipline as the Run 2 matrices | Low |
| C-R5-05 | Release manifest is `1.0-rc1 / VALIDATION_CANDIDATE`; approval explicitly deferred to Step 54, freeze to Step 55. Passing validation never implies approval | Low |

## The three-layer package holds

Final assembled inventory: **86 CORE (generic) + 10 PROFILE (ProjectOne) + 5 ADAPTER**. The boundary is machine-verified: the generic core carries no project or vendor name; the profile binds by hash; the adapters translate only. Platform migration is not a governance event — the promise from Step 1 §3.2.

## Finding closed during Run 5

**F-R5-01 — Portability leak in the Anthropic adapter.** The adapter's own prohibition list contained the literal string "ProjectOne-specific governance." Even as a self-prohibition, the literal project name made the adapter non-portable and failed R5-04. Corrected to "project-specific governance." Caught by the portability check, not by eye — the same class of leak the Run 1 spec had.

## Adapter capability gaps now formally declared (Step 41)

| Gap | Adapters | Mitigation | Risk acceptor |
|---|---|---|---|
| Live GitHub/CI operations | GitHub, Anthropic | Specify + unit-validate locally; live validation deferred to owner | John |
| Secret storage | GitHub, Anthropic, ChatGPT | Secrets never in chat; bound in owner environment via unbound interface | John |
| Persistent container state | Anthropic | Durable externalized packages, hash-chained, owner-retained | John |
| Per-role tool sandboxing | Anthropic, ChatGPT | Declarative here; enforced via GitHub/CI adapter | John |
| Different model-FAMILY independence | Anthropic | Route cross-family gates to human review or another platform | John |

---

# Run 6 (Steps 44–51) — Validation, Dry Run, Sustainability

This run **executed** the framework rather than describing it. An executable governance engine was built that reads its rules from the framework artifacts — change a contract and the engine's behavior changes. It hard-codes no governance.

| ID | Decision | Reversal cost |
|---|---|---|
| C-R6-01 | **Built an executable engine (`engine/paf_engine.py`) that loads rules from the artifacts.** Without it, Steps 45–47 would be assertions about behavior rather than observations of it | Moderate |
| C-R6-02 | Risk triggers are referenced as **class-qualified indices** (`R4.1`) resolving to the bound standard's declared text — not free-form strings | Low |
| C-R6-03 | Zero-tolerance criteria are evaluated **per criterion**, mapped to the violation that actually breaches them | Low |
| C-R6-04 | Sustainability thresholds derived **from measured dry-run data**, never invented. Proposed, not adopted — Step 49 requires owner approval | Low |

## Defects found by execution and corrected (Step 50)

All corrected by fixing the artifact or engine, never by weakening a control (VP-3).

| ID | Defect | Correction |
|---|---|---|
| **F-R6-01** | Engine had **no overlay enforcement**. A source with applicable 999 overlays could be read base-only and accepted — an agent acting on text that no longer means what it says (CR-3 violated in practice while satisfied on paper) | Added `read_effective_source()`; incomplete reads are refused. Portfolio extended with SR-ADV-02/04 |
| **F-R6-02** | **Risk classification failed OPEN.** An unrecognised trigger reference silently fell back to the work-type floor class, making a typo indistinguishable from a deliberate low classification — precisely the silent-omission failure mode the framework exists to prevent | Classification now **fails closed**: unresolved trigger input returns the highest class. Uncertainty routes upward, as the standard requires |
| **F-R6-03** | Two dry-run scenario paths used lifecycle edges the registry does not declare (`SOURCE_BUNDLE_VALIDATED→VERIFYING`, `DESIGN_REVIEW→REWORK_REQUIRED`). The **engine correctly refused both** — the defect was in the scenario authoring, and the registry was right (rework is reached from VERIFYING) | Scenario paths corrected to legal edges. Confirms the lifecycle control works under load |
| **F-R6-04** | Zero-tolerance reporting marked **all seven** criteria FAIL whenever any violation existed — dishonest reporting that asserts breaches which did not occur | Per-criterion mapping; only the breached criterion fails |
| **F-R6-05** | Sustainability thresholds artifact declared `layer` outside its header, failing R4-01 | Header structure corrected |

**F-R6-02 is the most significant.** A fail-open risk classifier would have quietly under-protected work for the life of the system, and no static check would have caught it — only execution did.

## Step 49 — OWNER APPROVAL REQUIRED (not yet given)

Sustainability thresholds are **PROPOSED**, derived from the measured baseline. Per the Dry-Run Acceptance Plan's `gateRule`, **Agent Framework v1 cannot be approved at Step 54 until John approves these thresholds.** This is a genuine human gate and is not inferrable from the dry run passing.

---

# Run 7 (Steps 52–56) — Validation Report, Approval, Freeze, Package

## Owner approvals recorded

| ID | Step | Subject | Decision | Basis |
|---|---|---|---|---|
| **APR-001** | 49 | Governance sustainability thresholds | **APPROVED AS PROPOSED** | Explicit owner review — "approve both" |
| **APR-002** | 54 | **Agent Framework v1** | **APPROVED** | Explicit owner review of the approval package |

Neither approval was inferred from silence, elapsed time, validation results, or agent recommendation. APR-001 was recorded first, per the Dry-Run Acceptance Plan `gateRule`.

**Residual risks the owner acknowledged in approving:** the 360/360 verification-mechanism mapping is assistant judgment and not independently verified (OD-05 remains open); live GitHub/CI, secrets, per-role sandboxing and cross-family independence cannot be satisfied on this platform; the framework has governed 12 simulated scenarios, not real production work; 75 requirements have untested consolidation fidelity.

## Defect found during freeze execution (Step 55)

**F-R7-01 — the header schema could not record its own freeze.** `FROZEN` was a declared status, but `artifactHeader` had no fields for *when* an artifact was frozen or *under which approval*, and `additionalProperties: false` rejected them. Freezing 69 artifacts failed validation immediately.

Corrected by extending the schema: `frozenAt` and `frozenUnder` are now **conditionally required whenever status is FROZEN**. A frozen artifact can no longer exist without traceable freeze authority — a stronger guarantee than before the defect appeared.

Caught because the full sweep was re-run *after* freezing rather than assumed to still hold. Corrected before the baseline was finalized; the freeze manifest was then regenerated against the corrected state.

## Framework v1 baseline

| Property | Value |
|---|---|
| Version | **1.0** (promoted from 1.0-rc1) |
| Release state | `APPROVED_FROZEN_BASELINE` |
| Components frozen | 127, each with SHA-256 |
| Validation at freeze | **9/9 suites** — 85 static checks, 5/5 conformance, 31/31 regression, 12/12 dry run with 0 zero-tolerance violations, 8/8 replay |
| Adapters | 5, with 9 declared gaps, all mitigated, risk acceptor John |
| Immutability | Frozen. Any change requires a governed change package and a new version — never an in-place edit |

## Defect found by the Framework Activation Checkpoint

**F-R7-02 — the freeze was not the terminal action.** The Step 55 freeze manifest was computed at 15:26, after which two baseline files were still modified: the Run 7 section was appended to this Decision Record (16,083 → 18,455 bytes), and the Run 7A continuity snapshot was superseded by the Framework v1 snapshot. The frozen manifest therefore listed one file that no longer existed and one hash that no longer matched.

**Severity: material.** A freeze that is followed by content edits is not a freeze. Had this shipped, the v1.0 baseline manifest would have misrepresented its own contents from the moment it was created — and every future integrity check against it would have failed for a reason unrelated to actual tampering, training everyone to ignore the check.

**Correction:** freeze re-executed as the genuinely last action, after all content — including this defect record — was final. The freeze procedure is now explicitly terminal: **nothing may be written to the baseline after the freeze manifest is generated.**

**Why it was caught:** the activation checkpoint verifies the frozen manifest against the actual files on disk rather than assuming the freeze was correct. Requirement 1 exists precisely for this, and it worked on its first real use. The checkpoint was run *after* packaging rather than being skipped as a formality.

---

# Steps 57–62 — ProjectOne Repository Design

Design only. No product features implemented; production application implementation remains NOT AUTHORIZED.

| Step | Deliverable | Traced to |
|---|---|---|
| 57 | Top-level repository structure — 10 directories, each with a named owner and a one-way dependency rule | VSA-1..8, CPM-5/6 |
| 58 | Vertical-slice template with a **required** `slice.manifest.json` | VSA-1, VSA-6 |
| 59 | Shared-platform structure, deliberately small, with a governed promotion path | VSA-2, VSA-5 |
| 60 | Configuration hierarchy with fail-closed defaults and secret **references** only | CONFIG, SEC |
| 61 | Test structure mapped to the 360-decision verification map | TEST, VSA-7, CPM-4 |
| 62 | Documentation structure with explicit per-area update triggers | DOC |

**Load-bearing design choices:**
- **Ownership is visible from the path.** If you cannot tell who owns a file from where it sits, the layout has failed.
- **`slice.manifest.json` is mandatory.** A slice without one is not a slice — it is ungoverned code. This makes ownership and dependency direction machine-checkable rather than conventional.
- **Cross-slice import is a build failure, not a review comment.** VSA-3 acyclicity is enforced by a deterministic CI check (Step 69), not by discipline.
- **`.github/` is where the declarative tool-permission matrix finally becomes enforced.** Step 17 was a specification; CODEOWNERS and branch protection are the enforcement.

## CP-001 — first governed change against the frozen baseline

Binding the repository URL and the owner's OD-01 decision required modifying the Profile, which was frozen under APR-002. Rather than edit it in place, a change package was raised: R2, reviewed, Profile `1.0 FROZEN → 1.1 ACTIVE`, hashes recorded before and after.

**The framework core (`framework/`) is byte-identical to v1.0** — verified. Only the ProjectOne Profile and additive design artifacts changed. Baseline advanced to **v1.1**, chained to v1.0 by explicit supersession basis. v1.0 is retained immutably.

**OD-01 RESOLVED — Option A.** The owner executes all GitHub operations. The assistant produces exact commands and expected output; the owner runs them and returns actual output, which becomes the evidence record. Credentials and secrets never touch the assistant platform — `secret_protection` handled by architecture, not exception.

## F-R7-02 recurred, in a second form

After re-freezing, the activation checkpoint failed again: I had edited `validation/activation_checkpoint.py` *after* generating the freeze manifest. Same defect class, different file.

Worth recording rather than quietly re-running: the freeze-is-terminal rule applies to **validation tooling as well as governed artifacts**, because the tooling lives inside the baseline. The rule now says so explicitly. That the checkpoint caught its own author twice, on consecutive attempts, is the strongest available evidence it is doing real work.

---

# Steps 63–72 — GitHub Repository Controls and CI (OWNER-EXECUTED)

Executed by John under OD-01 Option A. Every result was produced by the owner running the operation and returning output. The assistant independently verified the live public repository afterwards by cloning it. **No GitHub result is recorded from assistant execution.**

| Step | Result | Basis |
|---|---|---|
| 63 Repository | PASS | 15 files verified in `main` by independent clone |
| 64 Branch strategy | PASS | `main` + `work/<id>`; work merged via PR #1, branch deleted |
| 65 CODEOWNERS | PASS | Path→role mapping committed |
| 66 Branch protection | **PASS — verified by rejection** | Browser edit to `main` returned *"You can't commit to main because it is a protected branch"*, no override offered |
| 67 PR template | PASS | Loaded automatically on PR #1; enforced by check |
| 68 Issue templates | PASS | Blank issues disabled — every work item passes classification |
| 69 Required checks | PASS | 6 checks required, **source pinned to GitHub Actions** |
| 70 CI workflows | PASS | Least privilege (`contents: read`); all 6 observed green |
| 71 Evidence conventions | PASS | Committed |
| 72 Release/tag conventions | PASS | Tag ruleset active on `v*` |

## F-R8-01 — material defect in my own workflow

The Governance workflow listened only for the default `pull_request` types. Editing a PR description therefore did **not** re-trigger the governance metadata check — and "Re-run all checks" replays the *original* event payload, so a PR opened with an empty description could **never** pass that check, no matter how many times it was corrected or re-run.

**Why this mattered more than it looks:** a permanently unsatisfiable gate does not fail safe. The predictable human response is to disable or ignore the check, which removes the enforcement entirely. A control that cannot be satisfied by correct behaviour trains people to route around it.

Corrected by adding `types: [opened, edited, synchronize, reopened]`. Verified green.

## Owner findings — three holes I would have shipped

| ID | Finding | Consequence avoided |
|---|---|---|
| **OF-01** | Browser drag-upload **silently skips dot-prefixed paths**. All 7 `.github` files plus `.gitignore` were dropped with no warning | The repository would have *looked* complete while enforcing **nothing**. Caught because the owner checked the uploaded list against expectation instead of assuming success |
| **OF-02** | My instruction would have produced a doubled path `.github/.github/…` because GitHub retains directory context after a commit | Caught before commit |
| **OF-03** | Required status checks default to source **"Any source"** — meaning *any* entity with repository access can post a check with a matching name and satisfy the requirement | **Highest-consequence finding.** Every governance gate would have carried a forgeable green tick. Corrected by pinning the source to GitHub Actions |

OF-03 deserves emphasis: a required check satisfiable by an arbitrary reporter is not a control. The owner questioned a default rather than accepting it.

## Third-party access — Sourcery AI

Discovered mid-execution: Sourcery had write access and had **overwritten the PR description** — the field carrying risk class, evidence-honesty attestation, recovery procedure, and approval record. An external service able to rewrite the evidence surface is a governance problem, not a convenience question.

**Suspended by the owner** and excluded from required status checks. Residual risk: suspension is a setting rather than structural removal, and is reversible by the owner only. Accepted by John. Follow-up: confirm no Sourcery check appears on the next PR.

## Solo-owner limitation — recorded honestly

GitHub does not permit a PR author to approve their own pull request. With one human, requiring 1 approval would deadlock every merge permanently. Required approvals is therefore **0**.

**This is stated plainly rather than dressed up:** on this repository, human-review independence is **attested** (in the PR body), not **enforced**. Deterministic-check independence **is** enforced. That split is consistent with D-PAF-04, which already made deterministic checks the independence backbone on platforms lacking model diversity.

**Change trigger:** when a second human joins, set required approvals to 1. Human review then moves from attested to enforced.

---

# Steps 73–79 — Repository Assembly (OWNER-EXECUTED)

Framework v1 baseline, ProjectOne profile, and all four adapters committed to the repository via PR #3 and merged. Independently verified by clone: **153 files in `main`, 2 at root, all 87 framework hashes verify.**

| Step | Deliverable | Result |
|---|---|---|
| 73 | Repository scaffold | PASS — structure documented rather than faked with placeholder files |
| 74 | Framework v1 baseline | PASS — 87 files + SHA256SUMS; **baseline now tamper-evident inside the repository** |
| 75 | ProjectOne Profile | PASS — 11 artifacts including 5 registry bindings and approved thresholds |
| 76 | GitHub adapter config | PASS — records what is *enforced* vs. what is *attested* |
| 77 | ChatGPT adapter config | PASS — available, optional |
| 78 | Anthropic adapter config | PASS — clean-context independence + externalized-state protocols |
| 79 | Coding-workbench adapter | PASS — contract only |

## Three defects fixed

**F-R9-01 — the baseline check failed OPEN.** Implemented as inline shell — *"if the manifest exists, verify it; otherwise skip"* — it reported **SUCCESS while verifying nothing** when 137 files were committed to the wrong location. A green tick asserted the approved baseline was intact when the check had not examined a single file.

False assurance is worse than no control. Replaced with a script distinguishing three states, and tested against four: correct structure (87/87 pass), scaffold stage (pass), flattened upload (**fail**), one tampered file (**fail**).

**F-R9-02 — nothing detected the flattening.** 137 files landed at the repository root with every directory path discarded, and no automated control noticed. Detection depended entirely on the owner asking *"can you compare the files against the repo."* New `check_repository_layout.py` refuses non-allowlisted root files and governance artifacts outside `governance/`; it reports 240 violations against the broken branch.

**F-R9-03 — my instruction format caused a ruleset misconfiguration.** I supplied six required check names in a single code block; they were entered as **one combined check name** that can never report, blocking the merge indefinitely. It incidentally prevented the bad merge — by accident, not design. Ruleset rebuilt with seven separate entries, each pinned to GitHub Actions.

## TF-01 — tooling finding

Browser file upload failed **three consecutive times, in three distinct ways**: silently skipping dot-prefixed paths (dropping the entire `.github` directory), capping at 100 files, and silently discarding directory structure. Each failure was invisible at the point of action and detectable only by comparison afterwards.

Switched to GitHub Desktop, which displays full relative paths before committing. The same content committed correctly on the first attempt.

**The lesson is mine:** I should have changed tooling after the *first* failure rather than the third. Repeatedly adapting to a tool that silently loses data — batching around a file cap, hand-creating dot-files — is a false economy that cost most of a session. The framework's own principle applies: a control surface that fails silently should be replaced, not worked around.

---

# Step 80 — Technology Stack Resolution

Step 80 required resolving the stack **from governing sources**, treating earlier MVP stack as historical unless reaffirmed. An audit found less was governed than assumed.

**What was actually locked:** SQL Server / Azure SQL as the engine, Cytoscape.js for the process map, native analytics with no PM4Py (D-66), serverless posture (D-21).

**What was not governed at all:** backend language and framework — FastAPI and Python appear nowhere in the DDR, PRD, or 999 overlays. They were carried in working memory, which is not a governing source. This is exactly the case the Step 80 instruction anticipated.

| Change | Decision | Profile |
|---|---|---|
| **CP-002** | Backend: **Python + FastAPI** | 1.1 → 1.2 |
| **CP-003** | Frontend: **React** | 1.2 → 1.3 |
| **CP-004** | OQ-13 **narrowed**; Fabric excluded as host | 1.3 → 1.4 |

## CP-002 — backend, and a constraint that prevents rather than mitigates

Owner is strongest in SQL, then Python — which is where ProjectOne's work actually sits. Choosing an unfamiliar language would mean learning it *while* building a governed system.

Accepted tradeoff: Python cannot parallelize CPU-bound work across threads. Rather than log this as a performance risk, the owner asked whether a constraint recorded now would prevent it. It would — so **AC-MINING-PLACEMENT** was recorded: mining computes set-based in SQL; numpy only on already-reduced results; no row-wise Python over events; no mining in-request; no client-side computation over raw events.

Filed as a **design constraint, not a performance target**, because a design that puts mining in-request cannot be repaired by adding capacity — it requires restructuring. The testable line: *if a computation step receives raw event rows outside SQL, it is misplaced.*

On owner query, SQL was confirmed as the correct default over numpy on both performance and cost grounds: the dominant cost is data movement, and serverless billing means SQL-side work is billed once while extract-and-compute pays twice.

## CP-003 — frontend

React selected. Frontend is simultaneously the owner's weakest area and the product's most complex surface, so ecosystem depth and AI assistance matter more here than anywhere else in the stack.

Finding: the existing proof-of-concept widgets contain **zero D3 references** — hand-rolled SVG. No framework lock-in existed.

**AC-DOM-OWNERSHIP** recorded: one owner per container. Pattern A (D3 as pure math, React renders) is primary by volume for the chart library. Pattern B (library owns its container) is correct and permanent for Cytoscape.js and the D-28 animation engine. The owner explicitly corrected an earlier framing — Pattern B is not a fallback.

## CP-004 — OQ-13 narrowed, and a conflict with locked canon

The owner elected to keep the deployment target open as long as responsibly possible. The DDR supports this: D-21 locks posture while leaving target open, and D-27 already ties partition scheme to OQ-13.

**But Fabric conflicts with LOCKED D-62.** D-62 requires a UNIQUE constraint on the event natural key *enforced at the storage layer*. Fabric Warehouse supports `PRIMARY KEY` and `UNIQUE` only as `NOT ENFORCED` — duplicate inserts succeed. Verified against Microsoft's own documentation rather than asserted from memory.

Leaving Fabric nominally open would force every subsequent design step to pretend to accommodate an option that cannot satisfy locked canon. OQ-13 is therefore **narrowed, not closed** — genuinely open between Azure SQL Database and Managed Instance (and across providers), closed where a locked decision already closed it.

**Design tax recorded:** while OQ-13 is open, nothing may depend on an MI-only capability. Using one silently closes an intentionally open decision. Currently enforced by review; a deterministic DDL check should be added once there is schema to check.

**Not a DDR amendment.** Admitting Fabric later would require amending D-62 through the 999 overlay mechanism, not a Profile change.

## Forward requirements register — new mechanism

The owner directed that the Fabric-as-source position be logged separately and referenced in the Implementation Guide, which does not yet exist.

That exposed a gap: **a decision made now often imposes content on a document written later, and that obligation lived only in memory.** So `profile/PROJECTONE-Forward-Requirements.json` was created — six entries naming a target artifact, what it must contain, why, and an acceptance test. It is a **completion precondition**: no listed artifact may be marked complete without checking it.

FR-001 captures the owner's specific concern — the guide must state **both** halves of the Fabric position. Recording only "Fabric is out" would lead a future reader to decline a legitimate client integration. Both halves must travel together.

---

# Steps 87–100 — Local Developer Environment (OWNER-EXECUTED)

Merged via PR #4, 7/7 checks green. Independently verified: `main` at 165 files, all governance checks pass, framework baseline intact (87/87 hashes), and the framework's own 9 validation suites still pass from the repository copy.

**Steps 87–91 required no installation.** An environment audit found the owner already had VS Code 1.133.0, Python 3.13.5, uv 0.11.29, Node 24.16.0, git 2.54.0, SQL Server 2022 **Developer Edition** (two instances), ODBC 18, sqlcmd and SSMS 19. Two items needed only a PATH entry.

**Two decisions arose from the audit:**

- **Node amended 22 → 24** in the registry. Node 24 became LTS after the entry was written and the owner's machine already had it. The registry describes reality; downgrading a machine to match a document written from stale information is backwards. Tripwire recorded for Step 102 if the frontend build objects.
- **Development instance = `MSSQLSERVERLOCAL`** (empty) rather than the default instance, which holds 18 databases including six prototype artefacts — among them `project_one` and `ProjectOne`, differing by one letter. Using the empty instance removes the wrong-database risk structurally rather than by care.

**Pydantic added** to the registry on owner query, with a placement constraint: it validates at *trust boundaries* — request bodies, ingestion input, configuration — and must not validate row-wise over event data, which would violate AC-MINING-PLACEMENT. It guards the door, not the warehouse floor.

## Four defects found and corrected

| ID | Defect | Why it mattered |
|---|---|---|
| **F-R10-01** | `check_no_secrets.py` required **quoted** values. The `.env` format is unquoted, so the check was blind to the single most likely place a real secret appears. A test `.env` containing a password passed cleanly | `secret_protection` is non-waivable. A check unable to detect the obvious case protects nothing. Found by *negative testing* — writing a secret and confirming detection, rather than assuming |
| **F-R10-02** | Layout allowlist rejected `.env.example` | Would have failed the PR |
| **F-R10-03** | Adding `pyproject.toml` activated the ruff CI step for the first time — 24 violations, mostly in assistant-authored scripts | Would have failed the PR |
| **F-R10-04** | No `.gitattributes`. Windows converts LF→CRLF on checkout; the 87 baseline hashes were computed on LF | The baseline check would **fail locally and pass in CI** — exactly the divergence Step 94 exists to prevent |

## AE-01 — assistant error, material

The assistant ran governance checks against the owner's **branch**, found `check_baseline_integrity.py` absent and the workflow unfixed, and told the owner that a previously-reported fix had never been deployed.

**That report was wrong.** The fix was in `main`. The owner's local clone was stale — created before the Steps 73–79 merge and never pulled — so the branch was based on a `main` predating it and inherited none of those 125 files.

**Cost:** an unnecessary corrective bundle, merge conflicts when the branch was updated, an abandoned branch, roughly 45 minutes.

**Root cause:** diagnosing from a derived artefact (a branch) without first comparing against the authoritative one (`main`). Compounded by the assistant having verified against its own container copy rather than the repository — the two had silently diverged.

**Lesson:** when repository state looks wrong, compare against `main` before concluding anything is missing. A branch is not evidence of what the repository contains. This is the same failure class as reporting PASS without examining the branch: asserting a conclusion from something not actually inspected — which is what the framework exists to prevent, and which the assistant did while fixing an instance of it.

**Preventive measure:** pull after every merge. A stale local clone was the root enabler of the whole sequence.
