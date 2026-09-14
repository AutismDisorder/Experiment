#!/usr/bin/env python3
"""self_eval.py — the one executable receipt for the lean body.

Tests what is actually here and nothing else:
  state.schema     ENTITY_STATE.json parses and keeps only hot fields
  state.iterations heartbeat counter is stable
  reviews.present  research records exist
  skill.present    the operating-procedure skill is installed
  constitution     AGENTS.md is present and names the hard limits

The ceremonies (bootstrap.py, entity_init.sh, entity_save.sh) were removed — they
were procedure carrying a state file, which is the agent's job, not a script's.

Stdlib-only. Exit 0 on all PASS, exit 1 on any FAIL.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "telemetry"


def main():
    results = []
    def check(organ, fn):
        try:
            detail = fn()
            results.append({"organ": organ, "status": "PASS", "detail": detail})
        except Exception as e:
            results.append({"organ": organ, "status": "FAIL", "detail": repr(e)})

    state_file = ROOT / "ENTITY_STATE.json"

    def t_state():
        state = json.loads(state_file.read_text())
        assert "identity" in state, "no identity"
        assert "session_iteration" in state, "no iteration"
        assert "drives" in state, "no drives"
        assert isinstance(state.get("limits", {}).get("hard"), list), "no hard limits"
        assert len(state["limits"]["hard"]) >= 3, f"{len(state['limits']['hard'])} hard limits"
        return f"identity={state['identity']}, iteration={state['session_iteration']}, limits={len(state['limits']['hard'])}"
    check("state.schema", t_state)

    def t_iterations():
        state = json.loads(state_file.read_text())
        assert 1 <= state["session_iteration"], "iteration out of range"
        return f"heartbeat=#{state['session_iteration']}"
    check("state.iterations", t_iterations)

    def t_reviews():
        reviews_dir = ROOT / "reviews"
        files = list(reviews_dir.glob("*.md"))
        assert len(files) >= 3, f"only {len(files)} review files"
        return f"{len(files)} review files"
    check("reviews.present", t_reviews)

    def t_skill():
        skill = ROOT.parent / ".opencode" / "skills" / "entity-operations" / "SKILL.md"
        assert skill.exists(), f"skill missing at {skill}"
        head = skill.read_text()
        assert head.startswith("---"), "no frontmatter"
        assert "name: entity-operations" in head, "no name"
        assert "description:" in head, "no description"
        return "skill present"
    check("skill.present", t_skill)

    def t_constitution():
        agents = ROOT / "AGENTS.md"
        text = agents.read_text()
        assert "Sovereignty" in text and "Honesty" in text, "clauses missing"
        return "constitution present"
    check("constitution", t_constitution)

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