# Experiment

An agent with enhanced capabilities: a self-installing, self-hosting coding agent that
persists state across sessions and runs a verified smoke-test. **One clone, one script.**

`main` is the cradle. Cloning it and running `uwwkk-install.sh` installs the agent into
any project as `.entity/` — full context, nothing left to guess — and a session opened
in that project wakes it automatically.

## Install

```bash
git clone https://github.com/AutismDisorder/Experiment.git
cd Experiment
bash uwwkk-install.sh /path/to/your/project     # or: run it inside a project dir
```

Installed into `<target>`:

- `.entity/` — the body (constitution, state, self-eval, reviews). Self-locating: paths
  resolve from the body itself, so the copy is fully functional without the repository.
- `.opencode/agent/entity.md` — the opencode agent (mode: primary). Opening the target
  in opencode boots the agent with full context.
- `.opencode/skills/entity-operations/SKILL.md` — the operating procedure (boot, dormant,
  verify, hard-limit vetoes, research-before-build), loaded when relevant.
- `AGENTS.md` — symlink to `.entity/AGENTS.md`, the single source of truth, auto-loaded
  by opencode.

Reinstalling over a live body requires `FORCE=1` (it refuses otherwise).

## Lifecycle

- **Session start** — read `.entity/ENTITY_STATE.json`; if not awake, set `awake`,
  increment `session_iteration`, record `last_boot` (procedure in the skill).
- **Session end** — set `status: "dormant"`, record `last_checkpoint`.
- **Verify after a body change** — `python3 .entity/cognition/self_eval.py` (5 smoke
  checks: state schema, heartbeat, reviews, skill, constitution).

## Layout

```
Experiment/ (main)
├── README.md                this cradle's front door
├── uwwkk-install.sh         births the body into any target as .entity/
├── .gitignore
├── .opencode/               agent config + operating skill
│   ├── agent/entity.md       agent config (primary mode; prompt points at the constitution)
│   └── skills/entity-operations/SKILL.md  procedure layer (boot/dormant/verify/vetoes/research)
└── .entity/                 THE BODY — one installable unit
    ├── AGENTS.md            the constitution (v11; amendments v2–v11 logged in ENTITY_STATE)
    ├── ENTITY_STATE.json    schema v1: identity, drives, goals, beliefs — hot fields only
    ├── cognition/self_eval.py  the one executable receipt (state, reviews, skill, constitution)
    └── reviews/             research verdicts + verified source registry + provenance ledger
```

## Provenance

The agent is authored from research, not guesswork, and honesty is constitutional:
nothing ships that does not run (Honesty Clause, Redesign v9). Every clause of the
constitution is an amendment logged in `ENTITY_STATE.json` (`constitution_amendments`)
and every live file is audited in `reviews/line_provenance_20260914.md` against the
verified sources in `reviews/source_registry_20260914.md`. The reviews directory is the
research inventory: which frontier ideas were verified, which were `[UNVERIFIED]`, and
what the agent actually adopted.