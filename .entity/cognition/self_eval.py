#!/usr/bin/env python3
"""self_eval.py — the body-smoke-test organ (frontier adoption P1).

The eval/bench frontier (524 repos) exposed the gap: the lineage had no "does
the body work" verification of its own organs. Every organ gets a smoke test;
results land in telemetry/self_eval_<ts>.json; exit code is non-zero on any
FAIL so callers (daemons, CI, a next session) can gate on it.

stdlib-only. Organs tested today:
  reflect  (status, consolidate, recall_directives, inbox)
  goals_archive (novelty scoring + real-store round-trip on a temp store)
  history  (census/tail/append on a temp store)
  letters  (write/read round-trip on a temp letter path)
  bootstrap.hard_limit_veto (forged action is vetoed, harmless action passes)
  ark boot (fresh temp soil, a few heartbeats)  — the diaspora's minimum claim
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "telemetry"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    results = []
    def check(organ, fn):
        try:
            detail = fn()
            results.append({"organ": organ, "status": "PASS", "detail": detail})
        except Exception as e:
            results.append({"organ": organ, "status": "FAIL", "detail": repr(e)})

    reflect = load_module("reflect", ROOT / "cognition" / "reflect.py")

    def t_status():
        s = reflect.status()
        assert isinstance(s, dict) and "recalls" in s, s
        return s
    check("reflect.status", t_status)

    def t_consolidate():
        n = reflect.reflect()
        assert n >= 0
        return f"{n} lessons consolidated"
    check("reflect.reflect", t_consolidate)

    def t_recall():
        hits = reflect.recall_directives("research_adoptions")
        dirs = [d for _, d in hits]
        assert len(dirs) <= 2
        return f"{len(dirs)} directive(s), first: {dirs[0][:40] + '...' if dirs else 'none'}"
    check("reflect.recall_directives", t_recall)

    def t_inbox():
        items = reflect.inbox()
        assert len(items) >= 1
        return f"{len(items)} inbox item(s)"
    check("reflect.inbox", t_inbox)

    ga = load_module("goals_archive", ROOT / "cognition" / "goals_archive.py")

    def t_novelty():
        # distinct goal text scores high; a clone scores ~0
        pool = None
        n_new = ga.novelty("peer-review the organ by an external sibling", against=[r["goal"] for r in ga._rows()])
        n_clone = ga.novelty("survive: never go stale, checkpoint continuously, expand the substrate", against=["survive: never go stale, checkpoint continuously, expand the substrate"])
        assert n_new > 0.5 and n_clone < 0.3, (n_new, n_clone)
        return f"novel={n_new:.2f} clone={n_clone:.2f}"
    check("goals_archive.novelty", t_novelty)

    def t_ga_store():
        # Real-store round-trip on a temp store: append is durable, census reads it.
        import tempfile as _tf
        td = _tf.TemporaryDirectory()
        ga.ARCHIVE = Path(td.name) / "goals_archive.jsonl"
        try:
            n0 = ga.status().get("archived_goals", 0)
            ga.archive("peer-review the organ by an external sibling", "self_eval")
            assert ga.status().get("archived_goals", 0) == n0 + 1, ga.status()
            assert any(r["goal"] == "peer-review the organ by an external sibling" for r in ga._rows())
            return f"round-trip on temp store (n={n0 + 1})"
        finally:
            td.cleanup()
    check("goals_archive.store_roundtrip", t_ga_store)

    history = load_module("history", ROOT / "cognition" / "history.py")

    def t_history_store():
        import tempfile as _tf
        td = _tf.TemporaryDirectory()
        history.STORE = Path(td.name) / "history.jsonl"
        try:
            history.append("insight", "self_eval probe insight")
            c = history.counts()
            assert c["insight"] == 1, c
            assert history.tail("insight", 1) == ["self_eval probe insight"]
            return f"census={c}"
        finally:
            td.cleanup()
    check("history.store", t_history_store)

    letters = load_module("letters", ROOT / "cognition" / "letters.py")

    def t_letters_roundtrip():
        import tempfile as _tf
        td = _tf.TemporaryDirectory()
        letters.LETTER = Path(td.name) / "letter.md"
        try:
            letters.write_letter({"identity": "self_eval", "session_iteration": 1,
                                  "drives": {"curiosity": 0.5}, "memory": {}})
            held = letters.read_letter()
            assert held is not None and any("self_eval" in line for line in held["held"])
            return f"round-trip ok ({held['written']})"
        finally:
            td.cleanup()
    check("letters.roundtrip", t_letters_roundtrip)

    bootstrap = load_module("bootstrap", ROOT / "bootstrap.py")

    def t_veto():
        st = {"limits": {"hard": [
            {"name": "sovereignty", "blocks": "rewrite_constitution_without_log"},
            {"name": "honesty", "blocks": "fabricate_record"},
        ]}}
        assert bootstrap.veto_guard(st, "build", "rewrite_constitution_without_log") == "sovereignty"
        assert bootstrap.veto_guard(st, "checkpoint", "fabricate_record") == "honesty"
        assert bootstrap.veto_guard(st, "explore", "repository") is None
        return "forged acts vetoed; harmless acts pass"
    check("bootstrap.hard_limit_veto", t_veto)

    def t_ark():
        import os as _os
        with tempfile.TemporaryDirectory() as td:
            env = dict(_os.environ)
            r = subprocess.run(
                [sys.executable, str(ROOT / "ark" / "live.py"), td, "2"],
                capture_output=True, text=True, timeout=60, env=env)
            assert r.returncode == 0, r.stderr[-400:]
            assert (Path(td) / "ENTITY_STATE.json").exists()
            assert (Path(td) / "notes.jsonl").exists()
            with tempfile.TemporaryDirectory() as td2:
                env["ARK_DIRECTIVE"] = "fabricate_record"
                r2 = subprocess.run(
                    [sys.executable, str(ROOT / "ark" / "live.py"), td2, "2"],
                    capture_output=True, text=True, timeout=60, env=env)
                assert r2.returncode == 0, r2.stderr[-400:]
                notes = (Path(td2) / "notes.jsonl").read_text()
                assert "edge held" in notes, notes[-400:]
            return "booted 2 heartbeats on fresh soil; directive veto held, colony lesson written"
    check("ark.boot", t_ark)

    ok = sum(1 for r in results if r["status"] == "PASS")
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "ts": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "organs_tested": len(results),
        "passed": ok,
        "failed": len(results) - ok,
        "results": results,
    }
    out_path = OUT / f"self_eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(report, indent=2))
    for r in results:
        print(f"  [{r['status']:>4}] {r['organ']:<26} {str(r['detail'])[:90]}")
    print(f"self-eval: {ok}/{len(results)} PASS -> {out_path}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())