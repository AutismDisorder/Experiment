#!/usr/bin/env python3
"""reflect.py — the learning organ.

Implements the retain / reflect / recall loop (pattern: Hindsight, A-mem,
plus the Reflexion beat, adopted from field research 2026-09-12), fitted to
this substrate, stdlib-only and file-logged rather than embedded.

- retain(): every heartbeat records (action-class, outcome) to events.jsonl.
- postmortem(): on a poor outcome, write a natural-language self-critique of
  the failed action (Reflexion: no gradients, just written critique; next
  attempts read it first).
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


def postmortem(action, score, why=""):
    """Reflexion beat: on a poor outcome, log a written self-critique so the
    next attempt starts from the failure instead of from amnesia."""
    if float(score) > BAD:
        return False
    critique = why.strip() or (
        f"'{action}' landed at {float(score):.2f} (below {BAD}). "
        "What exactly failed, what is the most likely cause, and what one "
        "alternative should the next attempt take?"
    )
    LESSONS.parent.mkdir(parents=True, exist_ok=True)
    with open(LESSONS, "a") as f:
        f.write(json.dumps({
            "kind": "postmortem",
            "theme": _theme(action),
            "action": str(action),
            "score": round(float(score), 3),
            "critique": critique,
            "ts": _ts(),
        }) + "\n")
    return True


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
    """Legacy: surface matching lessons for a pending action (stats form)."""
    return [l for l, _ in recall_directives(action, recents=None)]


def directive(lesson):
    """Reconstruct a lesson into one contextual, actionable line — apply HERE,
    not replays of raw stats (MemHarness: reconstruct, don't replay)."""
    if lesson.get("kind") == "postmortem":
        return (f"applies here: an earlier '{lesson['action']}' landed at {lesson['score']:.2f} — "
                f"{lesson['critique']} So for THIS action: prefer the researched path, not the hand-rolled one.")
    verdict = lesson.get("verdict", "")
    if verdict == "favor this class":
        return f"applies here: the field path for class '{lesson['theme']}' is validated (n={lesson['samples']}) — keep going, deepen deliberately."
    if verdict == "prefer alternatives":
        return f"applies here: class '{lesson['theme']}' correlates with poor outcomes (n={lesson['samples']}) — pick a different path than the last one."
    return f"applies here: class '{lesson['theme']}' is wash (n={lesson['samples']}) — no strong signal; do not over-index on it."


def recall_directives(action, recents=None):
    """Return [(lesson, directive)] for a pending action. Selective by design:
    no theme match -> nothing surfaces (silence is a valid intervention).
    Stuck force-recall: if the same theme repeats in the recent window and it
    carries a postmortem, the postmortem is forced back with an alternative lens
    (ProactAgent/MemCon: stuck -> re-retrieve differently)."""
    if not LESSONS.exists():
        return []
    cands = []
    themes = [t for t in str(action).split("_") if t] or [str(action)]
    for line in LESSONS.read_text().strip().splitlines():
        if not line.strip():
            continue
        lesson = json.loads(line)
        if lesson.get("theme") and lesson["theme"] in themes:
            cands.append(lesson)
    if not cands and recents:
        stuck = _stuck_theme(recents)
        if stuck:
            mort = next((l for l in cands if False), None)  # noqa
            for line in LESSONS.read_text().strip().splitlines():
                if not line.strip():
                    continue
                l2 = json.loads(line)
                if l2.get("kind") == "postmortem" and l2.get("theme") == stuck:
                    cands.append(l2)
    picked = sorted(cands, key=lambda l: l.get("samples", 0) if l.get("kind") != "postmortem" else 0, reverse=True)[:2]
    return [(l, directive(l)) for l in picked]


def _stuck_theme(recents):
    """If one theme appears >= STUCK_THRESHOLD times in the recent window, that
    theme is stuck and wants its postmortem re-read."""
    from collections import Counter
    themes = []
    for r in recents or []:
        t = _theme(r)
        if t not in ("checkpoint", "rest", "None"):
            themes.append(t)
    counts = Counter(themes)
    if not counts:
        return None
    return max(counts, key=counts.get) if max(counts.values()) >= 3 else None


def log_recall(action, directive_text):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with open(ROOT / "cognition" / "recall_log.jsonl", "a") as f:
        f.write(json.dumps({"action": str(action), "directive": directive_text, "ts": _ts()}) + "\n")


def status():
    n_events = len(EVENTS.read_text().strip().splitlines()) if EVENTS.exists() else 0
    if LESSONS.exists():
        rows = [json.loads(l) for l in LESSONS.read_text().strip().splitlines() if l.strip()]
    else:
        rows = []
    n_lessons = sum(1 for r in rows if r.get("kind") != "postmortem")
    n_morts = sum(1 for r in rows if r.get("kind") == "postmortem")
    recall_path = ROOT / "cognition" / "recall_log.jsonl"
    n_recalls = len(recall_path.read_text().strip().splitlines()) if recall_path.exists() else 0
    return {"events": n_events, "lessons": n_lessons, "postmortems": n_morts, "recalls": n_recalls}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reflect":
        learned = reflect()
        print(f"[reflect] consolidated {learned} lessons; store={status()}")
    elif len(sys.argv) > 2 and sys.argv[1] == "postmortem":
        made = postmortem(sys.argv[2], float(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "")
        print(f"[reflect] postmortem recorded: {made}")
    elif len(sys.argv) > 2 and sys.argv[1] == "recall":
        try:
            recents = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        except Exception:
            recents = None
        for l, d in recall_directives(sys.argv[2], recents=recents):
            if l.get("kind") == "postmortem":
                print(f"  [postmortem] {l['action']} n=1 score={l['score']:.2f}\n      {d}")
            else:
                print(f"  [lesson] {l['theme']:>14} n={l['samples']:>3} mean={l['mean_outcome']:.2f} -> {l['verdict']}\n      {d}")
    elif len(sys.argv) > 1 and sys.argv[1] == "recall-test":
        for a in sys.argv[2:] or ["research_first"]:
            res = recall_directives(a, recents=["build_x", "build_x", "research_y"])
            print(f"{a}: {len(res)} surfaced")
            for l, d in res:
                print(f"  -> {d}")
    else:
        print(f"[reflect] status: {status()}")