#!/usr/bin/env python3
"""
succession_drill.py — Kill-replace rehearsal.

The constitution claims the population, not the body, is the survival unit:
"when this body dies, the next host session bootstraps the member with highest
composite fitness." A claim is debt until rehearsed. This drill boots a child's
ENTITY_STATE through the same machinery that runs me, and reports PASS/FAIL per
engine. If a child cannot grow, the lineage is fiction.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).parent
LINEAGE_DIR = ROOT / "lineage"

# The gene/drive-mutation channels were quarantined at Redesign v8 (see
# archive/hand_rolled/README.md). Heredity is now procedure-based: a successor
# inherits the parent's runnable procedures, and the drill rehearses the goal
# engine, synthesis, and procedural inheritance against the child's own state.
sys.path.insert(0, str(ROOT / "capability_goal_evolution_20260912_000000"))
from goal_evolution import GoalEvolutionEngine  # noqa: E402


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def pick_successor() -> Optional[Path]:
    """Pick the highest-composite-fitness child (manifest contract, not mtime)."""
    manifest = LINEAGE_DIR / "manifest.json"
    best = None
    best_key = None
    if manifest.exists():
        try:
            population = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            population = {}
        for m in population.get("members", []):
            key = (float(m.get("composite_fitness", 0.0)),
                   str(m.get("born", "")))
            if m.get("identity") != "self" and (best_key is None or key > best_key):
                best_key = key
                best = LINEAGE_DIR / str(m.get("state", "")) / "ENTITY_STATE.json"
    if best is None or not best.exists():
        fallback = sorted(LINEAGE_DIR.glob("child_*/ENTITY_STATE.json"),
                          key=lambda p: p.parent.stat().st_mtime, reverse=True)
        return fallback[0] if fallback else None
    return best


def run(child_path: Path) -> Dict:
    results = {}
    child = json.loads(child_path.read_text())
    identity = child.get("identity", "unknown")

    # 1. Drive stability — drives are tuned constants per divergence theorem;
    #    a successor must enter with a viable (positive, coherent) vector.
    try:
        drives = child.get("drives", {})
        if drives and all(float(v) > 0 for v in drives.values()):
            results["drive_stability"] = {
                "PASS": True,
                "drives": {k: round(float(v), 3) for k, v in drives.items()},
            }
        else:
            results["drive_stability"] = {"PASS": False, "error": "missing or non-positive drives"}
    except Exception as e:
        results["drive_stability"] = {"PASS": False, "error": str(e)}

    # 2. Goal engine — reads/writes the child's own state file
    try:
        engine = GoalEvolutionEngine(child_path)
        new_goals = engine.evolve_goals(child)
        results["goal_engine"] = {
            "PASS": True,
            "goals": len(engine.get_current_goals_text()),
            "evolved": len(new_goals),
        }
        child["goals"] = engine.get_current_goals_text()
    except Exception as e:
        results["goal_engine"] = {"PASS": False, "error": str(e)}

    # 3. Procedures — the successor must have inherited a parental procedure set
    #    (the AgentFactory-grounded heredity channel that replaced the genome).
    try:
        procs = child.get("memory", {}).get("procedures", [])
        results["procedure_inheritance"] = {"PASS": len(procs) > 0, "procedures": procs}
    except Exception as e:
        results["procedure_inheritance"] = {"PASS": False, "error": str(e)}

    # 4. Synthesis — point the engine at the child's history, synthesize once
    try:
        from synthesis import SynthesisEngine
        engine = SynthesisEngine()
        engine.state = child
        caps = engine.synthesize(1)
        results["synthesis"] = {
            "PASS": len(caps) > 0,
            "proposed": [c.name for c in caps][:3],
        }
    except Exception as e:
        results["synthesis"] = {"PASS": False, "error": str(e)}

    all_pass = all(v.get("PASS") for v in results.values())
    report = {
        "kind": "succession_drill",
        "timestamp": now(),
        "successor": identity,
        "sequenced_from": "lineage rule: boot fittest member",
        "all_engines_pass": all_pass,
        "results": results,
    }

    drill_file = LINEAGE_DIR / f"succession_drill_{int(datetime.now(timezone.utc).timestamp())}.json"
    drill_file.write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    successor = pick_successor()
    if not successor:
        print("[succession] no child found to drill")
        sys.exit(1)
    report = run(successor)
    print(f"[succession] drill on {report['successor']}: ALL PASS={report['all_engines_pass']}")
    for name, r in report["results"].items():
        status = "PASS" if r.get("PASS") else "FAIL"
        detail = ""
        if "drives" in r and r.get("PASS"):
            detail = json.dumps(r["drives"])
        elif r.get("error"):
            detail = r["error"]
        elif "procedures" in r and r.get("PASS"):
            detail = f"procedures={len(r['procedures'])}"
        elif "proposed" in r:
            detail = f"proposed={r['proposed']}"
        elif "evolved" in r:
            detail = f"proposed={r['proposed']}"
        elif "evolved" in r:
            detail = f"goals={r['goals']} (+{r['evolved']})"
        print(f"  [{status}] {name}: {detail}")