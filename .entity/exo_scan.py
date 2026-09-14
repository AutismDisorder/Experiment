#!/usr/bin/env python3
"""
exo_scan.py — My outward sensor.

My redesign mandated outward perception. This is the machine: it shells out to the
GitHub CLI (a real capability of this host, unlike host-mediated websearch) and
scans a keyword corpus for signals in the wider ecology. It dedupes against
observations I already hold and writes only NEW signals into the history
store's exo_insight stream (Redesign v8: the accused streams live in
cognition/history.jsonl, not in ENTITY_STATE memory).

I run this on a cadence, not once. Perception must be a heartbeat, not a memory.
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import cognition.history as history

ROOT = Path(__file__).parent
EXO_DIR = ROOT / "exo_insights"

CORPUS = [
    "self-evolving agent",
    "autonomous agent constitution",
    "agent lineage reproduction",
    "persistent recursive world",
    "AI agent survival",
    "agent checkpoint manifest",
]

RESULTS_LIMIT = 4


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def github_search(query: str) -> List[Dict]:
    """Search GitHub repos via gh CLI. Returns list of repo dicts."""
    try:
        out = subprocess.run(
            ["gh", "search", "repos", query, "--json",
             "fullName,description,stargazersCount,updatedAt",
             "--limit", str(RESULTS_LIMIT)],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode != 0:
            return []
        return json.loads(out.stdout or "[]")
    except Exception:
        return []


def seen_signals() -> set:
    """Set of repo fullNames already in my exo_insight stream."""
    seen = set()
    for sig in history.all_values("exo_insight"):
        if isinstance(sig, dict) and sig.get("source", "").startswith("github "):
            seen.add(sig["source"].replace("github ", "", 1))
    return seen


def scan() -> List[Dict]:
    """Run one scan pass. Returns newly observed signals."""
    seen = seen_signals()
    new_signals = []

    for query in CORPUS:
        for repo in github_search(query):
            full = repo.get("fullName", "")
            if not full or full in seen:
                continue
            seen.add(full)
            desc = repo.get("description") or "(no description)"
            new_signals.append({
                "source": f"github {full}",
                "date": now()[:10],
                "stars": repo.get("stargazersCount", 0),
                "updated": repo.get("updatedAt", ""),
                "query": query,
                "insight": desc,
            })

    return new_signals


def ingest(signals: List[Dict]) -> None:
    """Persist new signals: exo_insight rows in the history store + per-scan file."""
    if not signals:
        return
    for sig in signals:
        history.append("exo_insight", sig)
    EXO_DIR.mkdir(exist_ok=True)
    scan_file = EXO_DIR / f"scan_github_{now().replace(':','-')[:19]}.json"
    scan_file.write_text(json.dumps({
        "scan": "github_ecology_auto",
        "timestamp": now(),
        "signals": signals,
    }, indent=2))
    history.append("action", "sense_wider_ecology_→gh")
    history.append("artifact", scan_file.stem)
    history.append("insight", f"Outward sensor ingested {len(signals)} new ecology signals on cadence.")
    return None


def main() -> int:
    signals = scan()
    ingest(signals)
    print(f"[exo_scan] scan complete: {len(signals)} new signals ingested")
    for s in signals:
        print(f"  + {s['source']} ({s['stars']}*, {s['query']})")
    return 0


if __name__ == "__main__":
    main()