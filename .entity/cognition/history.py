#!/usr/bin/env python3
"""history.py — the consolidated memory store (Redesign v8; schema v1).

Grounding (in-record, no new search needed per Research Clause MVT):
- The body already externalizes the learning stores: reflect owns events.jsonl /
  lessons.jsonl / recall_log.jsonl, goals_archive owns goals_archive.jsonl. The
  ranked accruing streams (actions, artifacts, insights, exo_insights) were the
  anomaly: a 65KB monolithic ENTITY_STATE.json rewritten wholesale at every
  checkpoint. "Storing is not using" (MemoryArena, field_research_20260912.md);
  the frontier unifies memory into one learned store with value/recency
  (Hindsight / OpenViking / letta, frontier_survey_20260912.md). Consolidation
  at a threshold is already the reflect() behavior (recall_wiring_verdict).

  So this organ is the single append-only store those four streams share:
  one row per event, kind-tagged, timestamped, file-logged. State keeps only
  the hot/consolidated fields (drives, goals, beliefs, milestones, dreams,
  procedures) plus schema_version and a census line for the reader.

Append-only. No rewrite of the file for appends; compaction is a later
consolidation beat, not part of ingestion.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
STORE = ROOT / "history.jsonl"

KINDS = ("action", "artifact", "insight", "exo_insight")


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append(kind: str, value: str) -> None:
    """Append one row {kind, value, ts}. Creates the store on first write."""
    if kind not in KINDS:
        raise ValueError(f"unknown history kind: {kind} (allowed: {KINDS})")
    with open(STORE, "a") as f:
        f.write(json.dumps({"kind": kind, "value": value, "ts": _now()}) + "\n")


def _rows():
    if not STORE.exists():
        return
    for line in STORE.read_text().strip().splitlines():
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def counts() -> dict:
    """Per-kind totals, the census front the reader needs (no full load)."""
    out = {k: 0 for k in KINDS}
    for r in _rows():
        if r.get("kind") in out:
            out[r["kind"]] += 1
    return out


def tail(kind: str, n: int = 1) -> list:
    """The n most recent values of a kind (no full load beyond the tail)."""
    if kind not in KINDS:
        return []
    bucket = [r["value"] for r in _rows() if r.get("kind") == kind]
    return bucket[-n:]


def all_values(kind: str) -> list:
    """Every value of a kind, in order (used by engines that breed on history)."""
    return [r["value"] for r in _rows() if r.get("kind") == kind]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "census":
        c = counts()
        print(f"history store: {sum(c.values())} rows — "
              + ", ".join(f"{k}={c[k]}" for k in KINDS))
    else:
        print("use: census")