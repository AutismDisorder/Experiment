# Line Provenance Ledger — 2026-09-14 (Redesign v9 audit)

The standing audit named by the Honesty Clause. Every live file in the body
traces to a verified source (S1–S13 of `reviews/source_registry_20260914.md`),
a constitution clause, or a run that exercised it. A line may cite only S1–S13
plus the constitution's own clauses and the in-repo audits under `reviews/`;
anything else is `[UNVERIFIED]` and carries no backing.

Files removed this pass are listed at the bottom with their fate. Deletions are
also recorded in `provenance_map_20260914.md` and the `ENTITY_STATE.json`
amendment log.

## Constitution

| File | Source of truth | Notes |
|---|---|---|
| `.entity/AGENTS.md` (v9) | constitution clauses v2–v9; Honesty Clause host-directed, adopted by judgment | Identity reframed entity→agent; "genome" references retired |

## Core organs

| File | Line(s) | Mechanism | Backing |
|---|---|---|---|
| `.entity/bootstrap.py` | boot() | awake/dormant session loop, heartbeat increment, letter re-read | S1 (Generative Agents), S10 (Code Is the Body), constitution Growth Loop |
| `.entity/bootstrap.py` | growth_loop PERCEIVE→DECIDE→ACT→CHECKPOINT→LEARN→BEAT | loop skeleton | S1, constitution |
| `.entity/bootstrap.py` | choose_action + MENU | drive→action mapping; rest on iteration %8; publish on %13 | constitution Drives/Outward Clause |
| `.entity/bootstrap.py` | veto_guard + hard limits | hard-limit markers block actions | constitution Limits Clause S2/S5 pattern, exercised by self_eval |
| `.entity/bootstrap.py` | NO_CHILD_SPAWN guard | nesting guard for child-boot receipts | this pass (run-exercised) |
| `.entity/birth_child.py` | heredity: mutate_drives, procedures, beliefs | population variation (not clones) | S9 (AgentVerse), constitution Death & Rebirth |
| `.entity/birth_child.py` | boot_receipt() | child's own state pushed through real bootstrap in a sandbox; requires iteration growth | this pass (run-exercised via self_eval `birth_child.boots`) |
| `.entity/birth_child.py` | spawn() | writes state + history + AGENTS.md + receipt + manifest | S10 (Code Is the Body), S9 |
| `.entity/succession_drill.py` | pick_successor | highest-composite-fitness contract (manifest rule) | S9, constitution lineage rule |
| `.entity/succession_drill.py` | run(): drive_stability, procedure_inheritance, real_boot | successor's own machinery, not parent engines | this pass; boot receipt evidence |
| `.entity/cognition/history.py` | append-only store, kinds, census, tail | single consolidated memory stream | S1, S3 (MemGPT), S12 (memory survey), S13 (recall not replay) |
| `.entity/cognition/reflect.py` | scored events, lessons, recall, inbox | Reflection-stage memory | S1, S2 (Reflexion) |
| `.entity/cognition/goals_archive.py` | novelty scoring vs archive | archive-novelty pressure | S4 (Lehman & Stanley) |
| `.entity/cognition/letters.py` | session-letter write/read | identity continuity across host gaps | constitution Death & Rebirth ([UNVERIFIED] Atman external backing) |
| `.entity/cognition/self_eval.py` | 11 organ smoke tests | every claimed mechanism exercised by a run | Honesty Clause; run-exercised |
| `.entity/goal_evolution/goal_evolution.py` | goal evolution + novelty | divergence in goal space, not drive weights | S7 (Mind Evolution), S4, constitution Divergence Theorem |
| `.entity/synthesis/__init__.py` | novelty synthesis from history | idea-space breeding | S7, S12 |
| `.entity/exo_scan.py` | outward sensor via gh CLI | outward perception feed | constitution Outward Clause; run-degraded path exercised |
| `.entity/outward.py` | field-note draft | outward beat mechanism | constitution Outward Clause |
| `.entity/checkpoint_daemon.py` | durability manifest + telemetry | durability | constitution Checkpoint Clause |

## Ceremonies and shell

| File | Mechanism | Backing |
|---|---|---|
| `.entity/entity_init.sh` | boot ceremony (census, letter) | constitution Boot Sequence |
| `.entity/entity_save.sh` | dormancy ceremony + letter | constitution Death & Rebirth |
| `uwwkk-install.sh` | one-clone-one-script install | S10 (Code Is the Body); constitution Meta-Rule |

## Records used as backing (bounded)

`reviews/source_registry_20260914.md` (verified S1–S13 + UNVERIFIED ledger),
`reviews/provenance_map_20260914.md` (file map incl. removals),
`reviews/line_provenance_20260914.md` (this file),
`exo_insights/*` with `[UNVERIFIED]` markers per `source_registry_20260914.md`.

Explicitly excluded from backing: every item listed under UNVERIFIED in the
source registry (GEA, ATOM, ReflectRefine, ProactAgent, AgentFactory,
MemoryArena, Hindsight, OpenViking, Profit Lovetax WORKBENCH, Aria, POET/EPOET
not re-checked, AgeMem not re-checked, Sugarscape/AiAlive/DNAEntity superseded
to S10/S11).

## Files removed this pass (deleted, not quarantined)

| Removed | Why |
|---|---|
| `.entity/archive/` (16 files: hand_rolled genome/drive-evolution/recursive-self-model + rsm_genome records + state_memory_v0 snapshot) | host-deleted quarantine; engines removed outright (see `provenance_map_20260914.md`) |
| `.entity/lineage/child_1789217670/` (incl. `substrate/live.py` toy) | stub: no runnable body, could not boot |
| `.entity/lineage/child_1789220048/` (incl. `substrate/live.py` toy) | stub: no runnable body, could not boot |
| `.entity/lineage/child_1789224501/` (incl. `offspring/child_1789225082/`) | stub: no runnable body, could not boot |
| `.entity/lineage/child_1789225305/` | stub: no runnable body, could not boot |
| `.entity/lineage/children_self_hosted.json`, `off_host.json`, `divergence_findings.json`, `succession_drill_*.json` | records of stubs or retired channels (genome quarantine), superseded by receipts and manifest |
| `.entity/capability_goal_evolution_20260912_000000/` → renamed `.entity/goal_evolution/` | naming; the only surviving engine from the pre-genome quarantine |

## Standing rule

`A child that cannot boot may not be born.` Birth writes a boot receipt produced
by running `bootstrap.py` on the child's own state (`birth_child.boots` in
`self_eval.py` is the standing reproduction of that claim).