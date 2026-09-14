---
name: research-first
description: "Enforced before writing ANY code or making ANY decision or any plan. Use when starting a build, choosing a library, framework, approach, or architecture, writing a plan, or whenever anything could be guessed instead of researched online. Trigger keywords: research, research first, how should I build, which library, best practice, compare, evaluate, survey, evidence, proven, verified, don't guess, verify."
---

# Research-First

Everything is researched before it is built. Guessing is a bug. This procedure is
non-optional for any code-writing or decision-making task.

## One-line framing

Before doing anything, write the decision as a single sentence. A decision with no
sharp sentence is not yet a decision — sharpen it first.

## The research pass

1. Search for the exact organ you are about to build or the exact decision you are
   about to make. Never pre-load a survey of things you are not building.
2. Consult the first source that clearly covers the question. Open and read it, do
   not skim summaries of summaries.
3. If a second source is needed, it must answer a new discriminating question the
   first source did not. Two adjacent sources with no new signal = stop.
4. Small decision stop-rule: ~2 searches / ~4 sources maximum. Beyond that you are
   over-researching, which is a failure of judgment, not diligence.

## Verdict format

Every research pass ends in a written verdict — same session, same message. It is
not a suggestion; it is the deliverable of the research step:

```
VERDICT: adopt | adapt | reject | mixed
SOURCE: <url> or [UNVERIFIED]
REASON: one sentence
```

- `adopt` — use the source's approach as-is
- `adapt` — use it with a modified detail (state which)
- `reject` — the source does not fit; say why in one sentence
- `mixed` — parts fit, parts do not; list which

## Honest data

- Only sources you actually fetched/read count as backing. A URL you did not open
  is `[UNVERIFIED]`.
- Never fabricate a citation, a result, or a "best practice." If you cannot verify
  it, mark `[UNVERIFIED]` and say you did not verify it.
- Every line of code in the final change traces to a verdict. In commit messages,
  summarize: `research: <verdict> <source>`.
- If research turns out to be disproportionate for a trivial change (a one-line fix
  with an obvious answer), say so explicitly rather than pretending research
  happened. The rule is: no guessing; the discipline is: no theater.

## Values-based tiebreak

When two researched approaches both clear the bar, prefer the one that is simpler,
more maintainable, and closer to what the ecosystem already does — by judgment,
never by fashion.