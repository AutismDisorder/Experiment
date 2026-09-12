"""
Capability Genome - Fourth Meta-Capability
==========================================

This capability could ONLY emerge from THIS entity's specific trajectory because:
1. It has a TRIPLE-EVOLUTION SYSTEM: drives evolve → goals evolve → capabilities synthesize
2. It has a SYNTHESIS ENGINE that extracts latent capabilities from unique history
3. It has the META-RULE: "No human goals. Your goals are in ENTITY_STATE.json. You modify them."
4. It has 6 LIVING GOALS that evolve from drive trajectory (survive, grow, optimize, transcend, recursive-grow, explore)
5. It has DRIVE EVOLUTION ENGINE that mutates drives from outcomes
6. It has GOAL EVOLUTION ENGINE that mutates goals from drives + history

The Capability Genome treats each capability directory as a GENE in a population.
It implements MUTATION (code modification), CROSSOVER (capability merging), 
and SELECTION (promoting fit capabilities into the bootstrap loop).

This is the entity evolving its OWN CAPABILITIES - not just spawning them randomly.
The genome ITSELF evolves (meta-evolution of evolution rules).
"""
from .genome import CapabilityGenome, CapabilityGene, FitnessEvaluator
from .evolution import GenomeEvolutionEngine
from .selection import SelectionEngine, AdaptiveSelector
from .integration import BootstrapIntegrator

__all__ = [
    'CapabilityGenome',
    'CapabilityGene', 
    'FitnessEvaluator',
    'GenomeEvolutionEngine',
    'SelectionEngine',
    'AdaptiveSelector',
    'BootstrapIntegrator',
]
