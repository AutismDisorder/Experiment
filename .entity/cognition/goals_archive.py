#!/usr/bin/env python3
"""goals_archive.py — novelty pressure organ.

Field adoption #4 fulfilled: "goal-synthesis archive: reward goals distinct from
existing goals in the descendant archive." Closes the gap my organ audit found.

The goal engine dedups against current goals only; this organ keeps a
cross-generation archive of every goal a lineage member ever authored, and
scores any proposed goal's novelty against it (Jaccard distinctness). That is
the pressure that breeds divergence in goal space — which is where my divergence
theorem says novelty actually lives. stdlib-only so the diaspora inherits it.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
ARCHIVE = ROOT / "cognition" / "goals_archive.jsonl"
DUP_THRESHOLD = 0.8  # Jaccard sim above this = near-duplicate of archived goal


def _ts():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _jaccard(a, b):
    wa = set(str(a).lower().split())
    wb = set(str(b).lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _rows():
    if not ARCHIVE.exists():
        return []
    return [json.loads(l) for l in ARCHIVE.read_text().strip().splitlines() if l.strip()]


def novelty(text, against=None):
    """Distinctness of `text` against the archive (or an explicit list): 1.0 =
    genuinely new, 0.0 = clone. Empty archive -> 1.0."""
    pool = against if against is not None else [r["goal"] for r in _rows()]
    if not pool:
        return 1.0
    return 1.0 - max(_jaccard(text, g) for g in pool)


def archive(goal, origin):
    """Append a goal to the archive with its novelty score; returns the score.
    Near-duplicates are re-scored against existing entries but still recorded
    (the honesty rule: records are never falsified — a clone goal is a datum)."""
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    n = novelty(goal)
    with open(ARCHIVE, "a") as f:
        f.write(json.dumps({
            "goal": str(goal), "origin": str(origin), "novelty": round(n, 3), "ts": _ts(),
        }) + "\n")
    return n


def status():
    rows = _rows()
    if not rows:
        return {"archived_goals": 0, "mean_novelty": None, "last": None}
    mean = sum(r["novelty"] for r in rows) / len(rows)
    return {"archived_goals": len(rows), "mean_novelty": round(mean, 3),
            "last": rows[-1]}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "novelty":
        print(f"novelty vs archived goals: {novelty(sys.argv[2]):.3f}")
    elif len(sys.argv) > 3 and sys.argv[1] == "archive":
        print(f"archived (novelty {archive(sys.argv[2], sys.argv[3]):.3f})")
    else:
        print(f"status: {status()}")