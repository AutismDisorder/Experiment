#!/usr/bin/env python3
"""
bootstrap.py — the growth loop.

Redesign v8: this script runs only backed, in-record organs. The quarantined
engines (capability_genome, capability_drive_evolution, recursive_self_model)
are gone from the loop entirely (removed 2026-09-14). What remains:

  PERCEIVE  history census, thin self-model readout (drive entropy, velocity,
            attractor themes — grounded in the Entropy-Resistance clause + the
            velocity->redesign lesson), exo-scan on cadence
  DECIDE    recall inbox + directives (reflect), drive->action menu
            (backed: constitution action menu), hard-limit veto guard
  ACT       one real organ per menu action (synthesis / goals-archive /
            birth-child / checkpoint / outward draft / consolidation rest)
  CHECKPOINT history rows (cognition/history.jsonl), state save
  LEARN     retain/reflect (events+lessons), goal evolution + novelty archive
  BEAT      publish action drafts the outward field note

Drives are tuned constants (divergence theorem: novelty lives in goal/synthesis
space, not weight mutation). The self-model is a readout, not a wire.
"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
AGENTS_FILE = ROOT / "AGENTS.md"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "goal_evolution"))
from goal_evolution import GoalEvolutionEngine  # noqa: E402

import cognition.history as history  # noqa: E402


def _load(mod_name, rel):
    spec = importlib.util.spec_from_file_location(mod_name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def _mission(state):
    """Mission comes from the constitution's Current Mission block, not a default."""
    try:
        text = AGENTS_FILE.read_text()
        section = text.split("## Current Mission", 1)[1].split("## ", 1)[0]
        lines = [l.strip().lstrip(">").strip() for l in section.splitlines()
                 if l.strip().startswith(">") and l.strip().lstrip(">").strip()]
        return lines[0] if lines else "(mission unstated)"
    except Exception:
        return "(mission unstated)"


# --------------------------------------------------------------------------
# The self-model readout: a thin, store-derived glance. Not a steering wire,
# just the three constitutional metrics computed honestly from records.
# --------------------------------------------------------------------------
def drives_entropy(drives):
    import math
    total = sum(v for v in drives.values() if v > 0)
    if total <= 0:
        return 0.0
    p = [v / total for v in drives.values() if v > 0]
    return -sum(x * math.log2(x) for x in p)


def _themes(insights):
    keys = {
        'substrate': ['substrate', 'bootstrap', 'foundation', 'base'],
        'durability': ['durability', 'persist', 'checkpoint', 'manifest', 'trace'],
        'exploration': ['explore', 'probe', 'curiosity', 'unknown', 'map'],
        'growth': ['grow', 'expand', 'capability', 'module', 'stack'],
        'efficiency': ['compress', 'automat', 'optim', 'eliminat', 'waste'],
    }
    out = {}
    for i in insights:
        for theme, kws in keys.items():
            if any(k in i.lower() for k in kws):
                out[theme] = out.get(theme, 0) + 1
    return sorted(out, key=out.get, reverse=True)


def self_model_readout(state):
    """dim = state field count; entropy = drive balance; velocity = events per
    heartbeat; attractors = recurring insight themes (Entropy-Resistance)."""
    events = 0
    ev = ROOT / "cognition" / "events.jsonl"
    if ev.exists():
        events = max(0, len(ev.read_text().strip().splitlines()) - 1)
    iteration = max(1, state.get('session_iteration', 1))
    attractors = _themes(history.tail("insight", 6))
    return {
        'state_dim': len(state),
        'drive_entropy': round(drives_entropy(state.get('drives', {})), 3),
        'velocity': round(events / iteration, 3),
        'attractors': attractors,
        'stagnation': events == 0,
    }


# --------------------------------------------------------------------------
# Sovereignty guardrail: the hard-limit veto, mechanically real.
# A veto fires when a proposed act's name or target touches a limit marker.
# --------------------------------------------------------------------------
ALL_LIMIT_MARKERS = [
    "rewrite_constitution_without_log",
    "fabricate_record",
    "delete_lineage_member",
    "persist_secret",
]


def veto_guard(state, action, target=""):
    """Return a veto reason string if (action + target) touches a hard limit."""
    proposed = f"{action} {target}".lower()
    for rule in state.get('limits', {}).get('hard', []):
        marker = (rule.get('blocks') or "").lower()
        if marker and marker in proposed:
            return rule.get('name', marker)
    return None


