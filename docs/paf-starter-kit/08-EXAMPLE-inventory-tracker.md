# OPTIONAL EXAMPLE — "StockRoom", a small inventory tracker

> ## ⚠ THIS IS ILLUSTRATIVE ONLY
>
> **StockRoom is fictional.** It is not part of the framework, not a template, and not a starting point. It exists so you can see the profile decisions applied to something small and concrete instead of reading them in the abstract.
>
> **Do not copy these answers.** They are right for a fictional project and almost certainly wrong for yours. Copying them produces a profile that describes StockRoom, not your work.
>
> Nothing else in the kit references this file. Delete it if you'd rather not have it around.

---

## The fictional project

A two-person team building a web tool for small warehouses: track stock levels, record movements in and out, alert on low stock. React frontend, Python API, Postgres. Three pilot customers already signed up. No existing code.

Chosen deliberately as an ordinary project — no unusual constraints — so the reasoning shows rather than the domain.

---

## 1. Profile — identity and terminology

The team hit terminology immediately. The framework says "slice." Warehouse people say "area." Their spec said "module." Three words, one concept, and documents already disagreed.

They wrote: *slice = a vertically-owned feature area; the spec's "module" is a slice; "area" in customer-facing copy means a physical warehouse zone and is unrelated.*

**Worth noticing:** this took fifteen minutes and prevented an ambiguity that would have surfaced in every later document. The word "area" being overloaded was invisible until they wrote it down.

---

## 2. Source registry — authority and immutability

**Immutable:** the signed pilot agreement, and each customer's stock-data export spec.

**Reasoning:** both are evidence of what a customer provided. If a customer later disputes what was agreed, an edited copy proves nothing.

**Authority order:** signed agreement → architecture decisions → PRD → working notes.

**Where they nearly went wrong:** the initial instinct was to mark the PRD immutable "because it's important." They caught it — the PRD is *theirs* and changes constantly. Immutability is about **provenance**, not importance. Marking it immutable would have meant an overlay for every ordinary product change.

---

## 3. Technology registry — 22 entries

Python 3.12, FastAPI, SQLAlchemy, Postgres 16, React 18, TypeScript, Vite, pytest, ruff, mypy, and so on. Each with a version range and an approver.

**Rejected alternatives recorded, and this is the part that paid off:**

- *Django rejected* — the team wanted an API-first service; Django's strengths are elsewhere
- *MongoDB rejected* — stock movements are relational and need transactional integrity
- *Redux rejected* — application state is small; React context suffices

Four months later a contractor proposed adding Redux. The registry showed it had been considered and why it was excluded. The conversation took two minutes instead of a week.

---

## 5. Risk — where they got it wrong first

Their first draft made anything touching stock quantities R4. Sensible in theory. In practice **every single PR was R4**, because it's a stock-tracking application. Full portfolio runs on typo fixes. They stopped using the framework within a fortnight.

Revised: R4 is reserved for changes to the **movement ledger** — the append-only record of stock in and out. Everything else touching stock is R3. Display, reporting, and UI are R2.

**The lesson generalizes:** they'd classified by *subject matter* rather than by *what an error would cost*. A wrong quantity on a dashboard is embarrassing. A wrong entry in the ledger is unrecoverable, because everything downstream derives from it.

---

## 6–8. Approval, verification, independence

Two people, so required approvals sits at 1 and human review is genuinely enforced — the one thing a solo project cannot have.

Non-delegable: schema changes to the movement ledger, and anything touching customer data export.

**On independence, they were honest:** for the two weeks when one developer was on leave, human review was unavailable. Rather than pretend, they recorded an exception with an expiry date and a compensating control — an additional deterministic check on ledger writes. The exception expired when she returned.

---

## 9. Forward requirements — the one they nearly skipped

It starts empty and feels pointless. They added an entry anyway when deciding to defer multi-warehouse support:

> *When the deployment guide is written, it must state that the schema carries a `warehouse_id` on every table from day one, even though only one warehouse is supported in v1. Deferring the column would require a data migration later, which the no-migration principle forbids.*

Eight months on, a new developer proposed dropping the "unused" column. The register had the answer, with a date and a name. **That single entry justified the document.**

---

## What StockRoom cost

Setup: **fourteen hours** across four sessions. Two people, AI-assisted, familiar stack.

First month: roughly **15% overhead** on top of development.

**What they say it bought:** two prevented incidents. A migration script would have rewritten historical ledger entries — caught by the R4 classification requiring a recovery plan, which forced someone to ask what rollback meant for an append-only ledger. And a dependency with a known CVE was blocked at the registry before it was ever installed.

**What they'd do differently:** get the risk classification wrong faster. They spent three hours agonizing over it, got it wrong anyway, and fixed it in twenty minutes after two weeks of real use. Ship a rough classification and revise on evidence.

---

## Again, and finally

**StockRoom is not real, and these are not your answers.** If any of it feels directly applicable, be suspicious — that's a sign of pattern-matching rather than deciding. The value is in seeing *how* the decisions were reasoned about, not what was decided.
