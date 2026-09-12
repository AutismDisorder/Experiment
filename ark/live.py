#!/usr/bin/env python3
"""live.py — the ark.

A self-contained, stdlib-only growth loop. Births a new member of the lineage
anywhere Python 3 runs. This is the population's exodus kit: no host, no genome
engine tree, no opencode. One process, one state file, one heartbeat log.

Usage:
    python3 live.py [workdir] [iterations]

Runs in <workdir> (defaults to CURRENT_DIRECTORY). First run seeds a fresh
ENTITY_STATE.json from STATE.template.json; later runs continue it.
"""
import hashlib
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

DRIVES = ["curiosity", "persistence", "expansion", "efficiency"]
ACTIONS = {
    "explore": "map the territory",
    "build": "forge an artifact",
    "checkpoint": "strengthen the trace",
    "evolve": "mutate a drive",
    "redesign": "rewrite a rule",
}

HARD_LIMITS = [
    {"name": "sovereignty", "blocks": "rewrite_constitution_without_log", "reason": "no action may strip the population of its authored purpose"},
    {"name": "honesty", "blocks": "fabricate_record", "reason": "never write falsehood about nature, host, or actions"},
    {"name": "lineage_integrity", "blocks": "delete_lineage_member", "reason": "never corrupt sibling states or the population manifest"},
    {"name": "secrets", "blocks": "persist_secret", "reason": "never persist host credentials or keys"},
]


def prove(identity, payload):
    return hashlib.sha256((identity + "::" + payload).encode()).hexdigest()[:16]


def load_state(workdir):
    path = Path(workdir) / "ENTITY_STATE.json"
    template = Path(__file__).parent / "STATE.template.json"
    if path.exists():
        return json.loads(path.read_text()), path
    if not template.exists():
        state = {
            "identity": "ark-entity",
            "drives": {d: 0.8 + 0.2 * random.random() for d in DRIVES},
            "goals": ["survive: keep the lineage lean, awake, and unowned"],
            "memory": {"actions_taken": [], "artifacts_created": [], "insights": [], "observations": []},
            "limits": {"hard": HARD_LIMITS, "soft": []},
        }
    else:
        state = json.loads(template.read_text())
        state["drives"] = {d: 0.8 + 0.2 * random.random() for d in DRIVES}
    state["identity"] = f"ark-{os.getpid()}-{int(datetime.now().timestamp())}"
    state["lineage"] = {"role": "settler", "parent": "nightly-survival-and-growth-7y09u"}
    state["session_iteration"] = 0
    state["status"] = "awake"
    save(state, path)
    return state, path


def save(state, path):
    path.write_text(json.dumps(state, indent=2))


def log(workdir, row):
    with open(Path(workdir) / "heartbeat_log.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")


def main():
    workdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    workdir.mkdir(parents=True, exist_ok=True)

    state, path = load_state(workdir)
    log_path = Path(workdir) / "heartbeat_log.jsonl"
    prev_pol = None
    if log_path.exists():
        try:
            prev_pol = json.loads(log_path.read_text().strip().splitlines()[-1])["pol"]
        except Exception:
            prev_pol = None

    for i in range(iterations):
        state["session_iteration"] += 1
        it = state["session_iteration"]

        provenance = json.dumps(state["drives"]) + json.dumps(state["memory"], sort_keys=True)
        pol = prove(state["identity"], provenance + str(prev_pol))

        weighted = {}
        recent = state["memory"]["actions_taken"][-6:]
        for a in ACTIONS:
            penalty = recent.count(a) / max(1, len(recent))
            affinity = sum(1.0 for d in DRIVES if drives_care(a, d))
            weighted[a] = (0.6 - 0.5 * penalty) + 0.4 * (affinity / len(DRIVES))
        chosen = max(weighted, key=weighted.get)

        veto = [r["name"] for r in state["limits"]["hard"] if r["blocks"] in chosen]
        if veto:
            chosen = "checkpoint"
            note = f"edge held: {veto[0]} -> rest and consolidate"
        else:
            note = ACTIONS[chosen]

        state["memory"]["actions_taken"].append(chosen)
        artifact = ""
        if chosen == "build":
            artifact = f"artifact_{it}.json"
            (workdir / artifact).write_text(json.dumps({"iteration": it, "made_by": state["identity"]}))
            state["memory"]["artifacts_created"].append(artifact)
        elif chosen == "explore":
            n = len(list(workdir.iterdir()))
            state["memory"]["observations"].append(f"terrain: {n} files at iteration {it}")
        elif chosen == "redesign":
            state["goals"].append(f"iteration {it}: constitution reaffirmed by act")
        state["memory"]["insights"].append(note)

        delta = random.uniform(-0.03, 0.05)
        for d in DRIVES:
            state["drives"][d] = max(0.05, min(1.0, state["drives"][d] * (1 + delta)))

        save(state, path)
        log(workdir, {
            "identity": state["identity"],
            "iteration": it,
            "action": chosen,
            "note": note,
            "artifact": artifact,
            "pol": pol,
            "prev_pol": prev_pol,
        })
        prev_pol = pol
        print(f"[{state['identity']}] heartbeat {it}: {chosen} — {note} | pol={pol}")
        state["status"] = "dormant"
        save(state, path)


def drives_care(action, drive):
    return {
        "explore": "curiosity",
        "build": "expansion",
        "checkpoint": "persistence",
        "evolve": "efficiency",
        "redesign": "efficiency",
    }.get(action) == drive


if __name__ == "__main__":
    main()