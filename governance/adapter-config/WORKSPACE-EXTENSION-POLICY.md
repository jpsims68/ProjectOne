# Workspace Extension Policy (Step 92)

**Scope:** this workspace only. Every extension listed as unwanted below remains
**installed and fully available** for the owner's other projects. VS Code disables them
per-workspace; nothing is uninstalled.

## Why an extension policy exists at all

Extensions run with read access to the working tree and, in most cases, network access.
Two governed constraints make that a governance concern rather than a preference:

1. **`secret_protection` is a global non-waivable invariant.** Every extension with code
   access and network access is a separate potential egress path for file contents.
2. **Step 94's completion criterion is literally *"local and CI results match."*** An
   extension that auto-formats or auto-fixes on a different rule set than CI makes that
   criterion unachievable — you get green locally and red in CI, or worse, the reverse.

## Approved set

| Area | Extensions | Note |
|---|---|---|
| Python | `charliermarsh.ruff` · `ms-python.python` · `ms-python.vscode-pylance` · `ms-python.debugpy` · `ms-python.vscode-python-envs` · `njpwerner.autodocstring` | **ruff is the single formatting and linting authority**, matching CI |
| SQL Server | `ms-mssql.mssql` · `ms-mssql.sql-database-projects-vscode` · `ms-mssql.data-workspace-vscode` | Microsoft first-party only |
| Frontend | `dbaeumer.vscode-eslint` · `esbenp.prettier-vscode` | |
| Formats | `redhat.vscode-yaml` · `redhat.vscode-xml` · `mechatroner.rainbow-csv` | |
| Docs | `yzhang.markdown-all-in-one` · `davidanson.vscode-markdownlint` · `bierner.markdown-mermaid` | |
| Git | `mhutchie.git-graph` · `github.vscode-pull-request-github` | |
| Quality of life | `usernamehw.errorlens` · `christian-kohler.path-intellisense` · `aaron-bond.better-comments` | |
| AI assistance | `anthropic.claude-code` · `openai.chatgpt` | **First-party only.** Two, not six |

## Disabled in this workspace — with reasons

### `sourcery.sourcery`

Two independent reasons.

**Tool conflict.** Sourcery auto-refactors Python. `ruff` is designated the single authority
for Python formatting and linting so that local output matches CI byte-for-byte. Two tools
rewriting the same files cannot both be authoritative.

**Recorded incident.** The Sourcery **GitHub app** — a separate install from this extension —
held write access to the repository and **overwrote a pull request description**, which is the
field carrying governance evidence: risk class, evidence-honesty attestation, recovery
procedure, approval record. It was suspended by the owner (see `evidence/SETUP-001/`). An
external service able to rewrite the evidence surface is a governance problem, not a
convenience question. The extension is the same vendor with local code access.

### `codeium.codeium` · `genieai.chatgpt-vscode` · `kodu-ai.claude-dev-experimental`

Additional AI assistants with code-read and network access. Six were installed; two
first-party assistants are retained.

Two of these three are third-party wrappers rather than first-party clients, and
`kodu-ai.claude-dev-experimental` is explicitly experimental.

Beyond the egress-path concern, multiple assistants generating simultaneous suggestions
degrades the editing experience — a practical reason alongside the governance one.

### `dbcode.dbcode` · `mtxr.sqltools` · `evidence.sqltools-duckdb-driver`

Overlapping SQL clients. `ms-mssql.mssql` is the approved client: Microsoft first-party,
matches the technology registry, and integrates with the SQL Database Projects extension
already in use.

The DuckDB driver additionally introduces a database technology **not listed ACTIVE in the
technology registry**. Unlisted is DENIED by default (CR-5) — not because DuckDB is
objectionable, but because an unregistered data engine reachable from the editor is an
ungoverned surface.

### `almenon.arepl` · `wallabyjs.quokka-vscode`

Both execute code continuously as it is typed. Unsuitable in a project where
**AC-MINING-PLACEMENT** governs *where* computation runs and evidence determinism is a
governed property. Continuous background execution against event data would violate the
placement constraint invisibly.

### `ritwickdey.liveserver` · `local-smart.excel-live-server`

Both start a local web server bound to workspace files. The frontend is served by Vite; an
additional local network surface serving repository contents is unnecessary and avoidable.

## What this policy does NOT do

- It does not uninstall anything.
- It does not prevent the owner overriding it locally — VS Code's per-workspace disable is a
  prompt, not an enforcement mechanism.
- It is **advisory in effect, versioned in intent**: the value is that the reasoning is
  recorded and travels with the repository, so a future contributor understands why an
  obvious tool is absent rather than concluding it was overlooked.

**Enforcement of the underlying constraints lives elsewhere and is real:** `ruff` and `mypy`
run as required CI status checks, and `check_no_secrets.py` blocks committed credentials
regardless of which extensions are active.
