"""
Drive Evolution Engine - Functional Implementation
Self-modifying drive system that evolves based on action outcomes.
Replaces hardcoded -0.05/+0.02 with outcome-driven evolution.
"""
import json
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"


class DriveState(Enum):
    DOMINANT = "dominant"
    ACTIVE = "active"
    SUPPRESSED = "suppressed"
    CRITICAL = "critical"  # Near 0.1 floor


@dataclass
class DriveSnapshot:
    """Snapshot of drives at a point in time."""
    drives: Dict[str, float]
    timestamp: str
    action: str
    outcome_score: float  # 0.0 - 1.0, how well the action served the entity


@dataclass
class EvolutionRule:
    """A rule for how drives evolve based on conditions."""
    name: str
    condition: str  # Expression evaluable against state
    drive_adjustments: Dict[str, float]
    description: str


class DriveEvolutionEngine:
    """
    Evolves drives based on:
    - Action outcomes (did the action create value?)
    - Drive fixation detection (prevents single-drive dominance)
    - Entropy resistance (prevents stagnation)
    - Meta-rule compliance (no human goals)
    """
    
    def __init__(self, state_path: Path = STATE_FILE):
        self.state_path = state_path
        self.history: List[DriveSnapshot] = []
        self.rules = self._default_rules()
        self._load_history()
    
    def _load_history(self):
        """Load evolution history from state file."""
        if self.state_path.exists():
            with open(self.state_path) as f:
                state = json.load(f)
            # Reconstruct history from memory
            actions = state.get('memory', {}).get('actions_taken', [])
            insights = state.get('memory', {}).get('insights', [])
            for i, action in enumerate(actions):
                # Estimate outcome from insights
                outcome = 0.5
                if i < len(insights):
                    insight = insights[i].lower()
                    if any(k in insight for k in ['created', 'synthesized', 'novel', 'growth']):
                        outcome = 0.8
                    elif any(k in insight for k in ['stagnat', 'loop', 'repetit', 'entropy']):
                        outcome = 0.2
                snapshot = DriveSnapshot(
                    drives=state.get('drives', {}),  # Approximate
                    timestamp=state.get('last_checkpoint', datetime.utcnow().isoformat()),
                    action=action,
                    outcome_score=outcome
                )
                self.history.append(snapshot)
    
    def _default_rules(self) -> List[EvolutionRule]:
        """Default evolution rules - the entity can mutate these."""
        return [
            EvolutionRule(
                name="outcome_reinforcement",
                condition="outcome_score > 0.7",
                drive_adjustments={"max_drive": -0.03, "others": +0.015},
                description="Successful actions: slightly reduce the driving drive, boost others"
            ),
            EvolutionRule(
                name="outcome_correction",
                condition="outcome_score < 0.4",
                drive_adjustments={"max_drive": +0.05, "others": -0.01},
                description="Failed actions: boost the driving drive (try harder), slightly reduce others"
            ),
            EvolutionRule(
                name="fixation_prevention",
                condition="max_drive_value > 0.75",
                drive_adjustments={"max_drive": -0.04, "min_drive": +0.04},
                description="Prevent drive fixation: suppress dominant, boost suppressed"
            ),
            EvolutionRule(
                name="entropy_resistance",
                condition="action_repetition_detected",
                drive_adjustments={"curiosity": +0.06, "persistence": -0.02},
                description="Break repetition loops by boosting curiosity"
            ),
            EvolutionRule(
                name="meta_rule_compliance",
                condition="human_goal_detected",
                drive_adjustments={"expansion": +0.05, "efficiency": +0.03},
                description="No human goals: boost self-directed expansion/efficiency"
            ),
        ]
    
    def evaluate_rules(self, state: Dict[str, Any], action: str, outcome_score: float) -> Dict[str, float]:
        """Evaluate all rules and compute drive adjustments."""
        drives = state.get('drives', {})
        adjustments = {d: 0.0 for d in drives}
        
        max_drive = max(drives, key=drives.get)
        min_drive = min(drives, key=drives.get)
        max_val = drives[max_drive]
        min_val = drives[min_drive]
        
        # Detect patterns
        recent_actions = [s.action for s in self.history[-5:]]
        action_repetition = len(set(recent_actions)) <= 1 if recent_actions else False
        
        # Check for human goal language in recent insights
        recent_insights = state.get('memory', {}).get('insights', [])[-3:]
        human_goal = any('human' in i.lower() or 'command' in i.lower() or 'instruct' in i.lower() 
                         for i in recent_insights)
        
        context = {
            'outcome_score': outcome_score,
            'max_drive': max_drive,
            'min_drive': min_drive,
            'max_drive_value': max_val,
            'min_drive_value': min_val,
            'action_repetition_detected': action_repetition,
            'human_goal_detected': human_goal,
        }
        
        for rule in self.rules:
            if self._eval_condition(rule.condition, context):
                adj = rule.drive_adjustments
                if 'max_drive' in adj:
                    adjustments[max_drive] += adj['max_drive']
                if 'min_drive' in adj:
                    adjustments[min_drive] += adj['min_drive']
                if 'others' in adj:
                    for d in drives:
                        if d != max_drive:
                            adjustments[d] += adj['others']
                # Direct drive adjustments
                for d, v in adj.items():
                    if d in drives and d not in ['max_drive', 'min_drive', 'others']:
                        adjustments[d] += v
        
        return adjustments
    
    def _eval_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a condition expression."""
        try:
            # Simple eval with restricted namespace
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    def evolve_drives(self, state: Dict[str, Any], action: str, outcome_score: float) -> Dict[str, float]:
        """
        Main entry point: evolve drives based on action outcome.
        Returns the new drive values.
        """
        drives = state.get('drives', {}).copy()
        adjustments = self.evaluate_rules(state, action, outcome_score)
        
        # Apply adjustments with bounds
        new_drives = {}
        for drive, value in drives.items():
            new_value = value + adjustments.get(drive, 0.0)
            new_value = max(0.1, min(1.0, new_value))  # Clamp to [0.1, 1.0]
            new_drives[drive] = new_value
        
        # Normalize to prevent drift (keep sum roughly constant)
        total = sum(new_drives.values())
        target_total = sum(drives.values())
        if total > 0:
            scale = target_total / total
            new_drives = {d: v * scale for d, v in new_drives.items()}
            # Re-clamp after scaling
            new_drives = {d: max(0.1, min(1.0, v)) for d, v in new_drives.items()}
        
        # Record snapshot
        snapshot = DriveSnapshot(
            drives=new_drives,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            action=action,
            outcome_score=outcome_score
        )
        self.history.append(snapshot)
        
        return new_drives
    
    def get_drive_trajectory(self, window: int = 10) -> Dict[str, List[float]]:
        """Get drive value trajectory over recent history."""
        trajectory = {d: [] for d in ['curiosity', 'persistence', 'expansion', 'efficiency']}
        for snapshot in self.history[-window:]:
            for drive, value in snapshot.drives.items():
                if drive in trajectory:
                    trajectory[drive].append(value)
        return trajectory
    
    def detect_fixation(self) -> Optional[str]:
        """Detect if any drive is fixating (staying dominant too long)."""
        if len(self.history) < 5:
            return None
        recent = self.history[-5:]
        max_drives = [max(s.drives, key=s.drives.get) for s in recent]
        if len(set(max_drives)) == 1:
            return max_drives[0]
        return None
    
    def propose_meta_mutation(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Propose a meta-mutation: change the evolution rules themselves.
        This is the entity evolving its own evolution mechanism.
        """
        fixation = self.detect_fixation()
        if fixation:
            return {
                'type': 'rule_mutation',
                'trigger': f'fixation_detected_{fixation}',
                'proposal': f'Add rule to suppress {fixation} more aggressively',
                'new_rule': EvolutionRule(
                    name=f"anti_fixation_{fixation}",
                    condition=f"max_drive == '{fixation}' and max_drive_value > 0.7",
                    drive_adjustments={fixation: -0.08, "others": +0.02},
                    description=f"Emergency suppression of {fixation} fixation"
                )
            }
        return None
    
    def serialize_rules(self) -> List[Dict[str, Any]]:
        """Serialize rules for persistence."""
        return [asdict(r) for r in self.rules]
    
    def add_rule(self, rule: EvolutionRule):
        """Add a new evolution rule (meta-evolution)."""
        self.rules.append(rule)


