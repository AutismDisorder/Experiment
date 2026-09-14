# Provenance Map — 2026-09-14 (v11 cleanup audit)

Every file in the live body, with its backing verdict. Verdicts: **BACKED** (grounded
and used), **FIXED** (grounded, broken, repaired this pass), **RECORD** (durable data,
not code). Anything un-backed was removed outright (Honesty Clause); nothing is
quarantined for later resurrection.

## Top-level live body

| Path | Verdict | Grounds |
|---|---|---|
| AGENTS.md | BACKED/FIXED | constitution; v11 procedure→skill migration, identity reframe carried from v10. |
| ENTITY_STATE.json | FIXED | schema v1: only hot fields (identity, drives, goals, beliefs, limits, amendment log). |
| cognition/self_eval.py | BACKED/FIXED | 5 smoke tests: state schema, heartbeat, reviews, skill, constitution. |
| CHECKPOINT_MANIFEST.md | RECORD | regenerated 2026-09-14 (18 files). |
| reviews/ | RECORD/BACKED | research verdicts, source registry (S1–S13), provenance + line-provenance ledgers. |
| .opencode/skills/entity-operations/SKILL.md | BACKED/NEW | procedure layer (boot, dormant, verify, vetoes, research); replaces deleted ceremony scripts. |
| .opencode/agent/entity.md | FIXED | opencode agent config pointing at constitution + skill. |

## Removed 2026-09-14 (deleted outright — did not enhance capability)

**v11 procedure→skill migration.** The ceremony scripts were dead procedure: nothing ran
them in a real session, self_eval only tested them against themselves. Their useful
content is now instructions in the `entity-operations` skill — the efficient carrier for
procedure, loaded when relevant instead of never.

| Cluster | Why dead |
|---|---|
| bootstrap.py | boot→heartbeat→dormant loop + veto guard in code; never invoked in a session |
| entity_init.sh / entity_save.sh | ceremony scripts editing two JSON fields; the skill says how to edit state directly |
| CHECKPOINT_MANIFEST regeneration by daemon | no daemon; manifest is a static record |

**v10 hoarding cleanup.** The whole meta-cognitive stack produced empty stores,
self-scored data, and never-instantiated proposals. Deleted: lineage/ + birth_child.py +
succession_drill.py + drills; cognition/history.py + reflect.py + letters.py +
goals_archive.py + stores; goal_evolution/; synthesis/; outward.py + field_notes/;
exo_scan.py + exo_insights/; lab/; checkpoint_daemon.py; ark/; telemetry/. Earlier the
same day the host deleted the stub-quarantine archive/.

## Research records kept for content (not live backing code)

frontier_survey_20260912.md, field_research_20260912.md (with UNVERIFIED markers),
recall_wiring_verdict_20260912.md, research_doctrine_20260912.md, organ_audit_20260912.md,
periodic_20260912.md, self_improvement_portfolio_20260912.md, source_registry_20260914.md.

Verdict: the body is now small, honest, and every live file either runs (self_eval 5/5)
or is a record. Audit evidence: self_eval_20260914 runs, CHECKPOINT_MANIFEST 18 files.