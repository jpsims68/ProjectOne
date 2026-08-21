# Bootstrap Instructions

Getting from a folder of files to a working governed repository.

**Every command here was executed against a fresh project before this document was written.** Where something could not be tested from the authoring environment, it says so explicitly.

---

## Step 1 — Create the repository

Create an empty repository on GitHub. Do not add a README, `.gitignore`, or licence — you'll be adding files with a specific layout and an initial commit gets in the way.

Clone it locally.

> **Not on GitHub?** The framework itself is host-agnostic, but only the GitHub adapter has been exercised in production. The gates are plain Python and run anywhere; the workflow files and branch-protection steps are GitHub-specific. Budget extra time and read `04-MODIFICATION-GUIDE.md` on the adapter layer.

> **A warning that cost the originating project 45 minutes:** do not put your clone inside a syncing folder — OneDrive, Dropbox, iCloud Drive. Sync engines and git fight over `.git`, and the corruption is intermittent and hard to diagnose. On Windows, note that `Documents` and `Desktop` are often redirected into OneDrive. Use something like `C:\dev\yourproject`.

---

## Step 2 — Copy the kit into place

Layout matters — the checks resolve paths relative to the repository root.

```
your-repo/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── governance.yml
│   └── pull_request_template.md
├── governance/
│   ├── framework/          ← from kit framework/     (87 files, never edit)
│   ├── adapters/           ← from kit adapters/
│   ├── adapter-config/     ← from kit adapter-config/
│   ├── scripts/            ← from kit scripts/
│   └── profile/            ← from kit profile-template/, renamed
├── app/                    ← your code (name it whatever fits)
└── tests/
```

Notice `scripts/`, `framework/`, `adapters/` and `adapter-config/` all move **under** `governance/`. The kit is flat for browsing; the installed layout is nested.

Rename the profile templates from `YOURPROJECT-` to your own prefix. Keep it short and uppercase — it appears in artifact IDs throughout.

---

## Step 3 — Prove the gates before trusting them

**Do this before anything else works.** Not after.

```bash
python3 governance/scripts/bootstrap_selftest.py
```

Expected output ends with:

```
RESULT: every gate proved it can go red
```

It copies your repository to a temporary sandbox, deliberately breaks what each check guards, and confirms the check fails. Your repository is not modified.

### If a gate reports MISCONFIGURED

It failed on a *clean* tree, which means it's broken, not that you have a problem. Usual causes:

- **Wrong layout** — a check resolves paths from the repository root and isn't finding `governance/`. Re-read Step 2.
- **Python version** — the checks need 3.9+ for modern type syntax. `python3 --version`.
- **Line endings** — on Windows, if git converted `SHA256SUMS.txt` or the files it covers to CRLF, every hash mismatches. Add `* -text` to `.gitattributes` for the framework directory, re-clone, and try again.

### If a gate reports DEFECTIVE

It passed while its target was broken. **Stop and fix it.** This is the failure this framework exists to prevent, and a defective gate is worse than no gate — it produces confidence you haven't earned.

---

## Step 4 — Fill in the profile

This is the bulk of the work. `05-DECISIONS-YOU-MUST-MAKE.md` walks it, and `02-AI-KICKOFF-PROMPT.md` is how to do it with an assistant.

You do not have to finish all thirteen before continuing — but you should finish `Profile.json`, `Source-Registry.json`, and `Technology-Registry.json`, because the rest reference them.

**Leaving a document as `<<FILL IN>>` is fine and honest. Inventing plausible content to look complete is not.** An empty slot is visible; a fabricated one isn't.

---

## Step 5 — Create your own frozen baseline

The kit ships **without** a baseline or approval record, deliberately: a baseline records that a specific person approved a specific set of files on a specific date. Shipping one would hand you approvals nobody gave.

```bash
python3 governance/scripts/create_baseline.py --project MYPROJ --approver "Your Name"
```

This writes two files:

- `governance/manifests/MYPROJ-Frozen-Baseline-v1.0.json` — every governed file with its hash
- `governance/approvals/MYPROJ-Owner-Approval-Record.json` — the record naming you

Then do the three things it tells you:

