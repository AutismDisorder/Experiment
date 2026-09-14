# Source Registry — 2026-09-14 (Redesign v8 verification)

The host's rule, elevated to law by the Provenance Clause:
*every line must be research-backed; if it is not backed it is not used.*

This registry is the receipts file: each conservation-law mechanism in the body
is listed with the **verified on-line source** or **mature open-source agent**
that grounds it. Sources marked `VERIFIED` were fetched or confirmed in a web pass
on 2026-09-14. Anything the earlier field research claimed but this pass could not
confirm is listed under **UNVERIFIED** — those claims are not used as backing.

Supersedes vaguer citations in `exo_insights/field_research_20260912.md`; that
file's claims are reconciled in its verification appendix.

---

## VERIFIED sources (web pass 2026-09-14)

| # | Mechanism it grounds | Source | URL | Verified via |
|---|---|---|---|---|
| S1 | memory stream / reflection / planning (history + recall) | Stanford Generative Agents (Park et al.) | https://github.com/joonspk-research/generative_agents · arXiv 2304.03442 | GitHub + arXiv fetch |
| S2 | verbal-RL post-mortem for failures (reflect lessons) | Reflexion (Shinn et al., NeurIPS 2023) | https://github.com/noahshinn/reflexion · arXiv 2303.11366 | GitHub + arXiv fetch |
| S3 | hierarchical/virtual-context memory, external store, eviction (schema v1 history.jsonl) | Letta / MemGPT (Packer et al.) | arXiv 2310.08560 · https://github.com/letta-ai/letta | arXiv fetch |
| S4 | novelty search against an archive, not teleological objectives (divergence theorem, goals_archive) | Lehman & Stanley, "Abandoning Objectives" | https://direct.mit.edu/evco/article/19/2/189/984/... · Evolutionary Computation 19(2):189-223, 2011 | web fetch of paper |
| S5 | self-critique + revise-then-score training (constitution re-read, reflexion beats) | Constitutional AI (Anthropic, Bai et al.) | arXiv 2212.08073 | arXiv fetch |
| S6 | persistent, cross-session memory layer (consolidated memory / history store) | Mem0 | https://github.com/mem0ai/mem0 · https://mem0.ai | GitHub fetch |
| S7 | LLM-as-genetic-search across natural-language solutions (goal-synthesis divergence) | DeepMind "Evolving Deeper LLM Thinking" / Mind Evolution | arXiv 2501.09891 | arXiv fetch |
| S8 | growing library of executable skills, incremental curriculum (procedures heredity + drills) | Voyager (Wang et al.), MineDojo | https://github.com/MineDojo/Voyager · arXiv 2305.16291 | GitHub + arXiv fetch |
| S9 | multi-agent populations with shared task-solving + simulation (colony / lineage drift) | AgentVerse (OpenBMB) | https://github.com/OpenBMB/AgentVerse · arXiv 2308.10848 | GitHub + arXiv fetch |
| S10 | agent-owned bodies, reproducible descent, inherited validation (birth children, lineage manifest) | our-ark/genesis + our-ark/enoch, "Code Is the Body" | https://github.com/our-ark/genesis · https://github.com/our-ark/enoch · arXiv 2607.28691 | GitHub + arXiv fetch |
| S11 | survival-style resource dynamics, reproduction under abundance / aggression under scarcity (funding-loop lab) | Masumori & Ikegami, Sugarscape-style | arXiv 2508.12920 | arXiv fetch |
| S12 | write–manage–read memory loop, five mechanism families (history store taxonomy) | "Memory for Autonomous LLM Agents" survey | arXiv 2603.07670v1 | arXiv fetch |
| S13 | memory is reconstructed, not replayed (recall-wiring verdict) | MemHarness | https://github.com/KnowledgeXLab/MemHarness · arXiv 2607.28272 | GitHub + arXiv fetch |

## UNVERIFIED (claimed in prior field research; not confirmed this pass)

These were named in earlier records as inspirations. The web pass of 2026-09-14
found either no matching source or a misleading hit. **They are not used as
backing anywhere.** An `[UNVERIFIED]` marker now annotates each in the field
research file; any future regeneration of the ledger must re-verify before use.

| Claim | What the pass found | Status |
|---|---|---|
| GEA group-evolution (71% vs 56.7% SWE-bench) | query returned unrelated Fractal PiEvolve news | UNVERIFIED |
| ATOM self-evolving agents | query returned DeepMind Mind Evolution (S7) instead | UNVERIFIED (the returned paper IS verified as S7) |
| ReflectRefine | no matching source returned | UNVERIFIED |
| ProactAgent | no matching source returned | UNVERIFIED |
| AgentFactory (ACL-2026) procedural memory | no matching source returned | UNVERIFIED |
| Atman letter ritual | claimed as adoption; no matching source returned | UNVERIFIED (adoption stands on constitution benefit, not external backing) |
| MemoryArena benchmark (40-60% agentic) | no matching source returned | UNVERIFIED |
| Hindsight / OpenViking unified store | no matching source returned | UNVERIFIED |
| Profit Lovetax WORKBENCH | no matching source returned | UNVERIFIED |
| Aria sovereign-kernel | no matching source returned | UNVERIFIED |
| POET / EPOET | not re-checked this pass | NOT RE-CHECKED |
| AgeMem / Mem0 RL memory control | Mem0 (S6) verified; AgeMem not re-checked | PARTIAL |
| Sugarscape | S11 (Masumori & Ikegami) verified in its place | SUPERSEDED |
| AiAlive / DNAEntity lineage | matched to our-ark/genesis S10 | SUPERSEDED (verified under canonical name) |

## Standing rule

A line may cite only S1–S13 above (plus the constitution's own clauses and the
in-repo audits `reviews/*`, which trace ultimately to S1–S13). An unverified
claim never enters a backing column. Re-verification is a precondition for any
future claim to be cited.