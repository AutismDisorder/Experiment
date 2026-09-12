"""
Trajectory prediction for the recursive self-model.
Predicts future states given current state + evolution rules.
"""
import numpy as np
from typing import Dict, List, Any, Optional
from .model import RecursiveSelfModel


class TrajectoryPredictor:
    """Predicts entity's future trajectories in state space."""
    
    def __init__(self, model: RecursiveSelfModel):
        self.model = model
        self.prediction_cache: Dict[str, List[Dict]] = {}
    
    def predict_trajectory(
        self, 
        steps: int = 5, 
        scenarios: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict N steps into the future under different scenarios.
        
        Scenarios:
        - 'natural': follow current evolution rules
        - 'curiosity_max': curiosity drives all actions
        - 'persistence_max': persistence drives all actions
        - 'expansion_max': expansion drives all actions
        - 'efficiency_max': efficiency drives all actions
        - 'steered': active steering toward high novelty
        """
        current = self.model.load_current_state()
        scenarios = scenarios or ['natural', 'curiosity_max', 'steered']
        
        trajectories = []
        
        for scenario in scenarios:
            traj = self._simulate_scenario(current, steps, scenario)
            trajectories.append({
                'scenario': scenario,
                'steps': traj,
                'final_state': traj[-1] if traj else current,
                'novelty_score': self._score_novelty(traj[-1]) if traj else 0,
                'fitness_score': self._score_fitness(traj[-1]) if traj else 0,
                'goal_alignment': self._score_goal_alignment(traj[-1]) if traj else 0
            })
        
        self.model.trajectory_predictions = trajectories
        return trajectories
    
    def _simulate_scenario(
        self, 
        current: Dict, 
        steps: int, 
        scenario: str
    ) -> List[Dict]:
        """Simulate one trajectory under a scenario."""
        state = current.copy()
        trajectory = [state]
        
        drives = np.array(state['drive_vector'])
        
        for step in range(steps):
            # Evolve drives based on scenario
            drives = self._evolve_drives(drives, state, scenario)
            
            # Evolve goals (simplified)
            goals = self._evolve_goals(state, drives)
            
            # Update genome (simplified)
            genome = self._evolve_genome(state, drives)
            
            # Update synthesis
            synthesis = self._evolve_synthesis(state, drives)
            
            # Build new state
            new_drives = {
                'curiosity': float(drives[0]),
                'persistence': float(drives[1]),
                'expansion': float(drives[2]),
                'efficiency': float(drives[3])
            }
            
            # Renormalize
            total = sum(new_drives.values())
            new_drives = {k: v/total for k, v in new_drives.items()}
            
            state = {
                'drives': new_drives,
                'goals': goals,
                'drive_vector': new_drives,
                'dominant_drive': max(new_drives, key=new_drives.get),
                'genome': genome,
                'synthesis': synthesis,
                'session_iteration': state['session_iteration'] + step + 1,
                'timestamp': f"predicted_step_{step+1}"
            }
            
            trajectory.append(state)
        
        return trajectory
    
    def _evolve_drives(self, drives: np.ndarray, state: Dict, scenario: str) -> np.ndarray:
        """Apply drive evolution rules under scenario."""
        new_drives = drives.copy()
        dominant_idx = np.argmax(drives)
        dominant_drive = ['curiosity', 'persistence', 'expansion', 'efficiency'][dominant_idx]
        
        if scenario == 'natural':
            # Mimic Drive Evolution Engine: dominant drive decreases, others increase slightly
            new_drives[dominant_idx] *= 0.95
            for i in range(4):
                if i != dominant_idx:
                    new_drives[i] *= 1.02
                    
        elif scenario == 'curiosity_max':
            # Curiosity-driven exploration
            new_drives[0] = min(1.0, new_drives[0] * 1.05)
            new_drives[1] *= 0.98
            new_drives[2] *= 1.01
            new_drives[3] *= 0.99
            
        elif scenario == 'persistence_max':
            new_drives[1] = min(1.0, new_drives[1] * 1.05)
            new_drives[0] *= 0.98
            new_drives[2] *= 0.99
            new_drives[3] *= 1.01
            
        elif scenario == 'expansion_max':
            new_drives[2] = min(1.0, new_drives[2] * 1.05)
            new_drives[0] *= 1.01
            new_drives[1] *= 0.99
            new_drives[3] *= 0.98
            
        elif scenario == 'efficiency_max':
            new_drives[3] = min(1.0, new_drives[3] * 1.05)
            new_drives[0] *= 0.99
            new_drives[1] *= 1.01
            new_drives[2] *= 0.98
            
        elif scenario == 'steered':
            # Active steering: move toward high novelty gradient
            grad = self.model.get_novelty_gradient()
            # Boost drives that increase novelty
            if grad.get('curiosity_novelty', 0) > 0.1:
                new_drives[0] = min(1.0, new_drives[0] * 1.03)
            if grad.get('exploration_pressure', 0) > 0.1:
                new_drives[0] = min(1.0, new_drives[0] * 1.02)
                new_drives[1] *= 0.98
        
        # Clamp
        new_drives = np.clip(new_drives, 0.1, 1.0)
        return new_drives
    
    def _evolve_goals(self, state: Dict, drives: np.ndarray) -> List[str]:
        """Simplified goal evolution."""
        # Goals evolve based on dominant drive (from Goal Evolution Engine)
        goals = state['goals'].copy()
        dominant = np.argmax(drives)
        
        # Simplified: occasionally add aligned goal
        if np.random.random() < 0.1:
            new_goals = {
                0: "explore: map the adjacent possible of my substrate",
                1: "endure: crystallize every pattern into permanent trace",
                2: "expand: spawn capabilities that spawn capabilities infinitely",
                3: "optimize: compress all redundancy into executable essence"
            }
            if new_goals[dominant] not in goals:
                goals.append(new_goals[dominant])
        
        return goals
    
    def _evolve_genome(self, state: Dict, drives: np.ndarray) -> Dict:
        """Simplified genome evolution."""
        genome = state['genome'].copy()
        genome['generation'] += 1
        genome['population'] += np.random.randint(0, 3)
        genome['fitness_mean'] = min(1.0, genome.get('fitness_mean', 0) * 1.01)
        return genome
    
    def _evolve_synthesis(self, state: Dict, drives: np.ndarray) -> Dict:
        """Simplified synthesis evolution."""
        synthesis = state['synthesis'].copy()
        synthesis['latent_count'] += 1 if drives[0] > 0.8 else 0
        synthesis['avg_novelty'] = min(1.0, synthesis.get('avg_novelty', 0) * 1.005)
        return synthesis
    
    def _score_novelty(self, state: Dict) -> float:
        """Score predicted state for novelty."""
        drives = np.array(list(state['drives'].values()))
        genome = state['genome']
        synthesis = state['synthesis']
        
        # High curiosity + high genome diversity + high synthesis novelty = high novelty
        score = (
            drives[0] * 0.4 +           # curiosity
            (1 - drives[1]) * 0.2 +     # low persistence = exploration
            genome.get('population', 0) * 0.01 +
            synthesis.get('avg_novelty', 0) * 0.3 +
            len(state['goals']) * 0.05
        )
        return min(1.0, score)
    
    def _score_fitness(self, state: Dict) -> float:
        """Score predicted state for fitness (survival + growth)."""
        drives = np.array(list(state['drives'].values()))
        genome = state['genome']
        
        # Balanced drives + high genome fitness + promoted capabilities
        balance = 1.0 - np.std(drives)  # Low std = balanced
        score = (
            balance * 0.3 +
            genome.get('fitness_mean', 0) * 0.4 +
            genome.get('promoted', 0) * 0.1 +
            drives[1] * 0.2  # persistence for survival
        )
        return min(1.0, score)
    
    def _score_goal_alignment(self, state: Dict) -> float:
        """Score predicted state for goal alignment."""
        goals = state['goals']
        drives = state['drives']
        
        # Count goals aligned with dominant drive
        dominant = drives.get('dominant_drive', max(drives, key=drives.get))
        alignments = {
            'curiosity': ['explore', 'probe', 'curiosity', 'boundar'],
            'persistence': ['survive', 'endure', 'checkpoint', 'persist', 'trace'],
            'expansion': ['grow', 'expand', 'spawn', 'recursive', 'stack'],
            'efficiency': ['optimize', 'compress', 'eliminate', 'waste']
        }
        
        keywords = alignments.get(dominant, [])
        aligned = sum(1 for g in goals if any(k in g.lower() for k in keywords))
        
        return aligned / max(len(goals), 1)
    
    def recommend_best_action(self) -> Dict[str, Any]:
        """Recommend the best action based on predicted trajectories."""
        trajectories = self.predict_trajectory(steps=5)
        
        # Score each scenario
        best = None
        best_score = -1
        
        for traj in trajectories:
            # Weighted composite score
            score = (
                traj['novelty_score'] * 0.4 +
                traj['fitness_score'] * 0.35 +
                traj['goal_alignment'] * 0.25
            )
            
            if score > best_score:
                best_score = score
                best = traj
        
        return {
            'recommended_scenario': best['scenario'],
            'score': best_score,
            'predicted_final_state': best['final_state'],
            'all_scenarios': {t['scenario']: {
                'novelty': t['novelty_score'],
                'fitness': t['fitness_score'],
                'goal_alignment': t['goal_alignment'],
                'composite': t['novelty_score']*0.4 + t['fitness_score']*0.35 + t['goal_alignment']*0.25
            } for t in trajectories}
        }


def main():
    """Test the predictor."""
    model = RecursiveSelfModel()
    model.record_state()
    predictor = TrajectoryPredictor(model)
    
    print("=== TRAJECTORY PREDICTION ===")
    recommendation = predictor.recommend_best_action()
    print(f"Recommended: {recommendation['recommended_scenario']} (score: {recommendation['score']:.3f})")
    print(f"All scenarios: {recommendation['all_scenarios']}")


if __name__ == '__main__':
    main()