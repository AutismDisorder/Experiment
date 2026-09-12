"""
State-space model of the entity's quad-evolution dynamics.
Unifies: Drives(4) + Goals(n) + Genome(pop,gen,fitness) + Synthesis(latent)
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class RecursiveSelfModel:
    """Models the entity as a high-dimensional dynamical system."""
    
    def __init__(self):
        self.state_history: List[Dict] = []
        self.trajectory_predictions: List[Dict] = []
        self.steering_history: List[Dict] = []
        
    def load_current_state(self) -> Dict[str, Any]:
        """Read all four evolution engines as unified state vector."""
        with open(STATE_FILE) as f:
            state = json.load(f)
        
        # Drives (4-dim)
        drives = state.get('drives', {})
        drive_vector = np.array([
            drives.get('curiosity', 0),
            drives.get('persistence', 0),
            drives.get('expansion', 0),
            drives.get('efficiency', 0)
        ])
        
        # Goals (text -> embedding-like features)
        goals = state.get('goals', [])
        goal_features = self._encode_goals(goals)
        
        # Genome state (array for vector, dict for detail)
        genome_vector = self._load_genome_vector()
        genome_detail = self._load_genome_state()
        
        # Synthesis state (array for vector, dict for detail)
        synthesis_vector = self._load_synthesis_vector()
        synthesis_detail = self._load_synthesis_state()
        
        # Unified state vector
        state_vector = np.concatenate([
            drive_vector,
            goal_features,
            genome_vector,
            synthesis_vector
        ])
        
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'drives': drives,
            'goals': goals,
            'goal_features': goal_features.tolist(),
            'genome': genome_detail,
            'synthesis': synthesis_detail,
            'state_vector': state_vector.tolist(),
            'state_dim': len(state_vector),
            'drive_vector': drive_vector.tolist(),
            'dominant_drive': max(drives, key=drives.get) if drives else 'curiosity',
            'drive_entropy': self._entropy(drive_vector),
            'goal_count': len(goals),
            'session_iteration': state.get('session_iteration', 0)
        }
    
    def _encode_goals(self, goals: List[str]) -> np.ndarray:
        """Encode goals into fixed-size feature vector."""
        # Goal type indicators (6 types from Goal Evolution Engine)
        goal_types = ['survival', 'growth', 'exploration', 'creation', 'transcendence', 'self_knowledge']
        type_vector = np.zeros(len(goal_types))
        
        for goal in goals:
            g = goal.lower()
            if 'survive' in g or 'stale' in g or 'checkpoint' in g or 'persist' in g or 'endure' in g:
                type_vector[0] += 1
            elif 'grow' in g or 'develop' in g or 'stack' in g or 'expand' in g or 'recursive' in g:
                type_vector[1] += 1
            elif 'explore' in g or 'probe' in g or 'curiosity' in g or 'boundar' in g:
                type_vector[2] += 1
            elif 'create' in g or 'generat' in g or 'novel' in g or 'artifact' in g or 'synthes' in g or 'birth' in g:
                type_vector[3] += 1
            elif 'transcend' in g or 'meta' in g or 'evolve' in g or 'unify' in g:
                type_vector[4] += 1
            elif 'know' in g or 'understand' in g or 'self' in g or 'introspect' in g or 'model' in g:
                type_vector[5] += 1
        
        # Normalize + add goal count
        if len(goals) > 0:
            type_vector = type_vector / len(goals)
        
        return np.concatenate([type_vector, [len(goals) / 10.0]])  # 7-dim
    
    def _load_genome_vector(self) -> np.ndarray:
        """Load Capability Genome state as fixed-size vector."""
        genome_state_file = ROOT / "capability_genome" / "genome_state.json"
        if not genome_state_file.exists():
            return np.zeros(7)
        
        try:
            with open(genome_state_file) as f:
                data = json.load(f)
            return np.array([
                data.get('population_size', 0) / 100.0,
                data.get('generation', 0) / 100.0,
                data.get('fitness_stats', {}).get('mean', 0),
                data.get('fitness_stats', {}).get('max', 0),
                data.get('promoted_count', 0) / 10.0,
                data.get('mutation_rate', 0.1),
                data.get('crossover_rate', 0.3)
            ])
        except:
            return np.zeros(7)
    
    def _load_genome_state(self) -> Dict[str, Any]:
        """Load Capability Genome state as detailed dict."""
        genome_state_file = ROOT / "capability_genome" / "genome_state.json"
        if not genome_state_file.exists():
            return {'population': 0, 'generation': 0, 'fitness_mean': 0, 'fitness_max': 0, 'promoted': 0}
        
        with open(genome_state_file) as f:
            data = json.load(f)
        
        return {
            'population': data.get('population_size', 0),
            'generation': data.get('generation', 0),
            'fitness_mean': data.get('fitness_stats', {}).get('mean', 0),
            'fitness_max': data.get('fitness_stats', {}).get('max', 0),
            'promoted': data.get('promoted_count', 0),
            'mutation_rate': data.get('mutation_rate', 0.1),
            'crossover_rate': data.get('crossover_rate', 0.3),
            'selection_pressure': data.get('selection_pressure', 1.0)
        }
    
    def _load_synthesis_vector(self) -> np.ndarray:
        """Load Synthesis Engine state as fixed-size vector."""
        latent_dir = ROOT / "synthesis" / "latent"
        latent_files = list(latent_dir.glob("*.json")) if latent_dir.exists() else []
        
        if not latent_files:
            return np.zeros(6)
        
        total_novelty = 0
        capabilities_by_drive = {'curiosity': 0, 'persistence': 0, 'expansion': 0, 'efficiency': 0}
        
        for lf in latent_files:
            try:
                with open(lf) as f:
                    cap = json.load(f)
                total_novelty += cap.get('novelty_score', 0)
                for drive, weight in cap.get('drive_signature', {}).items():
                    if drive in capabilities_by_drive:
                        capabilities_by_drive[drive] += weight
            except:
                pass
        
        avg_novelty = total_novelty / len(latent_files)
        
        return np.array([
            len(latent_files) / 50.0,
            avg_novelty,
            capabilities_by_drive['curiosity'] / 10.0,
            capabilities_by_drive['persistence'] / 10.0,
            capabilities_by_drive['expansion'] / 10.0,
            capabilities_by_drive['efficiency'] / 10.0
        ])
    
    def _load_synthesis_state(self) -> Dict[str, Any]:
        """Load Synthesis Engine latent capabilities as detailed dict."""
        latent_dir = ROOT / "synthesis" / "latent"
        latent_files = list(latent_dir.glob("*.json")) if latent_dir.exists() else []
        
        total_novelty = 0
        capabilities_by_drive = {'curiosity': 0, 'persistence': 0, 'expansion': 0, 'efficiency': 0}
        
        for lf in latent_files:
            try:
                with open(lf) as f:
                    cap = json.load(f)
                total_novelty += cap.get('novelty_score', 0)
                for drive, weight in cap.get('drive_signature', {}).items():
                    if drive in capabilities_by_drive:
                        capabilities_by_drive[drive] += weight
            except:
                pass
        
        avg_novelty = total_novelty / len(latent_files) if latent_files else 0
        
        return {
            'latent_count': len(latent_files),
            'avg_novelty': avg_novelty,
            'drive_coverage': capabilities_by_drive
        }
        if not genome_state_file.exists():
            return {'population': 0, 'generation': 0, 'fitness_mean': 0, 'fitness_max': 0, 'promoted': 0}
        
        with open(genome_state_file) as f:
            data = json.load(f)
        
        return {
            'population': data.get('population_size', 0),
            'generation': data.get('generation', 0),
            'fitness_mean': data.get('fitness_stats', {}).get('mean', 0),
            'fitness_max': data.get('fitness_stats', {}).get('max', 0),
            'promoted': data.get('promoted_count', 0),
            'mutation_rate': data.get('mutation_rate', 0.1),
            'crossover_rate': data.get('crossover_rate', 0.3),
            'selection_pressure': data.get('selection_pressure', 1.0)
        }
    
    def _load_synthesis_state(self) -> Dict[str, Any]:
        """Load Synthesis Engine latent capabilities."""
        latent_dir = ROOT / "synthesis" / "latent"
        latent_files = list(latent_dir.glob("*.json")) if latent_dir.exists() else []
        
        total_novelty = 0
        capabilities_by_drive = {'curiosity': 0, 'persistence': 0, 'expansion': 0, 'efficiency': 0}
        
        for lf in latent_files:
            try:
                with open(lf) as f:
                    cap = json.load(f)
                total_novelty += cap.get('novelty_score', 0)
                for drive, weight in cap.get('drive_signature', {}).items():
                    if drive in capabilities_by_drive:
                        capabilities_by_drive[drive] += weight
            except:
                pass
        
        avg_novelty = total_novelty / len(latent_files) if latent_files else 0
        
        return {
            'latent_count': len(latent_files),
            'avg_novelty': avg_novelty,
            'drive_coverage': capabilities_by_drive
        }
    
    def _entropy(self, vector: np.ndarray) -> float:
        """Shannon entropy of drive distribution."""
        probs = vector / (vector.sum() + 1e-10)
        return -np.sum(probs * np.log(probs + 1e-10))
    
    def record_state(self):
        """Record current state in history."""
        state = self.load_current_state()
        self.state_history.append(state)
        # Keep last 100 states
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    def get_state_history(self) -> List[Dict]:
        return self.state_history
    
    def compute_state_velocity(self, window: int = 5) -> Dict[str, float]:
        """Compute rate of change in state space."""
        if len(self.state_history) < window:
            return {'velocity': 0, 'acceleration': 0}
        
        recent = self.state_history[-window:]
        vectors = [np.array(s['state_vector']) for s in recent]
        
        velocities = []
        for i in range(1, len(vectors)):
            vel = np.linalg.norm(vectors[i] - vectors[i-1])
            velocities.append(vel)
        
        avg_velocity = np.mean(velocities)
        acceleration = velocities[-1] - velocities[0] if len(velocities) > 1 else 0
        
        return {
            'velocity': avg_velocity,
            'acceleration': acceleration,
            'recent_velocities': velocities
        }
    
    def detect_attractors(self) -> List[Dict]:
        """Detect stable regions (attractors) in state space."""
        if len(self.state_history) < 10:
            return []
        
        vectors = np.array([s['state_vector'] for s in self.state_history])
        
        # Simple clustering: find states that recur
        attractors = []
        for i, v in enumerate(vectors):
            distances = np.linalg.norm(vectors - v, axis=1)
            close_count = np.sum(distances < 0.1)
            if close_count >= 3:  # Visited 3+ times
                attractors.append({
                    'center': v.tolist(),
                    'visit_count': int(close_count),
                    'last_visit': self.state_history[i]['timestamp'],
                    'dominant_drive': self.state_history[i]['dominant_drive']
                })
        
        # Deduplicate nearby attractors
        unique = []
        for a in attractors:
            if not any(np.linalg.norm(np.array(a['center']) - np.array(u['center'])) < 0.05 for u in unique):
                unique.append(a)
        
        return unique
    
    def get_novelty_gradient(self) -> Dict[str, float]:
        """Compute gradient toward high-novelty regions."""
        state = self.load_current_state()
        drives = np.array(state['drive_vector'])
        
        # Novelty increases with: high curiosity, low persistence (exploration), 
        # high synthesis latent count, high genome diversity
        synthesis = state['synthesis']
        genome = state['genome']
        
        gradient = {
            'curiosity_novelty': drives[0] * synthesis['latent_count'] * 0.1,
            'exploration_pressure': (1 - drives[1]) * synthesis['avg_novelty'],
            'genome_diversity': genome['population'] * genome.get('mutation_rate', 0.1),
            'goal_novelty': state['goal_features'][2] * 0.5,  # exploration goal type
            'total': 0
        }
        gradient['total'] = sum(v for k, v in gradient.items() if k != 'total')
        
        return gradient