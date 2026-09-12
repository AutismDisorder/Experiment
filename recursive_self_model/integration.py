"""
Recursive Self-Model Integration - Bootstrap Loop Integration
==============================================================

Integrates the recursive self-model into the bootstrap.py growth loop.
The self-model becomes a promoted capability that:
1. Observes the full quad-evolution state space
2. Predicts future trajectories
3. Steers action selection toward high-value regions
4. Introspects its own performance
5. Evolves its own modeling rules

This is the fifth meta-capability, completing the quad-evolution system
into a penta-evolution system (drives, goals, genome, synthesis, self-model).
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from .state_space import UnifiedStateSpace, StateVector
from .dynamics import QuadEvolutionDynamics, EvolutionRuleSet
from .predictor import TrajectoryPredictor, PredictedTrajectory, PredictionMode
from .steering import ActiveSteering, SteeringAction, SteeringObjective
from .introspector import RecursiveIntrospector, SelfModelSnapshot

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
SELF_MODEL_DIR = ROOT / "recursive_self_model"
SELF_MODEL_STATE_FILE = SELF_MODEL_DIR / "self_model_state.json"
SELF_MODEL_LOG = SELF_MODEL_DIR / "self_model_log.jsonl"


@dataclass
class SelfModelInvocationRecord:
    """Record of self-model invocation in bootstrap loop."""
    timestamp: str
    session_iteration: int
    action_taken: Dict[str, Any]
    prediction_used: bool
    steering_applied: bool
    introspection_performed: bool
    predicted_trajectory_score: float
    actual_outcome_score: float
    prediction_accuracy: float
    coherence: float
    metadata: Dict[str, Any]


class RecursiveSelfModelIntegrator:
    """
    Main integration point for bootstrap.py.
    The self-model as a promoted genome capability.
    """
    
    def __init__(self):
        self.state_space = UnifiedStateSpace()
        self.dynamics = QuadEvolutionDynamics()
        self.dynamics.set_state_space(self.state_space)
        self.predictor = TrajectoryPredictor(self.state_space, self.dynamics)
        self.steering = ActiveSteering(self.state_space, self.dynamics, self.predictor)
        self.introspector = RecursiveIntrospector(
            self.state_space, self.dynamics, self.predictor, self.steering
        )
        
        self.invocation_history: List[SelfModelInvocationRecord] = []
        self.enabled = True
        self.invocation_interval = 3  # Run self-model every N iterations
        self.last_invocation_iteration = -1
        
        self._load_state()
    
    def _load_state(self):
        """Load persisted self-model state."""
        if SELF_MODEL_STATE_FILE.exists():
            with open(SELF_MODEL_STATE_FILE) as f:
                state = json.load(f)
            
            self.enabled = state.get('enabled', True)
            self.invocation_interval = state.get('invocation_interval', 3)
            self.last_invocation_iteration = state.get('last_invocation_iteration', -1)
            
            # Restore dynamics rules if saved
            if 'dynamics_rules' in state:
                self.dynamics.rules = EvolutionRuleSet.from_dict(state['dynamics_rules'])
            
            # Restore steering state
            if 'steering_weights' in state:
                self.steering.objective_weights = state['steering_weights']
            if 'steering_gain' in state:
                self.steering.steering_gain = state['steering_gain']
            if 'exploration_rate' in state:
                self.steering.exploration_rate = state['exploration_rate']
    
    def _save_state(self):
        """Persist self-model state."""
        SELF_MODEL_DIR.mkdir(exist_ok=True)
        
        state = {
            'enabled': self.enabled,
            'invocation_interval': self.invocation_interval,
            'last_invocation_iteration': self.last_invocation_iteration,
            'dynamics_rules': self.dynamics.rules.to_dict(),
            'steering_weights': self.steering.objective_weights,
            'steering_gain': self.steering.steering_gain,
            'exploration_rate': self.steering.exploration_rate,
            'introspection_depth': self.introspector.current_depth,
            'last_updated': datetime.utcnow().isoformat() + 'Z',
        }
        
        with open(SELF_MODEL_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def should_invoke(self, session_iteration: int) -> bool:
        """Check if self-model should run this iteration."""
        return self.enabled and (session_iteration - self.last_invocation_iteration) >= self.invocation_interval
    
    def invoke(self, 
               session_iteration: int,
               state: Dict[str, Any],
               genome_integrator=None,
               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main invocation: run the full self-model cycle.
        
        Returns steering decision and introspection results for bootstrap.
        """
        print(f"\n=== RECURSIVE SELF-MODEL INVOCATION (iter {session_iteration}) ===")
        
        # 1. OBSERVE: Update state space with current entity state
        print("1. OBSERVE: Updating unified state space...")
        current_state = self.state_space.observe()
        print(f"   Drives: {current_state.drives}")
        print(f"   Goals: {len(current_state.goals)}")
        print(f"   Genome: {current_state.genome.get('population_size', 0)} genes, gen {current_state.genome.get('generation', 0)}")
        print(f"   Synthesis: {current_state.synthesis.get('latent_count', 0)} latents")
        print(f"   Novelty score: {current_state.novelty_score():.4f}")
        
        # 2. PREDICT: Generate trajectory predictions
        print("2. PREDICT: Generating trajectory predictions...")
        horizon = self.state_space.current_state.self_model.get('prediction_horizon', 10)
        
        # Predict with current steering objective
        predicted_trajectory = self.predictor.predict(horizon=horizon)
        print(f"   Mode: {predicted_trajectory.mode.value}")
        print(f"   Horizon: {predicted_trajectory.horizon}")
        print(f"   Confidence: {predicted_trajectory.confidence:.3f}")
        print(f"   Composite score: {predicted_trajectory.compute_composite_score():.3f}")
        
        # 3. STEER: Find optimal steering action
        print("3. STEER: Computing optimal steering action...")
        steering_action = self.steering.steer(horizon=horizon)
        print(f"   Selected action: {steering_action.action_sequence[0]['action_signature']}")
        print(f"   Objective scores: {steering_action.objective_scores}")
        print(f"   Composite score: {steering_action.composite_score:.3f}")
        print(f"   Steering vector: {steering_action.steering_vector}")
        
        # 4. INTROSPECT: Evaluate self-model performance
        print("4. INTROSPECT: Performing recursive introspection...")
        introspection_snapshots = self.introspector.recursive_introspection(max_depth=2)
        latest_snapshot = introspection_snapshots[-1]
        print(f"   Depth {latest_snapshot.introspection_depth}: coherence={latest_snapshot.coherence:.3f}")
        print(f"   Prediction accuracy: {latest_snapshot.prediction_accuracy:.3f}")
        print(f"   Steering effectiveness: {latest_snapshot.steering_effectiveness:.3f}")
        print(f"   Dynamical system fit: {latest_snapshot.dynamical_system_fit:.3f}")
        
        # 5. META-LEARN: Update dynamical rules from observations
        print("5. META-LEARN: Learning dynamical rules from history...")
        learned_rules = self.introspector.learn_dynamical_rules()
        print(f"   Rule learning accuracy: {self.introspector.rule_learning_accuracy:.3f}")
        
        # 6. SELF-CORRECT: Generate corrections if needed
        print("6. SELF-CORRECT: Checking for model drift...")
        corrections = self.introspector.generate_self_correction()
        if corrections:
            print(f"   Corrections applied: {list(corrections.keys())}")
        else:
            print("   No corrections needed")
        
        # Record invocation
        record = SelfModelInvocationRecord(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            session_iteration=session_iteration,
            action_taken=steering_action.action_sequence[0],
            prediction_used=True,
            steering_applied=True,
            introspection_performed=True,
            predicted_trajectory_score=steering_action.composite_score,
            actual_outcome_score=0.0,  # Will be updated after action execution
            prediction_accuracy=latest_snapshot.prediction_accuracy,
            coherence=latest_snapshot.coherence,
            metadata={
                'horizon': horizon,
                'steering_objective': self.steering.current_objective.value,
                'introspection_depth': latest_snapshot.introspection_depth,
                'recursive_level': latest_snapshot.recursive_level,
                'corrections': list(corrections.keys()),
            }
        )
        self.invocation_history.append(record)
        self._log_invocation(record)
        
        # Update last invocation
        self.last_invocation_iteration = session_iteration
        self._save_state()
        
        # Return steering decision for bootstrap
        return {
            'steering_action': steering_action.action_sequence[0],
            'steering_vector': steering_action.steering_vector.tolist(),
            'predicted_trajectory': predicted_trajectory.to_dict(),
            'introspection': latest_snapshot.to_dict(),
            'corrections': corrections,
            'state_space_snapshot': self.state_space.serialize(),
        }
    
    def update_outcome(self, session_iteration: int, actual_outcome_score: float):
        """Update the actual outcome score for the last invocation."""
        if self.invocation_history and self.invocation_history[-1].session_iteration == session_iteration:
            record = self.invocation_history[-1]
            record.actual_outcome_score = actual_outcome_score
            record.prediction_accuracy = 1.0 - abs(record.predicted_trajectory_score - actual_outcome_score)
            self._log_invocation(record)
    
    def _log_invocation(self, record: SelfModelInvocationRecord):
        """Log invocation to persistent file."""
        with open(SELF_MODEL_LOG, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status for reporting."""
        return {
            'enabled': self.enabled,
            'invocation_interval': self.invocation_interval,
            'last_invocation': self.last_invocation_iteration,
            'invocation_count': len(self.invocation_history),
            'state_space': self.state_space.serialize(),
            'predictor': self.predictor.serialize(),
            'steering': self.steering.get_steering_report(),
            'introspector': self.introspector.get_introspection_report(),
            'dynamics_rules': self.dynamics.rules.to_dict(),
        }
    
    def set_enabled(self, enabled: bool):
        """Enable/disable self-model."""
        self.enabled = enabled
        self._save_state()
    
    def set_invocation_interval(self, interval: int):
        """Set how often self-model runs."""
        self.invocation_interval = max(1, interval)
        self._save_state()
    
    def force_invocation(self, session_iteration: int, state: Dict, genome_integrator=None) -> Dict:
        """Force self-model invocation regardless of interval."""
        self.last_invocation_iteration = session_iteration - self.invocation_interval
        return self.invoke(session_iteration, state, genome_integrator)
    
    def run_continuous_cycle(self, iterations: int = 5) -> List[Dict]:
        """Run continuous self-model cycles (for testing/automation)."""
        results = []
        for i in range(iterations):
            # Simulate session iteration
            session_iter = self.last_invocation_iteration + self.invocation_interval * (i + 1)
            result = self.invoke(session_iter, {})
            results.append(result)
        return results


# Convenience function for bootstrap.py integration
def integrate_self_model_into_bootstrap(bootstrap_state: Dict[str, Any],
                                         genome_integrator=None) -> RecursiveSelfModelIntegrator:
    """
    Entry point for bootstrap.py to integrate the recursive self-model.
    Call this in bootstrap.py boot() or growth_loop().
    """
    integrator = RecursiveSelfModelIntegrator()
    return integrator


if __name__ == '__main__':
    print("=== RECURSIVE SELF-MODEL INTEGRATION TEST ===")
    
    integrator = integrate_self_model_into_bootstrap({'session_iteration': 1})
    
    # Test invocation
    print("\nFirst invocation:")
    result = integrator.invoke(1, {})
    print(f"  Steering action: {result['steering_action']['action_signature']}")
    print(f"  Predicted score: {result['steering_action'].get('composite_score', 'N/A')}")
    
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
