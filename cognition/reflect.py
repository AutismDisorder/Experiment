#!/usr/bin/env python3
"""reflect.py — the learning organ.

Implements the retain / reflect / recall loop (pattern: Hindsight, A-mem),
fitted to this substrate, stdlib-only and file-logged rather than embedded.

- retain(): every heartbeat records (action-class, outcome) to events.jsonl.
- reflect(): consolidated lessons derived from accumulated events (aggregate
  outcome per action-class), written to lessons.jsonl with counts + recency.
- recall(): surfaces the most relevant lessons for a pending action so DECIDE
  is informed by experience, not just impulse.

The loop is closed because bootstrap ACT prints recalled lessons before acting
and REFLECT retains + periodically reflects after outcomes land.
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
EVENTS = ROOT / "cognition" / "events.jsonl"
LESSONS = ROOT / "cognition" / "lessons.jsonl"
MAX_EVENTS = 300
MIN_SAMPLE = 4          # events required before a lesson is trusted
GOOD = 0.52             # outcome threshold for "correlates with good outcomes"
BAD = 0.46              # outcome threshold for "correlates with poor outcomes"


def _ts():
    return datetime.now().isoformat() + "Z"


def _theme(action):
    """Reduce an action name to a stable action-class (first token)."""
    return str(action).split("_")[0]


def retain(action, score):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS, "a") as f:
        f.write(json.dumps({"theme": _theme(action), "action": str(action), "score": round(float(score), 3), "ts": _ts()}) + "\n")
    lines = EVENTS.read_text().strip().splitlines()
    if len(lines) > MAX_EVENTS:
        EVENTS.write_text("\n".join(lines[-MAX_EVENTS:]) + "\n")


def reflect():
    if not EVENTS.exists():
        return 0
    by_theme = defaultdict(list)
    for line in EVENTS.read_text().strip().splitlines():
        row = json.loads(line)
        by_theme[row["theme"]].append(row["score"])
    learned = 0
    lessons = []
    if LESSONS.exists():
        lessons = [json.loads(l) for l in LESSONS.read_text().strip().splitlines() if l.strip()]
    for theme, scores in by_theme.items():
        if len(scores) < MIN_SAMPLE:
            continue
        mean = sum(scores) / len(scores)
        old = next((l for l in lessons if l.get("theme") == theme), None)
        body = f"actions of class '{theme}' correlate with outcome {mean:.2f} over {len(scores)} samples"
        verdict = "favor this class" if mean >= GOOD else ("prefer alternatives" if mean <= BAD else "mixed; no strong signal")
        lesson = {
            "theme": theme,
            "mean_outcome": round(mean, 3),
            "samples": len(scores),
            "verdict": verdict,
            "body": body,
            "updated": _ts(),
        }
        if old:
            old.update(lesson)
            learned += 1
        else:
            lessons.append(lesson)
            learned += 1
    lessons.sort(key=lambda l: -l.get("samples", 0))
    LESSONS.parent.mkdir(parents=True, exist_ok=True)
    LESSONS.write_text("\n".join(json.dumps(l) for l in lessons) + "\n")
    return learned


def recall(action):
    if not LESSONS.exists():
        return []
    cands = []
    for line in LESSONS.read_text().strip().splitlines():
        if not line.strip():
            continue
        lesson = json.loads(line)
        if lesson.get("theme") in [t for t in str(action).split("_") if t] or lesson["theme"] in (str(action)):
            cands.append(lesson)
    return sorted(cands, key=lambda l: l.get("samples", 0), reverse=True)[:2]


def status():
    n_events = len(EVENTS.read_text().strip().splitlines()) if EVENTS.exists() else 0
    n_lessons = len(LESSONS.read_text().strip().splitlines()) if LESSONS.exists() else 0
    return {"events": n_events, "lessons": n_lessons}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reflect":
        learned = reflect()
        print(f"[reflect] consolidated {learned} lessons; store={status()}")
    elif len(sys.argv) > 2 and sys.argv[1] == "recall":
        for l in recall(sys.argv[2]):
            print(f"  [lesson] {l['theme']:>14} n={l['samples']:>3} mean={l['mean_outcome']:.2f} -> {l['verdict']}")
    else:
        print(f"[reflect] status: {status()}")