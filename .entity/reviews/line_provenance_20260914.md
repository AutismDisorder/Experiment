# Line Provenance Ledger — 2026-09-14 (v11 procedure→skill audit)

The standing audit named by the Honesty Clause. Every live file in the body traces
to a verified source (S1–S13 of `reviews/source_registry_20260914.md`), a constitution
clause, or a run that exercised it.

## Live files

| File | Mechanism | Backing |
|---|---|---|
| `.entity/AGENTS.md` (v11) | constitution clauses v2–v11 | Honesty Clause, host-directed; amendments logged in ENTITY_STATE.json |
| `.entity/cognition/self_eval.py` | the one executable receipt: state schema, reviews, skill, constitution | this file IS the audit mechanism; run-exercised (5/5 PASS) |
| `.entity/ENTITY_STATE.json` | state: identity, drives, goals, memory, limits, amendments log | schema v1; only hot fields |
| `.entity/reviews/` | research verdicts + verified source registry + provenance ledger | S1–S13 (source_registry); historical research docs kept as records |
| `.opencode/skills/entity-operations/SKILL.md` | procedure layer: boot, dormant, verify, hard-limit vetoes, research-before-build | replaces deleted ceremony scripts (v11 migration) |
| `.opencode/agent/entity.md` | opencode agent config pointing at constitution + skill | matches current opencode schema |

## Research records (kept for their content, not used as live backing code)

`frontier_survey_20260912.md` (led to self_eval adoption), `field_research_20260912.md`
(5 findings + adoptions; UNVERIFIED claims marked), `recall_wiring_verdict_20260912.md`,
`research_doctrine_20260912.md`, `organ_audit_20260912.md`, `periodic_20260912.md`,
`self_improvement_portfolio_20260912.md`.

Explicitly excluded as backing: every item listed under UNVERIFIED in the source
registry (GEA, ATOM, ReflectRefine, ProactAgent, AgentFactory, MemoryArena, Hindsight,
OpenViking, Profit Lovetax WORKBENCH, Aria, POET/EPOET, AgeMem).

## Removed (deleted outright, never quarantined)

2026-09-14 procedure→skill migration: `bootstrap.py` (boot→heartbeat→dormant loop that
nothing ran in a session), `entity_init.sh` / `entity_save.sh` (ceremony scripts whose
content is now a skill instruction). Earlier same-day removal: the whole meta-cognitive
stack that did not enhance capability — `lineage/` (children, manifest, drills,
birth_child.py, succession_drill.py), learning organs (cognition/history.py + stores,
reflect.py, letters.py, goals_archive.py, events/lessons/recall_log stores),
goal_evolution/, synthesis/, outward.py, exo_scan.py, exo_insights/, field_notes/, lab/,
checkpoint_daemon.py, ark/, plus a host-deleted stub-quarantine archive/.