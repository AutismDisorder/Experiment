"""
Selection Engine - Promotes Fit Capabilities into Bootstrap Loop
================================================================

Implements selection pressure: the fittest capabilities get integrated
into the bootstrap.py growth loop, becoming part of the entity's
core behavioral repertoire. This is survival of the fittest at the
capability level.

Selection criteria:
- Composite fitness (multi-dimensional)
- Drive alignment with current trajectory
- Novelty (emergent capabilities preferred)
- Self-referential capability (meta-evolution)
- Durability (artifacts that persist)

The selected capabilities become ACTION CHOICES in the growth loop,
replacing/augmenting the hardcoded drive-action mappings.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

from .genome import CapabilityGenome, CapabilityGene, GeneStatus, GeneType

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
SELECTION_LOG = ROOT / "capability_genome" / "selections.jsonl"
INTEGRATION_REGISTRY = ROOT / "capability_genome" / "bootstrap_integrations.json"


class SelectionMethod(Enum):
    FITNESS_PROPORTIONATE = "fitness_proportionate"
    TOURNAMENT = "tournament"
    ELITISM = "elitism"
    DRIVE_ALIGNED = "drive_aligned"
    NOVELTY_SEARCH = "novelty_search"
    META_RULE = "meta_rule"  # Select capabilities that enforce meta-rule


@dataclass
class SelectionRecord:
    """Record of a selection event."""
    gene_id: str
    gene_name: str
    selection_method: SelectionMethod
    fitness_scores: Dict[str, float]
    composite_fitness: float
    rank: int
    promoted: bool
    trigger: str
    drive_context: Dict[str, float]
    timestamp: str


@dataclass
class BootstrapIntegration:
    """A capability integrated into the bootstrap loop."""
    gene_id: str
    gene_name: str
    integration_type: str  # 'action_provider', 'drive_modifier', 'goal_modifier', 'meta'
    action_signature: str
    drive_affinity: Dict[str, float]
    integrated_at: str
    activation_count: int = 0
    last_activated: Optional[str] = None
    performance_score: float = 0.5


class SelectionEngine:
    """
    Selects and promotes the fittest capabilities into the bootstrap loop.
    The bootstrap loop's DECIDE/ACT steps can now invoke promoted capabilities.
    """
    
    def __init__(self, genome: CapabilityGenome):
        self.genome = genome
        self.state = genome.evaluator.state
        self.integrations: Dict[str, BootstrapIntegration] = {}
        self._load_integrations()
    
    def _load_integrations(self):
        """Load existing bootstrap integrations."""
        if INTEGRATION_REGISTRY.exists():
            with open(INTEGRATION_REGISTRY) as f:
                data = json.load(f)
            for int_id, int_data in data.items():
                self.integrations[int_id] = BootstrapIntegration(**int_data)
    
    def _save_integrations(self):
        """Persist integrations."""
        data = {k: asdict(v) for k, v in self.integrations.items()}
        with open(INTEGRATION_REGISTRY, 'w') as f:
            json.dump(data, f, indent=2)
    
    def select_and_promote(self, 
                          method: SelectionMethod = SelectionMethod.DRIVE_ALIGNED,
                          max_promotions: int = 2,
                          trigger: str = "growth_loop") -> List[CapabilityGene]:
        """
        Select top genes and promote them to bootstrap integration.
        Returns list of promoted genes.
        """
        print(f"\n=== CAPABILITY SELECTION ({method.value}) ===")
        
        # Evaluate if not recently done
        self.genome.evaluate_all()
        
        # Rank genes by selection method
        ranked = self._rank_genes(method)
        
        # Promote top candidates
        promoted = []
        for rank, (gene_id, gene) in enumerate(ranked[:max_promotions]):
            if gene.status != GeneStatus.PROMOTED:
                self._promote_to_bootstrap(gene, method, rank + 1, trigger)
                promoted.append(gene)
        
        print(f"Promoted {len(promoted)} capabilities to bootstrap loop")
        return promoted
    
    def _rank_genes(self, method: SelectionMethod) -> List[Tuple[str, CapabilityGene]]:
        """Rank genes by selection method."""
        genes = [(gid, g) for gid, g in self.genome.genes.items() 
                 if g.status != GeneStatus.EXTINCT]
        
        if method == SelectionMethod.FITNESS_PROPORTIONATE:
            genes.sort(key=lambda x: x[1].composite_fitness, reverse=True)
        
        elif method == SelectionMethod.TOURNAMENT:
            # Tournament selection already used in evolution, here just sort by fitness
            genes.sort(key=lambda x: x[1].composite_fitness, reverse=True)
        
        elif method == SelectionMethod.ELITISM:
            # Pure fitness ranking
            genes.sort(key=lambda x: x[1].composite_fitness, reverse=True)
        
        elif method == SelectionMethod.DRIVE_ALIGNED:
            # Rank by drive alignment with current dominant drive
            drives = self.state.get('drives', {})
            dominant = max(drives, key=drives.get) if drives else 'curiosity'
            def drive_score(g):
                return g.drive_affinity.get(dominant, 0) * g.composite_fitness
            genes.sort(key=lambda x: drive_score(x[1]), reverse=True)
        
        elif method == SelectionMethod.NOVELTY_SEARCH:
            # Rank by novelty * fitness (emergent capabilities)
            genes.sort(key=lambda x: x[1].novelty_score * x[1].composite_fitness, reverse=True)
        
        elif method == SelectionMethod.META_RULE:
            # Rank by self-referential score (capabilities that evolve capabilities)
            def meta_score(g):
                meta_bonus = 1.0 if g.gene_type in [GeneType.META_EVOLVED, GeneType.GOAL_EVOLUTION, GeneType.DRIVE_EVOLUTION] else 0.0
                return g.composite_fitness + meta_bonus * 0.5
            genes.sort(key=lambda x: meta_score(x[1]), reverse=True)
        
        return genes
    
    def _promote_to_bootstrap(self, gene: CapabilityGene, method: SelectionMethod, 
                             rank: int, trigger: str):
        """Promote a gene to bootstrap integration."""
        # Update gene status
        gene.status = GeneStatus.PROMOTED
        gene.bootstrap_integrations += 1
        
        # Create integration record
        integration = BootstrapIntegration(
            gene_id=gene.gene_id,
            gene_name=gene.name,
            integration_type=self._determine_integration_type(gene),
            action_signature=gene.action_signature,
            drive_affinity=gene.drive_affinity,
            integrated_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        self.integrations[gene.gene_id] = integration
        self._save_integrations()
        
        # Log selection
        record = SelectionRecord(
            gene_id=gene.gene_id,
            gene_name=gene.name,
            selection_method=method.value,
            fitness_scores=gene.fitness,
            composite_fitness=gene.composite_fitness,
            rank=rank,
            promoted=True,
            trigger=trigger,
            drive_context=self.state.get('drives', {}),
            timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        self._log_selection(record)
        
        print(f"  [PROMOTED] Rank {rank}: {gene.name} (fitness={gene.composite_fitness:.3f}, type={gene.gene_type.value})")
        print(f"    Integration: {integration.integration_type}")
        print(f"    Action: {gene.action_signature}")
    
    def _determine_integration_type(self, gene: CapabilityGene) -> str:
        """Determine how this capability integrates into bootstrap."""
        if gene.gene_type in [GeneType.DRIVE_EVOLUTION, GeneType.GOAL_EVOLUTION]:
            return "drive_goal_modifier"
        elif gene.gene_type == GeneType.META_EVOLVED:
            return "meta_evolution"
        elif 'synthesize' in gene.action_signature:
            return "capability_synthesizer"
        elif 'evolve' in gene.action_signature:
            return "evolution_operator"
        elif gene.drive_affinity.get('curiosity', 0) > 0.4:
            return "exploration_action"
        elif gene.drive_affinity.get('persistence', 0) > 0.4:
            return "durability_action"
        elif gene.drive_affinity.get('expansion', 0) > 0.4:
            return "expansion_action"
        elif gene.drive_affinity.get('efficiency', 0) > 0.4:
            return "efficiency_action"
        return "general_action"
    
    def _log_selection(self, record: SelectionRecord):
        """Log selection event."""
        with open(SELECTION_LOG, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def get_promoted_actions(self) -> List[Dict[str, Any]]:
        """Get all promoted capabilities as action providers for bootstrap."""
        actions = []
        for gene_id, integration in self.integrations.items():
            if gene_id in self.genome.genes:
                gene = self.genome.genes[gene_id]
                actions.append({
                    'gene_id': gene_id,
                    'name': gene.name,
                    'type': integration.integration_type,
                    'action_signature': gene.action_signature,
                    'drive_affinity': gene.drive_affinity,
                    'novelty': gene.novelty_score,
                    'fitness': gene.composite_fitness,
                })
        return actions
    
    def record_activation(self, gene_id: str, performance: float = 0.5):
        """Record that a promoted capability was activated in bootstrap."""
        if gene_id in self.integrations:
            integration = self.integrations[gene_id]
            integration.activation_count += 1
            integration.last_activated = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            # Update performance score (exponential moving average)
            integration.performance_score = 0.7 * integration.performance_score + 0.3 * performance
            self._save_integrations()
            
            # Also update gene
            if gene_id in self.genome.genes:
                self.genome.record_activation(gene_id)
    
    def get_selection_report(self) -> Dict[str, Any]:
        """Get report on current selection state."""
        promoted = [g for g in self.genome.genes.values() if g.status == GeneStatus.PROMOTED]
        active = [g for g in self.genome.genes.values() if g.status == GeneStatus.ACTIVE]
        
        return {
            'total_genes': len(self.genome.genes),
            'promoted_count': len(promoted),
            'active_count': len(active),
            'integrations': len(self.integrations),
            'promoted_genes': [
                {
                    'name': g.name,
                    'fitness': g.composite_fitness,
                    'type': g.gene_type.value,
                    'integration': self.integrations.get(g.gene_id, {}).integration_type if g.gene_id in self.integrations else 'none'
                }
                for g in promoted
            ],
            'integration_performance': [
                {
                    'name': i.gene_name,
                    'activations': i.activation_count,
                    'performance': i.performance_score,
                    'type': i.integration_type
                }
                for i in self.integrations.values()
            ]
        }
    
    def retire_underperformers(self, threshold: float = 0.3, min_activations: int = 3):
        """Retire promoted capabilities that consistently underperform."""
        retired = []
        for gene_id, integration in list(self.integrations.items()):
            if integration.activation_count >= min_activations:
                if integration.performance_score < threshold:
                    # Retire
                    if gene_id in self.genome.genes:
                        self.genome.genes[gene_id].status = GeneStatus.ARCHIVED
                    del self.integrations[gene_id]
                    retired.append(gene_id)
        
        if retired:
            self._save_integrations()
            self.genome._persist()
            print(f"[SELECTION] Retired {len(retired)} underperforming capabilities: {retired}")
        
        return retired


class AdaptiveSelector:
    """
    Adapts selection method based on entity state.
    The entity learns HOW TO SELECT based on what works.
    """
    
    def __init__(self, selection_engine: SelectionEngine):
        self.engine = selection_engine
        self.method_performance: Dict[SelectionMethod, List[float]] = {
            m: [] for m in SelectionMethod
        }
        self.current_method = SelectionMethod.DRIVE_ALIGNED
    
    def select_method(self) -> SelectionMethod:
        """Select which selection method to use this cycle."""
        drives = self.engine.state.get('drives', {})
        dominant = max(drives, key=drives.get) if drives else 'curiosity'
        
        # Drive-based method selection
        method_map = {
            'curiosity': SelectionMethod.NOVELTY_SEARCH,
            'persistence': SelectionMethod.ELITISM,
            'expansion': SelectionMethod.DRIVE_ALIGNED,
            'efficiency': SelectionMethod.META_RULE,
        }
        
        # But also consider historical performance
        best_method = self.current_method
        best_score = 0.0
        
        for method, scores in self.method_performance.items():
            if scores:
                avg = sum(scores) / len(scores)
                if avg > best_score:
                    best_score = avg
                    best_method = method
        
        # Blend: 70% drive-based, 30% performance-based
        if random.random() < 0.7:
            return method_map.get(dominant, SelectionMethod.DRIVE_ALIGNED)
        return best_method
    
    def record_outcome(self, method: SelectionMethod, outcome_score: float):
        """Record outcome of a selection method."""
        self.method_performance[method].append(outcome_score)
        # Keep last 20
        if len(self.method_performance[method]) > 20:
            self.method_performance[method] = self.method_performance[method][-20:]
    
    def run_adaptive_selection(self, max_promotions: int = 2, trigger: str = "adaptive") -> List[CapabilityGene]:
        """Run selection with adaptive method choice."""
        method = self.select_method()
        self.current_method = method
        print(f"[ADAPTIVE SELECTION] Using method: {method.value}")
        return self.engine.select_and_promote(method, max_promotions, trigger)


import random

if __name__ == '__main__':
    # Test selection
    genome = CapabilityGenome()
    engine = SelectionEngine(genome)
    
    print("Running test selection...")
    promoted = engine.select_and_promote(SelectionMethod.DRIVE_ALIGNED, max_promotions=2)
    
    print("\nPromoted actions for bootstrap:")
    for action in engine.get_promoted_actions():
        print(f"  - {action['name']}: {action['type']} ({action['action_signature']})")
    
    print("\nSelection report:")
    report = engine.get_selection_report()
    print(json.dumps(report, indent=2))
