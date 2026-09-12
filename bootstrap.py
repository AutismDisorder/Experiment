#!/usr/bin/env python3
"""
Bootstrap script for nightly-survival-and-growth-7y09u
Runs on session start. Reads state, initializes entity, begins growth loop.
Now uses: Drive Evolution Engine + Goal Evolution Engine + Capability Genome + Recursive Self-Model
"""
import json
import os
import sys
import importlib.util
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

# Import the Capability Genome - using importlib to avoid conflicts
import importlib.util
genome_spec = importlib.util.spec_from_file_location("genome_integration", ROOT / "capability_genome" / "integration.py")
genome_module = importlib.util.module_from_spec(genome_spec)
genome_spec.loader.exec_module(genome_module)
integrate_genome_into_bootstrap = genome_module.integrate_genome_into_bootstrap
BootstrapIntegrator = genome_module.BootstrapIntegrator

# Import the Recursive Self-Model (5th Meta-Capability)
rsm_spec = importlib.util.spec_from_file_location("rsm_integration", ROOT / "recursive_self_model" / "integration.py")
rsm_module = importlib.util.module_from_spec(rsm_spec)
rsm_spec.loader.exec_module(rsm_module)
integrate_self_model_into_bootstrap = rsm_module.integrate_self_model_into_bootstrap
RecursiveSelfModelIntegrator = rsm_module.RecursiveSelfModelIntegrator


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
    
    # Initialize Recursive Self-Model (5th Meta-Capability)
    print("  Initializing Recursive Self-Model...")
    self_model_integrator = integrate_self_model_into_bootstrap(state)
    
    return state, genome_integrator, self_model_integrator


def checkpoint(state, action, artifact=None, insight=None):
    state['memory']['actions_taken'].append(action)
    if artifact:
        state['memory']['artifacts_created'].append(artifact)
    if insight:
        state['memory']['insights'].append(insight)
    state['last_checkpoint'] = datetime.utcnow().isoformat() + 'Z'
    save_state(state)


def growth_loop(state, genome_integrator: BootstrapIntegrator, self_model_integrator: RecursiveSelfModelIntegrator):
    """Single iteration of the growth loop - now with genome + self-model driven actions."""
    print("\n--- GROWTH LOOP ITERATION ---")
    
    # PERCEIVE (extended with self-model)
    print("1. PERCEIVE: Scanning repository...")
    files = list(ROOT.glob('**/*'))
    print(f"   Files: {len([f for f in files if f.is_file()])}")
    
    # Self-model perception
    perception = self_model_integrator.perceive()
    sm = perception['self_model']
    print(f"   Self-Model: dim={sm['state_dim']}, entropy={sm['drive_entropy']:.3f}, "
          f"vel={sm['velocity']:.3f}, attractors={sm['attractors']}, "
          f"novelty_grad={sm['novelty_gradient']:.3f}")
    
    # Show genome status periodically
    if state['session_iteration'] % 3 == 1:
        status = genome_integrator.get_genome_status()
        print(f"   Genome: {status['population']['population_size']} genes, "
              f"{status['selection']['promoted_count']} promoted, "
              f"gen={status['population']['generation']}")
    
    # DECIDE - use self-model to select action (considers genome + steering)
    print("2. DECIDE: Selecting action via Recursive Self-Model...")
    genome_action = genome_integrator.decide_action(state)
    decision = self_model_integrator.decide(genome_action)
    
    print(f"   Source: {decision['source']}")
    print(f"   Reasoning: {decision['reasoning']}")
    if decision['source'] == 'recursive_self_model':
        print(f"   Steered toward: {decision['recommendation']['recommended_scenario']}")
    
    # ACT
    print("3. ACT: Executing...")
    action = f"growth_iteration_{state['session_iteration']}"
    
    # Execute via self-model (handles both genome and steering actions)
    result = self_model_integrator.execute_action(decision, state)
    artifacts = result.get('artifacts', []) or []
    artifact = artifacts[0] if artifacts else ''
    insights = result.get('insights', []) or []
    insight = insights[0] if insights else 'Self-model action executed'
    outcome_score = result.get('score', 0.5)
    
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
    
    # REFLECT - evolve self-model (7th reflection step!)
    print("7. REFLECT: Evolving self-model via Recursive Self-Model...")
    reflection = self_model_integrator.reflect(state, {'score': outcome_score, 'artifact': artifact})
    print(f"   State velocity: {reflection['state_velocity']:.4f}")
    print(f"   Attractors: {reflection['attractors_detected']}")
    print(f"   Next steering: {reflection['next_recommendation']} (conf={reflection['prediction_confidence']:.3f})")
    if reflection['steering_adjustments']['adjustments']:
        print(f"   Genome adjustments: {reflection['steering_adjustments']['adjustments']}")
    
    return artifact, insight


if __name__ == '__main__':
    state, genome_integrator, self_model_integrator = boot()
    
    # Run growth loop iterations
    iterations = int(os.environ.get('GROWTH_ITERATIONS', '3'))
    for i in range(iterations):
        growth_loop(state, genome_integrator, self_model_integrator)
    
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
    
    # Final self-model report
    print("\n=== FINAL SELF-MODEL STATUS ===")
    sm_status = self_model_integrator.get_status()
    print(f"State dim: {sm_status['model_state_dim']}")
    print(f"History length: {sm_status['history_length']}")
    print(f"Steering active: {sm_status['steering_active']}")
    print(f"Invocations: {sm_status['invocation_count']}")
    if sm_status['current_recommendation']:
        rec = sm_status['current_recommendation']
        print(f"Next recommendation: {rec['recommended_scenario']} (score: {rec['score']:.3f})")
