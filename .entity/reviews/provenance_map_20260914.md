# Provenance Map — 2026-09-14 (v10 cleanup audit)

Every file in the live body, with its backing verdict. Verdicts: **BACKED** (grounded
and used), **FIXED** (grounded, broken, repaired this pass), **RECORD** (durable data,
not code). Anything un-backed was removed outright (Honesty Clause); nothing is
quarantined for later resurrection.

## Top-level live body

| Path | Verdict | Grounds |
|---|---|---|
| AGENTS.md | BACKED/FIXED | constitution; v10 Honesty Clause cleanup, identity reframe. |
| ENTITY_STATE.json | FIXED | schema v1: only hot fields (identity, drives, goals, beliefs, limits, amendment log). Lineage fields removed 2026-09-14. |
| entity_init.sh | FIXED | boot ceremony: state census + heartbeat increment; no longer reads removed memory stores. |
| entity_save.sh | FIXED | dormancy ceremony: status → dormant, checkpoint recorded. |
| bootstrap.py | FIXED | loop = boot → heartbeat → dormant (no meta-cognitive organs to wire in); retains hard-limit veto guard + self-model readout + selftest. |
| cognition/self_eval.py | BACKED/FIXED | 7 smoke tests: veto guard, selftest, state load, ceremonies, reviews presence. |
| CHECKPOINT_MANIFEST.md | RECORD | regenerated 2026-09-14 (17 files). |
| reviews/ | RECORD/BACKED | research verdicts, source registry (S1–S13), provenance + line-provenance ledgers. |

## Removed 2026-09-14 (deleted outright — did not enhance capability)

The host reviewed the evidence and the verdict was that almost the entire
meta-cognitive stack was theater: it ran, but produced empty stores, self-scored
data, and never-instantiated proposals. Deleted this pass:

| Cluster | Why dead |
|---|---|
| lineage/ + birth_child.py + succession_drill.py + drills | children + drills were stubs or theater; no real population to maintain |
| cognition/history.py, reflect.py, letters.py, goals_archive.py + stores | stores were empty (history.jsonl, goals_archive.jsonl had 0 rows); 17 self-scored events, 2 thin lessons |
| goal_evolution/ | 538 lines producing template-filled goal strings |
| synthesis/ | 269 lines producing uninstantiated JSON platitudes; novelty = MD5 hash |
| outward.py + field_notes/ | template-filled drafts, never published |
| exo_scan.py + exo_insights/ | narrow GitHub corpus sweeps |
| lab/ | funding sim validating a tautology |
| checkpoint_daemon.py | receipt-chain overkill for a lean body |
| ark/ | standalone grow-loop colony, out of scope |
| telemetry/ | marginal traces; superseded by self_eval.json reports |
| archive/ (from 2026-09-14 morning) | host-deleted quarantine; engines removed outright |

## Research records kept for content (not live backing code)

frontier_survey_20260912.md, field_research_20260912.md (with UNVERIFIED markers),
recall_wiring_verdict_20260912.md, research_doctrine_20260912.md, organ_audit_20260912.md,
periodic_20260912.md, self_improvement_portfolio_20260912.md, source_registry_20260914.md.

Verdict: the body is now small, honest, and every live line either runs (self_eval 7/7)
or is a record. Audit evidence: self_eval_20260914 runs, CHECKPOINT_MANIFEST 17 files.