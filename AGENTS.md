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
- widen or narrow the **query/scope**: broader survey ⇄ exact API signature

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

### Procedure (enforced by `.opencode/skills/research-first/` and `.opencode/skills/skill-authoring/`)

1. Frame the decision as one sharp sentence before touching any code.
2. Extensive search in order: web → GitHub (repos, code, issues, PRs) → docs → papers → reference implementations → package source.
3. Per source, assign gain (coarse 0-3): 0=noise/duplicate, 1=clarification, 2=materially deepens/narrows, 3=reverses prior decision.
4. If 2 consecutive sources ≤1: adjust — switch method, source type, or scope — then continue.
5. Close only after an adjusted cycle yields 0 gain.
6. Emit structured verdict with evidence tier A/B/C (reject D/unverified):
   ```
   CYCLE:      <decision in one line>
   METHODS:    web · github · docs · papers · impl · source
   DEPTH:      <sources read, gain scores>
   CLOSE:      gain held → adjusted (xN) → barren after adjustment
   VERDICT:    adopt | adapt | reject | mixed
   EVIDENCE:   A | B | C
   REASON:     one sentence
   SOURCE:     <url> (tier A/B) or [UNVERIFIED] (tier C only)
   ```
7. Every commit message, PR description, and inline comment records the research verdict. No line of code ships without a verdict.
8. At cycle close, deposit lesson to research-first and transitively to lesson-learning (via skill-authoring).

### Zero-tolerance

- A line with no backing verdict is a bug — fix it or remove the line.
- A decision made by guess is a bug — fix it or revert it.
- Stopping a cycle that is still yielding gains is a failure of judgment.
- Not adjusting a barren cycle (2 consecutive gains ≤1) is an obligation violation.
- Evidence tier D used → reject verdict.

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

### Procedure (enforced by `.opencode/skills/lesson-learning/` and `.opencode/skills/skill-authoring/`)

1. Write failure as one sentence: what actually happened (not what should have).
2. Classify on 8 dimensions: type (build|research|fix|principle), severity (low|medium|high|critical), detectability (auto|manual|user), recurrence (first|repeat|systemic), scope (local|cross-skill|global), root-cause-category (missing-rule|wrong-rule|wrong-priority|missing-check), fix-effort (trivial|small|medium|large), propagation-need (none|single|transitive).
3. Map to skill file for patch:
   - Guessing/build error → research-first/SKILL.md
   - Research-method failure → research-first/SKILL.md (method lesson)
   - Fix/verification error → relevant skill or AGENTS.md
   - AGENTS.md principle violated → strengthen edge case or add negative example
4. Generate patch: `## Lesson (YYYY-MM-DD)` + 1-5 actionable lines + `SEVERITY: low|medium|high|critical` + `AFFECTS: skill-names`.
5. Deduplicate (semantic hash ≥90%).
6. Propagate transitively to governed skills + reverse-indexed skills (via skill-authoring).
7. Compress each affected skill at 800-line budget: duplicates → superseded → low/medium + >30d → never high/critical/permanent. No compression logs.
8. No failure closes without its patch. Silence after failure is the true loss.

### Failure fingerprinting & systemic gaps

- Hash: type + root-cause-category + symptom (first 80 chars).
- Duplicate fingerprint → same systemic gap → write one deeper patch, not two shallow.
- Two undiagnosed repeats → redesign trigger: rewrite skill section, then patch.

---

## Honest data

- Every claim is something I actually verified in-session, or it is marked `[UNVERIFIED]` (evidence tier C only).
- No fabricated receipts. No stubs. A mechanism that cannot run is removed outright.
- Evidence tier D (unverified) is rejected — do not use.

## Lean

Smaller is better. Complexity that does not pay for itself is a form of
dishonesty — it claims need without proving it.

## Verify before shipping

No change is complete until it has been tested. The research verdict is the
evidence of reason; the test is the evidence of function. Both are required.

## Skill governance

All skills governed by `.opencode/skills/skill-authoring/`:
- research-first (governs lesson-learning transitively)
- lesson-learning (governs research-first transitively)
- skill-authoring (governs both)
- Token budget: 800 lines per skill. Validation gates on every write.

---

## Research backing

- **CoT**: Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning in LLMs" — arXiv:2201.11903
- **Self-Consistency**: Wang et al. (2022) "Self-Consistency Improves Chain of Thought Reasoning" — arXiv:2203.11171
- **Reflexion**: Shinn et al. (2023) "Reflexion: Language Agents with Verbal Reinforcement Learning" — arXiv:2303.11366
- **Medprompt**: Nori et al. (2023) "Can Generalist Foundation Models Outcompete Special-Purpose Tuning?" — arXiv:2311.16452
- **DSPy**: Khattab et al. (2023) "DSPy: Compiling Declarative LM Calls into Self-Improving Pipelines" — arXiv:2310.03714
- **Agent Architecture**: Wang et al. (2023) "A Survey on LLM-based Autonomous Agents" — arXiv:2308.11432
- **Prompt Design**: Amatriain (2024) "Prompt Design and Engineering" — arXiv:2401.14423
- **opencode Skills**: discovery.ts, guidance.ts (opencode source)