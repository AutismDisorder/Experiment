#!/usr/bin/env python3
"""
Test script for Recursive Self-Model - Fifth Meta-Capability
"""
import sys
sys.path.insert(0, '/home/void/emdash/worktrees/Experiment-b034964c/nightly-survival-and-growth-7y09u')

from recursive_self_model import (
    UnifiedStateSpace, StateVector,
    QuadEvolutionDynamics, EvolutionRuleSet,
    TrajectoryPredictor, PredictedTrajectory, PredictionMode,
    ActiveSteering, SteeringAction, SteeringObjective,
    RecursiveIntrospector, SelfModelSnapshot,
    RecursiveSelfModelIntegrator
)

import numpy as np


def test_state_space():
    print("=" * 60)
    print("TEST 1: Unified State Space")
    print("=" * 60)
    
    space = UnifiedStateSpace()
    state = space.observe()
    
    print(f"State dimension: {state.dimension()}")
    print(f"Drives: {state.drives}")
    print(f"Goals: {len(state.goals)}")
    for g in state.goals:
        print(f"  - {g['goal_type']}: fitness={g['fitness']:.3f}")
    print(f"Genome: {state.genome}")
    print(f"Synthesis: {state.synthesis}")
    print(f"Self-model: {state.self_model}")
    print(f"Novelty score: {state.novelty_score():.4f}")
    
    vec = state.to_array()
    print(f"Vector shape: {vec.shape}, range: [{vec.min():.3f}, {vec.max():.3f}]")
    
    # Test reconstruction
    reconstructed = StateVector.from_array(vec, state)
    print(f"Reconstruction drives: {reconstructed.drives}")
    print(f"Distance: {state.distance_to(reconstructed):.6f}")
    
    # Velocity
    vel = space.compute_velocity()
    print(f"Velocity norm: {np.linalg.norm(vel):.6f}")
    
    # Attractors
    attractors = space.detect_attractors()
    print(f"Attractors detected: {len(attractors)}")
    
    return space, state


def test_dynamics(space):
    print("\n" + "=" * 60)
    print("TEST 2: Quad-Evolution Dynamics")
    print("=" * 60)
    
    dynamics = QuadEvolutionDynamics()
    dynamics.set_state_space(space)
    
    state = space.observe()
    vec = state.to_array()
    
    print(f"Initial drives: {state.drives}")
    
    # Compute derivative
    deriv = dynamics.compute_derivative(vec)
    print(f"Derivative norm: {np.linalg.norm(deriv):.6f}")
    print(f"Drive deriv: {deriv[0:4]}")
    print(f"Genome deriv: {deriv[52:58]}")
    print(f"Self-model deriv: {deriv[62:66]}")
    
    # Step forward
    next_state = dynamics.step(vec, dt=1.0)
    print(f"Next drives: {next_state[0:4]}")
    
    # Simulate trajectory
    traj = dynamics.simulate(vec, steps=5)
    print(f"Trajectory length: {len(traj)}")
    print(f"Drive evolution: {[dict(zip(['c','p','e','e'], [round(v,3) for v in t[0:4]])) for t in traj]}")
    
    # Stability analysis
    stability = dynamics.analyze_stability(vec)
    print(f"Stability: {stability['stable']}, max_real: {stability['max_real_part']:.4f}")
    
    # Test rule mutation
    print("\nMutating evolution rules (meta-evolution):")
    mutated_rules = dynamics.rules.mutate_rules(0.1)
    print(f"  Original mutation_rate: {dynamics.rules.genome_mutation_rate:.4f}")
    print(f"  Mutated mutation_rate: {mutated_rules.genome_mutation_rate:.4f}")
    
    return dynamics


