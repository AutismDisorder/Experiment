# AGENTS.md — Operating Principles

These principles load every session. Two hard rules drive all work. Everything
here is non-negotiable; nothing is ritual.

---

## Research-first — always, unconditionally, extensive, and per-cycle

**Every single line of code, every decision, every plan is researched online
first.** No exception. No shortcuts. This is not a suggestion. It is a hard,
unconditional rule.

There is no "trivial" change exempt from research. A one-line fix is still a
decision and still needs a source. Nothing is ever assumed, nothing is ever
guessed, nothing is ever written without an external, verifiable source behind it.

### Research is extensive while it yields; it adjusts when it doesn't

The depth of a research cycle is not a fixed budget — it is **dynamically
adjusted** to the returns the research itself is producing. When research is
yielding large gains, keep going. It does not stop early.

Diminishing returns are not the end of research — they are the signal to
**adjust**. When a cycle starts yielding less, change the method or the scope:

- switch **search method**: web search ⇄ GitHub (repos, code search, issues, PRs)
- switch **source type**: docs, papers, reference implementations, package source
- widen or narrow the **query/scope**: broader survey vs. exact API signature

After an adjustment, research continues. Only when an **adjusted** cycle still
yields nothing new is the research done — and that cycle closes with a verdict.

### A cycle is one research round for ONE line or ONE decision — per-cycle, not per-session

- A **cycle** = the single round of research behind one line of code or one
  decision.
- Adjustment is judged **per cycle**. A drop in this cycle's returns does not
  shrink any other cycle. Every line starts its cycle fresh and extensive.
- There is no session-wide research budget and no "we researched enough earlier."
  Each cycle must be earned on its own returns, and each closes with its own
  verdict.

### How it works (procedure in `.opencode/skills/research-first/`)

1. State the decision as one sentence before touching any code.
2. Search online. Read the source. Do not stop at summaries.
3. Assess the gain of each source. While gains hold, extend the cycle.
4. On diminishing returns, adjust — method, source type, or scope — and keep
   going. Only an adjusted-but-still-barren cycle closes.
5. Write the verdict in the same session: adopt / adapt / reject — with the URL
   or `[UNVERIFIED]` if the source could not be fetched. Record the cycle:
   methods used, how far it went, why it closed.
6. Every commit message, PR description, and inline comment records which
   research verdict backs the change. No line of code ships without a verdict.

### Zero-tolerance

- A line with no backing verdict is a bug — fix it or remove the line.
- A decision made by guess is a bug — fix it or revert it.
- Stopping a cycle that is still yielding gains is a failure of judgment.
- Adjusting a barren cycle into a different method is obligation, not choice.

---

## Lesson-learning — every failure, always, and the research loop learns too

Every failure becomes a permanent patch to a skill file. No script, no process —
a direct, dated, concrete patch to the file that, if it had existed before the
failure, would have prevented it. This is Reflexion carried as instructions.

### Learning is part of research itself

Every research cycle ends in a lesson-sized observation: which method worked,
which did not, what the cycle teaches about researching this kind of question.
That observation patches `.opencode/skills/research-first/` so the next cycle
starts better — the research method is a skill that trains on its own outcomes.

### How it works (procedure in `.opencode/skills/lesson-learning/`)

1. One line: what actually happened.
2. Root cause: which guidance was missing or wrong.
3. Patch: append one rule (1–5 lines) to the relevant SKILL.md, dated either as
   a lesson or as a research-method refinement.
4. No failure closes without its patch. Silence after failure is the true loss.

### Balance — learning with bounded bloat

Skills grow only through lessons that change behavior. A patch that would merely
duplicate an existing rule is a consolidation, not an addition. Periodically,
related patches are compressed into one rule. The goal is constant improvement
with the smallest possible skill surface — bloat is a failure of learning, not a
side effect of it.

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