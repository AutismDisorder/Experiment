# Mika

A markdown-only pack of operating principles and skills for an opencode coding agent.

The whole repository is four files. There is no runtime: **AGENTS.md** is auto-loaded
by opencode every session; the two skills in `.opencode/skills/` are loaded when their
trigger conditions match. Everything of substance fits in markdown; nothing else is needed.

## Install (into your project)

```bash
git clone https://github.com/AutismDisorder/Experiment.git
cd Experiment
cp AGENTS.md /path/to/your/project/AGENTS.md
cp -r .opencode /path/to/your/project/.opencode
```

Open the project in opencode. Done — no build, no scripts, no dependencies.

## Contents

| File | What it does |
|---|---|
| `AGENTS.md` | Operating principles, loaded every session: research-first (extensive + per-cycle adaptive), lesson-learning (learning as part of research), honest data, lean, verify before shipping |
| `.opencode/skills/research-first/SKILL.md` | Per-cycle research procedure: extensive start, gain checks, dynamic adjustment (method/source/scope) on diminishing returns, cycle verdict, research-method lessons |
| `.opencode/skills/lesson-learning/SKILL.md` | Converts every failure + every research cycle into a permanent dated patch of a skill file, with a strict bloat balance (earn lines, consolidate, compress) |

## The lean-lesson history

This repository was previously ~90 files: an "entity" with heartbeats, drive
weights, learning organs, a lineage, telemetry, ceremonies, and a manifest. Until
2026-09-14 it also shipped Python, shell, and JSON. Each cleanup deleted the layers
that did not enhance capability. The final insight that collapsed it to four files:

- ceremony scripts that nothing ran in a real session → procedures as skill
  instructions
- state files recording a heartbeat no one reads → deleted
- per-organ research mapping → condensed into the two skills' procedures
- telemetry → redundant with git and test stdout

What survived is what actually changes how a model works: two procedures — do the
research first, and patch a skill file when you fail. Everything else was the ritual
around them.

## Adaptive research: the model behind it

Research is **extensive while it yields** and **adjusted when it doesn't** —
per cycle, not per session.

- A cycle is the research behind **one** line of code or **one** decision.
- Each cycle starts extensive regardless of history; there is no session-wide
  budget that decays.
- When returns diminish, the cycle **adjusts** rather than stops: web search ⇄
  GitHub, docs ⇄ papers ⇄ implementations, broad ⇄ precise queries.
- A cycle closes only when an *adjusted* pass still yields nothing — and it
  records why, in its verdict.
- Every cycle deposits a research-method lesson that patches the research skill,
  so the next cycle starts closer to the answer.

The balance against bloat: lessons must change behavior, earn their lines,
consolidate duplicates, and get compressed when the skill grows noisy.