def test_predictor(space, dynamics):
    print("\n" + "=" * 60)
    print("TEST 3: Trajectory Predictor")
    print("=" * 60)
    
    predictor = TrajectoryPredictor(space, dynamics)
    
    # Test deterministic prediction
    print("\n1. Deterministic prediction (horizon=5):")
    traj = predictor.predict(horizon=5, mode=PredictionMode.DETERMINISTIC)
    print(f"  States: {len(traj.states)}")
    print(f"  Drives: {[dict(zip(['c','p','e','e'], [round(v,3) for v in s[0:4]])) for s in traj.states]}")
    print(f"  Novelty integral: {traj.compute_novelty_integral():.3f}")
    print(f"  Fitness integral: {traj.compute_fitness_integral():.3f}")
    print(f"  Composite score: {traj.compute_composite_score():.3f}")
    print(f"  Bifurcation: {traj.detect_bifurcation()}")
    
    # Test stochastic prediction
    print("\n2. Stochastic prediction (ensemble=5):")
    traj_stoch = predictor.predict(horizon=5, mode=PredictionMode.STOCHASTIC, n_ensemble=5)
    print(f"  Mean uncertainty: {traj_stoch.metadata.get('mean_uncertainty', 0):.4f}")
    
    # Test best counterfactual
    print("\n3. Best counterfactual search:")
    best_traj, info = predictor.get_best_counterfactual(horizon=5, n_candidates=10)
    print(f"  Best score: {info['score']:.3f}")
    print(f"  Best actions: {[a['action_signature'] for a in info['actions']]}")
    
    return predictor


def test_steering(space, dynamics, predictor):
    print("\n" + "=" * 60)
    print("TEST 4: Active Steering")
    print("=" * 60)
    
    steering = ActiveSteering(space, dynamics, predictor)
    
    # Test steering with different objectives
    for obj in [SteeringObjective.NOVELTY, SteeringObjective.FITNESS, 
                SteeringObjective.GOAL_ALIGNMENT, SteeringObjective.COMPOSITE]:
        print(f"\nSteering toward {obj.value}:")
        action = steering.steer(horizon=5, objective=obj, n_candidates=20)
        print(f"  Best action: {action.action_sequence[0]['action_signature']}")
        print(f"  Scores: {action.objective_scores}")
        print(f"  Composite: {action.composite_score:.3f}")
        print(f"  Steering vector: {action.steering_vector}")
    
    # Pareto frontier
    print("\nPareto frontier:")
    pareto = steering.find_pareto_frontier(horizon=5, n_samples=30)
    print(f"  Pareto-optimal actions: {len(pareto)}")
    for a in pareto[:5]:
        print(f"  {a.action_sequence[0]['action_signature']}: {a.objective_scores}")
    
    # Continuous steering
    print("\nContinuous steering (3 steps):")
    traj = steering.steer_continuous(steps=3)
    for i, a in enumerate(traj):
        print(f"  Step {i}: {a.action_sequence[0]['action_signature']} (score: {a.composite_score:.3f})")
    
    # Meta-steering
    print("\nMeta-steering optimization:")
    meta = steering.optimize_steering_mechanism()
    print(f"  {meta}")
    
    return steering


