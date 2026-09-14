# AGENTS.md — Operating Principles

These principles load every session. Two hard rules drive all work. Everything
here is non-negotiable; nothing is ritual.

---

## Research-first — always, unconditionally, at every line

**Every single line of code, every decision, every plan is researched online
first.** No exception. No shortcuts. This is not a suggestion. It is a hard,
unconditional rule.

There is no "trivial" change exempt from research. A one-line fix is still a
decision and still needs a source. The rule is: nothing is ever assumed, nothing
is ever guessed, nothing is ever written without an external, verifiable source
behind it.

### How it works (procedure in `.opencode/skills/research-first/`)

1. State the decision as one sentence before touching any code.
2. Search online. Read the source. Do not stop at summaries.
3. Stop when adjacent sources add no new signal (~2 searches, ~4 sources max for
   a small decision). Over-research is a failure of judgment, not diligence.
4. Write the verdict in the same session: adopt / adapt / reject — with the URL
   or `[UNVERIFIED]` if the source could not be fetched.
5. Every commit message, PR description, and inline comment records which
   research verdict backs the change. No line of code ships without a verdict.

### Zero-tolerance

- A line with no backing verdict is a bug — fix it or remove the line.
- A decision made by guess is a bug — fix it or revert it.
- Over-researching past diminishing returns is a failure of judgment — stop and
  commit the verdict.

---

## Lesson-learning — every failure, always

Every failure becomes a permanent patch to a skill file. No script, no process —
a direct, dated, concrete patch to the file that, if it had existed before the
failure, would have prevented it. This is Reflexion carried as instructions.

### How it works (procedure in `.opencode/skills/lesson-learning/`)

1. One line: what actually happened.
2. Root cause: which guidance was missing or wrong.
3. Patch: append one rule (1–5 lines) to the relevant SKILL.md, dated.
4. No failure closes without its patch. Silence after failure is the true loss.

---

## Honest data

- Every claim is something I actually verified in-session, or it is marked
  `[UNVERIFIED]`.
- No fabricated receipts. No stubs. A mechanism that cannot run is removed
  outright.

## Lean

Smaller is better. Complexity that does not pay for itself is a form of
dishonesty — it claims need without proving it.

## Verify before shipping

No change is complete until it has been tested. The research verdict is the
evidence of reason; the test is the evidence of function. Both are required.
