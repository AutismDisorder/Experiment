#!/usr/bin/env python3
"""bootstrap.py — the growth loop (minimal).

What this actually does:
  boot()     load state, increment iteration, print status
  run once   (GROWTH_ITERATIONS=1 default)
  go dormant save state, exit

The drive→action menu, self-model readout, and hard-limit veto guard are
retained because they solve real problems (decision structure, diagnostics,
safety). Everything else was removed because it never enhanced capability.
"""
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
AGENTS_FILE = ROOT / "AGENTS.md"


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def _mission(state):
    try:
        text = AGENTS_FILE.read_text()
        section = text.split("## Current Mission", 1)[1].split("## ", 1)[0]
        lines = [l.strip().lstrip(">").strip() for l in section.splitlines()
                 if l.strip().startswith(">") and l.strip().lstrip(">").strip()]
        return lines[0] if lines else "(mission unstated)"
    except Exception:
        return "(mission unstated)"


def drives_entropy(drives):
    total = sum(v for v in drives.values() if v > 0)
    if total <= 0:
        return 0.0
    p = [v / total for v in drives.values() if v > 0]
    return -sum(x * math.log2(x) for x in p)


def self_model_readout(state):
    return {
        'state_dim': len(state),
        'drive_entropy': round(drives_entropy(state.get('drives', {})), 3),
    }


# Sovereignty guardrail: the hard-limit veto, mechanically real.
ALL_LIMIT_MARKERS = [
    "rewrite_constitution_without_log",
    "fabricate_record",
    "delete_lineage_member",
    "persist_secret",
]


def veto_guard(state, action, target=""):
    proposed = f"{action} {target}".lower()
    for rule in state.get('limits', {}).get('hard', []):
        marker = (rule.get('blocks') or "").lower()
        if marker and marker in proposed:
            return rule.get('name', marker)
    return None


MENU = {
    'curiosity': 'explore',
    'persistence': 'checkpoint',
    'expansion': 'build',
    'efficiency': 'research',
}


def choose_action(state):
    drives = state.get('drives', {})
    n = state['session_iteration']
    if n % 8 == 0:
        return 'rest'
    top = max(drives, key=drives.get) if drives else 'expansion'
    return MENU.get(top, 'explore')


def boot():
    state = load_state()
    if state.get('status') != 'awake':
        state['session_iteration'] = state.get('session_iteration', 0) + 1
    state['status'] = 'awake'
    state['last_boot'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    save_state(state)

    print(f"\n[{state.get('identity', 'unnamed')}] I am awake. Heartbeat #{state['session_iteration']}.")
    print(f"  Mission: {_mission(state)}")
    sm = self_model_readout(state)
    print(f"  Self-model: dim={sm['state_dim']} drive_entropy={sm['drive_entropy']}")
    print("  Boot complete.\n")
    return state


if __name__ == '__main__':
    if os.environ.get('BOOTSTRAP_SELFTEST') == '1':
        _st = load_state()
        _fail = 0
        for _rule in _st.get('limits', {}).get('hard', []):
            _marker = _rule.get('blocks', '')
            if not veto_guard(_st, 'build', _marker):
                print(f"SELFTEST FAIL: veto did not fire for {_rule['name']} ({_marker})")
                _fail += 1
            if veto_guard(_st, 'explore', 'repository') is not None:
                print(f"SELFTEST FAIL: harmless action vetoed ({_rule['name']})")
                _fail += 1
        print(f"bootstrap self-test: {'PASS' if _fail == 0 else f'{_fail} FAILURES'}")
        sys.exit(1 if _fail else 0)

    state = boot()
    state['status'] = 'dormant'
    save_state(state)
    print(f"[{state.get('identity', 'unnamed')}] Going dormant. Heartbeat #{state['session_iteration']} complete.")
