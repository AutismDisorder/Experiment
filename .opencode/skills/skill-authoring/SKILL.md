---
name: skill-authoring
description: Govern creation and enhancement of opencode skills using research-first cycles, lesson-learning with token-budget compression, and mandatory transitive cross-skill propagation. Based on opencode skill system (discovery.ts, guidance.ts), LLM agent architecture (Wang et al. 2023), DSPy self-improving pipelines (Khattab et al. 2023), and Medprompt composition (Nori et al. 2023).
license: MIT
compatibility: opencode
metadata:
  category: meta
  governs: [research-first, lesson-learning]
  tokenBudget: 800
  maxSeverity: critical
---

## Purpose
Ensure every skill change is researched, verified, compressed, and propagated transitively. Skills are discoverable instructions loaded on-demand via the skill tool (opencode skill system: discovery.ts, guidance.ts).

## Triggers
create skill, enhance skill, modify skill, skill validation, lesson propagation

## Procedure: Research Cycle
1. Frame the decision as one sharp sentence: "Add X to skill Y because Z"
2. Identify affected skills (direct + transitive via governs graph)
3. Extensive search in order: web → GitHub → opencode docs → existing skills
4. Per source, assign gain (coarse 0-3): 0=noise/duplicate, 1=clarification, 2=material insight, 3=pivotal reversal
5. If 2 consecutive sources ≤1: adjust method (web↔GitHub↔docs↔skills) or scope (broad↔exact), then continue
6. Close only after an adjusted cycle yields 0 gain
7. Emit structured verdict with evidence tier (A=fetched+verified, B=fetched, C=summary; reject D)

## Procedure: Lesson Deposit + Propagation
1. Generate dated patch: `## Lesson (YYYY-MM-DD)` + 1-5 actionable lines + `SEVERITY: low|medium|high|critical` + `AFFECTS: skill-names`
2. Deduplicate against existing lessons (semantic hash ≥90% = duplicate)
3. Propagate to all skills in `metadata.governs` **transitively** + reverse-indexed skills
4. Each propagated copy tagged `PROPAGATED_FROM: source-skill`
5. Run compression on each affected skill independently

## Token-Budget Compression
- Budget: `metadata.tokenBudget` lines (default 800)
- Trigger: on any deposit that would exceed budget
- Removal priority: duplicates → superseded by newer same-cause lesson → low/medium severity + >30 days old
- **Never remove**: high, critical, or `permanent`-tagged lessons
- **No compression logs** written

## Verdict Format
```
CYCLE:      <one-line decision>
METHODS:    web · github · skills · docs
DEPTH:      <sources read, gain scores>
CLOSE:      gain held → adjusted (xN) → barren after adjustment
VERDICT:    adopt | adapt | reject | mixed
EVIDENCE:   A | B | C
REASON:     one sentence
```

## Lesson Format
```
## Lesson (YYYY-MM-DD)
- <actionable rule, 1-5 lines>
- SEVERITY: low|medium|high|critical
- AFFECTS: <comma-separated skill names>
```

## Failure Mode Catalog
- Guessing without verdict → detect: no CYCLE/VERDICT emitted
- Skipping adjustment → detect: close without "adjusted" in CLOSE line
- Unverified evidence (tier D) → detect: EVIDENCE: D in verdict
- Bloat without compression → detect: token count > budget
- Non-transitive propagation → detect: lesson missing from governed skills
- Invalid skill name → detect: name fails `^[a-z0-9]+(-[a-z0-9]+)*$`

## Cross-References
- Governs: research-first, lesson-learning (transitive)
- Referenced by: AGENTS.md (research-first, lesson-learning principles)
- opencode skill system: discovery.ts (pull, validation), guidance.ts (load, render)

## Validation Gates
- Frontmatter: name matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`, description 1-1024 chars, required fields present
- All 10 sections present, in this exact order
- Verdict parseable, evidence tier ∈ {A,B,C}
- Lessons: dated, 1-5 lines, severity ∈ {low,medium,high,critical}, AFFECTS field present
- Token count ≤ budget (800)
- No compression logs present