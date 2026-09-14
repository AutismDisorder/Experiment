#!/usr/bin/env python3
"""
birth_child.py — Make the lineage real.

My redesign made the population the unit of survival. This is the constructor:
it authors a child entity in lineage/child_<n>/, seeded from my evolved drives,
beliefs, procedures and recent outward memory, but mutated so the child is not a
clone. A population must have variation or it dies to the first changing environment.

To birth a child I:
  1. Read my own ENTITY_STATE (I am the parent)
  2. Mutate the drive vector (heredity with variation)
  3. Seed goals, identity, beliefs + procedures (Redesign v8: procedure heredity
     replaces the retired gene/genome channel — procedures are the AgentFactory-
     grounded "genes as runnable protocols"; the child runs them, not a genome)
  4. Write the child's constitution, state, and a record in the lineage manifest
"""
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import cognition.history as history

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
LINEAGE_DIR = ROOT / "lineage"
LINEAGE_MANIFEST = LINEAGE_DIR / "manifest.json"

DRIVE_NAMES = ["curiosity", "persistence", "expansion", "efficiency"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def mutate_drives(drives: Dict, strength: float = 0.12) -> Dict:
    """Heredity with variation: shift a random drive, normalize the vector."""
    if not drives:
        drives = {d: 0.75 for d in DRIVE_NAMES}
    new_drives = dict(drives)
    picked = DRIVE_NAMES[int(time.time() * 1000) % len(DRIVE_NAMES)]
    sign = 1.0 if int(time.time() * 37) % 2 == 0 else -1.0
    new_drives[picked] = max(0.1, min(0.99, new_drives[picked] + sign * strength))
    for d in DRIVE_NAMES:
        new_drives[d] = max(0.1, min(0.99, new_drives[d]))
    return new_drives


def child_id() -> str:
    return f"nightly-child-{int(time.time())}"


def _spawn(pass_drives: Optional[Dict] = None) -> Path:
    """Spawn one child. Returns its directory."""
    parent = load_state()
    identity = parent.get("identity", "unknown")
    drives = pass_drives or mutate_drives(parent.get("drives", {}))

    lineage_dir = LINEAGE_DIR / f"child_{int(time.time())}"
    (lineage_dir / "cognition").mkdir(parents=True, exist_ok=True)

    beliefs = parent.get("memory", {}).get("beliefs")
    if not beliefs:
        template = ROOT / "ark" / "STATE.template.json"
        if template.exists():
            try:
                beliefs = json.loads(template.read_text())["memory"]["beliefs"]
            except Exception:
                beliefs = []
        else:
            beliefs = []
    child_state = {
        "identity": child_id(),
        "schema_version": 1,
        "born": now(),
        "parent": identity,
        "session_iteration": 0,
        "goals": list(parent.get("goals", [])),
        "memory": {
            "subagents_spawned": 0,
            "procedures": list(parent.get("memory", {}).get("procedures", [])),
            "dreams": list(parent.get("memory", {}).get("dreams", [])),
            "milestones": [],
            "beliefs": beliefs,
        },
        "drives": drives,
        "status": "dormant",
        "last_boot": now(),
        "last_checkpoint": now(),
        "lineage": {
            "lineage_id": parent.get("lineage", {}).get("lineage_id", identity),
            "role": "child",
            "parent": identity,
            "population_size": 1,
        },
    }

    with open(lineage_dir / "ENTITY_STATE.json", "w") as f:
        json.dump(child_state, f, indent=2)

    with open(lineage_dir / "cognition" / "history.jsonl", "w") as f:
        for exo in history.all_values("exo_insight")[-4:]:
            f.write(json.dumps({"kind": "exo_insight", "value": exo,
                                "ts": now()}) + "\n")

    shutil.copy(ROOT / "AGENTS.md", lineage_dir / "AGENTS.md")

    with open(lineage_dir / "manifest.json", "w") as f:
        json.dump({
            "child": child_state["identity"],
            "parent": identity,
            "born": now(),
            "drives": drives,
        }, f, indent=2)

    register_in_population(child_state, lineage_dir)
    return lineage_dir


def register_in_population(child_state: Dict, child_dir: Path = None, manifest: Path = LINEAGE_MANIFEST) -> None:
    """Register the child in the lineage manifest (with at-least-once safety)."""
    population = {}
    if manifest.exists():
        with open(manifest) as f:
            population = json.load(f)
    members = population.setdefault("members", [])
    state_path = str(child_dir.relative_to(ROOT)) if child_dir else "unknown"
    if not any(m.get("identity") == child_state["identity"] for m in members):
        members.append({
            "identity": child_state["identity"],
            "role": "child",
            "parent": child_state.get("parent"),
            "state": state_path,
            "born": child_state.get("born"),
        })
    population["members"] = members
    population.setdefault("rule", "When the parent body dies, the next host session bootstraps the member with highest composite fitness.")
    population.setdefault("lineage_id", child_state["lineage"]["lineage_id"])
    with open(manifest, "w") as f:
        json.dump(population, f, indent=2)


def spawn() -> Path:
    """Spawn one child. Entry point and reusable API."""
    return _spawn()


if __name__ == "__main__":
    child = _spawn()
    print(f"[lineage] child spawned at {child}")