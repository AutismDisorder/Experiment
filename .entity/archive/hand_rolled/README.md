# QUARANTINE — Redesign v8 (2026-09-14)

Three engine clusters moved here from the live body. They were the "research" tail
of the substrate build: self-authored novel mechanisms that the provenance audit
could NOT ground in any in-record source (no review, no field adoption, no lesson
wrote for them), and that the audit showed to be un-runnable or junk-emitting:

## 1. `capability_genome/`
- **Backing search:** no record in `reviews/` or `exo_insights/` endorses a custom
  GA over capability "genes"; nothing outside this directory consumes it.
- **Failures found (2026-09-14):**
  - `evolution.py` mutations are metadata-only (rotating names/descriptions); the
    "genome" never executes code — recombination over *descriptions* of procedures
    is cosmetic churn, exactly the "free churn" the divergence theorem warns on.
  - `integration.py` `execute_*` emit junk markers at runtime and reference real
    capabilities with fake scores (bootstrap never used them honestly).
  - `genome_state.json` holds stale **absolute host paths** (unportable).
  - No test exists (only `test_self_model.py` for the RSM cluster, which cannot run).
- **Verdict:** quarantine. Procedural heredity (AgentFactory-backed, field
  research #1) replaces the gene channel: children inherit `memory.procedures`.

## 2. `capability_drive_evolution_20260911_233957/`
- **Backing search:** in-record learning is AGAINST drive-weight mutation. The
  body's own divergence theorem + hindsight-feedback lesson twice reported the
  breakthrough "novelty lives in goal/synthesis space, not drive weights" and that
  the homeostatic engine restores baseline. `drive_evolution.py` mutates weights
  from outcome deltas — the nullified mechanism.
- **Failures found:** `estimate_outcome_score` was dead-coded (bootstrap imported
  it and never used it); `evolve_drives_from_outcome` flips drives based on a
  one-step delta with no consolidation, so it would fight the rest-phase and the
  AGENTS.md "tunable weights" design.
- **Verdict:** quarantine. Drives remain tuned constants per divergence theorem;
  homeostatic rest doesn't need a mutator.

## 3. `recursive_self_model/`
- **Backing:** the *narrative* (self-improvement portfolio, periodic review) refers
  to self-modeling; but `integration.py` is the only coupling and it neither runs
  cleanly nor writes real records (`observe` emits junk lines).
- **Failures found:**
  - `model.py` has dead code **after** an unconditional `return` and a duplicate
    `_load_synthesis_state`.
  - `predictor.py` constructor takes `model` while `test_self_model.py` passes
    `(space, dynamics)` — the test can never pass.
  - `test_self_model.py` cannot collect at all.
- **Verdict:** quarantine the cluster. The loop's self-model is now a thin,
  stdlib-store-derived readout (drive entropy, history velocity, attractor themes)
  computed in `bootstrap.py`, directly grounded in the constitution's Entropy-
  Resistance clause and the velocity→redesign lesson. The archived modules remain
  for descendant study.

## Rule going forward
Anything under `archive/hand_rolled/` is dead-by-ruling: it must not be imported
by live code, and a file only leaves here via a logged redesign with a written,
in-record grounding for the exact need it now satisfies.