# Lessons Already Paid For

Failures suffered on a real project running this framework. Each one cost time, and each is preventable if you know about it. Inherit them free.

Add your own as you find them. This is the document that stops a project relearning the same thing every quarter.

---

## 1. A check that has never failed is not known to work

**The single most valuable lesson here.**

Three separate CI checks were found passing while examining nothing:

- A test gate globbed `tests/**/*.py`. Bash has no globstar by default, so it matched nothing, printed "no tests yet," and passed. **The tests had never run in CI.**
- `pip-audit` pointed at a requirements file that did not exist. It reported "no dependencies yet" and passed. **Nothing was ever audited.**
- `bandit` targeted two directories that did not exist. Same outcome. **No source was ever scanned.**

All three were green for weeks across multiple merges. Green CI meant nothing, and nobody knew.

Worse: the test gate was **suppressing a real failure.** CI was pinned to Python 3.12 while the project required 3.13. The smoke tests would have caught it immediately — if they had ever run.

**What to do**

- Negative-test every gate: break its target deliberately, confirm it goes red. `bootstrap_selftest.py` does this.
- Assert a check **examined something** — "files scanned: 1" — never merely that it exited 0.
- Distinguish **absent-expected** (assert it explicitly) from **absent-unexpected** (fail). "Target missing, therefore pass" is the defect.
- Green CI is evidence only to the extent each gate has been proven capable of going red.

**It recurs.** A check written *specifically to prevent this* passed all ten of its violation fixtures on its first run — because it scanned nothing when given a file argument. The fixture harness caught it in seconds. Without the harness it would have shipped as a required check that could never fail.

---

## 2. Never diagnose repository state from a branch

A problem was diagnosed by examining a branch rather than the main line. The branch was stale. The diagnosis was confidently wrong, and the fix built on it was wrong too. **45 minutes lost**, plus the cost of unwinding.

**What to do**

- Verify against the authoritative source — the remote, not a local copy, not a branch, not a summary, not memory.
- A branch is not evidence of what the repository contains.
- After any merge, pull before further work.
- When an agent has been executing code, its working copy has silently diverged. Re-clone rather than trust it.

---

## 3. Sync folders corrupt git repositories

The clone lived inside OneDrive. Sync locks and git operations fought; failures were intermittent and hard to attribute.

**What to do**

- Keep clones outside OneDrive, Dropbox, iCloud Drive.
- On Windows, `Documents` and `Desktop` are often redirected into OneDrive. Use `C:\dev\`.
- Moving? Clone fresh at the new location rather than dragging the folder — nothing then travels through the sync engine.

---

## 4. Browser upload silently mangles multi-file commits

Uploading 137 files through the GitHub web interface flattened the directory structure, dropped dot-files, and capped at 100 files. **Silently.** The PR had to be abandoned and rebuilt.

**What to do**

- Use a desktop git client or the command line for anything multi-file or nested.
- Never use browser upload for a commit with directory structure.

---

## 5. Auditing the wrong environment produces noise that looks like findings

A local `pip-audit` reported **316 vulnerabilities across 49 packages**. Alarming — and almost entirely irrelevant. It had audited the *global* Python install: Jupyter, PyTorch, LangChain, everything ever installed on that machine. **41 of the 49 packages had nothing to do with the project.**

The eight that did were stale only because `pip install -r` leaves already-satisfied packages alone. Resolved cleanly in a fresh environment: **zero** vulnerabilities.

The real finding was not 316 CVEs. It was that **the local environment and CI had silently diverged.**

**What to do**

- Audit the project environment, never a global interpreter.
- Commit a lockfile and have CI install from it with a frozen flag, so divergence fails loudly.
- When a result looks absurd, question the measurement before the subject.

---

## 6. Removing a line without knowing everything it does

A `pip install --upgrade pip` line was removed from CI because its stated purpose had gone away. The next run failed: `pip-audit` audits the **resolved environment**, and pip is part of it. The shipped pip carried four known vulnerabilities.

The line had a second, load-bearing purpose nobody had identified.

**What to do**

- Before deleting something in a working system, ask what else it might be doing.
- When you restore it, **write the reason inline** so it isn't removed a third time.

---

## 7. Documentation drifts from reality faster than you expect

A continuity snapshot read "step 100" while the repository was at step 109. It also claimed 6 forward requirements when 10 existed — and a rule forbade marking a document complete without checking that register. A reader trusting "6" would have stopped four short.

At its worst the repository was **four sessions ahead** of the document describing it, and a session nearly resumed from the wrong point.

**What to do**

- Update state documents at the **end of every session**, not when convenient.
- Derive facts from the repository — file counts, hashes, statuses — never transcribe from memory.
- On resume, read state from the repository and treat any summary, including your own, as suspect.

---

## 8. An enumeration after a colon is not a specification

A requirement said: scan for *"capabilities absent from Azure SQL Database: [four examples]"*. Its acceptance test required failing on those four.

A check implementing exactly four would have **passed its own acceptance test while missing its purpose** — the objective was the governing clause, the four were illustrative.

**What to do**

- When a requirement states an objective and then gives examples, build to the objective.
- If the acceptance test is narrower than the objective, the test is the defect.
- Amend the wording so the requirement and the implementation agree, rather than leaving them to diverge.

---

## 9. A check that cries wolf is worse than no check

Two near-misses:

- A secret-scanner flagged tool caches (`.mypy_cache`) after any type-check run. It failed locally every time on nothing. Left alone, it would have trained the reader to ignore a real finding.
- A SQL scanner nearly blocked all three-part names — but names referencing the *current* database are legal. It would have false-positived on ordinary code.

**What to do**

- Every check needs a **clean control fixture** that would trip a naive implementation.
- Precision is not polish. A disregarded check is no check.

---

## 10. Never assert a document does not exist without searching everywhere

An agent was asked whether a step-by-step plan existed for the next phase of work.
It searched one of two unpacked packages, found nothing, and reported that no plan
existed. A plan was then improvised and used to number two days of work.

The plan had been in the other package the whole time — already unpacked, already
on disk, never searched.

The cost was not the wasted planning. It was that the improvised numbers were
recorded in a state document as completed steps, asserting work was done that had
never been performed. A successor reading it would have skipped that work.

**What to do**

- A negative claim needs a complete search, not a partial one. "I did not find it"
  and "it does not exist" are different statements.
- Say which places you searched. That makes the gap visible to someone who knows
  the material better than you do.
- When you improvise structure because canonical structure appears to be missing,
  mark it as improvised. Then it is correctable rather than load-bearing.

---

## 10. Approval is never implied

Recorded as an absolute: **approval is never satisfied by silence, elapsed time, an agent's recommendation, or emergency status.**

It reads as obvious and is violated constantly — an agent proposes, nobody objects, work proceeds, and everyone later believes it was approved.

**What to do**

- Require explicit approval, recorded with a name and a date.
- An agent may recommend. It may never infer consent from silence.
