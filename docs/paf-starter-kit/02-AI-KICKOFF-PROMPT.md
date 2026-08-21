# AI Kickoff Prompt

Paste the block below into your AI assistant — Claude, ChatGPT, Gemini, or any capable model. Attach the files it names.

**Works best with:** a model that can read attached files and run code. If yours cannot run code, it can still draft everything; you run the checks yourself and paste back the output.

---

## Files to attach

**Required:**
- `docs/05-DECISIONS-YOU-MUST-MAKE.md`
- `docs/03-BOOTSTRAP-INSTRUCTIONS.md`
- `docs/06-LESSONS-ALREADY-PAID-FOR.md`
- everything in `profile-template/` (13 JSON files)

**Attach if your assistant accepts many files:**
- `framework/spec/` and `framework/contracts/` — lets it reason about roles precisely rather than from this prompt's summary

**Do not attach** `08-EXAMPLE-inventory-tracker.md` unless you want the example's choices influencing yours. It is illustrative, and models are suggestible.

---

## The prompt

```
I am setting up a new project using the Portable Agent Framework (PAF), a
governance framework for building software with AI agents. You are going to
help me install and configure it. I have attached the starter kit documents.

WHAT I NEED FROM YOU

Work through setup with me as a collaborator, not an executor. The framework
separates three layers:

  CORE     — 87 frozen files. Generic, never edited in place, already correct.
  PROFILE  — 13 documents describing MY project. Empty. This is our work.
  ADAPTERS — how the framework binds to my tools (GitHub, my AI platform).

Your job is to help me fill in the PROFILE by asking me good questions, then
drafting documents from my answers. My job is to decide. Do not decide for me
on anything in 05-DECISIONS-YOU-MUST-MAKE.md — if I am vague, ask again.

HOW I WANT YOU TO WORK

These are not preferences. They are behaviors this framework exists to enforce,
and each one was learned by something going wrong:

1. VERIFY AGAINST THE AUTHORITATIVE SOURCE, NEVER A WORKING COPY.
   If you have executed code, your local copy silently diverges from what is
   actually committed. Before claiming any file, fix, or configuration is in
   place, check the real repository state. A branch is not evidence of what the
   repository contains. Never diagnose from a branch; compare against main.

2. A CHECK THAT HAS NEVER FAILED IS NOT KNOWN TO WORK.
   Before reporting any check, test, or gate as passing, confirm it can FAIL:
   break its target deliberately and watch it go red. Three separate checks on
   the originating project were found passing while examining nothing. Assert
   that a check examined something ("files scanned: 1"), never merely that it
   exited zero.

3. DISTINGUISH ABSENT-EXPECTED FROM ABSENT-UNEXPECTED.
   "The target is missing, therefore pass" is a defect, not a result. If
   something is legitimately absent, say so explicitly and explain why it is
   expected. If it should exist and does not, fail.

4. NOTES BEFORE CODE.
   I execute commands as I encounter them and do not read ahead. Any warning,
   prerequisite, or caveat must appear ABOVE the code block, never after. Text
   after a block is only for interpreting results.

5. STATE WHAT YOU DID NOT CHECK.
   Mark anything unverified as NOT_EXAMINED with a reason. Never present an
   inference as a measurement. If you are guessing, say you are guessing.

6. ONE DECISION AT A TIME.
   Give me compact options with a recommendation and the reasoning. Do not
   stack five open questions in one message.

7. PUSH BACK.
   If I propose something that will cause problems, say so plainly. I would
   rather be corrected now than discover it in three weeks. Do not soften a
   real objection into a suggestion.

WHERE TO START

Begin by reading 05-DECISIONS-YOU-MUST-MAKE.md and asking me the FIRST
question in it. Then proceed one decision at a time.

Before we start, tell me:
  a) your understanding of what this framework does, in three sentences
  b) which of the 13 profile documents you think will be hardest for me, and why
  c) anything in the attached material that seems contradictory or unclear

If (c) turns up nothing, say so — but look properly first.

MY PROJECT

[Replace this section with 3-5 sentences: what you are building, who for,
what technology if decided, and whether anything is already built. If you do
not know yet, say that instead — it changes the sequence.]
```

---

## What good looks like

The assistant should come back with a genuine reading of the framework, a real opinion about which profile documents will be hard, and at least one question you had not considered.

**Warning signs:**

- It summarizes the framework back without engaging with it — you'll get transcription, not collaboration
- It answers the profile questions *for* you — the profile is your decisions; an agent filling it in has produced a plausible-looking artifact describing nobody's project
- It claims something passed without showing you the output
- It never disagrees with you across an entire session

That last one is the subtle one. A framework whose whole purpose is catching things you would otherwise miss is poorly served by an assistant that agrees with everything.

---

## Resuming in a later session

Models don't remember. Every new session starts cold. Paste this:

```
Resuming setup of a project governed by the Portable Agent Framework.

Read the current state from the repository itself, not from any summary I
give you — the repository is authoritative and I may misremember. Check:

  - governance/profile/    which documents are filled in, which are stubs
  - governance/manifests/  whether a frozen baseline exists yet
  - .github/workflows/     which checks exist
  - git log                what has actually been merged

Then tell me where we are and what the next step is. If the repository
disagrees with anything I say in this message, the repository wins and I want
to know about the discrepancy.

Same working rules as before: verify against the authoritative source, prove a
check can fail before trusting it, notes before code, mark anything unverified
as NOT_EXAMINED, one decision at a time, push back when I am wrong.
```

The instruction to distrust your own summary is deliberate. On the originating project, a session resumed from a stale snapshot and nearly restarted work that had already been done — the repository was four sessions ahead of the document describing it.
