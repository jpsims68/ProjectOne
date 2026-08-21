# What This Costs You

The honest version. Read it before you commit, not after.

---

## The overhead is real

| | Cost |
|---|---|
| Setup | 11–22 hours with an AI assistant, 40–70 without |
| Every PR | 5–15 minutes of governance metadata once fluent, 30–60 for your first |
| Adding a technology | A change package and an approval, not just an install |
| Changing a constraint | 30–90 minutes |
| Adding a check | 2–4 hours, because the fixture matrix is not optional |
| Every session end | 15–30 minutes updating state documents |
| **Steady state** | **roughly 10–20% on top of the work itself** |

Nothing here makes you faster. It makes certain kinds of failure loud instead of silent, and it costs you time to do that.

---

## The friction you'll actually feel

**The PR template is long.** Risk classification, evidence, recovery, independent review, approval. Your first one takes an hour and feels absurd for a one-line change. That curve is steep — the fifth takes ten minutes — but the first one is genuinely unpleasant.

**Checks block merges.** Sometimes for reasons that feel pedantic. That's the deal: a gate you can wave through isn't a gate.

**The allowlist is strict.** Reaching for a small utility library means a registry entry and an approval. Sometimes you'll want to install something and just move on, and you can't.

**Nothing is edited in place.** Frozen artifacts get superseded, immutable sources get overlaid. Both are more work than editing a file.

**It's opinionated about honesty in a way that's occasionally uncomfortable.** You'll be asked to record that a control is *attested, not enforced*, or to mark something NOT_EXAMINED rather than assuming it's fine. That is the point, and it still stings.

---

## When NOT to use this

**Throwaway spikes and prototypes.** Code you will delete. The framework has a `ROLE_SPIKE` contract precisely so exploratory work can run *outside* the governed path. Use it, or don't govern the spike at all.

**Solo projects with no consequences.** A personal tool nobody depends on, no clients, no compliance. The overhead buys you nothing.

**Genuinely short-lived work.** Under a few weeks, setup won't amortize.

**When you don't yet know what you're building.** The profile asks what you're allowed to build with and what counts as risky. If those answers are still moving, wait. Installing this during discovery produces a profile that's wrong by the time it's finished.

**When nobody will enforce it.** A framework you route around is worse than none — it produces documented confidence you haven't earned. If you'll bypass the checks under deadline, don't install them.

---

## When it earns its keep

**When an AI agent does most of the work.** This is the strongest case. An agent produces plausible output at volume, and plausibility is precisely what review is bad at catching. Mechanical gates catch what reading does not.

**When silent failure is expensive.** Client data, money, compliance, anything where finding out in six months costs far more than the 15% overhead.

**When the project outlives your memory of it.** Six months on, "why is it like this?" has an answer with a date and a name.

**When more than one person — or one agent — touches it.** Role contracts and explicit authority are worth most where handoffs happen.

**When you need to prove something later.** Evidence records, approval records, and an immutable baseline are how you demonstrate what was decided and checked, rather than asserting it.

---

## The honest summary

This framework is a **bet that silent failure costs more than visible friction.**

That bet is right for a client-facing system built largely by AI agents. It is wrong for a weekend project. Most work sits somewhere between, and the judgment is yours.

If you're unsure: install it, do the one governed change in Step 8, and see how the friction feels on something trivial. That hour will tell you more than any amount of further reading.

And if you decide against it — read `06-LESSONS-ALREADY-PAID-FOR.md` anyway. Those lessons cost real time to learn and don't require adopting anything.
