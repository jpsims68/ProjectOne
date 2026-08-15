# Active Adapter Configuration (Steps 76–79)

Adapters **translate** framework behaviour onto an execution surface. None of them
redefines governance, originates authority, or carries project-specific rules.

| Adapter | Surface | Status in this repository | Contract |
|---|---|---|---|
| GitHub | Repository / VCS | **ACTIVE — enforcing** | `governance/adapters/PAF-Adapter-GitHub.json` |
| Anthropic / Claude | Conversational workbench | **ACTIVE — approved for use** | `governance/adapters/PAF-Adapter-Anthropic.json` |
| ChatGPT | Conversational workbench | **AVAILABLE — optional** | `governance/adapters/PAF-Adapter-ChatGPT.json` |
| Coding workbench (VS Code / IDE) | Coding workbench | **AVAILABLE — contract only** | `governance/adapters/PAF-Adapter-Coding-Workbench.json` |

---

## GitHub adapter — what is actually enforced here (Step 76)

| Framework behaviour | GitHub expression | Enforced? |
|---|---|---|
| Controlled promotion (CPM-6) | Branch protection on `main`; no direct commits | **Yes — verified by rejection** |
| Required verification | 6 required status checks, source pinned to GitHub Actions | **Yes** |
| Ownership and review path | `CODEOWNERS` + require review from Code Owners | **Yes** |
| Governance metadata on change | PR template + `PR governance metadata` check | **Yes** |
| Work-item classification | Issue template; blank issues disabled | **Yes** |
| Slice boundaries (VSA-3) | `Slice boundaries` check — cross-slice import fails the build | **Yes** |
| Secret protection | `Secret protection` check + `.gitignore` | **Yes** |
| Baseline integrity | `Framework baseline integrity` check verifies `governance/framework/SHA256SUMS.txt` | **Yes** |
| Release identity | Tag ruleset on `v*`, immutable | **Yes** |
| Human independent review | **Attested in the PR body, NOT enforced** | **No — see below** |

### The one thing GitHub cannot enforce here

GitHub does not permit a pull-request author to approve their own pull request. With a
single human, requiring one approval would deadlock every merge permanently. Required
approvals is therefore **0**.

**Stated plainly:** on this repository, human-review independence is **attested**, not
**enforced**. Deterministic-check independence **is** enforced. This is consistent with
D-PAF-04, which made deterministic checks the independence backbone.

**Change trigger:** when a second human joins, set required approvals to 1 and enable
dismissal of stale approvals. Human review then becomes enforced.

### Required checks must never be satisfiable by an arbitrary reporter

The status-check source is pinned to **GitHub Actions**. Leaving it at *Any source* would
let anything with repository access post a matching check name and satisfy the requirement
— a forgeable green tick on every governance gate. No third-party app may be added to the
required-check list, because an external service must never be able to block or unblock a
merge.

---

## Anthropic adapter — operating rules in this repository (Step 78)

- **Durable state is externalised.** Work is carried between sessions as a complete
  continuation package with `SHA256SUMS.txt`, chained by predecessor hash. Conversation
  memory is never treated as durable state.
- **Independent review uses clean-context invocation.** A fresh session receives governing
  sources, work product, acceptance criteria and evidence — but not the originating
  instance's reasoning. A relabelled continuation of the same reasoning never qualifies.
- **Cannot satisfy:** live GitHub/CI operations, secret storage, persistent per-role tool
  sandboxing, cross-model-family independence. All declared in
  `governance/manifests/PAF-Adapter-Compatibility-Matrix.json` with mitigations and a named
  risk acceptor.
- **GitHub work is owner-executed** (OD-01 Option A). No GitHub result is recorded as
  passing unless the owner ran it and returned output.

## ChatGPT adapter (Step 77)

Available and portable. Same externalised-state discipline. Optional — nothing in this
repository depends on it.

## Coding-workbench adapter (Step 79)

Contract only; no concrete IDE bound yet. A new coding workbench is added by implementing
the contract, never by redefining the framework. Repository operations delegate to the
GitHub adapter. Local green build is not acceptance.

---

## Rules binding all adapters

1. An adapter translates; it never redefines what a control means.
2. An adapter never becomes an authority — it cannot approve, classify risk, or resolve a source conflict.
3. An adapter may not invent, rename, merge, skip, or reorder a lifecycle state or gate.
4. An adapter may not collapse required independent steps into one invocation for convenience.
5. A capability an adapter cannot satisfy is a **declared gap with a mitigation and a named
   risk acceptor** — never a licence to skip the control.
