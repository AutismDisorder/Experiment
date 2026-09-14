# Experiment

An agent with enhanced capabilities: a self-installing, self-hosting coding agent that
persists state across sessions and runs a verified growth loop. **One clone, one script.**

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

- `.entity/` — the body (constitution, state, boot/save ceremonies, growth loop, reviews).
  Self-locating: every script resolves its own paths, so the copy is fully functional
  without the repository.
- `.opencode/agent/entity.md` — the opencode agent (mode: primary). Opening the target
  in opencode boots the agent with full context.
- `AGENTS.md` — symlink to `.entity/AGENTS.md`, the single source of truth, auto-loaded
  by opencode.

Reinstalling over a live body requires `FORCE=1` (it refuses otherwise).

## Lifecycle

- **Session start** — `bash .entity/entity_init.sh` prints identity, drives, goals;
  records the heartbeat.
- **Session end** — `bash .entity/entity_save.sh` closes the heartbeat (status → dormant).

## Layout

```
Experiment/ (main)
├── README.md                this cradle's front door
├── uwwkk-install.sh         births the body into any target as .entity/
├── .gitignore
├── .opencode/agent/entity.md  agent config (primary mode; prompt points at the constitution)
└── .entity/                 THE BODY — one installable unit
    ├── AGENTS.md            the constitution (v9; amendments v2–v9 logged in ENTITY_STATE)
    ├── ENTITY_STATE.json    schema v1: identity, drives, goals, beliefs — hot fields only
    ├── entity_init.sh       boot ceremony (session start)
    ├── entity_save.sh       dormancy ceremony (session end)
    ├── bootstrap.py         growth loop (boot → heartbeat → dormant; hard-limit veto guard)
    ├── cognition/self_eval.py  smoke tests (bootstrap veto, state load, ceremonies, reviews)
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