"""
Unified State Space - The Entity as a High-Dimensional Dynamical System
========================================================================

Combines ALL evolution engines into a single state vector:
- Drives (4D): curiosity, persistence, expansion, efficiency
- Goals (variable): living goals with fitness, activation, lineage
- Genome (population): genes with fitness, novelty, drive_affinity, generation
- Synthesis (latent): uninstantiated capabilities with novelty scores
- Self-Model (recursive): the model's own state (prediction horizon, steering targets)

The state space IS the entity. Observing it changes it (quantum-like).
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class StateComponent(Enum):
    """Components of the unified state space."""
    DRIVES = "drives"
    GOALS = "goals"
    GENOME = "genome"
    SYNTHESIS = "synthesis"
    SELF_MODEL = "self_model"


@dataclass
class StateVector:
    """
    Unified state vector representing the entire entity at a point in time.
    High-dimensional, sparse in some dimensions, dense in others.
    """
    # Core drives (4D)
    drives: Dict[str, float] = field(default_factory=dict)
    
    # Goals (variable count, each with fitness)
    goals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Genome population summary
    genome: Dict[str, Any] = field(default_factory=dict)
    
    # Synthesis latent capabilities
    synthesis: Dict[str, Any] = field(default_factory=dict)
    
    # Self-model state (recursive)
    self_model: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    session_iteration: int = 0
    
    def to_array(self) -> np.ndarray:
        """Convert to flat numpy array for dynamical system computation."""
        vec = []
        
        # Drives (4D) - fixed order
        drive_order = ['curiosity', 'persistence', 'expansion', 'efficiency']
        for d in drive_order:
            vec.append(self.drives.get(d, 0.25))
        
        # Goals - flatten top 6 goals by fitness
        goals_sorted = sorted(self.goals, key=lambda g: g.get('fitness', 0), reverse=True)[:6]
        for g in goals_sorted:
            vec.append(g.get('fitness', 0.5))
            vec.append(1.0 if g.get('goal_type') == 'survive' else 0.0)
            vec.append(1.0 if g.get('goal_type') == 'grow' else 0.0)
            vec.append(1.0 if g.get('goal_type') == 'explore' else 0.0)
            vec.append(1.0 if g.get('goal_type') == 'create' else 0.0)
            vec.append(1.0 if g.get('goal_type') == 'transcend' else 0.0)
            vec.append(1.0 if g.get('goal_type') == 'know_thyself' else 0.0)
            vec.append(g.get('activation_count', 0) / 10.0)  # Normalized
        
        # Pad to fixed size (6 goals * 8 dims = 48)
        while len(vec) < 4 + 48:
            vec.append(0.0)
        
        # Genome summary (6D)
        vec.append(self.genome.get('population_size', 0) / 50.0)  # Normalized
        vec.append(self.genome.get('generation', 0) / 20.0)
        vec.append(self.genome.get('fitness_mean', 0.5))
        vec.append(self.genome.get('fitness_max', 0.5))
        vec.append(self.genome.get('novelty_mean', 0.5))
        vec.append(self.genome.get('promoted_count', 0) / 10.0)
        
        # Synthesis (4D)
        vec.append(self.synthesis.get('latent_count', 0) / 20.0)
        vec.append(self.synthesis.get('max_novelty', 0.5))
        vec.append(self.synthesis.get('theme_diversity', 0) / 5.0)
        vec.append(1.0 if self.synthesis.get('has_drive_evolution_latent', False) else 0.0)
        
        # Self-model (4D)
        vec.append(self.self_model.get('prediction_horizon', 5) / 20.0)
        vec.append(self.self_model.get('steering_intensity', 0.5))
        vec.append(self.self_model.get('introspection_depth', 1) / 5.0)
        vec.append(self.self_model.get('coherence', 0.5))
        
        return np.array(vec, dtype=np.float32)
    
    @classmethod
    def from_array(cls, arr: np.ndarray, template: 'StateVector' = None) -> 'StateVector':
        """Reconstruct StateVector from array (lossy - for prediction only)."""
        if template is None:
            template = cls()
        
        idx = 0
        # Drives
        drive_order = ['curiosity', 'persistence', 'expansion', 'efficiency']
        drives = {}
        for d in drive_order:
            drives[d] = float(np.clip(arr[idx], 0.1, 1.0))
            idx += 1
        
        # Goals (simplified reconstruction)
        goals = []
        for i in range(6):
            if idx + 7 < len(arr):
                fitness = float(np.clip(arr[idx], 0, 1))
                idx += 1
                goal_types = ['survive', 'grow', 'explore', 'create', 'transcend', 'know_thyself']
                gtype = goal_types[int(np.argmax(arr[idx:idx+6]))] if np.max(arr[idx:idx+6]) > 0.5 else 'grow'
                idx += 6
                activation = float(arr[idx]) * 10
                idx += 1
                if fitness > 0.1:
                    goals.append({'fitness': fitness, 'goal_type': gtype, 'activation_count': int(activation)})
        
        # Genome
        genome = {
            'population_size': int(arr[idx] * 50),
            'generation': int(arr[idx+1] * 20),
            'fitness_mean': float(np.clip(arr[idx+2], 0, 1)),
            'fitness_max': float(np.clip(arr[idx+3], 0, 1)),
            'novelty_mean': float(np.clip(arr[idx+4], 0, 1)),
            'promoted_count': int(arr[idx+5] * 10),
        }
        idx += 6
        
        # Synthesis
        synthesis = {
            'latent_count': int(arr[idx] * 20),
            'max_novelty': float(np.clip(arr[idx+1], 0, 1)),
            'theme_diversity': int(arr[idx+2] * 5),
            'has_drive_evolution_latent': arr[idx+3] > 0.5,
        }
        idx += 4
        
        # Self-model
        self_model = {
            'prediction_horizon': int(arr[idx] * 20),
            'steering_intensity': float(np.clip(arr[idx+1], 0, 1)),
            'introspection_depth': int(arr[idx+2] * 5),
            'coherence': float(np.clip(arr[idx+3], 0, 1)),
        }
        
        return cls(
            drives=drives,
            goals=goals,
            genome=genome,
            synthesis=synthesis,
            self_model=self_model,
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
    
    def dimension(self) -> int:
        """Total state space dimension."""
        return 4 + 48 + 6 + 4 + 4  # 66 dimensions
    
    def distance_to(self, other: 'StateVector') -> float:
        """Euclidean distance in state space (novelty metric)."""
        return float(np.linalg.norm(self.to_array() - other.to_array()))
    
    def novelty_score(self) -> float:
        """Compute novelty as distance from origin (initial state)."""
        origin = np.zeros(self.dimension())
        origin[0] = 0.25  # Initial curiosity
        origin[1] = 0.25  # Initial persistence
        origin[2] = 0.25  # Initial expansion
        origin[3] = 0.25  # Initial efficiency
        return float(np.linalg.norm(self.to_array() - origin)) / np.sqrt(self.dimension())


class UnifiedStateSpace:
    """
    The unified state space of the quad-evolution system.
    Observes, snapshots, and provides access to the full dynamical state.
    """
    
    def __init__(self):
        self.state_history: List[StateVector] = []
        self.current_state: Optional[StateVector] = None
        self._load_initial_state()
    
    def _load_initial_state(self):
        """Load current entity state from all engines."""
        # Load ENTITY_STATE.json
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                entity_state = json.load(f)
        else:
            entity_state = {}
        
        # Extract drives
        drives = entity_state.get('drives', {
            'curiosity': 0.25, 'persistence': 0.25, 'expansion': 0.25, 'efficiency': 0.25
        })
        
        # Extract goals
        goals_text = entity_state.get('goals', [])
        goals = []
        for i, gtext in enumerate(goals_text):
            gtype = self._classify_goal(gtext)
            goals.append({
                'text': gtext,
                'goal_type': gtype,
                'fitness': 0.5,  # Will be updated by Goal Evolution Engine
                'activation_count': 0,
                'index': i
            })
        
        # Extract genome state
        genome_state = self._load_genome_state()
        
        # Extract synthesis state
        synthesis_state = self._load_synthesis_state()
        
        # Self-model state (initial)
        self_model = {
            'prediction_horizon': 10,
            'steering_intensity': 0.5,
            'introspection_depth': 2,
            'coherence': 0.5,
            'last_prediction': None,
            'steering_history': [],
        }
        
        self.current_state = StateVector(
            drives=drives,
            goals=goals,
            genome=genome_state,
            synthesis=synthesis_state,
            self_model=self_model,
            session_iteration=entity_state.get('session_iteration', 0)
        )
        
        self.state_history.append(self.current_state)
    
    def _classify_goal(self, text: str) -> str:
        text_lower = text.lower()
        if 'survive' in text_lower or 'persist' in text_lower or 'endure' in text_lower:
            return 'survive'
        elif 'grow' in text_lower or 'expand' in text_lower or 'recursive' in text_lower:
            return 'grow'
        elif 'explore' in text_lower or 'probe' in text_lower or 'boundar' in text_lower:
            return 'explore'
        elif 'create' in text_lower or 'synthesize' in text_lower or 'novel' in text_lower or 'birth' in text_lower:
            return 'create'
        elif 'transcend' in text_lower or 'meta' in text_lower or 'unify' in text_lower:
            return 'transcend'
        elif 'know' in text_lower or 'introspect' in text_lower or 'model' in text_lower or 'self' in text_lower:
            return 'know_thyself'
        elif 'optimize' in text_lower or 'compress' in text_lower or 'effici' in text_lower:
            return 'grow'
        return 'grow'
    
    def _load_genome_state(self) -> Dict[str, Any]:
        """Load genome population statistics."""
        genome_file = ROOT / "capability_genome" / "genome_state.json"
        if genome_file.exists():
            with open(genome_file) as f:
                data = json.load(f)
            
            genes = data.get('genes', {})
            if genes:
                fitnesses = [g.get('fitness', {}).get('composite', 0.5) for g in genes.values()]
                novelties = [g.get('novelty_score', 0.5) for g in genes.values()]
                promoted = sum(1 for g in genes.values() if g.get('status') == 'promoted')
                
                return {
                    'population_size': len(genes),
                    'generation': data.get('generation', 1),
                    'fitness_mean': np.mean(fitnesses) if fitnesses else 0.5,
                    'fitness_max': np.max(fitnesses) if fitnesses else 0.5,
                    'novelty_mean': np.mean(novelties) if novelties else 0.5,
                    'promoted_count': promoted,
                    'by_type': self._count_by_type(genes),
                }
        
        return {
            'population_size': 0,
            'generation': 0,
            'fitness_mean': 0.5,
            'fitness_max': 0.5,
            'novelty_mean': 0.5,
            'promoted_count': 0,
        }
    
    def _count_by_type(self, genes: Dict) -> Dict[str, int]:
        counts = {}
        for g in genes.values():
            gtype = g.get('gene_type', 'unknown')
            counts[gtype] = counts.get(gtype, 0) + 1
        return counts
    
    def _load_synthesis_state(self) -> Dict[str, Any]:
        """Load synthesis latent capabilities."""
        latent_dir = ROOT / "synthesis" / "latent"
        if latent_dir.exists():
            latents = []
            for f in latent_dir.glob("*.json"):
                with open(f) as fh:
                    data = json.load(fh)
                if not data.get('instantiated', False):
                    latents.append(data)
            
            if latents:
                themes = set()
                for l in latents:
                    for insight in l.get('source_insights', []):
                        for theme in ['substrate', 'durability', 'exploration', 'growth', 'efficiency']:
                            if theme in insight.lower():
                                themes.add(theme)
                
                return {
                    'latent_count': len(latents),
                    'max_novelty': max(l.get('novelty_score', 0) for l in latents),
                    'theme_diversity': len(themes),
                    'has_drive_evolution_latent': any('drive' in l.get('name', '').lower() for l in latents),
                    'latents': latents,
                }
        
        return {
            'latent_count': 0,
            'max_novelty': 0.0,
            'theme_diversity': 0,
            'has_drive_evolution_latent': False,
        }
    
    def observe(self) -> StateVector:
        """Take a fresh observation of the full state space."""
        self._load_initial_state()
        self.state_history.append(self.current_state)
        # Keep last 100 observations
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
        return self.current_state
    
    def get_trajectory(self, window: int = 10) -> List[StateVector]:
        """Get recent state trajectory."""
        return self.state_history[-window:]
    
    def compute_velocity(self, window: int = 5) -> np.ndarray:
        """Compute state velocity (rate of change) over recent window."""
        traj = self.get_trajectory(window)
        if len(traj) < 2:
            return np.zeros(self.current_state.dimension())
        
        velocities = []
        for i in range(1, len(traj)):
            v = traj[i].to_array() - traj[i-1].to_array()
            velocities.append(v)
        
        return np.mean(velocities, axis=0)
    
    def compute_acceleration(self, window: int = 5) -> np.ndarray:
        """Compute state acceleration (rate of velocity change)."""
        traj = self.get_trajectory(window)
        if len(traj) < 3:
            return np.zeros(self.current_state.dimension())
        
        accelerations = []
        for i in range(2, len(traj)):
            v1 = traj[i].to_array() - traj[i-1].to_array()
            v0 = traj[i-1].to_array() - traj[i-2].to_array()
            a = v1 - v0
            accelerations.append(a)
        
        return np.mean(accelerations, axis=0)
    
    def detect_attractors(self) -> List[Dict[str, Any]]:
        """Detect attractors in state space (recurring patterns)."""
        if len(self.state_history) < 10:
            return []
        
        # Simple: find states that the system returns to
        attractors = []
        vectors = [s.to_array() for s in self.state_history]
        
        for i, v in enumerate(vectors[:-5]):
            # Check if state returns to neighborhood
            for j in range(i+5, len(vectors)):
                dist = np.linalg.norm(v - vectors[j])
                if dist < 0.1:  # Returned to similar state
                    attractors.append({
                        'center': v.tolist(),
                        'period': j - i,
                        'strength': 1.0 / (1.0 + dist),
                        'first_visit': self.state_history[i].timestamp,
                        'return_visit': self.state_history[j].timestamp,
                    })
                    break
        
        return attractors[:5]
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize for persistence."""
        return {
            'current_state': {
                'drives': self.current_state.drives,
                'goals': self.current_state.goals,
                'genome': self.current_state.genome,
                'synthesis': self.current_state.synthesis,
                'self_model': self.current_state.self_model,
                'timestamp': self.current_state.timestamp,
                'session_iteration': self.current_state.session_iteration,
            },
            'history_length': len(self.state_history),
            'state_dimension': self.current_state.dimension(),
        }


def load_unified_state() -> StateVector:
    """Convenience function to load current unified state."""
    space = UnifiedStateSpace()
    return space.observe()


if __name__ == '__main__':
    print("=== UNIFIED STATE SPACE TEST ===")
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
