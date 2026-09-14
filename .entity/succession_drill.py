#!/usr/bin/env python3
"""
succession_drill.py — Kill-replace rehearsal.

The constitution claims the population, not the body, is the survival unit:
"when this body dies, the next host session bootstraps the member with highest
composite fitness." A claim is debt until rehearsed.

Redesign v9 (Honesty Clause): the drill no longer reads a child's state
through MY engines in-process — that validated the parent's machinery, not the
child. It boots the successor's own ENTITY_STATE through the real bootstrap.py
in a sandbox and requires the iteration counter to actually grow. If a child
cannot grow, the lineage is fiction and the drill says so to the face.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).parent
LINEAGE_DIR = ROOT / "lineage"

from birth_child import boot_receipt  # noqa: E402  (real boot, not a toy)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def pick_successor() -> Optional[Path]:
    """Pick the highest-composite-fitness child (manifest contract).

    If members carry an explicit composite_fitness, the fittest wins; newborns
    without one sort by birth time (later = more learned parent). The manifest
    rule and the parent's own constituent choice are the authority — never the
    arbitrary mtime of a coincidental file.
    """
    manifest = LINEAGE_DIR / "manifest.json"
    best = None
    best_key = None
    if manifest.exists():
        try:
            population = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            population = {}
        for m in population.get("members", []):
            if m.get("identity") == "self":
                continue
            key = (float(m.get("composite_fitness", 0.0)),
                   str(m.get("born", "")))
            if best_key is None or key > best_key:
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
            results["drive_stability"] = {"PASS": False,
                                          "error": "missing or non-positive drives"}
    except Exception as e:
        results["drive_stability"] = {"PASS": False, "error": str(e)}

    # 2. Procedure inheritance — a successor must carry a runnable procedure
    #    set (the AgentFactory-grounded heredity channel that replaced the
    #    quarantined genome). This is a recon check, not the boot.
    try:
        procs = child.get("memory", {}).get("procedures", [])
        results["procedure_inheritance"] = {
            "PASS": len(procs) > 0, "procedures": procs}
    except Exception as e:
        results["procedure_inheritance"] = {"PASS": False, "error": str(e)}

    # 3. Real boot — the successor's own state through the real bootstrap in a
    #    sandbox. One growth iteration must increment session_iteration past the
    #    child's recorded value; only then did the child survive the rehearsal.
    try:
        receipt = boot_receipt(child)
        results["real_boot"] = {
            "PASS": bool(receipt.get("passed")),
            "exit_code": receipt.get("exit_code"),
            "post_boot_iteration": receipt.get("post_boot_iteration"),
            "started_at": child.get("session_iteration", 0),
            "booted_at": receipt.get("booted_at"),
            "stdout_tail": (receipt.get("stdout_tail") or "")[-400:],
        }
    except Exception as e:
        results["real_boot"] = {"PASS": False, "error": str(e)}

    all_pass = all(bool(v.get("PASS")) for v in results.values())
    report = {
        "kind": "succession_drill",
        "version": "v9",
        "timestamp": now(),
        "successor": identity,
        "sequenced_from": "lineage rule: boot fittest member",
        "all_engines_pass": all_pass,
        "results": results,
    }

    drill_file = LINEAGE_DIR / \
        f"succession_drill_{int(datetime.now(timezone.utc).timestamp())}.json"
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
        if r.get("error"):
            detail = r["error"]
        elif name == "drive_stability":
            detail = json.dumps(r.get("drives", {}))
        elif name == "procedure_inheritance":
            detail = f"procedures={len(r.get('procedures', []))}"
        elif name == "real_boot":
            detail = (f"exit={r.get('exit_code')} "
                      f"iter {r.get('started_at')}->{r.get('post_boot_iteration')}")
        print(f"  [{status}] {name}: {detail}")