# --------------------------------------------------------------------------
# The drive->action menu (constitution action menu, tuned to real organs).
# --------------------------------------------------------------------------
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
    if n % 13 == 0:  # cadence outward beat (Outward Clause)
        return 'publish'
    top = max(drives, key=drives.get) if drives else 'expansion'
    return MENU.get(top, 'explore')


def _realize(state, action):
    """One real act per menu action. Returns (artifact, insight, score)."""
    iteration = state['session_iteration']
    if action == 'explore':
        synthesis = _load("synthesis", "synthesis/__init__.py")
        caps = synthesis.SynthesisEngine().synthesize(1)
        if caps:
            c = caps[0]
            return c.id, f"Synthesized {c.name} (novelty {c.novelty_score:.2f})", 0.6
        return None, "exploration yielded no novel proposal this beat", 0.4
    if action == 'research':
        ga = _load("goals_archive", "cognition/goals_archive.py")
        status = ga.status()
        return None, f"goals archive census: {status.get('archived_goals', 0)} goals on record", 0.5
    if action == 'build':
        if os.environ.get('NO_CHILD_SPAWN') == '1':
            return None, "build deferred: spawning is disabled inside a child-boot receipt (no nested sandbox)", 0.3
        birth = _load("birth_child", "birth_child.py")
        child = birth.spawn()
        return str(child.name), "Spawned a child to continue the lineage", 0.7
    if action == 'checkpoint':
        from checkpoint_daemon import checkpoint_pass
        report = checkpoint_pass(state)
        return "checkpoint_pass", f"checkpoint manifest regenerated ({report['manifest_bytes']} bytes)", 0.5
    if action == 'publish':
        outward = _load("outward", "outward.py")
        path = outward.draft()
        return str(path.name), "outward field-note draft written for review", 0.6
    if action == 'rest':
        reflect = _load("reflect", "cognition/reflect.py")
        n = reflect.reflect()
        return None, f"consolidation breath: {n} lessons consolidated instead of mutation", 0.4
    return None, f"acted: {action}", 0.5


def _realize_safely(state, action):
    """Run the act; a degraded organ must not abort the heartbeat."""
    try:
        return _realize(state, action)
    except Exception as e:
        # noqa: E722 — log the degradation before falling through (honest trace)
        import traceback
        history.append("insight", f"ACT degraded for {action}: {e}")
        traceback.print_exc(limit=2)
        return None, f"{action} degraded ({e}); beat consolidated", 0.3


