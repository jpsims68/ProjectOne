# Decisions You Must Make

The profile is empty **by design**. These are the choices only you can make, in the order they should be made — each builds on the ones above it.

An AI assistant can draft, check, and challenge. It cannot tell you what you care about. If your assistant answers these for you, you will end up with a plausible-looking artifact describing nobody's project.

---

## Before you start

Two habits worth adopting now:

- **`<<FILL IN>>` is an honest answer.** A visible gap is safe. A confident fabrication is not.
- **Write down *why*, not just *what*.** In six months the reasoning is what you'll need, and it's the first thing lost.

---

## 1. What is this project, and what do you call things?

**File:** `Profile.json` · **Time:** 20–30 min

Project identity, the framework version you're binding to, and your terminology.

Terminology matters more than it looks. If your domain calls something a "case" and the framework calls it an "instance," write the mapping down once. Otherwise every later document drifts, and drift between documents is how contradictions enter a system that looks consistent.

**Decide:** project ID and prefix · bound framework version · terminology mappings · any product constraints already fixed.

---

## 2. Which documents are authoritative, and which can never be edited?

**File:** `Source-Registry.json` · **Time:** 45–90 min · **The most consequential decision here**

Two separate questions:

**Authority.** When two documents disagree, which wins? You need a tier model and a resolution rule. Without one, every conflict becomes an argument, and the loudest recent document tends to win — which is exactly wrong.

**Immutability.** Which sources can never be edited in place? A client's requirements document, a signed contract, a specification you were handed. These become evidence of what was provided and when. Changes to them go in an overlay register instead.

**Decide:** the tier model · the resolution rule · which sources are immutable · where overlays live.

> Rushing immutability is the decision people most regret. Marking something immutable that shouldn't be creates friction forever. Failing to mark something that should be means it gets quietly edited and you lose the ability to prove what was originally asked for.

---

## 3. What are you allowed to build with?

**File:** `Technology-Registry.json` · **Time:** 60–120 min

Every language, framework, library, tool, and service. **Allowlist-based: anything unlisted is denied.** That is the point, and it is also why this takes longer than expected.

For each: name, category, approved version range, role, who approved it, when, and — valuably — what alternatives were rejected and why.

**Decide:** every tool you'll use · version ranges · pinning policy (do you commit a lockfile?) · what "approved" requires.

> Recording rejected alternatives sounds like busywork and isn't. Six months on, someone reaches for the obvious tool you deliberately excluded, sees no reason recorded, and helpfully adds it.

---

## 4. Who owns what?

**File:** `Ownership.json` · **Time:** 20–40 min

Which role owns which area. Solo, this feels absurd — you own everything. Do it anyway: it's what lets you notice when you're wearing the wrong hat, and the whole role-contract model depends on it.

**Decide:** areas and owners · how ownership changes.

---

## 5. What counts as risky?

**File:** `Risk.json` · **Time:** 45–75 min

Risk classes R1–R4, what triggers each, and the escalation rule.

**Keep this rule intact: uncertainty routes upward.** If impact cannot be bounded from available evidence, it is the higher class. That's what stops the classification bending under deadline pressure.

**Decide:** what makes something R4 for *your* project · default risk per work type · what can downgrade a classification, and who may.

> Both failure modes are fatal. Everything R4 and nobody uses the framework. Everything R1 and it does nothing. You will get this wrong first time — plan the revision rather than agonizing now.

---

## 6. Who approves what, and what can never be delegated?

**File:** `Human-Approval.json` · **Time:** 30–60 min

Approval classes, who holds each, which are non-delegable.

**Preserve this:** approval is never satisfied by silence, elapsed time, an agent's recommendation, or urgency. Every one of those is a route by which unapproved things get approved.

**Decide:** approval classes · primary approver · non-delegable gates · what happens when the approver is unavailable.

---

## 7. How do you prove a claim is true?

**File:** `Verification.json` · **Time:** 45–75 min

For each kind of claim, what evidence class settles it: a deterministic check, a test, human review, an independent model, an audit trail.

**Decide:** evidence classes · which claims need which · what "reproducible" means here.

> Watch for claims with **no mechanism**. That's a coverage gap, not a satisfied requirement. On the originating project, 25 decisions needed observability evidence from tooling that had not been selected — recorded as an explicit gap rather than quietly assumed.

---

## 8. What does independent review mean when you're one person?

**File:** `Independence.json` · **Time:** 20–40 min

Four mechanisms exist: separate invocation with clean context, deterministic non-judgmental check, human review, different model or model family.

Solo, be honest. GitHub won't let you approve your own PR, so required approvals sits at 0 and human-review independence is **attested, not enforced**. Say so. Claiming a control you don't have is worse than recording the gap — it produces false confidence exactly where you're weakest.

**Decide:** which mechanisms are actually available · what independence means here · what compensates where it's absent.

---

## 9. The remaining documents

**Files:** `Lifecycle.json`, `Exception.json`, `Build-Requirements.json`, `Sustainability-Thresholds.json`, `Forward-Requirements.json` · **Time:** 30–60 min total

Mostly derived from the decisions above. Two worth a moment:

**`Exception.json`** — how a rule gets waived. Every exception needs an ID, an expiry, and a compensating control. An exception without an expiry is a silent permanent change to the rules.

**`Forward-Requirements.json`** — starts empty and becomes one of the most valuable documents you own. It records obligations placed on artifacts **that do not exist yet**: "when we write the deployment guide, it must state X, because we decided Y today."

> A decision made now often imposes content on a document written later. Without a register, that obligation lives only in memory and is silently dropped. Treat it as a **completion precondition** — before marking any listed artifact complete, check the register.

---

## After the profile

Return to `03-BOOTSTRAP-INSTRUCTIONS.md`, Step 5: create your own frozen baseline and approval record.

**One thing to hold onto.** The profile is not paperwork you complete and file. It is the record of what you decided and why, and its value shows up months later when you or someone else asks "why is it like this?" — and there's an answer, with a date and a name on it.
