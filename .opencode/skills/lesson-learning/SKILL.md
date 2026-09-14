---
name: lesson-learning
description: "Use after any failure — bug, broken test, user correction, wrong design call, a research cycle that did not yield, or any outcome worse than expected. Also use at the end of every research cycle to deposit a research-method lesson. Converts failures into permanent dated patches of skill files, with bounded bloat. Trigger keywords: lesson, mistake, I was wrong, fix this, bug, failing test, correction, what went wrong, reflexion, learn from this, research lesson, don't repeat."
---

# Lesson-Learning

Failures are the highest-value data. Every failure becomes a permanent patch to
the relevant skill file so the same mistake cannot repeat silently. Learning is
part of every loop — including research.

## When this triggers

- A test fails or the code does not work
- A user corrects you or points out an error
- You make a wrong judgment call or a poor decision
- A research cycle closed without a usable answer — that method, scope, or query
  did not work and must not be the default next time
- A research cycle closed with gains — record why the method worked, so the next
  cycle starts there
- Any outcome materially worse than expected

## One-line failure

Write the failure as a single sentence: what actually happened, not what should
have happened. If you cannot say it in one line you have not understood it.

## Root cause, not symptom

Ask: which guidance was missing or wrong? Answer against the skill files:

- If the failure was a guessing/build error → the patch belongs to
  `.opencode/skills/research-first/SKILL.md` — a check or a rule that would have
  caught this
- If the failure was a research-method failure → the patch belongs to
  `.opencode/skills/research-first/SKILL.md` as a method lesson
  ("for this kind of question, this source/query works; this one does not")
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

A research-method patch uses the same format but names the winning/losing method:

```
## Lesson (2026-09-14)
- For <kind of question>: <source/method/query> wins; <other> does not.
- Evidence: <one line from the CYCLE record>
```

The patch is an instruction, not a script. It must be so concrete that the
behavior change is mechanical. If the patch is vague or unfalsifiable, rewrite
it until it is actionable.

## Bloat balance — the constant-learning contract

Learning improves the skills without deadline-bloat in exchange:

- **A patch must change behavior.** If the rule already exists, do not append a
  duplicate — consolidate the two into the sharper wording.
- **Each lesson must earn its lines.** 1–5 lines of rule, zero lines of padding.
- **Compress periodically.** When a skill section grows noisy with dated patches,
  fold the live rules into the section body and drop the superseded ones. Tag
  the compression in the section header (e.g., "compressed 2026-09-14").
- **Vague lessons are rejected at the door.** A lesson you cannot apply to a
  future decision is bloat, not learning.

Constant improvement + smallest possible skill surface. The skill that never
shrinks is not learning; it is accumulating.

## Multiple failures

If two failures share the same root cause and same dated symptom, they signal a
single systemic gap — write one deeper patch, not two shallow ones. A flaw
diagnosed twice without being fixed is a redesign trigger: rewrite the relevant
skill section, then patch.

## Non-negotiable

No failure is closed without its lesson patch. No research cycle closes without
its method observation. Silence after failure is the one true loss. The chain of
learning is: fail → one line → root cause → patch → next.