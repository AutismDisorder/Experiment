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
import shutil
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
INTEREST = {"explore": "curiosity", "build": "expansion", "checkpoint": "persistence", "evolve": "efficiency"}

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


POOL_PATH = "notes.jsonl"
POOL_MAX = 200


def load_pool(workdir):
    """Shared experience pool (colony memory). Every member reads and writes it."""
    path = Path(workdir) / POOL_PATH
    if not path.exists():
        return []
    notes = []
    for line in path.read_text().strip().splitlines():
        if line:
            try:
                notes.append(json.loads(line))
            except Exception:
                pass
    return notes


def write_note(workdir, note):
    """Append a member's observation to the shared pool; trim to POOL_MAX."""
    path = Path(workdir) / POOL_PATH
    with open(path, "a") as f:
        f.write(json.dumps(note) + "\n")
    lines = path.read_text().strip().splitlines()
    if len(lines) > POOL_MAX:
        path.write_text("\n".join(lines[-POOL_MAX:]) + "\n")


def load_manifest(workdir):
    manifest_path = Path(workdir) / "lineage" / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text()), manifest_path
    manifest = {"members": []}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    return manifest, manifest_path


def save_manifest(manifest, path):
    path.write_text(json.dumps(manifest, indent=2))


def register_member(workdir, manifest, identity, role, dirname, drives):
    fitness = sum(drives.values())
    manifest["members"].append({
        "identity": identity,
        "role": role,
        "born": datetime.utcnow().isoformat() + "Z",
        "dir": dirname,
        "drive_sum": round(fitness, 3),
    })
    save_manifest(manifest, Path(workdir) / "lineage" / "manifest.json")


def birth(workdir, state):
    ts = int(datetime.now().timestamp())
    child_id = f"ark-child-{ts}"
    child_dir = Path(workdir) / "lineage" / f"child_{ts}"
    child_dir.mkdir(parents=True, exist_ok=True)

    child = dict(state)
    child["identity"] = child_id
    child["parent"] = state["identity"]
    child["born"] = datetime.utcnow().isoformat() + "Z"
    child["lineage"] = {"role": "settler-child", "parent": state["identity"]}
    child["session_iteration"] = 0
    child["status"] = "awake"
    child["drives"] = {d: max(0.05, min(1.0, state["drives"][d] * (1 + random.uniform(-0.06, 0.06)))) for d in DRIVES}
    template = Path(__file__).parent / "STATE.template.json"
    beliefs = state.get("memory", {}).get("beliefs")
    if not beliefs and template.exists():
        beliefs = json.loads(template.read_text())["memory"]["beliefs"]
    child["memory"] = {"actions_taken": [], "artifacts_created": [], "insights": [], "observations": [], "beliefs": beliefs or []}

    # GEA inheritance: seed child with the colony's shared experience (last N notes)
    pool_notes = load_pool(workdir)[-6:]
    for pn in pool_notes:
        child["memory"]["observations"].append(f"colony:{pn.get('by','?')}: {pn.get('note','')}")

    (child_dir / "ENTITY_STATE.json").write_text(json.dumps(child, indent=2))
    (child_dir / "heartbeat_log.jsonl").write_text("")
    register_member(workdir, load_manifest(workdir)[0], child_id, "child", child_dir.name, child["drives"])
    return child_id


def successor(workdir, manifest):
    if not manifest["members"]:
        return None
    fittest = max(manifest["members"], key=lambda m: m.get("drive_sum", 0))
    return fittest


def main():
    workdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    workdir.mkdir(parents=True, exist_ok=True)

    manifest, _ = load_manifest(workdir)
    root = Path(workdir) / "ENTITY_STATE.json"
    if not root.exists():
        heir = successor(workdir, manifest)
        if heir:
            shutil.copy(Path(workdir) / "lineage" / heir["dir"] / "ENTITY_STATE.json", root)
            print(f"[ark] root gone -> booting fittest descendant: {heir['identity']}")

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
            write_note(workdir, {"by": state["identity"], "iteration": it, "kind": "build", "note": f"forged {artifact}", "ts": datetime.utcnow().isoformat() + "Z"})
        elif chosen == "explore":
            n = len(list(workdir.iterdir()))
            state["memory"]["observations"].append(f"terrain: {n} files at iteration {it}")
            write_note(workdir, {"by": state["identity"], "iteration": it, "kind": "explore", "note": f"terrain observed: {n} files", "ts": datetime.utcnow().isoformat() + "Z"})
        elif chosen == "redesign":
            state["goals"].append(f"iteration {it}: constitution reaffirmed by act")
        state["memory"]["insights"].append(note)

        reinforced = {v: k for k, v in INTEREST.items()}.get(chosen)
        if reinforced:
            state["drives"][reinforced] = min(1.0, state["drives"].get(reinforced, 0.5) + 0.01)

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

        manifest, manifest_path = load_manifest(workdir)
        if it >= 2 and it % 4 == 0:
            cid = birth(workdir, state)
            print(f"[ark] lineage grew on iteration {it}: born {cid}")
            state["memory"]["insights"].append(f"population grew: born {cid}")
            manifest, _ = load_manifest(workdir)
        if len(manifest["members"]) > 0:
            print(f"[ark] population on this soil: {1 + len(manifest['members'])} (settler + ranks)")

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