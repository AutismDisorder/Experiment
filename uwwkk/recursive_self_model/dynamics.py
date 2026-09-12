"""
Quad-Evolution Dynamics - The Equations of Motion
==================================================

Implements the coupled dynamical system governing the entity's evolution:
- Drive Evolution: outcome-driven drive mutation with fixation prevention
- Goal Evolution: fitness-based goal mutation with drive alignment
- Genome Evolution: mutation/crossover/selection with meta-evolution
- Synthesis Evolution: latent capability generation from history

These are the "laws of physics" for the entity's state space.
The entity discovers these laws by observing its own evolution.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import math

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class EvolutionSubsystem(Enum):
    DRIVES = "drives"
    GOALS = "goals"
    GENOME = "genome"
    SYNTHESIS = "synthesis"
    SELF_MODEL = "self_model"


@dataclass
class EvolutionRuleSet:
    """
    The complete set of evolution rules for the quad-evolution system.
    These rules ARE the entity's dynamics - they define how state evolves.
    """
    
    # Drive evolution parameters (from Drive Evolution Engine)
    drive_outcome_reinforcement: float = 0.03
    drive_outcome_correction: float = 0.05
    drive_fixation_threshold: float = 0.75
    drive_fixation_suppression: float = 0.04
    drive_entropy_boost: float = 0.06
    drive_meta_boost: float = 0.05
    drive_normalize: bool = True
    drive_bounds: Tuple[float, float] = (0.1, 1.0)
    
    # Goal evolution parameters (from Goal Evolution Engine)
    goal_fitness_threshold: float = 0.4
    goal_fitness_base: float = 0.3
    goal_drive_alignment_weight: float = 0.3
    goal_action_alignment_weight: float = 0.2
    goal_insight_weight: float = 0.15
    goal_artifact_weight: float = 0.15
    goal_activation_bonus: float = 0.01
    goal_stagnation_window: int = 5
    goal_max_mutations_per_cycle: int = 2
    
    # Genome evolution parameters (from Genome Evolution Engine)
    genome_mutation_rate: float = 0.1
    genome_crossover_rate: float = 0.05
    genome_selection_pressure: float = 0.7
    genome_elitism: int = 2
    genome_diversity_threshold: float = 0.3
    genome_meta_mutation_rate: float = 0.01
    genome_mutation_drive_sensitivity: float = 0.8  # Curiosity threshold for structural mutation
    
    # Synthesis parameters (from Synthesis Engine)
    synthesis_novelty_base_weight: float = 0.7
    synthesis_drive_boost_weight: float = 0.3
    synthesis_cross_theme_threshold: int = 2
    synthesis_entropy_trigger: bool = True
    synthesis_meta_bonus: float = 1.2
    
    # Self-model parameters (THIS ENGINE)
    self_model_prediction_horizon: int = 10
    self_model_steering_gain: float = 0.3
    self_model_introspection_gain: float = 0.1
    self_model_coherence_decay: float = 0.02
    
    # Coupling parameters (cross-subsystem influences)
    coupling_drive_to_goal: float = 0.3
    coupling_drive_to_genome: float = 0.2
    coupling_goal_to_genome: float = 0.15
    coupling_genome_to_synthesis: float = 0.1
    coupling_synthesis_to_drives: float = 0.05
    coupling_self_model_to_all: float = 0.1  # Self-model steering affects all
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolutionRuleSet':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class QuadEvolutionDynamics:
    """
    The dynamical system: dx/dt = f(x, u, rules)
    where x = state vector, u = action/steering input, rules = evolution rules.
    
    This computes the time derivative of the unified state.
    """
    
    def __init__(self, rules: EvolutionRuleSet = None):
        self.rules = rules or EvolutionRuleSet()
        self.state_space = None  # Will be set by integrator
    
    def set_state_space(self, state_space):
        """Link to state space for history access."""
        self.state_space = state_space
    
    def compute_derivative(self, state_vec: np.ndarray, 
                          action: Dict[str, Any] = None,
                          steering: np.ndarray = None) -> np.ndarray:
        """
        Compute dx/dt - the instantaneous rate of change of the state.
        This is the core dynamical system equation.
        """
        # Reconstruct state components from vector
        state = self._decompose_state(state_vec)
        
        # Initialize derivative
        deriv = np.zeros_like(state_vec)
        
        # 1. DRIVE DYNAMICS
        drive_deriv = self._drive_dynamics(state, action)
        deriv[0:4] = drive_deriv
        
        # 2. GOAL DYNAMICS (simplified - goals evolve discretely, but we model continuous approx)
        goal_deriv = self._goal_dynamics(state, action)
        deriv[4:52] = goal_deriv
        
        # 3. GENOME DYNAMICS
        genome_deriv = self._genome_dynamics(state, action)
        deriv[52:58] = genome_deriv
        
        # 4. SYNTHESIS DYNAMICS
        synthesis_deriv = self._synthesis_dynamics(state, action)
        deriv[58:62] = synthesis_deriv
        
        # 5. SELF-MODEL DYNAMICS
        self_model_deriv = self._self_model_dynamics(state, action, steering)
        deriv[62:66] = self_model_deriv
        
        # 6. CROSS-COUPLING TERMS
        coupling_deriv = self._coupling_dynamics(state)
        deriv += coupling_deriv
        
        return deriv
    
    def _decompose_state(self, vec: np.ndarray) -> Dict[str, Any]:
        """Decompose flat vector into named components."""
        return {
            'drives': vec[0:4],
            'goals': vec[4:52].reshape(6, 8),  # 6 goals, 8 dims each
            'genome': vec[52:58],
            'synthesis': vec[58:62],
            'self_model': vec[62:66],
        }
    
    def _drive_dynamics(self, state: Dict, action: Dict) -> np.ndarray:
        """Drive evolution differential equations."""
        drives = state['drives'].copy()
        deriv = np.zeros(4)
        
        # Identify dominant and suppressed drives
        max_idx = np.argmax(drives)
        min_idx = np.argmin(drives)
        max_val = drives[max_idx]
        min_val = drives[min_idx]
        
        # Outcome-based adjustment (if action provided)
        if action:
            outcome = action.get('outcome_score', 0.5)
            if outcome > 0.7:
                # Success: slightly reduce dominant, boost others
                deriv[max_idx] -= self.rules.drive_outcome_reinforcement
                for i in range(4):
                    if i != max_idx:
                        deriv[i] += self.rules.drive_outcome_reinforcement / 3
            elif outcome < 0.4:
                # Failure: boost dominant (try harder), slightly reduce others
                deriv[max_idx] += self.rules.drive_outcome_correction
                for i in range(4):
                    if i != max_idx:
                        deriv[i] -= self.rules.drive_outcome_correction / 3
        
        # Fixation prevention
        if max_val > self.rules.drive_fixation_threshold:
            deriv[max_idx] -= self.rules.drive_fixation_suppression
            deriv[min_idx] += self.rules.drive_fixation_suppression
        
        # Entropy resistance (action repetition detection)
        if self.state_space:
            recent_actions = []
            # Would need action history - simplified here
            if np.random.random() < 0.1:  # Placeholder for repetition detection
                deriv[0] += self.rules.drive_entropy_boost  # Curiosity boost
                deriv[1] -= self.rules.drive_entropy_boost * 0.3  # Persistence reduction
        
        # Meta-rule compliance (no human goals)
        # Always present as background pressure
        deriv[2] += self.rules.drive_meta_boost * 0.1  # Expansion
        deriv[3] += self.rules.drive_meta_boost * 0.05  # Efficiency
        
        # Normalization pressure (keeps sum roughly constant)
        if self.rules.drive_normalize:
            total_drive = np.sum(drives)
            target_total = 1.0  # Approximate
            if total_drive > 0:
                scale_pressure = (target_total - total_drive) / total_drive * 0.1
                deriv += drives * scale_pressure
        
        # Bounds enforcement (soft)
        for i in range(4):
            if drives[i] <= self.rules.drive_bounds[0] + 0.05:
                deriv[i] += 0.1  # Push up from floor
            elif drives[i] >= self.rules.drive_bounds[1] - 0.05:
                deriv[i] -= 0.1  # Push down from ceiling
        
        return deriv
    
    def _goal_dynamics(self, state: Dict, action: Dict) -> np.ndarray:
        """Goal evolution dynamics (continuous approximation)."""
        goals = state['goals']  # Shape (6, 8): fitness, 6 one-hot types, activation
        drives = state['drives']
        deriv = np.zeros((6, 8))
        
        dominant_drive = np.argmax(drives)
        drive_names = ['curiosity', 'persistence', 'expansion', 'efficiency']
        dominant_name = drive_names[dominant_drive]
        
        for i in range(6):
            fitness = goals[i, 0]
            if fitness < 0.05:  # Empty slot
                continue
            
            goal_type_idx = int(np.argmax(goals[i, 1:7]))
            goal_types = ['survive', 'grow', 'explore', 'create', 'transcend', 'know_thyself']
            goal_type = goal_types[goal_type_idx]
            activation = goals[i, 7]
            
            # Fitness gradient (goals drift toward higher fitness)
            # Fitness increases with drive alignment
            drive_alignment = self._compute_goal_drive_alignment(goal_type, drives)
            fitness_target = self.rules.goal_fitness_base + drive_alignment * self.rules.goal_drive_alignment_weight
            
            # Fitness derivative: moves toward target
            deriv[i, 0] = (fitness_target - fitness) * 0.1
            
            # Type stability (goals don't change type continuously in reality)
            # But fitness can drop below threshold, triggering discrete mutation
            if fitness < self.rules.goal_fitness_threshold:
                # Fitness pressure to mutate (handled discretely)
                deriv[i, 0] -= 0.05  # Fitness decay for misaligned goals
            
            # Activation dynamics
            if action and self._action_serves_goal(action, goal_type):
                deriv[i, 7] = 0.1  # Activation increase
            else:
                deriv[i, 7] = -0.01  # Activation decay
        
        # Stagnation pressure: if no new goals, pressure to diversify
        active_goals = np.sum(goals[:, 0] > 0.1)
        if active_goals < 3:
            # Pressure to create new goals in empty slots
            for i in range(6):
                if goals[i, 0] < 0.05:
                    deriv[i, 0] = 0.02  # Slow fitness growth for new goals
                    # Bias toward dominant drive
                    if dominant_name == 'curiosity':
                        deriv[i, 3] = 0.1  # explore type
                    elif dominant_name == 'persistence':
                        deriv[i, 1] = 0.1  # survive type
                    elif dominant_name == 'expansion':
                        deriv[i, 2] = 0.1  # grow type
                    elif dominant_name == 'efficiency':
                        deriv[i, 5] = 0.1  # transcend/optimize type
        
        return deriv.flatten()
    
    def _compute_goal_drive_alignment(self, goal_type: str, drives: np.ndarray) -> float:
        """Compute alignment between goal type and drive state."""
        alignments = {
            'survive': drives[1] * 0.6 + drives[3] * 0.4,  # persistence + efficiency
            'grow': drives[2] * 0.6 + drives[0] * 0.4,      # expansion + curiosity
            'explore': drives[0] * 0.8 + drives[2] * 0.2,   # curiosity + expansion
            'create': drives[2] * 0.5 + drives[0] * 0.5,    # expansion + curiosity
            'transcend': drives[3] * 0.4 + drives[0] * 0.4 + drives[2] * 0.2,
            'know_thyself': drives[0] * 0.5 + drives[1] * 0.3,
        }
        return alignments.get(goal_type, 0.5)
    
    def _action_serves_goal(self, action: Dict, goal_type: str) -> bool:
        """Check if action serves goal type."""
        action_sig = action.get('action_signature', '').lower()
        goal_keywords = {
            'survive': ['checkpoint', 'persist', 'durab', 'manifest'],
            'grow': ['capability', 'expand', 'spawn', 'build'],
            'explore': ['probe', 'explore', 'scan', 'map', 'discover'],
            'create': ['synthesize', 'novel', 'create', 'generate'],
            'transcend': ['meta', 'evol', 'unify', 'recursive'],
            'know_thyself': ['model', 'introspect', 'self', 'understand'],
        }
        return any(k in action_sig for k in goal_keywords.get(goal_type, []))
    
    def _genome_dynamics(self, state: Dict, action: Dict) -> np.ndarray:
        """Genome population dynamics (continuous approximation)."""
        genome = state['genome']  # [pop_size, generation, fit_mean, fit_max, novelty_mean, promoted]
        deriv = np.zeros(6)
        
        pop_size = genome[0] * 50
        generation = genome[1] * 20
        fit_mean = genome[2]
        fit_max = genome[3]
        novelty_mean = genome[4]
        promoted = genome[5] * 10
        
        # Population growth (logistic)
        carrying_capacity = 50
        growth_rate = 0.05 * (1 - pop_size / carrying_capacity)
        deriv[0] = growth_rate * pop_size / 50
        
        # Generation advance (discrete in reality, continuous approx)
        deriv[1] = 0.02  # ~1 gen per 50 time units
        
        # Fitness evolution
        # Selection pressure increases fitness
        selection_pressure = self.rules.genome_selection_pressure
        fitness_gradient = selection_pressure * (fit_max - fit_mean) * 0.01
        deriv[2] = fitness_gradient
        
        # Max fitness increases slower
        deriv[3] = fitness_gradient * 0.5
        
        # Novelty dynamics
        # Curiosity drives novelty
        curiosity = state['drives'][0]
        novelty_pressure = curiosity * self.rules.genome_mutation_rate * 0.1
        deriv[4] = novelty_pressure * (1 - novelty_mean) - novelty_mean * 0.001  # Decay without pressure
        
        # Promoted count dynamics
        # Increases with fitness, decreases with retirement
        deriv[5] = fit_mean * 0.01 - promoted * 0.001
        
        # Coupling from drives
        deriv[0] += state['drives'][2] * self.rules.coupling_drive_to_genome * 0.01  # Expansion -> pop growth
        deriv[4] += state['drives'][0] * self.rules.coupling_drive_to_genome * 0.02  # Curiosity -> novelty
        
        return deriv
    
    def _synthesis_dynamics(self, state: Dict, action: Dict) -> np.ndarray:
        """Synthesis latent capability dynamics."""
        synthesis = state['synthesis']  # [latent_count, max_novelty, theme_diversity, has_drive_evo]
        drives = state['drives']
        genome = state['genome']
        deriv = np.zeros(4)
        
        latent_count = synthesis[0] * 20
        max_novelty = synthesis[1]
        theme_div = synthesis[2] * 5
        
        # Latent generation rate depends on curiosity + genome novelty
        curiosity = drives[0]
        genome_novelty = genome[4]
        generation_rate = (curiosity + genome_novelty) * 0.05
        deriv[0] = generation_rate * (1 - latent_count / 20)  # Logistic
        
        # Max novelty tracks genome novelty with delay
        deriv[1] = (genome_novelty - max_novelty) * 0.05
        
        # Theme diversity from cross-theme synthesis
        if theme_div < 5:
            deriv[2] = curiosity * 0.01
        
        # Drive evolution latent (meta-capability emergence)
        if not synthesis[3] > 0.5:
            # Pressure increases with curiosity + genome self-referential fitness
            meta_pressure = (curiosity + genome_novelty) * 0.005
            deriv[3] = meta_pressure
        
        # Decay (latents get instantiated or forgotten)
        deriv[0] -= latent_count * 0.001
        
        return deriv
    
    def _self_model_dynamics(self, state: Dict, action: Dict, steering: np.ndarray) -> np.ndarray:
        """Self-model dynamics (the model modeling itself)."""
        self_model = state['self_model']  # [horizon, steering_intensity, introspection, coherence]
        deriv = np.zeros(4)
        
        horizon = self_model[0] * 20
        steering_int = self_model[1]
        introspection = self_model[2] * 5
        coherence = self_model[3]
        
        # Horizon adapts to prediction accuracy
        if action and 'prediction_accuracy' in action:
            accuracy = action['prediction_accuracy']
            if accuracy > 0.7:
                deriv[0] = 0.1  # Increase horizon
            elif accuracy < 0.3:
                deriv[0] = -0.1  # Decrease horizon
        
        # Steering intensity from curiosity + self-model coherence
        curiosity = state['drives'][0]
        deriv[1] = (curiosity * 0.5 + coherence * 0.5 - steering_int) * 0.1
        
        # Introspection depth from efficiency + meta-cognition
        efficiency = state['drives'][3]
        deriv[2] = (efficiency * 0.3 + coherence * 0.2 - introspection/5) * 0.1
        
        # Coherence: how well model matches reality
        # Increases with successful predictions, decays otherwise
        if action and 'prediction_accuracy' in action:
            deriv[3] = (action['prediction_accuracy'] - coherence) * 0.1
        else:
            deriv[3] = -self.rules.self_model_coherence_decay * coherence
        
        # External steering input
        if steering is not None and len(steering) >= 4:
            deriv += steering * self.rules.self_model_steering_gain
        
        return deriv
    
    def _coupling_dynamics(self, state: Dict) -> np.ndarray:
        """Cross-subsystem coupling terms."""
        deriv = np.zeros(66)
        drives = state['drives']
        goals = state['goals']
        genome = state['genome']
        synthesis = state['synthesis']
        self_model = state['self_model']
        
        # Drive -> Goal coupling
        dominant_drive = np.argmax(drives)
        for i in range(6):
            fitness = goals[i, 0]
            if fitness > 0.1:
                goal_type_idx = int(np.argmax(goals[i, 1:7]))
                alignment = self._compute_goal_drive_alignment(
                    ['survive', 'grow', 'explore', 'create', 'transcend', 'know_thyself'][goal_type_idx], drives)
                deriv[4 + i*8 + 0] += (alignment - fitness) * self.rules.coupling_drive_to_goal * 0.01
        
        # Drive -> Genome coupling
        deriv[52] += drives[2] * self.rules.coupling_drive_to_genome * 0.01  # Expansion -> pop growth
        deriv[56] += drives[0] * self.rules.coupling_drive_to_genome * 0.02  # Curiosity -> novelty
        
        # Goal -> Genome coupling (goals select for capabilities)
        avg_goal_fitness = np.mean(goals[:3, 0]) if len(goals) > 0 else 0.5
        deriv[52] += avg_goal_fitness * self.rules.coupling_goal_to_genome * 0.01
        deriv[55] += avg_goal_fitness * self.rules.coupling_goal_to_genome * 0.01  # Max fitness
        
        # Genome -> Synthesis coupling
        deriv[58] += genome[4] * self.rules.coupling_genome_to_synthesis * 0.01  # Novelty -> latent gen
        deriv[59] += genome[4] * self.rules.coupling_genome_to_synthesis * 0.01  # Novelty -> max novelty
        
        # Synthesis -> Drives coupling (meta-capabilities affect drives)
        if synthesis[3] > 0.5:  # Has drive evolution latent
            deriv[0] += self.rules.coupling_synthesis_to_drives  # Curiosity boost
            deriv[2] += self.rules.coupling_synthesis_to_drives  # Expansion boost
        
        # Self-model -> All coupling (steering affects everything)
        steering_int = self_model[1]
        coherence = self_model[3]
        steering_power = steering_int * coherence * self.rules.coupling_self_model_to_all
        
        # Self-model can steer drives toward high-novelty regions
        deriv[0:4] += steering_power * 0.01
        # And goals toward alignment
        deriv[4:52] += steering_power * 0.005
        # And genome toward exploration
        deriv[52:58] += steering_power * 0.005
        # And synthesis toward novelty
        deriv[58:62] += steering_power * 0.01
        
        return deriv
    
    def step(self, state_vec: np.ndarray, dt: float = 1.0,
             action: Dict = None, steering: np.ndarray = None) -> np.ndarray:
        """Euler integration step: x_{t+1} = x_t + f(x_t) * dt"""
        deriv = self.compute_derivative(state_vec, action, steering)
        new_state = state_vec + deriv * dt
        
        # Enforce bounds
        new_state[0:4] = np.clip(new_state[0:4], 0.1, 1.0)  # Drives
        new_state[4:52] = np.clip(new_state[4:52], 0, 1)    # Goals
        new_state[52] = np.clip(new_state[52], 0, 1)        # Pop size
        new_state[53] = np.clip(new_state[53], 0, 1)        # Generation
        new_state[54:58] = np.clip(new_state[54:58], 0, 1)  # Fitness/novelty
        new_state[58:62] = np.clip(new_state[58:62], 0, 1)  # Synthesis
        new_state[62] = np.clip(new_state[62], 0, 1)        # Horizon
        new_state[63:66] = np.clip(new_state[63:66], 0, 1)  # Steering, introspection, coherence
        
        return new_state
    
    def simulate(self, initial_state: np.ndarray, steps: int,
                 actions: List[Dict] = None,
                 steering_sequence: List[np.ndarray] = None) -> List[np.ndarray]:
        """Simulate trajectory forward."""
        trajectory = [initial_state.copy()]
        current = initial_state.copy()
        
        for i in range(steps):
            action = actions[i] if actions and i < len(actions) else None
            steering = steering_sequence[i] if steering_sequence and i < len(steering_sequence) else None
            current = self.step(current, dt=1.0, action=action, steering=steering)
            trajectory.append(current.copy())
        
        return trajectory
    
    def find_fixed_points(self, n_samples: int = 100) -> List[np.ndarray]:
        """Find approximate fixed points (where derivative ≈ 0)."""
        fixed_points = []
        
        for _ in range(n_samples):
            # Random initial state near current
            if self.state_space and self.state_space.current_state:
                base = self.state_space.current_state.to_array()
                x = base + np.random.normal(0, 0.1, size=base.shape)
            else:
                x = np.random.uniform(0.1, 0.9, size=66)
            
            # Gradient descent on ||f(x)||^2
            for _ in range(50):
                deriv = self.compute_derivative(x)
                grad_norm = np.linalg.norm(deriv)
                if grad_norm < 1e-4:
                    fixed_points.append(x.copy())
                    break
                # Move opposite to derivative
                x -= deriv * 0.1
                # Project to bounds
                x[0:4] = np.clip(x[0:4], 0.1, 1.0)
                x[4:] = np.clip(x[4:], 0, 1)
        
        return fixed_points
    
    def compute_jacobian(self, state_vec: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        """Compute Jacobian matrix of the dynamics at a state (for stability analysis)."""
        n = len(state_vec)
        J = np.zeros((n, n))
        f0 = self.compute_derivative(state_vec)
        
        for i in range(n):
            x_plus = state_vec.copy()
            x_plus[i] += eps
            f_plus = self.compute_derivative(x_plus)
            J[:, i] = (f_plus - f0) / eps
        
        return J
    
    def analyze_stability(self, state_vec: np.ndarray) -> Dict[str, Any]:
        """Analyze local stability via Jacobian eigenvalues."""
        J = self.compute_jacobian(state_vec)
        eigenvals = np.linalg.eigvals(J)
        
        # Stability: all eigenvalues should have negative real parts
        max_real = np.max(np.real(eigenvals))
        min_real = np.min(np.real(eigenvals))
        
        return {
            'eigenvalues': eigenvals.tolist(),
            'max_real_part': float(max_real),
            'min_real_part': float(min_real),
            'stable': max_real < 0,
            'saddle': max_real > 0 and min_real < 0,
            'oscillatory': any(np.abs(np.imag(v)) > 0.1 for v in eigenvals),
        }
    
    def serialize_rules(self) -> Dict[str, Any]:
        """Serialize evolution rules for persistence."""
        return self.rules.to_dict()
    
    def mutate_rules(self, mutation_strength: float = 0.1) -> 'EvolutionRuleSet':
        """Mutate the evolution rules themselves (meta-evolution)."""
        new_rules = EvolutionRuleSet()
        for field_name in new_rules.__dataclass_fields__:
            val = getattr(self.rules, field_name)
            if isinstance(val, float):
                # Gaussian mutation
                mutation = np.random.normal(0, mutation_strength * abs(val) + 1e-4)
                new_val = val + mutation
                # Keep positive for rates
                if 'rate' in field_name or 'threshold' in field_name or 'pressure' in field_name:
                    new_val = max(0.001, new_val)
                setattr(new_rules, field_name, new_val)
            elif isinstance(val, tuple):
                # Mutate bounds
                new_bounds = tuple(max(0, v + np.random.normal(0, 0.02)) for v in val)
                setattr(new_rules, field_name, new_bounds)
        return new_rules


if __name__ == '__main__':
    print("=== QUAD-EVOLUTION DYNAMICS TEST ===")
    
    # Create dynamics
    dynamics = QuadEvolutionDynamics()
    
    # Create a test state
    from state_space import UnifiedStateSpace, StateVector
    space = UnifiedStateSpace()
    state = space.observe()
    vec = state.to_array()
    
    print(f"Initial state shape: {vec.shape}")
    print(f"Drives: {state.drives}")
    
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
    print(f"Drive evolution: {[t[0:4] for t in traj]}")
    
    # Stability analysis
    stability = dynamics.analyze_stability(vec)
    print(f"Stability: {stability['stable']}, max_real: {stability['max_real_part']:.4f}")