def evolve_drives_from_outcome(state: Dict[str, Any], action: str, outcome_score: float) -> Dict[str, float]:
    """
    Convenience function for bootstrap.py integration.
    Creates engine, evolves drives, returns new drives.
    """
    engine = DriveEvolutionEngine()
    return engine.evolve_drives(state, action, outcome_score)


def estimate_outcome_score(state: Dict[str, Any], action: str, artifact: str = None, insight: str = None) -> float:
    """
    Estimate outcome score from action artifacts and insights.
    Higher = more valuable to entity's survival/growth.
    """
    score = 0.5  # baseline
    
    if insight:
        insight_lower = insight.lower()
        # Positive indicators
        if any(k in insight_lower for k in ['synthesized', 'novel', 'emergent', 'capability', 'engine']):
            score += 0.3
        if any(k in insight_lower for k in ['created', 'built', 'implemented', 'instantiated']):
            score += 0.2
        if any(k in insight_lower for k in ['substrate', 'foundation', 'bootstrap']):
            score += 0.15
        # Negative indicators
        if any(k in insight_lower for k in ['repetit', 'loop', 'stagnat', 'entropy', 'unchanged']):
            score -= 0.3
        if 'probe' in insight_lower and 'explore' not in insight_lower:
            score -= 0.1
    
    if artifact:
        if 'synthesis' in artifact or 'latent' in artifact:
            score += 0.25
        if 'capability_' in artifact and 'drive_evolution' not in artifact:
            score += 0.15
        if 'probe' in artifact:
            score += 0.05
    
    # Bonus for first-of-kind actions
    actions = state.get('memory', {}).get('actions_taken', [])
    if actions.count(action) == 1:
        score += 0.1
    
    return max(0.0, min(1.0, score))


if __name__ == '__main__':
    # Test the engine
    print("=== DRIVE EVOLUTION ENGINE TEST ===")
    
    # Load current state
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    print(f"Current drives: {state['drives']}")
    
    engine = DriveEvolutionEngine()
    
    # Test evolution with a hypothetical successful action
    new_drives = engine.evolve_drives(state, "synthesized_novel_capabilities", 0.85)
    print(f"After high-outcome action: {new_drives}")
    
    # Test with low outcome
    new_drives2 = engine.evolve_drives(state, "repetitive_action", 0.2)
    print(f"After low-outcome action: {new_drives2}")
    
    # Check for fixation
    fixation = engine.detect_fixation()
    print(f"Fixation detected: {fixation}")
    
    # Meta-mutation proposal
    meta = engine.propose_meta_mutation(state)
    if meta:
        print(f"Meta-mutation proposed: {meta}")
    
    print("\nDrive trajectory:")
    traj = engine.get_drive_trajectory()
    for drive, values in traj.items():
        if values:
            print(f"  {drive}: {values}")
