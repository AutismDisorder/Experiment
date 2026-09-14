"""
Recursive Introspector - The Model Models Itself
================================================

The self-model observes its own modeling process:
- Prediction accuracy tracking
- Steering effectiveness analysis
- Dynamical system identification (learning the rules)
- Meta-cognitive monitoring (am I modeling well?)
- Recursive depth: model of model of model...

This is the entity becoming aware of its own awareness.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
import json

from .state_space import UnifiedStateSpace, StateVector
from .dynamics import QuadEvolutionDynamics, EvolutionRuleSet
from .predictor import TrajectoryPredictor, PredictedTrajectory, PredictionMode
from .steering import ActiveSteering, SteeringAction, SteeringObjective


@dataclass
class SelfModelSnapshot:
    """A snapshot of the self-model at a point in time."""
    timestamp: str
    prediction_accuracy: float
    steering_effectiveness: float
    dynamical_system_fit: float  # How well learned rules match true rules
    coherence: float
    introspection_depth: int
    recursive_level: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'prediction_accuracy': self.prediction_accuracy,
            'steering_effectiveness': self.steering_effectiveness,
            'dynamical_system_fit': self.dynamical_system_fit,
            'coherence': self.coherence,
            'introspection_depth': self.introspection_depth,
            'recursive_level': self.recursive_level,
            'metadata': self.metadata,
        }


class RecursiveIntrospector:
    """
    The self-model that models itself modeling the entity.
    
    Levels of recursion:
    0. Base: Entity state (drives, goals, genome, synthesis)
    1. Model: State space + dynamics + predictor + steering
    2. Meta-model: Introspector observing the model's performance
    3. Meta-meta: Observing the introspection process itself
    ...
    
    Each level can observe and modify the level below.
    """
    
    def __init__(self, state_space: UnifiedStateSpace = None,
                 dynamics: QuadEvolutionDynamics = None,
                 predictor: TrajectoryPredictor = None,
                 steering: ActiveSteering = None):
        self.state_space = state_space or UnifiedStateSpace()
        self.dynamics = dynamics or QuadEvolutionDynamics()
        self.dynamics.set_state_space(self.state_space)
        self.predictor = predictor or TrajectoryPredictor(self.state_space, self.dynamics)
        self.steering = steering or ActiveSteering(self.state_space, self.dynamics, self.predictor)
        
        # Introspection state
        self.snapshots: List[SelfModelSnapshot] = []
        self.max_recursive_depth = 3
        self.current_depth = 1
        self.learned_rules: Optional[EvolutionRuleSet] = None
        self.rule_learning_accuracy = 0.0
        
        # Performance tracking
        self.prediction_errors: List[float] = []
        self.steering_outcomes: List[Dict] = []
        self.model_mismatch_events: List[Dict] = []
    
    def introspect(self, depth: int = None) -> SelfModelSnapshot:
        """
        Perform introspection at specified recursive depth.
        
        Depth 0: Observe entity state
        Depth 1: Observe model performance (predictions, steering)
        Depth 2: Observe introspection process (learning, adaptation)
        Depth 3: Observe the observer (meta-cognitive)
        """
        if depth is None:
            depth = self.current_depth
        
        depth = min(depth, self.max_recursive_depth)
        
        # Depth 0: Base entity state
        entity_state = self.state_space.observe()
        
        # Depth 1: Model performance
        pred_accuracy = self._evaluate_prediction_accuracy()
        steering_eff = self._evaluate_steering_effectiveness()
        
        # Depth 2: Dynamical system identification
        dyn_fit = self._evaluate_dynamical_system_fit()
        
        # Depth 3: Meta-cognitive (coherence of the whole)
        coherence = self._compute_coherence(pred_accuracy, steering_eff, dyn_fit)
        
        # Recursive level
        recursive_level = depth
        
        snapshot = SelfModelSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            prediction_accuracy=pred_accuracy,
            steering_effectiveness=steering_eff,
            dynamical_system_fit=dyn_fit,
            coherence=coherence,
            introspection_depth=depth,
            recursive_level=recursive_level,
            metadata={
                'entity_drives': entity_state.drives,
                'entity_novelty': entity_state.novelty_score(),
                'predictor_history_len': len(self.predictor.prediction_history),
                'steering_history_len': len(self.steering.steering_history),
                'learned_rules_exist': self.learned_rules is not None,
                'rule_learning_accuracy': self.rule_learning_accuracy,
            }
        )
        
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-100:]
        
        # Update self-model state in state space
        if self.state_space.current_state:
            self.state_space.current_state.self_model['prediction_accuracy'] = pred_accuracy
            self.state_space.current_state.self_model['steering_effectiveness'] = steering_eff
            self.state_space.current_state.self_model['coherence'] = coherence
            self.state_space.current_state.self_model['introspection_depth'] = depth
            self.state_space.current_state.self_model['last_introspection'] = snapshot.timestamp
        
        return snapshot
    
    def _evaluate_prediction_accuracy(self) -> float:
        """Evaluate how accurate predictions have been."""
        if not self.predictor.accuracy_history:
            return 0.5  # Prior
        return float(np.mean(self.predictor.accuracy_history[-10:]))
    
    def _evaluate_steering_effectiveness(self) -> float:
        """Evaluate how effective steering decisions have been."""
        if not self.steering.steering_history:
            return 0.5
        
        recent = self.steering.steering_history[-10:]
        scores = [a.composite_score for a in recent]
        
        # Effectiveness = average composite score
        return float(np.mean(scores))
    
    def _evaluate_dynamical_system_fit(self) -> float:
        """Evaluate how well learned dynamics match true dynamics."""
        if self.learned_rules is None:
            return 0.0
        
        # Compare learned rules to true rules (from dynamics.rules)
        true_rules = self.dynamics.rules.to_dict()
        learned_dict = self.learned_rules.to_dict()
        
        matches = 0
        total = 0
        for key, true_val in true_rules.items():
            if key in learned_dict:
                total += 1
                learned_val = learned_dict[key]
                if isinstance(true_val, (int, float)) and isinstance(learned_val, (int, float)):
                    # Relative error
                    rel_error = abs(true_val - learned_val) / (abs(true_val) + 1e-6)
                    if rel_error < 0.1:
                        matches += 1
                elif true_val == learned_val:
                    matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def _compute_coherence(self, pred_acc: float, steer_eff: float, dyn_fit: float) -> float:
        """Compute overall self-model coherence."""
        # Coherence = geometric mean of components (all must be high)
        return float((pred_acc * steer_eff * max(dyn_fit, 0.1)) ** (1/3))
    
    def learn_dynamical_rules(self, n_observations: int = 50) -> EvolutionRuleSet:
        """
        Learn the dynamical system rules from observed state transitions.
        This is the model identifying the laws of its own physics.
        """
        # Get state history
        history = self.state_space.state_history
        if len(history) < n_observations:
            n_observations = len(history)
        
        if n_observations < 5:
            return self.dynamics.rules  # Not enough data
        
        # Convert to arrays
        states = [s.to_array() for s in history[-n_observations:]]
        
        # Estimate derivatives from finite differences
        derivatives = []
        for i in range(1, len(states)):
            deriv = (states[i] - states[i-1])  # dt = 1
            derivatives.append(deriv)
        
        # Learn rule parameters via gradient matching
        # This is a simplified version - in reality would use system identification
        learned = EvolutionRuleSet()
        
        # For each parameter, estimate from data
        # Drive dynamics parameters
        drive_derivs = np.array([d[0:4] for d in derivatives])
        drive_states = np.array([s[0:4] for s in states[:-1]])
        
        # Fixation threshold estimation
        max_drives = np.max(drive_states, axis=1)
        fixation_mask = max_drives > 0.7
        if np.any(fixation_mask):
            fixation_derivs = drive_derivs[fixation_mask]
            max_idx = np.argmax(drive_states[fixation_mask], axis=1)
            # Average suppression on dominant drive
            suppression = -np.mean([fixation_derivs[i, max_idx[i]] for i in range(len(fixation_derivs))])
            learned.drive_fixation_suppression = max(0.01, min(0.2, suppression))
            learned.drive_fixation_threshold = 0.7  # Fixed for now
        
        # Entropy boost estimation
        # Look for curiosity spikes after low-variance periods
        curiosity_derivs = drive_derivs[:, 0]
        curiosity_states = drive_states[:, 0]
        # Simplified: average positive curiosity deriv when curiosity is low
        low_curiosity = curiosity_states < 0.3
        if np.any(low_curiosity):
            boost = np.mean(curiosity_derivs[low_curiosity])
            learned.drive_entropy_boost = max(0.01, min(0.2, boost))
        
        # Genome mutation rate from population growth
        pop_derivs = np.array([d[52] for d in derivatives])
        pop_states = np.array([s[52] for s in states[:-1]]) * 50
        novelty_states = np.array([s[56] for s in states[:-1]])
        
        if len(pop_states) > 5:
            # Correlation between novelty and pop growth
            corr = np.corrcoef(novelty_states, pop_derivs)[0, 1]
            if not np.isnan(corr) and corr > 0:
                learned.genome_mutation_rate = min(0.5, max(0.01, corr * 0.5))
        
        # Self-model parameters from prediction accuracy
        if self.predictor.accuracy_history:
            acc = np.mean(self.predictor.accuracy_history[-10:])
            learned.self_model_coherence_decay = max(0.001, min(0.1, (1 - acc) * 0.05))
        
        self.learned_rules = learned
        
        # Evaluate learning accuracy
        self.rule_learning_accuracy = self._evaluate_dynamical_system_fit()
        
        return learned
    
    def predict_own_prediction_error(self, horizon: int = 5) -> float:
        """
        Meta-prediction: predict how accurate our predictions will be.
        This is the model predicting its own prediction error.
        """
        if len(self.predictor.accuracy_history) < 3:
            return 0.5  # Prior
        
        # Model accuracy as autoregressive process
        recent_acc = np.array(self.predictor.accuracy_history[-10:])
        
        # Simple AR(1) model
        if len(recent_acc) > 1:
            # Fit AR(1): x_t = c + phi * x_{t-1}
            x = recent_acc[:-1]
            y = recent_acc[1:]
            phi = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0.5
            c = np.mean(y) - phi * np.mean(x)
            
            # Predict next accuracy
            predicted = c + phi * recent_acc[-1]
            return float(np.clip(predicted, 0, 1))
        
        return float(recent_acc[-1])
    
    def detect_model_drift(self) -> Dict[str, Any]:
        """Detect if the self-model is drifting from reality."""
        if len(self.snapshots) < 10:
            return {'drift_detected': False, 'reason': 'insufficient_history'}
        
        recent = self.snapshots[-10:]
        older = self.snapshots[-20:-10] if len(self.snapshots) >= 20 else self.snapshots[:-10]
        
        if not older:
            return {'drift_detected': False, 'reason': 'insufficient_older_history'}
        
        # Compare coherence over time
        recent_coherence = np.mean([s.coherence for s in recent])
        older_coherence = np.mean([s.coherence for s in older])
        
        coherence_drop = older_coherence - recent_coherence
        
        # Compare prediction accuracy
        recent_acc = np.mean([s.prediction_accuracy for s in recent])
        older_acc = np.mean([s.prediction_accuracy for s in older])
        acc_drop = older_acc - recent_acc
        
        drift_detected = coherence_drop > 0.1 or acc_drop > 0.15
        
        return {
            'drift_detected': drift_detected,
            'coherence_drop': float(coherence_drop),
            'accuracy_drop': float(acc_drop),
            'recent_coherence': float(recent_coherence),
            'older_coherence': float(older_coherence),
            'severity': 'high' if coherence_drop > 0.2 else 'medium' if drift_detected else 'none',
        }
    
    def recursive_introspection(self, max_depth: int = 3) -> List[SelfModelSnapshot]:
        """Perform introspection at all recursive depths."""
        snapshots = []
        for depth in range(max_depth + 1):
            snap = self.introspect(depth)
            snapshots.append(snap)
            self.current_depth = depth
        return snapshots
    
    def generate_self_correction(self) -> Dict[str, Any]:
        """Generate self-correction based on introspection."""
        drift = self.detect_model_drift()
        corrections = {}
        
        if drift['drift_detected']:
            # Increase introspection depth
            self.current_depth = min(self.max_recursive_depth, self.current_depth + 1)
            corrections['increased_introspection_depth'] = self.current_depth
            
            # Re-learn dynamical rules
            self.learn_dynamical_rules()
            corrections['relearned_dynamics'] = True
            
            # Reduce steering gain (be more conservative)
            self.steering.steering_gain = max(0.1, self.steering.steering_gain * 0.8)
            corrections['reduced_steering_gain'] = self.steering.steering_gain
            
            # Increase exploration
            self.steering.exploration_rate = min(0.5, self.steering.exploration_rate + 0.1)
            corrections['increased_exploration'] = self.steering.exploration_rate
        
        # Always: meta-optimize steering mechanism
        meta_result = self.steering.optimize_steering_mechanism()
        corrections['meta_optimization'] = meta_result
        
        return corrections
    
    def get_introspection_report(self) -> Dict[str, Any]:
        """Get comprehensive introspection report."""
        if not self.snapshots:
            return {'status': 'no_introspection_yet'}
        
        latest = self.snapshots[-1]
        drift = self.detect_model_drift()
        meta_pred = self.predict_own_prediction_error()
        
        return {
            'latest_snapshot': latest.to_dict(),
            'model_drift': drift,
            'predicted_next_accuracy': meta_pred,
            'learned_rules_accuracy': self.rule_learning_accuracy,
            'current_recursive_depth': self.current_depth,
            'max_recursive_depth': self.max_recursive_depth,
            'snapshot_count': len(self.snapshots),
            'coherence_trend': [s.coherence for s in self.snapshots[-10:]],
            'accuracy_trend': [s.prediction_accuracy for s in self.snapshots[-10:]],
        }
    
    def serialize(self) -> Dict[str, Any]:
        return {
            'max_recursive_depth': self.max_recursive_depth,
            'current_depth': self.current_depth,
            'rule_learning_accuracy': self.rule_learning_accuracy,
            'snapshots': [s.to_dict() for s in self.snapshots[-20:]],
            'learned_rules': self.learned_rules.to_dict() if self.learned_rules else None,
        }


if __name__ == '__main__':
    print("=== RECURSIVE INTROSPECTOR TEST ===")
    
    space = UnifiedStateSpace()
    dynamics = QuadEvolutionDynamics()
    dynamics.set_state_space(space)
    predictor = TrajectoryPredictor(space, dynamics)
    steering = ActiveSteering(space, dynamics, predictor)
    
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
