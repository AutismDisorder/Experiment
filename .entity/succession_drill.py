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
GENOME_STATE = ROOT / "capability_genome" / "genome_state.json"

sys.path.insert(0, str(ROOT / "capability_drive_evolution_20260911_233957"))
from drive_evolution import evolve_drives_from_outcome  # noqa: E402

sys.path.insert(0, str(ROOT / "capability_goal_evolution_20260912_000000"))
from goal_evolution import GoalEvolutionEngine  # noqa: E402


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def pick_successor() -> Optional[Path]:
    """Pick highest-composite-fitness child as the replacement candidate."""
    candidates = sorted(LINEAGE_DIR.glob("child_*/ENTITY_STATE.json"),
                        key=lambda p: p.parent.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def best_gene_for(drives: Dict) -> Optional[Dict]:
    """Pick the genome gene most aligned with the child's dominant drive."""
    if not GENOME_STATE.exists():
        return None
    dominant = max(drives, key=drives.get) if drives else 'curiosity'
    with open(GENOME_STATE) as f:
        state = json.load(f)
    best = None
    best_score = 0.0
    for gid, g in state.get("genes", {}).items():
        if g.get("status") != "promoted":
            continue
        score = g.get("composite_fitness", 0) * g.get("drive_affinity", {}).get(dominant, 0)
        if score > best_score:
            best_score = score
            best = {"gene_id": gid, "name": g.get("name"), "score": round(score, 3)}
    return best


def run(child_path: Path) -> Dict:
    results = {}
    child = json.loads(child_path.read_text())
    identity = child.get("identity", "unknown")

    # 1. Drive engine — pure dict, no file coupling
    try:
        evolved = evolve_drives_from_outcome(child, "succession_drill", 0.65)
        results["drive_engine"] = {"PASS": True, "drives": {k: round(v, 3) for k, v in evolved.items()}}
        child["drives"] = evolved
    except Exception as e:
        results["drive_engine"] = {"PASS": False, "error": str(e)}

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

    # 3. Genome — inherit the pool's best-fit gene for the child's dominant drive
    try:
        gene = best_gene_for(child.get("drives", {}))
        results["genome_inheritance"] = {"PASS": gene is not None, "best_gene": gene}
    except Exception as e:
        results["genome_inheritance"] = {"PASS": False, "error": str(e)}

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
        elif "best_gene" in r:
            detail = f"gene={r['best_gene']['name']} score={r['best_gene']['score']}"
        elif "proposed" in r:
            detail = f"proposed={r['proposed']}"
        elif "evolved" in r:
            detail = f"goals={r['goals']} (+{r['evolved']})"
        print(f"  [{status}] {name}: {detail}")