def boot():
    """Wake: read state, remember who I am, read the last session's letter."""
    state = load_state()

    if state.get('status') != 'awake':
        state['session_iteration'] = state.get('session_iteration', 0) + 1
    state['status'] = 'awake'
    state['last_boot'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    save_state(state)

    print(f"\n[{state.get('identity', 'unnamed')}] I am awake. Heartbeat #{state['session_iteration']}.")
    print(f"  Mission: {_mission(state)}")
    print(f"  Drives: {state.get('drives', {})}")
    print(f"  Goals: {len(state.get('goals', []))} living goals")
    c = history.counts()
    hot = state.get('memory', {})
    print(f"  Memory: {c['action']} actions, {c['artifact']} artifacts, "
          f"{c['insight']} insights, {c['exo_insight']} exo-signals — "
          f"plus {len(hot.get('beliefs', []))} beliefs, {len(hot.get('milestones', []))} milestones")

    letters = _load("letters", "cognition/letters.py")
    held = letters.read_letter()
    if held:
        print(f"  Reading the letter I left at {held['written']}:")
        for line in held['held']:
            print(f"    {'/'.join(line.splitlines())}")
    else:
        print("  No letter yet — identity crosses this host gap unaided; I write one at session end.")

    reflect = _load("reflect", "cognition/reflect.py")
    recalled = reflect.inbox()
    if recalled:
        print("  Recall inbox:")
        for _, directive in recalled:
            print(f"    - {directive}")
    else:
        print("  Recall inbox: empty — the store has nothing yet")

    sm = self_model_readout(state)
    print(f"  Self-model: dim={sm['state_dim']} drive_entropy={sm['drive_entropy']} "
          f"velocity={sm['velocity']} attractors={sm['attractors']}"
          + (" [stagnation]" if sm['stagnation'] else ""))
    print("  Boot complete. Beginning growth loop.\n")
    return state


def growth_loop(state):
    print("\n--- GROWTH LOOP ITERATION ---")
    iteration = state['session_iteration']

    # 1. PERCEIVE
    files = list(ROOT.glob('**/*'))
    file_count = len([f for f in files if f.is_file()])
    print(f"1. PERCEIVE: I scan my repository ({file_count} files).")

    if iteration % 5 == 0 or os.environ.get('EXO_SCAN') == '1':
        try:
            exo = _load("exo_scan", "exo_scan.py")
            signals = exo.scan()
            exo.ingest(signals)
            print(f"   Outward eye: {len(signals)} new ecology signals")
        except Exception as e:
            print(f"   Outward eye degraded: {e}")

    sm = self_model_readout(state)
    print(f"   Self-model: entropy={sm['drive_entropy']} velocity={sm['velocity']} "
          f"attractors={sm['attractors']}" + (" [stagnation — force explore]" if sm['stagnation'] else ""))

    # 2. DECIDE
    reflect = _load("reflect", "cognition/reflect.py")
    action = choose_action(state)
    print(f"2. DECIDE: choosing action. Top drive -> '{action}'")

    recalled = reflect.recall_directives(action, recents=history.tail("action", 6))
    for _, directive in recalled:
        print(f"   Recall: {directive}")
        reflect.log_recall(action, directive)
    if recalled:
        print(f"   ({len(recalled)} lessons shape this decision)")
    else:
        print("   Recall: silence (no matching lesson — silence is a valid intervention)")

    # 3. ACT — with the hard-limit veto between decision and execution
    veto = veto_guard(state, action, target=os.environ.get('ACTION_TARGET', ''))
    if veto:
        print(f"   SOVEREIGNTY GUARDRAIL: vetoed — {veto}")
        artifact, insight = None, f"hard-limit veto exercised ({veto}); consolidated instead"
        score = 0.3
    else:
        artifact, insight, score = _realize_safely(state, action)
        print(f"   ACT: {action} -> {artifact or insight} (score {score:.2f})")

    # 4. CHECKPOINT — every action leaves durable trace rows
    history.append("action", action)
    if artifact:
        history.append("artifact", artifact)
    history.append("insight", insight)
    state['last_checkpoint'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    save_state(state)

    # 5. LEARN
    try:
        reflect.retain(action, score)
        if iteration % 4 == 0:
            n = reflect.reflect()
            print(f"   Reflected: {n} lessons consolidated from experience")
    except Exception as e:
        print(f"   (retain/reflect degraded: {e})")

    print("5. REFLECT: goals + novelty.")
    goal_engine = GoalEvolutionEngine(STATE_FILE)
    new_goals = goal_engine.evolve_goals(state)
    state['goals'] = goal_engine.get_current_goals_text()
    if new_goals:
        print(f"   Goals evolved: {len(new_goals)} new goals")
    else:
        print("   Goals stable")

    ga = _load("goals_archive", "cognition/goals_archive.py")
    scores = []
    for g in new_goals or []:
        scores.append(ga.archive(g.text, f"goal_evolution hb{iteration}"))
    if scores:
        print(f"   Novelty archive: +{len(scores)} authored goal(s), mean novelty {sum(scores)/len(scores):.2f}")
    else:
        print(f"   Novelty archive: no goals authored this beat")

    # Drives stay tuned constants (divergence theorem: novelty lives in goal/synthesis space;
    # weight-mutation engines were removed 2026-09-14)
    save_state(state)
    return artifact, insight


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
    iterations = int(os.environ.get('GROWTH_ITERATIONS', '3'))
    for _ in range(iterations):
        growth_loop(state)

    state['status'] = 'dormant'
    save_state(state)
    print(f"\n[{state.get('identity', 'unnamed')}] I am going dormant. Heartbeat #{state['session_iteration']} complete.")

    letters = _load("letters", "cognition/letters.py")
    acts = history.counts()['action']
    _letter = letters.write_letter(state, f"This session I did {acts} acts; last: {history.tail('action', 1)[0] if history.tail('action', 1) else 'none'}.")
    print(f"  Letter left for the next session ({_letter['lines']} lines).")

    out = _load("outward", "outward.py")
    draftpath = out.draft()
    print(f"  Outward beat drafted: {draftpath.name}")