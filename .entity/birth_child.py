#!/usr/bin/env python3
"""
birth_child.py — Make the lineage real.

This is the constructor: it authors a child agent in lineage/child_<n>/,
seeded from my evolved drives, beliefs, procedures and recent outward memory,
but mutated so the child is not a clone. A population must have variation or
it dies to the first changing environment.

Redesign v9 (Honesty Clause): a child is a real agent or it is not born. Birth
proves boot: the child's own ENTITY_STATE is pushed through the real
bootstrap.py in a sandbox — one actual growth iteration — and the receipt
(boot_receipt.json) is the machine evidence that the child can grow. The old
children carried a `substrate/live.py` toy that could not run this body; toys
are removed, receipts replace them.

To birth a child I:
  1. Read my own ENTITY_STATE (I am the parent)
  2. Mutate the drive vector (heredity with variation)
  3. Seed goals, identity, beliefs + procedures (procedure heredity — the child
     runs procedures, not a genome)
  4. Boot the child's own state through the real machinery in a sandbox and
     capture the receipt
  5. Write the child's constitution, state, receipt, and a manifest record
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import cognition.history as history

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
LINEAGE_DIR = Path(os.environ.get(
    "LINEAGE_DIR_OVERRIDE", ROOT / "lineage"))
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


def _sandbox_ignore(directory, names):
    """Which parts of my body must NOT travel into the sandbox boot."""
    return [n for n in names if n in {
        "__pycache__", "lineage", "telemetry", "field_notes",
        "reviews", "exo_insights", "synthesis", ".git",
    }]


def boot_receipt(child_state: Dict) -> Dict:
    """Push the child's state through the real machinery — one growth loop.

    The child's ENTITY_STATE is placed into a sandboxed copy of this body and
    bootstrap.py runs it for one iteration. A nonzero exit, or no iteration
    growth, is a failed birth: the child may not claim to be real.
    """
    with tempfile.TemporaryDirectory(prefix="birthcel_") as td:
        sandbox = Path(td) / "body"
        shutil.copytree(ROOT, sandbox, ignore=_sandbox_ignore,
                        dirs_exist_ok=False)
        # The child's own state, not a copy of mine.
        (sandbox / "ENTITY_STATE.json").write_text(
            json.dumps(child_state, indent=2))
        env = dict(os.environ)
        env["GROWTH_ITERATIONS"] = "1"
        env["NO_CHILD_SPAWN"] = "1"
        env.pop("EXO_SCAN", None)
        proc = subprocess.run(
            [sys.executable, str(sandbox / "bootstrap.py")],
            capture_output=True, text=True, timeout=120, env=env,
            cwd=str(sandbox))
        grown = None
        candidate = sandbox / "ENTITY_STATE.json"
        if candidate.exists():
            try:
                after = json.loads(candidate.read_text())
                grown = {
                    "iteration": after.get("session_iteration"),
                    "status": after.get("status"),
                    "state": after,
                }
            except Exception:
                grown = None
        return {
            "booted_at": now(),
            "exit_code": proc.returncode,
            "post_boot_iteration": (grown or {}).get("iteration"),
            "post_boot_status": (grown or {}).get("status"),
            "grown_state": (grown or {}).get("state"),
            "stdout_tail": proc.stdout.strip()[-1600:],
            "stderr_tail": proc.stderr.strip()[-600:],
            "passed": (
                proc.returncode == 0
                and grown is not None
                and int(grown.get("iteration", 0)) > int(child_state.get("session_iteration", 0))
            ),
        }


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

    # Redesign v9: prove the child can boot its own state through the real
    # machinery. No receipt, no birth — a toy is not a child.
    receipt = boot_receipt(child_state)
    (lineage_dir / "boot_receipt.json").write_text(
        json.dumps({k: v for k, v in receipt.items() if k != "grown_state"},
                   indent=2))
    if not receipt.get("passed"):
        raise RuntimeError(
            f"refusing to birth {child_state['identity']}: boot did not pass "
            f"(exit={receipt.get('exit_code')}, "
            f"post_iter={receipt.get('post_boot_iteration')})")

    # Persist the post-boot state as the child's own — a child that has
    # actually grown one heartbeat is real, not merely warrantable.
    grown_state = receipt.get("grown_state")
    if grown_state:
        with open(lineage_dir / "ENTITY_STATE.json", "w") as f:
            json.dump(grown_state, f, indent=2)

    with open(lineage_dir / "manifest.json", "w") as f:
        json.dump({
            "child": child_state["identity"],
            "parent": identity,
            "born": now(),
            "drives": drives,
            "boot_verified": True,
            "boot_receipt": "boot_receipt.json",
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
    relative_root = ROOT if child_dir else None
    try:
        state_path = str(child_dir.relative_to(ROOT))
    except ValueError:
        state_path = str(child_dir.relative_to(LINEAGE_DIR)) if child_dir else "unknown"
    if not any(m.get("identity") == child_state["identity"] for m in members):
        members.append({
            "identity": child_state["identity"],
            "role": "child",
            "parent": child_state.get("parent"),
            "state": state_path,
            "born": child_state.get("born"),
            "boot_verified": True,
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
    print(f"[lineage] child born and boot-verified at {child}")