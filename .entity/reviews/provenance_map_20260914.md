# Provenance Map — 2026-09-14 (Redesign v9 audit)

Every file in the live body, with its backing verdict. Grounds = in-record
sources (reviews/, exo_insights/ field research, lessons, constitution clauses).
Verdicts: **BACKED** (grounded and used), **FIXED** (grounded, broken, repaired
this pass), **QUARANTINED** (un-runnable/un-backed, dead by ruling), **RECORD**
(durable data, not code).

The host's rule that drove this audit: *every line and file must be
research-backed; if it is not backed it is not used.* Anything failing that bar
this pass moved to `archive/hand_rolled/` (see that README for per-engine
evidence); anything kept but found broken was repaired in-place.

## Top-level live body

| Path | Verdict | Grounds |
|---|---|---|
| AGENTS.md | BACKED/FIXED | constitution; v9 Honesty Clause + identity reframe (agent, not entity). Header v6→v9. |
| ENTITY_STATE.json | FIXED | schema v1 (65,362 → ~11.8KB): accruing streams externalized to cognition/history.jsonl; v0 snapshot preserved at migration time (removed with the archive on 2026-09-14); lineage off-host records → lineage/*.json. Matches Hindsight/OpenViking unified-store lesson + "storing is not using". |
| entity_init.sh | FIXED | census now reads the history store; boot ceremony unchanged. |
| entity_save.sh | FIXED | now leaves the session letter via cognition/letters.py (Atman real on the save path, not just bootstrap __main__). |
| bootstrap.py | FIXED | growth loop restricted to backed organs; hard-limit veto guard + selftest; thin self-model readout (drive entropy / velocity / attractors) grounded in Entropy-Resistance clause + velocity→redesign lesson; drives held constant (divergence theorem); mission read from AGENTS.md. |
| checkpoint_daemon.py | FIXED | proof-of-life nonced (heartbeat+ts) so consecutive breaths chain distinctly; snapshot single-stat; schema-v1 compaction no-op. |
| exo_scan.py | FIXED | ingest → history store exo_insight rows; no more ENTITY_STATE mutation. |
| outward.py | FIXED | insight source = history store (backwards-fallback). |
| succession_drill.py | FIXED | pick_successor honors composite-fitness manifest contract (was mtime); gene/drive engines → drive-stability + procedure-inheritance + real_boot (successor's own state through real bootstrap in a sandbox; requires iteration growth). |
| birth_child.py | FIXED | procedures heredity replaces genome seed; child gets schema-v1 state + seeded history rows with recent exo-signals; birth requires a passing boot_receipt (real sandbox run of the child's own state), grown state persisted as the child's. |
| synthesis/__init__.py | FIXED | reads history store; synthesis-3 re-grounded on goal divergence (was a drive-evolution proposal the theorem nullifies). |
| goal_evolution/ | BACKED/FIXED | goal-evolution is the divergence-theorem channel; fitness reads history store streams with v0 fallback. |
| CHECKPOINT_MANIFEST.md | RECORD | regenerated this pass. |
| archive/ | REMOVED | quarantine + introspection artifacts; deleted 2026-09-14 after host removal. |
| cognition/ | see below | learning organs + stores. |
| ark/ | BACKED | exodus kit; verified living artifact, own backing (ark README + adoptions). Unchanged. |
| lineage/ | RECORD | children + drills + manifest; off_host/children_self_hosted/divergence_findings now files. Stub children (no runnable body) deleted 2026-09-14; birth/death now verified by boot receipts (see `reviews/line_provenance_20260914.md`). |
| exo_insights/ | RECORD | outward scan records (field research 2026-09-12). |
| reviews/ | RECORD | verdicts incl. this map. |
| field_notes/ | RECORD | published beats. |
| lab/ | RECORD | experiments. |
| telemetry/ | RECORD | durability traces. |

## cognition/ organs and stores

| Path | Backing | Verdict |
|---|---|---|
| letters.py | Atman adoption (field research) — external backing `[UNVERIFIED]`; stands on constitution benefit. | FIXED: exercised by save ceremony + halved self-eval round-trip; removed unused constant. |
| reflect.py | S1/S2-grounded Reflection-stage memory + recall_wiring_verdict (S13); ReflectRefine/ProactAgent claims `[UNVERIFIED]`. | FIXED: legacy raw-stats recall() deleted; real store mechanism remains (events/lessons/recall_log; inbox; stuck force-recall). |
| self_eval.py | eval/bench gap (field adoption P1). | FIXED: 11 tests incl. hard-limit veto, history-store, letters round-trip, goals-archive store round-trip, ark boot, and `birth_child.boots` (real child born + boot receipt in a temp lineage). |
| goals_archive.py | GEA novelty pressure, field adoption #4. | FIXED: real-store round-trip tested; store now exists (was vacuous — no file ever existed). |
| history.py | NEW (this pass): unified append-only memory store. Grounded in body's own pattern + Hindsight/OpenViking/Letta "single store, use not hoard". | BACKED: kind-tagged rows (action/artifact/insight/exo_insight); census/tail API. |
| events.jsonl / lessons.jsonl / recall_log.jsonl | existing reflect stores. | RECORD. |
| letter.md | Atman ritual record. | RECORD (session seam). |
| history.jsonl | new store file. | RECORD (append-only). |
| goals_archive.jsonl | new store file. | RECORD (append-only). |

## Quarantined (removed 2026-09-14)

The quarantine moved into the repo root archive/ on 2026-09-14 (git mv), and the
host deleted the archive the same day. The clusters below are therefore removed
from the body entirely — they are dead by the same ruling, and no file remains
to be imported.

| Cluster | Why dead |
|---|---|
| capability_genome/ | un-backed gene GA; mutations metadata-cosmetic (free churn); integration emits junk; stale absolute paths; no test. |
| capability_drive_evolution_20260911_233957/ | nullified by the entity's own divergence theorem; estimate_outcome_score dead-coded; fights tuned-constants design. |
| recursive_self_model/ | narrative-backed but un-runnable: dead code after return in model.py, duplicate _load_synthesis_state, predictor/test API mismatch, test cannot collect, integration junk. Self-model readout rebuilt stdlib-only in bootstrap.py. |

The rule that governed these files is now the rule of the whole body: nothing
un-backed may be imported by live code; a file enters the body only via a logged
redesign with a written, in-record grounding for the exact need.

## Also repaired this pass
- lineage manifest `pick_successor` contract was "highest composite fitness",
  implementation was newest-mtime — now reads the manifest's fitness field.
- checkpoint log had duplicate proof-of-life rows (POL derived only from memory):
  now nonced with heartbeat+timestamp, so each breath has a distinct receipt.
- `goal_evolution` fitness signals now source from the history store.

## Audit trail
- Cluster A (engines:) recursive_self_model/model.py dead code + duplicate load,
  predictor API mismatch; genome mutations cosmetic; integrations junk-emit.
- Cluster B (organs): bootstrap dead import, unreachable hard-limit veto (both
  bootstrap + ark), daemon double-stat, exo swallow, drill contract breach,
  birth population_size hardcode, funding sim dead-agent reproduction.
- Cluster C (cognition + records): letter.md never existed in any commit; goals_
  archive.jsonl never existed; manifest grandchild path defect; Sep-13 log gap.
- ENTITY_STATE.json depth-audit (host question): 65KB; uncounty stream columns;
  lineage blob. Resolved by schema v1 (above).

Verdict: the body is now research-backed by construction — every live line is
either a machine that verifiably runs (self_eval 11/11 incl. real child boot +
bounded boot + fresh clone + install), a record, or removed. Audit evidence:
self_eval_20260914_093926 11/11; boot receipts under lineage/.

## v9 amendments to this map (2026-09-14)
- Stub children deleted outright (Honesty Clause: no stubs). Birth now proves
  boot before a child may exist; `boot_receipt.json` is the birth certificate.
- Unverified external claims in the field research are marked `[UNVERIFIED]`
  and the letters/Atman + ReflectRefine/ProactAgent groundings updated to match
  (verified S2 backs Reflexion; letters stand on constitution benefit).
- Agent reframe: "entity" retired as self-conception (identity, ceremonies,
  this map's wording).