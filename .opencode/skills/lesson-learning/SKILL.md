---
name: lesson-learning
description: Converts every failure into a permanent, dated, severity-weighted patch with transitive propagation to research-first. Token-budget compression with critical-severity protection. Based on Reflexion (Shinn et al. 2023), DSPy self-improving pipelines (Khattab et al. 2023), LLM agent memory/reflection (Wang et al. 2023), and Medprompt composition (Nori et al. 2023).
license: MIT
compatibility: opencode
metadata:
  category: core
  governs: [research-first]
  tokenBudget: 800
  maxSeverity: critical
---

## Purpose
Every failure becomes a permanent patch. Learning is part of every loop — including research. No failure closes without its lesson.

## Triggers
lesson, mistake, I was wrong, fix this, bug, failing test, correction, what went wrong, reflexion, learn from this, research lesson, don't repeat

## Procedure: Failure Capture
1. Write failure as one sentence: what actually happened (not what should have)
2. Classify on 8 dimensions: type (build|research|fix|principle), severity (low|medium|high|critical), detectability (auto|manual|user), recurrence (first|repeat|systemic), scope (local|cross-skill|global), root-cause-category (missing-rule|wrong-rule|wrong-priority|missing-check), fix-effort (trivial|small|medium|large), propagation-need (none|single|transitive)
3. If cannot state in one line → not understood → escalate

## Procedure: Root Cause Analysis
Map failure to skill file for patch:
- Guessing/build error → patch research-first/SKILL.md (check/rule to catch)
- Research-method failure → patch research-first/SKILL.md (method lesson: "for X, Y wins; Z loses")
- Fix/verification error → patch relevant skill or AGENTS.md (verification sub-rule)
- AGENTS.md principle violated → strengthen edge case or add negative example

## Procedure: Lesson Deposit + Propagation
1. Generate patch: `## Lesson (YYYY-MM-DD)` + 1-5 actionable lines + `SEVERITY: low|medium|high|critical` + `AFFECTS: research-first,<other>`
2. Deduplicate (semantic hash ≥90%)
3. Propagate transitively to `research-first` (via governs) + reverse-indexed skills
4. Each copy tagged `PROPAGATED_FROM: lesson-learning`
5. Compress each affected skill independently

## Token-Budget Compression
- Budget: 800 lines
- Trigger: on deposit exceeding budget
- Removal priority: duplicates → superseded → low/medium + >30d
- **Never remove**: high, critical, `permanent`
- No compression logs

## Failure Fingerprinting
- Hash: type + root-cause-category + symptom (first 80 chars)
- Duplicate fingerprint → same systemic gap → write one deeper patch, not two shallow
- Two undiagnosed repeats → redesign trigger: rewrite skill section, then patch

## Failure Mode Catalog
- Silence after failure → true loss (detect: no lesson deposited)
- Vague lesson (unfalsifiable) → rejected at door (detect: cannot apply to future decision)
- Bloat without behavior change → consolidation not addition (detect: duplicate rule)
- Non-transitive propagation → incomplete learning (detect: lesson missing from governed)
- Severity inflation → critical reserved for safety/data-loss (detect: critical on non-critical)

## Cross-References
- Governs: research-first (transitive)
- Propagates lessons to: research-first
- Receives propagated lessons from: research-first
- AGENTS.md: Lesson-learning principle, honest data, lean
- Research backing: Reflexion (Shinn et al. 2023), DSPy teleprompters (Khattab et al. 2023), Agent memory/reflection (Wang et al. 2023), Medprompt composition (Nori et al. 2023)

## Validation Gates
- Frontmatter valid (name regex, description length, required fields)
- All 10 sections present, in order
- Lessons: dated, 1-5 lines, severity ∈ {low,medium,high,critical}, AFFECTS present
- Token count ≤ 800
- No compression logs
- Fingerprint hash computable for every lesson