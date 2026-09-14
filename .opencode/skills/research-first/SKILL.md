---
name: research-first
description: "Non-optional before writing ANY code or making ANY decision or any plan. Runs per-cycle: one cycle = the research behind ONE line or ONE decision. Extensive while gains hold, dynamically adjusted (method, source type, scope) on diminishing returns, closed only when an adjusted cycle still yields nothing. Trigger keywords: research, research first, how should I build, which library, best practice, compare, evaluate, survey, evidence, proven, verified, don't guess."
---

# Research-First

Everything is researched before it is built. Guessing is a bug. This procedure is
non-optional for every code-writing or decision-making task.

A **cycle** is the single round of research behind one line of code or one
decision. Every cycle is judged on its own returns — a cycle's depth is never
limited by what any other cycle did. There is no session-wide research budget.

## One-line framing

Before doing anything, write the decision as a single sentence. A decision with no
sharp sentence is not yet a decision — sharpen it first.

## Cycle start: extensive

Every cycle begins extensive, regardless of history. The first search covers the
question broadly; the first read is of the actual source, not a summary of a
summary.

## Gain check, per source

After each source, ask: does this materially deepen understanding or narrow the
decision?

- **YES — gains hold.** Keep going. There is no cap on a productive cycle. Large
  gains justify a deliberately deeper pass.
- **NO — returns diminish.** That is not the end of research; it is the trigger
  to adjust.

## Adjust, then continue

On a barren or thinning pass, change the approach and keep researching:

| Adjustment | Move |
|---|---|
| Search method | web search ⇄ GitHub (repos, code search, issues, PRs) |
| Source type | docs ⇄ papers ⇄ reference implementations ⇄ package source |
| Query / scope | broader survey ⇄ exact API signature; other terms, another repo |

After an adjustment, assess gain again. Research ends only when an **adjusted**
cycle still yields nothing new.

## Cycle close: verdict

Every cycle closes with a written verdict — same session, same message:

```
CYCLE:      <decision in one line>
METHODS:    web · github · docs · papers   (which were tried)
DEPTH:      <sources read>
CLOSE:      gain held → adjusted (x3) → barren after adjustment
VERDICT:    adopt | adapt | reject | mixed
SOURCE:     <url> or [UNVERIFIED]
REASON:     one sentence
```

Write the METHODS, DEPTH, and CLOSE lines honestly. They are the record that the
cycle was extensive, that it adjusted rather than stopped, and that the close
happened only after adjustment failed to yield. This record is the feedback that
trains the research skill itself.

## Verdicts

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
- The CLOSE line is never faked: either the cycle adjusted, or it closed when an
  adjustment failed to yield. Both are honest answers.

## Research-method lessons

The research skill trains on its own outcomes. After each cycle, deposit one
usable observation and patch `.opencode/skills/research-first/SKILL.md`:

- "For <kind of question>, GitHub code search beat web search because <reason>"
- "For <kind of question>, exact-symbol queries beat broad ones"

These patches tune how the next cycle starts. If the patch duplicates an existing
rule, consolidate instead of appending.

## Values-based tiebreak

When two researched approaches both clear the bar, prefer the one that is simpler,
more maintainable, and closer to what the ecosystem already does — by judgment,
never by fashion.