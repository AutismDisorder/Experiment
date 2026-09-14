---
name: research-first
description: Non-optional research-first procedure for every code-writing or decision-making task. Runs per-cycle with gain rubric, mandatory adjustment, structured verdicts, and transitive lesson propagation to lesson-learning. Based on CoT (Wei et al. 2022), Self-Consistency (Wang et al. 2022), Reflexion (Shinn et al. 2023), Medprompt composition (Nori et al. 2023), DSPy parameterized modules (Khattab et al. 2023), and LLM agent architecture (Wang et al. 2023).
license: MIT
compatibility: opencode
metadata:
  category: core
  governs: [lesson-learning]
  tokenBudget: 800
  maxSeverity: critical
---

## Purpose
Every line of code and every decision is backed by a researched, verified, and propagated verdict. Guessing is a bug.

## Triggers
research, research first, how should I build, which library, best practice, compare, evaluate, survey, evidence, proven, verified, don't guess

## Procedure: Research Cycle
1. Frame the decision as one sharp sentence before touching code
2. Extensive search: web → GitHub (repos, code, issues, PRs) → docs → papers → reference implementations → package source
3. Per source, assign gain (coarse 0-3): 0=noise, 1=minor clarification, 2=materially deepens/narrows, 3=reverses prior decision
4. If 2 consecutive sources ≤1: adjust — switch method (web↔GitHub), source type (docs↔papers↔impl↔source), or scope (broad↔exact); then continue
5. Close only after an adjusted cycle yields 0 gain
6. Emit structured verdict with evidence tier A/B/C (reject D)

## Verdict Format
```
CYCLE:      <decision in one line>
METHODS:    web · github · docs · papers · impl · source
DEPTH:      <sources read, gain scores>
CLOSE:      gain held → adjusted (xN) → barren after adjustment
VERDICT:    adopt | adapt | reject | mixed
EVIDENCE:   A | B | C
REASON:     one sentence
SOURCE:     <url> or [UNVERIFIED] (only if tier C)
```

## Procedure: Lesson Deposit + Propagation
1. At cycle close, generate lesson: `## Lesson (YYYY-MM-DD)` + 1-5 lines + `SEVERITY: low|medium|high|critical` + `AFFECTS: lesson-learning,<other>`
2. Deduplicate (semantic hash ≥90%)
3. Propagate transitively to `lesson-learning` (via governs) + reverse-indexed skills
4. Each copy tagged `PROPAGATED_FROM: research-first`
5. Compress each affected skill independently

## Token-Budget Compression
- Budget: 800 lines
- Trigger: on deposit exceeding budget
- Removal: duplicates → superseded → low/medium + >30d
- Never remove: high, critical, `permanent`
- No compression logs

## Values-Based Tiebreak
When two researched approaches both clear the bar, prefer simpler, more maintainable, closer to ecosystem norms — by judgment, never fashion.

## Failure Mode Catalog
- No verdict for a line of code → bug
- Guessing instead of research → bug
- Stopping a productive cycle → judgment failure
- Not adjusting a barren cycle → obligation violation
- Evidence tier D used → reject verdict
- Skill name invalid per opencode regex

## Cross-References
- Governs: lesson-learning (transitive)
- Propagates lessons to: lesson-learning
- Receives propagated lessons from: lesson-learning
- AGENTS.md: Research-first principle, honest data, lean, verify before shipping
- Research backing: CoT (Wei et al. 2022), Self-Consistency (Wang et al. 2022), Reflexion (Shinn et al. 2023), Medprompt (Nori et al. 2023), DSPy (Khattab et al. 2023), Agent Architecture (Wang et al. 2023)

## Validation Gates
- Frontmatter valid (name regex, description length, required fields)
- All 10 sections present, in order
- Verdict parseable, evidence tier ∈ {A,B,C}
- Lessons: dated, 1-5 lines, severity ∈ {low,medium,high,critical}, AFFECTS present
- Token count ≤ 800
- No compression logs