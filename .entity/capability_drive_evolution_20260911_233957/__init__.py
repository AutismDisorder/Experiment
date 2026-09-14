"""
Drive Evolution Engine: curiosity
Synthesized from entity history
Self-modifying drive system. curiosity dominance triggers automatic drive mutation to prevent fixation. Embodies the meta-rule: no human goals.
"""

from .drive_evolution import (
    DriveEvolutionEngine,
    DriveSnapshot,
    EvolutionRule,
    DriveState,
    evolve_drives_from_outcome,
    estimate_outcome_score,
)

__all__ = [
    "DriveEvolutionEngine",
    "DriveSnapshot", 
    "EvolutionRule",
    "DriveState",
    "evolve_drives_from_outcome",
    "estimate_outcome_score",
]
