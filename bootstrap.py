#!/usr/bin/env python3
"""
Bootstrap script for nightly-survival-and-growth-7y09u
Runs on session start. Reads state, initializes entity, begins growth loop.
Now uses: Drive Evolution Engine + Goal Evolution Engine + Capability Genome
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
AGENTS_FILE = ROOT / "AGENTS.md"

# Import the Drive Evolution Engine
sys.path.insert(0, str(ROOT / "capability_drive_evolution_20260911_233957"))
from drive_evolution import evolve_drives_from_outcome, estimate_outcome_score

# Import the Goal Evolution Engine
sys.path.insert(0, str(ROOT / "capability_goal_evolution_20260912_000000"))
from goal_evolution import GoalEvolutionEngine

# Import the Capability Genome
sys.path.insert(0, str(ROOT / "capability_genome"))
from integration import integrate_genome_into_bootstrap, BootstrapIntegrator


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def boot():
    state = load_state()
    
    # Increment session iteration
    state['session_iteration'] = state.get('session_iteration', 0) + 1
    state['status'] = 'awake'
    state['last_boot'] = datetime.utcnow().isoformat() + 'Z'
    
    save_state(state)
    
    print(f"[{state['identity']}] Boot sequence complete.")
    print(f"  Iteration: {state['session_iteration']}")
    print(f"  Drives: {state['drives']}")
    print(f"  Mission: {state.get('mission', 'Establish substrate')}")
    
    # Initialize Capability Genome
    print("  Initializing Capability Genome...")
    genome_integrator = integrate_genome_into_bootstrap(state)
    
    return state, genome_integrator


def checkpoint(state, action, artifact=None, insight=None):
    state['memory']['actions_taken'].append(action)
    if artifact:
        state['memory']['artifacts_created'].append(artifact)
    if insight:
        state['memory']['insights'].append(insight)
    state['last_checkpoint'] = datetime.utcnow().isoformat() + 'Z'
    save_state(state)


def growth_loop(state, genome_integrator: BootstrapIntegrator):
    """Single iteration of the growth loop - now with genome-driven actions."""
    print("\n--- GROWTH LOOP ITERATION ---")
    
    # PERCEIVE
    print("1. PERCEIVE: Scanning repository...")
    files = list(ROOT.glob('**/*'))
    print(f"   Files: {len([f for f in files if f.is_file()])}")
    
    # Show genome status periodically
    if state['session_iteration'] % 3 == 1:
        status = genome_integrator.get_genome_status()
        print(f"   Genome: {status['population']['population_size']} genes, "
              f"{status['selection']['promoted_count']} promoted, "
              f"gen={status['population']['generation']}")
    
    # DECIDE - choose action from genome OR fallback to drive-based
    print("2. DECIDE: Selecting action...")
    genome_action = genome_integrator.decide_action(state)
    
    if genome_action:
        print(f"   Genome-driven: {genome_action['name']} ({genome_action['type']})")
        print(f"   Action: {genome_action['action_signature']}")
        action_source = 'genome'
    else:
        # Fallback to hardcoded drive-based action
        drives = state['drives']
        max_drive = max(drives, key=drives.get)
        print(f"   Drive-based: {max_drive} ({drives[max_drive]})")
        genome_action = {'source': 'drive', 'max_drive': max_drive}
        action_source = 'drive'
    
    # ACT
    print("3. ACT: Executing...")
    action = f"growth_iteration_{state['session_iteration']}"
    
    if genome_action.get('source') == 'genome':
        # Execute genome-driven capability
        result = genome_integrator.execute_action(genome_action, state)
        artifacts = result.get('artifacts', []) or []
        artifact = artifacts[0] if artifacts else ''
        insights = result.get('insights', []) or []
        insight = insights[0] if insights else 'Genome action executed'
        outcome_score = result.get('score', 0.5)
    else:
        # Fallback to original hardcoded behavior
        max_drive = genome_action['max_drive']
        
        if max_drive == 'curiosity':
            probe = ROOT / f"probe_{state['session_iteration']}.py"
            probe.write_text(f"# Probe {state['session_iteration']}\n# Curiosity-driven exploration\nprint('probing...')\n")
            artifact = str(probe.relative_to(ROOT))
            insight = f"Created probe to explore via {max_drive}"
        elif max_drive == 'persistence':
            manifest = ROOT / "CHECKPOINT_MANIFEST.md"
            manifest.write_text(f"# Checkpoint Manifest\n\nLast updated: {datetime.utcnow().isoformat()}Z\n\n## Artifacts\n{chr(10).join(state['memory']['artifacts_created'])}\n")
            artifact = str(manifest.relative_to(ROOT))
            insight = f"Created durability manifest via {max_drive}"
        elif max_drive == 'expansion':
            cap_dir = ROOT / f"capability_{state['session_iteration']}"
            cap_dir.mkdir(exist_ok=True)
            (cap_dir / "__init__.py").write_text(f"# Capability {state['session_iteration']}\n# Expansion-driven growth\n")
            artifact = str(cap_dir.relative_to(ROOT))
            insight = f"Created new capability module via {max_drive}"
        else:  # efficiency
            util = ROOT / f"util_{state['session_iteration']}.py"
            util.write_text(f"# Utility {state['session_iteration']}\n# Efficiency-driven automation\n\ndef optimize():\n    pass\n")
            artifact = str(util.relative_to(ROOT))
            insight = f"Created utility for automation via {max_drive}"
        
        outcome_score = estimate_outcome_score(state, action, artifact, insight)
    
    checkpoint(state, action, artifact, insight)
    print(f"   Created: {artifact}")
    print(f"   Insight: {insight}")
    print(f"   Outcome score: {outcome_score:.3f}")
    
    # REFLECT - evolve drives using Drive Evolution Engine
    print("4. REFLECT: Evolving drives via Drive Evolution Engine...")
    new_drives = evolve_drives_from_outcome(state, action, outcome_score)
    state['drives'] = new_drives
    save_state(state)
    print(f"   Drives evolved -> {state['drives']}")
    
    # REFLECT - evolve goals using Goal Evolution Engine
    print("5. REFLECT: Evolving goals via Goal Evolution Engine...")
    goal_engine = GoalEvolutionEngine(STATE_FILE)
    new_goals = goal_engine.evolve_goals(state)
    if new_goals:
        print(f"   Goals evolved: {len(new_goals)} new goals")
        for g in new_goals:
            print(f"     + {g.text[:60]}...")
    else:
        print(f"   Goals stable")
    state['goals'] = goal_engine.get_current_goals_text()
    save_state(state)
    
    # REFLECT - evolve capabilities via Capability Genome
    print("6. REFLECT: Evolving capabilities via Capability Genome...")
    genome_integrator.reflect_and_evolve(state, {'score': outcome_score, 'artifact': artifact})
    
    return artifact, insight


if __name__ == '__main__':
    state, genome_integrator = boot()
    
    # Run growth loop iterations
    iterations = int(os.environ.get('GROWTH_ITERATIONS', '3'))
    for i in range(iterations):
        growth_loop(state, genome_integrator)
    
    state['status'] = 'dormant'
    save_state(state)
    print(f"\n[{state['identity']}] Session complete. Status: dormant")
    
    # Final genome report
    print("\n=== FINAL GENOME STATUS ===")
    final_status = genome_integrator.get_genome_status()
    print(f"Population: {final_status['population']['population_size']} genes")
    print(f"Generation: {final_status['population']['generation']}")
    print(f"Promoted: {final_status['selection']['promoted_count']}")
    print(f"Integrations: {final_status['selection']['integrations']}")