```bash
# 1. Read the approval record. It says you approved this. Make that true.
cat governance/approvals/MYPROJ-Owner-Approval-Record.json

# 2. Confirm the baseline verifies
python3 governance/scripts/check_baseline_integrity.py     # must PASS

# 3. Re-prove the gates now that a real baseline exists
python3 governance/scripts/bootstrap_selftest.py
```

**On a fresh project this hashes roughly 115 files** — 87 framework, 5 adapters, 2 adapter-config, 13 profile, and the scripts.

The generator refuses to overwrite an existing baseline. That's intentional: a frozen baseline is never edited, only superseded by a new version through a governed change. See `04-MODIFICATION-GUIDE.md`.

---

## Step 6 — Adapt the workflows

`.github/workflows/ci.yml` and `governance.yml` are a **Python/uv reference implementation**. The gate discipline transfers to any stack; the commands don't.

If you're on Python, they work nearly as-is — adjust the version pin and directory names.

If you're not, replace the commands but preserve four properties, which is where the value actually lives:

1. **Every step either does its work or fails.** No step may conclude "target absent, therefore pass."
2. **Absent-expected is asserted explicitly.** Absent-unexpected fails.
3. **Dependencies install from a lockfile**, so CI and local cannot silently diverge.
4. **Job `name:` values are the required-check names.** Renaming a job silently detaches its required check — a merge gate that quietly stops existing.

> **Expect your first CI runs to fail.** On the originating project the harness took three pushes to go green, and every failure was a real finding: a build-backend error, a genuine CVE surfaced by a check that had never worked, then a regression from removing a line that turned out to be load-bearing. If your first run fails, the system is working.

---

## Step 7 — Configure branch protection

> **This is the least-proven part of the kit.** It could not be executed from the authoring environment — it requires an authenticated browser session. The steps below come from direct experience on a live repository, but were not re-validated on a fresh one. Read the screens carefully rather than following blindly.

In **Settings → Rules → Rulesets**, create a ruleset targeting your default branch:

| Setting | Value | Why |
|---|---|---|
| Enforcement status | **Active** | Evaluate-only mode enforces nothing |
| Bypass list | **Empty** | Including yourself. A bypass that exists gets used. |
| Require a pull request before merging | On | |
| Require status checks to pass | On | |
| Required checks | all your check jobs | Add each by name |
| **Source for each check** | **GitHub Actions** | **Not "Any source"** — that permits forgeable results |
| Require branches up to date before merging | On | Prevents merging against a stale base |
| Block force pushes | On | |
| Restrict deletions | On | |

**Required approvals** will likely be **0** if you're solo — GitHub won't let you approve your own PR, so any higher number blocks every merge. That is a real limitation, and it means human-review independence on a solo repository is **attested, not enforced**. Record it that way in `Independence.json` rather than claiming a control you don't have.

Also check **Settings → Actions → General**: workflow permissions should be **read-only** by default. A compromised action with write access can push directly, and no merge rule stops it.

---

## Step 8 — One governed change, end to end

Do this before real work. It is the highest-value hour in the whole setup.

1. Branch: `work/SETUP-001-first-change`
2. Change one line of a README
3. Commit, push, open a PR
4. **Fill in the PR template properly.** All of it. It will take 30–60 minutes the first time and 5–10 thereafter.
5. Watch every check run
6. Merge, delete the branch, pull

What you're testing isn't the change — it's whether the machinery works and whether you can live with the friction. If the PR body feels unbearable, better to learn that now, on a one-line change, than on something that matters.

---

## Troubleshooting

**"A check fails on a clean tree."** Misconfigured, not a finding. Step 3.

**"A check passes when it shouldn't."** The serious one. Run the self-test. If it reports every gate proved, then your check is fine but doesn't cover that case — write a fixture and extend it.

**"Baseline integrity fails after I edited a framework file."** Working as designed. You edited a frozen artifact. Revert it, and read `04-MODIFICATION-GUIDE.md` on why the answer is almost never to change `framework/`.

**"CI passes locally but fails on the runner."** Environment divergence — the thing lockfiles exist to prevent. Confirm CI installs from the lockfile and that your local environment does too. Auditing a global interpreter instead of the project environment produces noise that looks like findings.

**"I don't know what to put in a profile document."** Leave it `<<FILL IN>>` and move on. Come back when the project has taught you the answer. An honest gap beats a confident fabrication.
