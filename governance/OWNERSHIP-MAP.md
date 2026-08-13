# Ownership Map (Step 65 companion)

CODEOWNERS maps paths to GitHub handles. This file maps them to **framework roles**, which
is the governing fact. When a second human joins, only the handle changes.

| Path | Framework role | Protected | Change authority |
|---|---|---|---|
| `/slices/**` | slice owner (ROLE_CODING) | no | ROLE_ARCHITECTURE |
| `/platform/**` | ROLE_ARCHITECTURE | **yes** | HUMAN_OWNER |
| `/contracts/**` | ROLE_ARCHITECTURE | **yes** | HUMAN_OWNER |
| `/data/**` | ROLE_ARCHITECTURE | **yes** | HUMAN_OWNER |
| `/ops/**` | ROLE_SECURITY_RELEASE | no | HUMAN_OWNER |
| `/config/**` | ROLE_CODING (+ ROLE_SECURITY_RELEASE review) | no | HUMAN_OWNER |
| `/tests/**` | ROLE_QUALITY | no | ROLE_QUALITY |
| `/docs/**` | ROLE_TECH_DOC | no | ROLE_ARCHITECTURE |
| `/governance/**` | ROLE_ORCHESTRATOR | **yes** | HUMAN_OWNER |
| `/.github/**` | ROLE_SECURITY_RELEASE | **yes** | HUMAN_OWNER |

## Solo-owner limitation — read this

With one human, GitHub **cannot** enforce human independent review: GitHub does not permit
a PR author to approve their own pull request, so "require 1 approval" would make every
merge impossible.

This is a real constraint, not a reason to weaken the control. It is handled as follows:

- **Independence comes from deterministic checks**, which GitHub *can* enforce as required
  status checks. This was always the framework's independence backbone (D-PAF-04).
- **Human review is recorded in the PR body**, not in GitHub's reviewer mechanic — the
  owner explicitly attests to the review in the governance metadata block.
- **When a second human joins**, enable "require 1 approval" and "dismiss stale approvals",
  and human review moves from attested to enforced.

Recorded honestly: on a solo repository, human-review independence is **attested, not
enforced**. Deterministic checks are enforced. Do not describe it as more than it is.
