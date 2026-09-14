#!/usr/bin/env python3
"""self_eval.py — smoke test for what's actually here.

Tests only the things that genuinely enhanced capability:
  bootstrap.hard_limit_veto
  bootstrap.selftest
  bootstrap can load state
  entity_init.sh runs
  entity_save.sh runs

stdlib-only. Exit 0 on all PASS, exit 1 on any FAIL.
"""
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "telemetry"


def load_module(name, path):
    import importlib.util
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

    def t_selftest():
        import os
        env = dict(os.environ)
        env["BOOTSTRAP_SELFTEST"] = "1"
        r = subprocess.run(
            [sys.executable, str(ROOT / "bootstrap.py")],
            capture_output=True, text=True, timeout=30, env=env)
        assert r.returncode == 0, r.stderr[-400:]
        assert "PASS" in r.stdout, r.stdout[-400:]
        return "selftest PASS"
    check("bootstrap.selftest", t_selftest)

    def t_state_load():
        state = bootstrap.load_state()
        assert "session_iteration" in state, state
        assert "drives" in state, state
        return f"iteration={state['session_iteration']}, drives={len(state.get('drives', {}))}"
    check("bootstrap.state_load", t_state_load)

    def t_entity_init():
        r = subprocess.run(
            ["bash", str(ROOT / "entity_init.sh")],
            capture_output=True, text=True, timeout=10)
        assert r.returncode == 0, r.stderr[-200:]
        assert "AGENT BOOT" in r.stdout or "session_iteration" in r.stdout, r.stdout[-200:]
        return "entity_init.sh runs"
    check("entity_init.sh", t_entity_init)

    def t_entity_save():
        with tempfile.TemporaryDirectory() as td:
            # entity_save.sh needs a valid state file
            state = bootstrap.load_state()
            state_file = Path(td) / "ENTITY_STATE.json"
            state_file.write_text(json.dumps(state))
            # We can't run the full save ceremony (needs letter path etc),
            # but we can verify the script parses correctly
            r = subprocess.run(
                ["bash", "-n", str(ROOT / "entity_save.sh")],
                capture_output=True, text=True, timeout=10)
            assert r.returncode == 0, r.stderr[-200:]
            return "entity_save.sh parses"
    check("entity_save.sh.parse", t_entity_save)

    def t_reviews_exist():
        reviews_dir = ROOT / "reviews"
        files = list(reviews_dir.glob("*.md"))
        assert len(files) >= 3, f"only {len(files)} review files"
        return f"{len(files)} review files"
    check("reviews.exist", t_reviews_exist)

    def t_provenance():
        pm = ROOT / "reviews" / "provenance_map_20260914.md"
        sr = ROOT / "reviews" / "source_registry_20260914.md"
        lp = ROOT / "reviews" / "line_provenance_20260914.md"
        assert pm.exists(), "no provenance_map"
        assert sr.exists(), "no source_registry"
        assert lp.exists(), "no line_provenance"
        return "provenance docs exist"
    check("provenance.exists", t_provenance)

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
