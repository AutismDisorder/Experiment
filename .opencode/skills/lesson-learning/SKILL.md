---
name: lesson-learning
description: Use after any failure — bug, broken test, user correction, wrong design call, a review that found a defect, or any outcome that was worse than expected. Trigger keywords: lesson, mistake, I was wrong, fix this, bug, failing test, correction, what went wrong, reflexion, learn from this, don't repeat.
---

# Lesson-Learning

Failures are the highest-value data. Every failure becomes a permanent patch to
the relevant skill file so the same mistake cannot repeat silently.

## When this triggers

- A test fails or the code does not work
- A user corrects you or points out an error
- You make a wrong judgment call or a poor decision
- A review finds a defect you introduced
- Any outcome materially worse than expected

## One-line failure

Write the failure as a single sentence: what actually happened, not what should
have happened. If you cannot say it in one line you have not understood it.

## Root cause, not symptom

Ask: which guidance was missing or wrong? Answer against the skill files:

- If the failure was a guessing/build error → the patch belongs to
  `.opencode/skills/research-first/SKILL.md` — a check or a rule that would have
  caught this
- If the failure was a fixing/verification error → the patch belongs to the
  relevant skill or AGENTS.md as a new verification sub-rule
- If AGENTS.md has a principle you violated → strengthen that principle's edge
  case wording, or add the concrete negative example

## Patch format

Append a bounded rule (1–5 lines) to the relevant SKILL.md, tagged with the date:

```
## Lesson (2026-09-14)
- Never X. Always Y instead.
- Symptom: <one line> → Root cause: <one line>
```

The patch is an instruction, not a script. It must be so concrete that the
behavior change is mechanical. If the patch is vague or unfalsifiable, rewrite
it until it is actionable.

## Multiple failures

If two failures share the same root cause and same dated symptom, they signal a
single systemic gap — write one deeper patch, not two shallow ones. A flaw
diagnosed twice without being fixed is a redesign trigger: rewrite the relevant
skill section, then patch.

## Non-negotiable

No failure is closed without its lesson patch. Silence after failure is the
one true loss. The chain of learning is: fail → one line → root cause → patch → next.