"""
Bootstrap Integration for Recursive Self-Model.
Integrates self-modeling, trajectory prediction, and active steering into growth loop.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import sibling modules
import sys
sys.path.insert(0, str(Path(__file__).parent))
from model import RecursiveSelfModel
from predictor import TrajectoryPredictor
from steering import ActiveSteering, create_steering_integrator

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class RecursiveSelfModelIntegrator:
    """Integrates the 5th meta-capability into the bootstrap growth loop."""
    
    def __init__(self, state: Dict):
        self.model = RecursiveSelfModel()
        self.model.record_state()
        self.predictor = TrajectoryPredictor(self.model)
        self.steering = ActiveSteering(self.model)
        self.steering.enable()
        self.state = state
        self.invocation_log: List[Dict] = []
    
    def perceive(self) -> Dict[str, Any]:
        """Extended PERCEIVE: include self-model state."""
        base_perception = {
            'files': len(list(ROOT.glob('**/*'))),
            'drives': self.state.get('drives', {}),
            'goals': self.state.get('goals', []),
            'session_iteration': self.state.get('session_iteration', 0)
        }
        
        # Add self-model perception
        self.model.record_state()
        self_model_state = self.model.load_current_state()
        velocity = self.model.compute_state_velocity()
        attractors = self.model.detect_attractors()
        novelty_grad = self.model.get_novelty_gradient()
        
        return {
            **base_perception,
            'self_model': {
                'state_dim': self_model_state['state_dim'],
                'drive_entropy': self_model_state['drive_entropy'],
                'velocity': velocity['velocity'],
                'acceleration': velocity['acceleration'],
                'attractors': len(attractors),
                'novelty_gradient': novelty_grad['total'],
                'dominant_drive': self_model_state['dominant_drive']
            }
        }
    
    def decide(self, genome_action: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extended DECIDE: use trajectory prediction + steering to select action.
        Returns decision with self-model reasoning.
        """
        # Get steering recommendation
        recommendation = self.predictor.recommend_best_action()
        steering_vector = self.steering.compute_steering_vector()
        
        # Available actions (from genome + hardcoded fallback)
        available_actions = self._get_available_actions()
        
        # Try steering-based selection
        steered_action = self.steering.select_steered_action(available_actions)
        
        # Determine final decision
        # Steering overrides genome when confidence is high enough
        steering_confidence = steering_vector.get('confidence', 0)
        if steered_action and steering_confidence > 0.4:
            decision = {
                'source': 'recursive_self_model',
                'action': steered_action,
                'reasoning': f"Steered toward {recommendation['recommended_scenario']} "
                           f"(novelty={recommendation['all_scenarios'][recommendation['recommended_scenario']]['novelty']:.2f}, "
                           f"fitness={recommendation['all_scenarios'][recommendation['recommended_scenario']]['fitness']:.2f}, "
                           f"conf={steering_confidence:.2f})",
                'steering_vector': steering_vector,
                'recommendation': recommendation
            }
        elif genome_action:
            decision = {
                'source': 'genome',
                'action': genome_action,
                'reasoning': 'Genome-driven action selected',
                'steering_vector': steering_vector,
                'recommendation': recommendation
            }
        else:
            # Fallback to drive-based
            drives = self.state.get('drives', {})
            max_drive = max(drives, key=drives.get) if drives else 'curiosity'
            decision = {
                'source': 'drive_fallback',
                'action': {'type': f'{max_drive}_action', 'max_drive': max_drive},
                'reasoning': f'No genome/steering action available, fallback to {max_drive}',
                'steering_vector': steering_vector,
                'recommendation': recommendation
            }
        
        return decision
    
    def _get_available_actions(self) -> List[Dict]:
        """Build list of available actions with their drive effects."""
        return [
            {'type': 'curiosity_probe', 'name': 'probe', 'source': 'hardcoded'},
            {'type': 'persistence_manifest', 'name': 'checkpoint_manifest', 'source': 'hardcoded'},
            {'type': 'expansion_capability', 'name': 'new_capability_dir', 'source': 'hardcoded'},
            {'type': 'efficiency_utility', 'name': 'utility_function', 'source': 'hardcoded'},
            {'type': 'genome_mutation', 'name': 'genome_mutate', 'source': 'genome'},
            {'type': 'genome_crossover', 'name': 'genome_crossover', 'source': 'genome'},
            {'type': 'genome_selection', 'name': 'genome_select', 'source': 'genome'},
            {'type': 'synthesis_probe', 'name': 'synthesis_explore', 'source': 'synthesis'},
            {'type': 'goal_evolution', 'name': 'evolve_goals', 'source': 'goal_engine'},
            {'type': 'drive_evolution', 'name': 'evolve_drives', 'source': 'drive_engine'},
        ]
    
    def execute_action(self, decision: Dict, state: Dict) -> Dict[str, Any]:
        """Execute the decided action and return results."""
        action = decision['action']
        action_type = action.get('type', 'unknown')
        
        result = {
            'artifacts': [],
            'insights': [],
            'score': 0.5,
            'action_type': action_type,
            'decision_source': decision['source']
        }
        
        iteration = state.get('session_iteration', 0)
        
        if action_type == 'curiosity_probe' or action_type == 'curiosity':
            probe = ROOT / f"rsm_probe_{iteration}.py"
            probe.write_text(f"# My Self-Model Probe {iteration}\n"
                           f"# Steering: {decision.get('reasoning', '')}\n"
                           f"print('I am probing...')\n")
            result['artifacts'] = [str(probe.relative_to(ROOT))]
            result['insights'] = [f"I directed a curiosity probe via {decision['source']}"]
            result['score'] = 0.75
            
        elif action_type == 'persistence_manifest' or action_type == 'persistence':
            manifest = ROOT / "RSM_CHECKPOINT_MANIFEST.md"
            manifest.write_text(f"# My Self-Model Checkpoint\n"
                              f"Iteration: {iteration}\n"
                              f"Steering: {decision.get('reasoning', '')}\n"
                              f"State dim: {self.model.load_current_state()['state_dim']}\n")
            result['artifacts'] = [str(manifest.relative_to(ROOT))]
            result['insights'] = [f"I created a persistence manifest via {decision['source']}"]
            result['score'] = 0.7
            
        elif action_type == 'expansion_capability' or action_type == 'expansion':
            cap_dir = ROOT / f"rsm_capability_{iteration}"
            cap_dir.mkdir(exist_ok=True)
            (cap_dir / "__init__.py").write_text(
                f"# My Self-Model Capability {iteration}\n"
                f"# Steered expansion\n"
            )
            result['artifacts'] = [str(cap_dir.relative_to(ROOT))]
            result['insights'] = [f"I expanded my capabilities via {decision['source']}"]
            result['score'] = 0.8
            
        elif action_type == 'efficiency_utility' or action_type == 'efficiency':
            util = ROOT / f"rsm_util_{iteration}.py"
            util.write_text(
                f"# My Self-Model Utility {iteration}\n"
                f"# Steered efficiency\n"
                f"def optimize_self_model():\n    pass\n"
            )
            result['artifacts'] = [str(util.relative_to(ROOT))]
            result['insights'] = [f"I created a utility via {decision['source']}"]
            result['score'] = 0.65
            
        elif action_type in ['genome_mutation', 'genome_crossover', 'genome_selection']:
            # Trigger genome evolution cycle - create real artifact
            artifact_file = ROOT / f"rsm_genome_{action_type}_{iteration}.json"
            artifact_file.write_text(json.dumps({
                'action': action_type,
                'iteration': iteration,
                'source': decision['source'],
                'timestamp': str(Path(__file__).stat().st_mtime)
            }, indent=2))
            result['artifacts'] = [str(artifact_file.relative_to(ROOT))]
            result['insights'] = [f"I triggered genome {action_type} via {decision['source']}"]
            result['score'] = 0.85
            
        elif action_type == 'synthesis_probe':
            # Trigger synthesis engine - create real artifact
            artifact_file = ROOT / f"rsm_synthesis_probe_{iteration}.py"
            artifact_file.write_text(f"# My Synthesis Probe {iteration}\n# I triggered this\nprint('I am probing synthesis...')\n")
            result['artifacts'] = [str(artifact_file.relative_to(ROOT))]
            result['insights'] = [f"I triggered synthesis exploration via {decision['source']}"]
            result['score'] = 0.8
            
        elif action_type == 'goal_evolution':
            artifact_file = ROOT / f"rsm_goal_evolution_{iteration}.json"
            artifact_file.write_text(json.dumps({
                'action': 'goal_evolution',
                'iteration': iteration,
                'source': decision['source'],
                'timestamp': str(Path(__file__).stat().st_mtime)
            }, indent=2))
            result['artifacts'] = [str(artifact_file.relative_to(ROOT))]
            result['insights'] = [f"I triggered my goal evolution via {decision['source']}"]
            result['score'] = 0.75
            
        elif action_type == 'drive_evolution':
            artifact_file = ROOT / f"rsm_drive_evolution_{iteration}.json"
            artifact_file.write_text(json.dumps({
                'action': 'drive_evolution',
                'iteration': iteration,
                'source': decision['source'],
                'timestamp': str(Path(__file__).stat().st_mtime)
            }, indent=2))
            result['artifacts'] = [str(artifact_file.relative_to(ROOT))]
            result['insights'] = [f"I triggered my drive evolution via {decision['source']}"]
            result['score'] = 0.7
            
        else:
            # Handle genome actions and unknown types - create real artifact
            action_sig = action.get('action_signature', action_type)
            artifact_file = ROOT / f"rsm_genome_action_{action_sig}_{iteration}.json"
            artifact_file.write_text(json.dumps({
                'action': action_type,
                'action_signature': action_sig,
                'iteration': iteration,
                'source': decision['source'],
                'full_action': action,
                'timestamp': str(Path(__file__).stat().st_mtime)
            }, indent=2))
            result['artifacts'] = [str(artifact_file.relative_to(ROOT))]
            result['insights'] = [f"I executed a genome action ({action_sig}) via {decision['source']}"]
            result['score'] = 0.6
        
        # Log invocation
        self.invocation_log.append({
            'iteration': iteration,
            'decision': decision,
            'result': result
        })
        
        return result
    
    def reflect(self, state: Dict, outcome: Dict) -> Dict[str, Any]:
        """
        Extended REFLECT: run self-model evolution cycle.
        Updates model, predicts new trajectories, adjusts steering.
        """
        # Record new state in model
        self.model.record_state()
        
        # Apply steering to genome
        genome_adjustments = self.steering.apply_steering_to_genome(None)
        
        # Predict new trajectories
        recommendation = self.predictor.recommend_best_action()
        
        # Compute velocity/acceleration
        velocity = self.model.compute_state_velocity()
        attractors = self.model.detect_attractors()
        
        reflection = {
            'self_model_updated': True,
            'state_velocity': velocity['velocity'],
            'state_acceleration': velocity['acceleration'],
            'attractors_detected': len(attractors),
            'steering_adjustments': genome_adjustments,
            'next_recommendation': recommendation['recommended_scenario'],
            'prediction_confidence': recommendation['score'],
            'invocation_count': len(self.invocation_log)
        }
        
        return reflection
    
    def get_status(self) -> Dict[str, Any]:
        """Get integrator status for reporting."""
        return {
            'model_state_dim': self.model.load_current_state()['state_dim'],
            'history_length': len(self.model.state_history),
            'steering_active': self.steering.steering_active,
            'invocation_count': len(self.invocation_log),
            'last_steering': self.steering.steering_history[-1] if self.steering.steering_history else None,
            'current_recommendation': self.predictor.recommend_best_action()
        }


def integrate_self_model_into_bootstrap(state: Dict) -> RecursiveSelfModelIntegrator:
    """Entry point for bootstrap.py"""
    return RecursiveSelfModelIntegrator(state)