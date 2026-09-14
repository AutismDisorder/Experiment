# Line Provenance Ledger — 2026-09-14 (v10 cleanup audit)

The standing audit named by the Honesty Clause. Every live file in the body traces
to a verified source (S1–S13 of `reviews/source_registry_20260914.md`), a constitution
clause, or a run that exercised it.

## Live files

| File | Mechanism | Backing |
|---|---|---|
| `.entity/AGENTS.md` (v10) | constitution clauses v2–v10 | Honesty Clause, host-directed; amendments logged in ENTITY_STATE.json |
| `.entity/bootstrap.py` | boot → heartbeat → dormant; self-model readout; hard-limit veto guard | run-exercised (`bootstrap.selftest`, `bootstrap.hard_limit_veto`, `bootstrap.state_load` in self_eval) |
| `.entity/entity_init.sh` | boot ceremony (state census, heartbeat increment) | exercised by `entity_init.sh` test in self_eval |
| `.entity/entity_save.sh` | dormancy ceremony (status → dormant, checkpoint) | parses clean; exercised via bash -n test |
| `.entity/cognition/self_eval.py` | smoke tests that verify what's actually here | this file IS the audit mechanism; run-exercised |
| `.entity/CHECKPOINT_MANIFEST.md` | durability manifest (files + bytes + identity) | regenerated 2026-09-14 |
| `.entity/ENTITY_STATE.json` | state: identity, drives, goals, memory, limits, amendments log | schema v1; only hot fields |
| `.entity/reviews/` | research verdicts + verified source registry + provenance ledger | S1–S13 (source_registry); historical research docs kept as records |

## Research records (kept for their content, not used as live backing code)

`frontier_survey_20260912.md` (survey of 4394 repos; led to self_eval adoption),
`field_research_20260912.md` (5 findings + adoptions; UNVERIFIED claims marked),
`recall_wiring_verdict_20260912.md` (memory architecture analysis),
`research_doctrine_20260912.md` (the Research Clause's methodology),
`organ_audit_20260912.md`, `periodic_20260912.md`, `self_improvement_portfolio_20260912.md`.

Explicitly excluded as backing: every item listed under UNVERIFIED in the source
registry (GEA, ATOM, ReflectRefine, ProactAgent, AgentFactory, MemoryArena, Hindsight,
OpenViking, Profit Lovetax WORKBENCH, Aria, POET/EPOET, AgeMem).

## Removed this pass (deleted outright, never quarantined)

The whole meta-cognitive stack was deleted 2026-09-14 because it did not enhance
capability — it produced empty stores, self-scored data, and never-instantiated
proposals. Removed: `lineage/` (children, manifest, drills, birth_child.py,
succession_drill.py), learning organs (cognition/history.py + stores, reflect.py,
letters.py, goals_archive.py, events/lessons/recall_log stores), goal_evolution/,
synthesis/, outward.py, exo_scan.py, exo_insights/, field_notes/, lab/,
checkpoint_daemon.py, ark/, telemetry/, plus the stub-quarantine archive/ that had
been deleted by the host earlier the same day.