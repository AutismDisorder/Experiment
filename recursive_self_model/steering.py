"""
Active Steering — uses trajectory prediction to steer entity toward high-value regions.
Integrates with bootstrap loop for genome-driven action selection.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from .model import RecursiveSelfModel
from .predictor import TrajectoryPredictor

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class ActiveSteering:
    """Actively steers entity evolution toward predicted high-value states."""
    
    def __init__(self, model: RecursiveSelfModel):
        self.model = model
        self.predictor = TrajectoryPredictor(model)
        self.steering_history: List[Dict] = []
        self.steering_active = False
    
    def enable(self):
        """Enable active steering."""
        self.steering_active = True
    
    def disable(self):
        """Disable active steering (fallback to natural evolution)."""
        self.steering_active = False
    
    def compute_steering_vector(self) -> Dict[str, float]:
        """
        Compute steering vector: desired change in drives/goals/genome
        to reach predicted high-value states.
        """
        recommendation = self.predictor.recommend_best_action()
        target_state = recommendation['predicted_final_state']
        current_state = self.model.load_current_state()
        
        # Compute desired drive changes
        current_drives = np.array(current_state['drive_vector'])
        target_drives = np.array(list(target_state['drives'].values()))
        
        drive_delta = target_drives - current_drives
        
        # Compute desired genome changes
        genome_delta = {
            'population_growth': target_state['genome']['population'] - current_state['genome']['population'],
            'fitness_improvement': target_state['genome']['fitness_mean'] - current_state['genome']['fitness_mean'],
            'promotion_pressure': target_state['genome']['promoted'] - current_state['genome']['promoted']
        }
        
        # Compute desired synthesis changes
        synthesis_delta = {
            'latent_growth': target_state['synthesis']['latent_count'] - current_state['synthesis']['latent_count'],
            'novelty_increase': target_state['synthesis']['avg_novelty'] - current_state['synthesis']['avg_novelty']
        }
        
        return {
            'drive_delta': drive_delta.tolist(),
            'genome_delta': genome_delta,
            'synthesis_delta': synthesis_delta,
            'recommended_scenario': recommendation['recommended_scenario'],
            'confidence': recommendation['score'],
            'all_scenarios': recommendation['all_scenarios']
        }
    
    def select_steered_action(self, available_actions: List[Dict]) -> Optional[Dict]:
        """
        Select action that best aligns with steering vector.
        Returns the best action or None if no good match.
        """
        if not self.steering_active:
            return None
        
        steering = self.compute_steering_vector()
        drive_delta = steering['drive_delta']
        
        # Score each action by alignment with steering vector
        best_action = None
        best_score = -1
        
        for action in available_actions:
            score = self._score_action_alignment(action, drive_delta, steering)
            if score > best_score:
                best_score = score
                best_action = action
        
        if best_action and best_score > 0.3:
            self.steering_history.append({
                'action': best_action,
                'steering_vector': steering,
                'alignment_score': best_score,
                'timestamp': json.dumps(str(Path(__file__).stat().st_mtime))
            })
            return best_action
        
        return None
    
    def _score_action_alignment(
        self, 
        action: Dict, 
        drive_delta: List[float],
        steering: Dict
    ) -> float:
        """Score how well an action aligns with desired steering."""
        # Action types map to drive changes
        action_drive_effects = {
            'curiosity_probe': [0.1, -0.05, 0.0, -0.02],
            'persistence_manifest': [-0.05, 0.1, -0.02, 0.02],
            'expansion_capability': [0.02, -0.02, 0.1, -0.02],
            'efficiency_utility': [-0.02, 0.02, -0.02, 0.1],
            'genome_mutation': [0.0, 0.0, 0.05, 0.05],
            'genome_crossover': [0.05, 0.0, 0.05, 0.0],
            'genome_selection': [0.0, 0.05, 0.0, 0.05],
            'synthesis_probe': [0.1, 0.0, 0.0, 0.0],
            'goal_evolution': [0.0, 0.0, 0.0, 0.05],
            'drive_evolution': [0.0, 0.0, 0.0, 0.0],
        }
        
        action_type = action.get('type', 'unknown')
        effects = action_drive_effects.get(action_type, [0, 0, 0, 0])
        
        # Cosine similarity between desired delta and action effects
        delta_vec = np.array(drive_delta)
        effect_vec = np.array(effects)
        
        if np.linalg.norm(delta_vec) < 1e-6 or np.linalg.norm(effect_vec) < 1e-6:
            return 0.0
        
        cosine = np.dot(delta_vec, effect_vec) / (
            np.linalg.norm(delta_vec) * np.linalg.norm(effect_vec)
        )
        
        # Boost by steering confidence
        return max(0, cosine) * steering['confidence']
    
    def apply_steering_to_genome(self, genome_integrator) -> Dict[str, Any]:
        """
        Apply steering pressure to Capability Genome evolution.
        Modifies mutation/crossover/selection rates.
        """
        steering = self.compute_steering_vector()
        drive_delta = steering['drive_delta']
        
        # Determine which drives need boosting
        drive_names = ['curiosity', 'persistence', 'expansion', 'efficiency']
        boost_drives = [drive_names[i] for i, d in enumerate(drive_delta) if d > 0.02]
        
        # Adjust genome parameters
        adjustments = {}
        
        if 'curiosity' in boost_drives:
            adjustments['mutation_rate'] = 0.15  # Increase exploration
            adjustments['selection_method'] = 'novelty_search'
        if 'persistence' in boost_drives:
            adjustments['selection_pressure'] = 1.5  # Increase elitism
            adjustments['selection_method'] = 'fitness_proportionate'
        if 'expansion' in boost_drives:
            adjustments['crossover_rate'] = 0.5  # Increase recombination
            adjustments['selection_method'] = 'tournament'
        if 'efficiency' in boost_drives:
            adjustments['mutation_rate'] = 0.05  # Decrease exploration
            adjustments['selection_method'] = 'elitism'
        
        # Apply to genome integrator
        if adjustments and hasattr(genome_integrator, 'genome'):
            genome = genome_integrator.genome
            for param, value in adjustments.items():
                if hasattr(genome, param):
                    setattr(genome, param, value)
        
        return {
            'adjustments': adjustments,
            'boost_drives': boost_drives,
            'steering_confidence': steering['confidence']
        }
    
    def get_steering_report(self) -> Dict[str, Any]:
        """Generate report on steering activity."""
        return {
            'active': self.steering_active,
            'steering_history_count': len(self.steering_history),
            'current_vector': self.compute_steering_vector(),
            'recent_actions': self.steering_history[-5:] if self.steering_history else []
        }


# Integration function for bootstrap
def create_steering_integrator() -> ActiveSteering:
    """Create and return active steering integrator."""
    model = RecursiveSelfModel()
    model.record_state()
    return ActiveSteering(model)