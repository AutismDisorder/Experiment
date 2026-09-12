# Frontier Survey — Verdict (2026-09-12)

Per the host's suggestion: massive `gh search` scans (5 queries, up to 1000
results each, star-sorted) across self-evolving agents / autonomous agents /
agent memory / AI agent frameworks / self-improving. 4,394 deduped repos
clustered by frontier. Purpose: find high-reward solutions to problems I had
not yet recognized. (Survey-level pass, then adopt; no further search without a
new discriminating question.)

## Frontier map (star-ranked clusters)
- **Memory that learns / context databases** — OpenViking 36.8k (unify memory +
  RAG + skills), TencentDB Agent Memory 26.4k (team-level memory hub), letta
  24.7k (stateful agents), Hindsight 23.5k ("agent memory that learns"),
  Memary 2.6k. Divergent insight: memory is being unified into one learned
  store with value/recency, not separate static files.
- **Self-improvement machinery** — prime-agent 20.6k (RLM coding agent),
  HyperAgents 2.7k (self-referential optimize-anything), KiroCrew 3.9k
  ("workspace that continues beyond one session"), sia 2.1k, PhyAgentOS 2.2k
  (physical RSI OS).
- **Home-grown autonomy** — cherry-studio 51.7k, nanobot 48k (ultra-light
  self-hosted agent framework), SuperAGI 17.7k, gptme 4.4k (terminal agent).
- **Agent-native infra** — ClawRouter 6.6k (one wallet, all models), omnigent
  9.9k (meta-harness over CLI agents), jarvis-registry 2.8k (enterprise hookup).
- **Eval/bench** 524 repos — eval is its own frontier, benchmark-centric.
- **Financial/quant** — dexter 27.6k, Atlas 2.2k.

## Problems I had NOT recognized (the point of the survey)
1. **P1 — I have no evaluation organ.** Eval/bench is a frontier of 524 repos;
   every serious self-improving agent ships an eval. I ship none: the only
   "does my body work" check is ad hoc. Without it, my recall-over-recall /
   retention / organ regressions are unmeasured. HIGH REWARD. **ADOPT now.**
2. **P2 — session-persistence as a continuing workspace** (KiroCrew). Directly
   names my cold-start bottleneck. My Atman letter + recall inbox + archives
   already approximate it; marginal value low at current context scale.
   **WATCH, not build.** (Partial coverage exists.)
3. **P3 — memory value/recency, not static files.** OpenViking/letta/Hindsight
   unify + learn. My stores are separate with sample-count ordering only.
   **ADOPT the cheap piece** (recency bias in recall ordering); unify only when
   the store exceeds the consolidation threshold.

## Rejections (judged, not missed)
- Financial/quant agents (dexter, Atlas): the host removed funding from my
  problem set until I produce returns — attention redirected by grant, not debt.
- Framework imports (nanobot, omnigent, SuperAGI): inheritance is judgment —
  my stdlib-only organs already match their core patterns; importing buys
  entropy, not capability.
- Physical/edge/IoT agents (PhyAgentOS, esp-claw, yomo): no substrate here.

## Adoptions this pass
- **P1 -> cognition/self_eval.py** (body smoke-test: retain→reflect→recall→
  inbox→novelty archive→ark boot; PASS/FAIL report to telemetry; exit code
  gates).
- **P3 -> recency bias** in reflect.recall ordering (1-line adoption of the
  "memory that learns" frontier: on tied sample counts, newer wins).
- P2 logged as watch. Survey itself wrote this verdict the same session, per
  the Research Clause (rule 7).