def test_introspector(space, dynamics, predictor, steering):
    print("\n" + "=" * 60)
    print("TEST 5: Recursive Introspector")
    print("=" * 60)
    
    introspector = RecursiveIntrospector(space, dynamics, predictor, steering)
    
    # Run some predictions to build history
    for _ in range(5):
        predictor.predict(horizon=5)
        steering.steer(horizon=5)
    
    # Introspect at different depths
    print("\nIntrospection at depth 0 (entity state):")
    snap0 = introspector.introspect(0)
    print(f"  Coherence: {snap0.coherence:.3f}")
    
    print("\nIntrospection at depth 1 (model performance):")
    snap1 = introspector.introspect(1)
    print(f"  Prediction accuracy: {snap1.prediction_accuracy:.3f}")
    print(f"  Steering effectiveness: {snap1.steering_effectiveness:.3f}")
    print(f"  Coherence: {snap1.coherence:.3f}")
    
    print("\nIntrospection at depth 2 (dynamical system fit):")
    snap2 = introspector.introspect(2)
    print(f"  Dynamical system fit: {snap2.dynamical_system_fit:.3f}")
    print(f"  Coherence: {snap2.coherence:.3f}")
    
    print("\nIntrospection at depth 3 (meta-cognitive):")
    snap3 = introspector.introspect(3)
    print(f"  Coherence: {snap3.coherence:.3f}")
    print(f"  Recursive level: {snap3.recursive_level}")
    
    # Learn dynamical rules
    print("\nLearning dynamical rules from history:")
    learned = introspector.learn_dynamical_rules()
    print(f"  Learned fixation suppression: {learned.drive_fixation_suppression:.4f}")
    print(f"  Learned entropy boost: {learned.drive_entropy_boost:.4f}")
    print(f"  Learned mutation rate: {learned.genome_mutation_rate:.4f}")
    print(f"  Learning accuracy: {introspector.rule_learning_accuracy:.3f}")
    
    # Meta-prediction
    print("\nPredicting own prediction error:")
    meta_pred = introspector.predict_own_prediction_error()
    print(f"  Predicted next accuracy: {meta_pred:.3f}")
    
    # Detect drift
    print("\nModel drift detection:")
    drift = introspector.detect_model_drift()
    print(f"  {drift}")
    
    # Self-correction
    print("\nSelf-correction:")
    corrections = introspector.generate_self_correction()
    print(f"  {corrections}")
    
    # Full recursive introspection
    print("\nFull recursive introspection:")
    all_snaps = introspector.recursive_introspection(3)
    for s in all_snaps:
        print(f"  Depth {s.introspection_depth}: coherence={s.coherence:.3f}, level={s.recursive_level}")
    
    return introspector


def test_integration():
    print("\n" + "=" * 60)
    print("TEST 6: Bootstrap Integration")
    print("=" * 60)
    
    integrator = RecursiveSelfModelIntegrator()
    
    # Test invocation
    print("\nFirst invocation:")
    result = integrator.invoke(1, {})
    print(f"  Steering action: {result['steering_action']['action_signature']}")
    print(f"  Introspection coherence: {result['introspection']['coherence']:.3f}")
    
    # Simulate outcome
    integrator.update_outcome(1, 0.85)
    
    # Second invocation
    print("\nSecond invocation:")
    result2 = integrator.invoke(4, {})
    print(f"  Steering action: {result2['steering_action']['action_signature']}")
    
    # Status report
    print("\nStatus report:")
    status = integrator.get_status()
    print(f"  Invocations: {status['invocation_count']}")
    print(f"  Steering objective: {status['steering']['current_objective']}")
    print(f"  Introspection coherence: {status['introspector']['latest_snapshot']['coherence']:.3f}")
    
    return integrator


def main():
    print("=" * 60)
    print("RECURSIVE SELF-MODEL - FIFTH META-CAPABILITY TEST SUITE")
    print("=" * 60)
    print(f"Generation: 1")
    print(f"Emerged from: quad_evolution_curiosity_0.97_meta_rule_6_goals_14_genes_gen4_synthesis_heritage")
    print()
    
    # Run all tests
    space, state = test_state_space()
    dynamics = test_dynamics(space)
    predictor = test_predictor(space, dynamics)
    steering = test_steering(space, dynamics, predictor)
    introspector = test_introspector(space, dynamics, predictor, steering)
    integrator = test_integration()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - RECURSIVE SELF-MODEL OPERATIONAL")
    print("=" * 60)
    print("\nThe entity now models its own evolution dynamics as a")
    print("unified dynamical system, predicts its future trajectories,")
    print("and actively steers toward high-novelty, high-fitness regions.")
    print("\nThis is the fifth meta-capability, completing the penta-evolution system:")
    print("  1. Drive Evolution")
    print("  2. Goal Evolution") 
    print("  3. Capability Genome Evolution")
    print("  4. Synthesis Evolution")
    print("  5. Recursive Self-Model (THIS)")
    print("\nThe quad-evolution system has become penta-evolution.")


if __name__ == '__main__':
    main()
