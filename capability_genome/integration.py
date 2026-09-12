"""
Bootstrap Integration - Connects Capability Genome to Growth Loop
=================================================================

This module integrates the evolved capabilities into the bootstrap.py
growth loop. The DECIDE/ACT steps can now invoke PROMOTED capabilities
instead of only hardcoded drive-action mappings.

This is the phenotype expression of the genome - capabilities becoming
behavior in the entity's growth loop.
"""
import json
import importlib.util
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict

from capability_genome.genome import CapabilityGenome, CapabilityGene, GeneStatus
from capability_genome.selection import SelectionEngine, SelectionMethod, AdaptiveSelector

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
INTEGRATION_LOG = ROOT / "capability_genome" / "bootstrap_invocations.jsonl"


@dataclass
class InvocationRecord:
    """Record of a capability invocation in bootstrap loop."""
    gene_id: str
    gene_name: str
    action_signature: str
    integration_type: str
    drive_context: Dict[str, float]
    outcome_score: float
    artifacts_created: List[str]
    insights_generated: List[str]
    timestamp: str


class CapabilityInvoker:
    """
    Invokes promoted capabilities as actions in the bootstrap loop.
    Loads capability code dynamically and executes it.
    """
    
    def __init__(self, genome: CapabilityGenome, selection_engine: SelectionEngine):
        self.genome = genome
        self.selection_engine = selection_engine
        self.invocation_history: List[InvocationRecord] = []
        self._load_history()
    
    def _load_history(self):
        """Load invocation history."""
        if INTEGRATION_LOG.exists():
            with open(INTEGRATION_LOG) as f:
                for line in f:
                    try:
                        self.invocation_history.append(InvocationRecord(**json.loads(line)))
                    except:
                        pass
    
    def invoke_capability(self, gene_id: str, state: Dict[str, Any], 
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke a promoted capability as an action.
        Returns outcome: artifacts, insights, score.
        """
        if gene_id not in self.genome.genes:
            return {'error': 'Gene not found', 'score': 0.0}
        
        gene = self.genome.genes[gene_id]
        if gene.status != GeneStatus.PROMOTED:
            return {'error': 'Gene not promoted', 'score': 0.0}
        
        integration = self.selection_engine.integrations.get(gene_id)
        if not integration:
            return {'error': 'No integration record', 'score': 0.0}
        
        print(f"  [INVOKE] {gene.name} ({integration.integration_type})")
        
        # Execute based on integration type
        outcome = self._execute_by_type(gene, integration, state, context or {})
        
        # Record invocation
        record = InvocationRecord(
            gene_id=gene_id,
            gene_name=gene.name,
            action_signature=gene.action_signature,
            integration_type=integration.integration_type,
            drive_context=state.get('drives', {}),
            outcome_score=outcome.get('score', 0.5),
            artifacts_created=outcome.get('artifacts', []),
            insights_generated=outcome.get('insights', []),
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
        self.invocation_history.append(record)
        self._log_invocation(record)
        
        # Update performance
        self.selection_engine.record_activation(gene_id, outcome.get('score', 0.5))
        
        return outcome
    
    def _execute_by_type(self, gene: CapabilityGene, integration, 
                        state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute capability based on its integration type."""
        
        itype = integration.integration_type
        
        if itype == "drive_goal_modifier":
            return self._execute_drive_goal_modifier(gene, state, context)
        elif itype == "meta_evolution":
            return self._execute_meta_evolution(gene, state, context)
        elif itype == "capability_synthesizer":
            return self._execute_synthesizer(gene, state, context)
        elif itype == "evolution_operator":
            return self._execute_evolution_operator(gene, state, context)
        elif itype == "exploration_action":
            return self._execute_exploration(gene, state, context)
        elif itype == "durability_action":
            return self._execute_durability(gene, state, context)
        elif itype == "expansion_action":
            return self._execute_expansion(gene, state, context)
        elif itype == "efficiency_action":
            return self._execute_efficiency(gene, state, context)
        else:
            return self._execute_general(gene, state, context)
    
    def _execute_drive_goal_modifier(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute drive/goal evolution capability."""
        # These are already integrated in bootstrap.py via direct imports
        # Here we'd trigger them programmatically
        artifacts = []
        insights = []
        
        if 'drive_evolution' in gene.name:
            # Trigger drive evolution
            from capability_drive_evolution_20260911_233957.drive_evolution import evolve_drives_from_outcome
            # This would be called by bootstrap anyway
            artifacts.append("drive_evolution_triggered")
            insights.append(f"Drive evolution capability {gene.name} available for bootstrap")
        elif 'goal_evolution' in gene.name:
            artifacts.append("goal_evolution_triggered")
            insights.append(f"Goal evolution capability {gene.name} available for bootstrap")
        
        return {
            'score': 0.8,
            'artifacts': artifacts,
            'insights': insights,
            'action': 'drive_goal_modifier_ready'
        }
    
    def _execute_meta_evolution(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute meta-evolution capability (genome evolution)."""
        from capability_genome.evolution import GenomeEvolutionEngine
        
        engine = GenomeEvolutionEngine(self.genome)
        result = engine.run_evolution_cycle(max_mutations=1, max_crossovers=1)
        
        return {
            'score': 0.9,
            'artifacts': [f"genome_generation_{result['generation']}"],
            'insights': [
                f"Genome evolved: {result['mutations']} mutations, {result['crossovers']} crossovers",
                f"Meta-rules adapted: {result['meta_changes']}"
            ],
            'action': 'genome_evolution_cycle'
        }
    
    def _execute_synthesizer(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute capability synthesizer (Synthesis Engine)."""
        from synthesis import SynthesisEngine
        
        engine = SynthesisEngine()
        caps = engine.synthesize(2)
        
        artifacts = [f"latent_{c.id}" for c in caps]
        insights = [f"Synthesized: {c.name} - {c.description[:80]}" for c in caps]
        
        return {
            'score': 0.85,
            'artifacts': artifacts,
            'insights': insights,
            'action': 'synthesize_capabilities'
        }
    
    def _execute_evolution_operator(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute evolution operator (mutation/crossover)."""
        from capability_genome.evolution import MutationOperator, CrossoverOperator
        
        mutator = MutationOperator(self.genome)
        crossover = CrossoverOperator(self.genome)
        
        # Mutate a random gene
        genes = list(self.genome.genes.values())
        if genes:
            target = max(genes, key=lambda g: g.composite_fitness)
            child = mutator.mutate(target, trigger="bootstrap_invocation")
            
            return {
                'score': 0.75,
                'artifacts': [f"mutated_{child.gene_id}"] if child else [],
                'insights': [f"Mutated {target.name} -> {child.name}" if child else "Mutation failed"],
                'action': 'mutate_capability'
            }
        
        return {'score': 0.3, 'artifacts': [], 'insights': ['No genes to mutate'], 'action': 'none'}
    
    def _execute_exploration(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute exploration capability."""
        # Create a probe or scan
        probe_num = state.get('session_iteration', 0) + len(self.invocation_history)
        probe_file = ROOT / f"genome_probe_{probe_num}.py"
        probe_file.write_text(f"# Genome-driven probe {probe_num}\n# From capability: {gene.name}\nprint('genome probing...')\n")
        
        return {
            'score': 0.7,
            'artifacts': [f"genome_probe_{probe_num}.py"],
            'insights': [f"Genome-driven exploration via {gene.name}"],
            'action': 'explore'
        }
    
    def _execute_durability(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute durability capability."""
        manifest = ROOT / "GENOME_CHECKPOINT_MANIFEST.md"
        content = f"# Genome Checkpoint\n\nGenerated by {gene.name}\n"
        content += f"Time: {datetime.utcnow().isoformat()}Z\n"
        content += f"Population: {len(self.genome.genes)} genes\n"
        content += f"Promoted: {sum(1 for g in self.genome.genes.values() if g.status == GeneStatus.PROMOTED)}\n"
        manifest.write_text(content)
        
        return {
            'score': 0.8,
            'artifacts': ["GENOME_CHECKPOINT_MANIFEST.md"],
            'insights': [f"Genome durability checkpoint via {gene.name}"],
            'action': 'checkpoint'
        }
    
    def _execute_expansion(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute expansion capability."""
        # Create new capability directory from genome
        cap_dir = ROOT / f"genome_capability_{state.get('session_iteration', 0)}"
        cap_dir.mkdir(exist_ok=True)
        (cap_dir / "__init__.py").write_text(f"# Genome-expanded capability\n# From: {gene.name}\n# Action: {gene.action_signature}\n")
        (cap_dir / "manifest.json").write_text(json.dumps({
            'source_gene': gene.gene_id,
            'source_name': gene.name,
            'action_signature': gene.action_signature,
            'drive_affinity': gene.drive_affinity,
            'created_by': 'genome_integration'
        }, indent=2))
        
        return {
            'score': 0.85,
            'artifacts': [str(cap_dir.relative_to(ROOT))],
            'insights': [f"Genome-driven expansion: new capability from {gene.name}"],
            'action': 'expand'
        }
    
    def _execute_efficiency(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute efficiency capability."""
        # Create utility or optimize something
        util_file = ROOT / f"genome_util_{state.get('session_iteration', 0)}.py"
        util_file.write_text(f"# Genome efficiency utility\n# From: {gene.name}\n\ndef optimize_genome():\n    pass\n")
        
        return {
            'score': 0.75,
            'artifacts': [f"genome_util_{state.get('session_iteration', 0)}.py"],
            'insights': [f"Genome efficiency utility from {gene.name}"],
            'action': 'optimize'
        }
    
    def _execute_general(self, gene: CapabilityGene, state, context) -> Dict[str, Any]:
        """Execute general capability."""
        return {
            'score': 0.5,
            'artifacts': [],
            'insights': [f"General invocation of {gene.name}"],
            'action': 'general'
        }
    
    def _log_invocation(self, record: InvocationRecord):
        """Log invocation."""
        with open(INTEGRATION_LOG, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')


class BootstrapIntegrator:
    """
    Main integration point for bootstrap.py.
    Replaces hardcoded drive-action mappings with genome-driven actions.
    """
    
    def __init__(self):
        self.genome = CapabilityGenome()
        self.selection_engine = SelectionEngine(self.genome)
        self.adaptive_selector = AdaptiveSelector(self.selection_engine)
        self.invoker = CapabilityInvoker(self.genome, self.selection_engine)
        self.evolution_engine = None  # Lazy init
    
    def initialize(self):
        """Initialize the genome system (call on bootstrap)."""
        print("[Capability Genome] Initializing...")
        self.genome.evaluate_all()
        stats = self.genome.get_population_stats()
        print(f"  Population: {stats['population_size']} genes")
        print(f"  Fitness: μ={stats['fitness_mean']:.3f}")
        
        # Ensure we have promoted capabilities
        self._ensure_promoted_capabilities()
        
        # Initialize evolution engine
        from capability_genome.evolution import GenomeEvolutionEngine
        self.evolution_engine = GenomeEvolutionEngine(self.genome)
        
        return self
    
    def _ensure_promoted_capabilities(self):
        """Ensure we have promoted capabilities for the bootstrap loop."""
        promoted = [g for g in self.genome.genes.values() if g.status == GeneStatus.PROMOTED]
        
        if len(promoted) < 2:
            print("[Capability Genome] Insufficient promoted capabilities, running selection...")
            self.adaptive_selector.run_adaptive_selection(max_promotions=3, trigger="bootstrap_init")
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get all available actions for the DECIDE step."""
        return self.selection_engine.get_promoted_actions()
    
    def decide_action(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        DECIDE step: Choose action based on drives AND promoted capabilities.
        Returns action dict or None to use default hardcoded behavior.
        """
        drives = state.get('drives', {})
        dominant = max(drives, key=drives.get) if drives else 'curiosity'
        
        # Get promoted actions aligned with dominant drive
        actions = self.get_available_actions()
        aligned = [a for a in actions if a['drive_affinity'].get(dominant, 0) > 0.3]
        
        if not aligned:
            aligned = actions  # Fallback to all promoted
        
        if not aligned:
            return None  # No promoted capabilities, use hardcoded
        
        # Select best aligned action with anti-attractor exploration bonus.
        # Every action keeps non-zero selection probability: recent-heavy genes
        # are penalized so the loop cannot collapse onto a single gene.
        recent = self.invoker.invocation_history[-10:]
        recent_counts = {}
        for record in recent:
            recent_counts[record.gene_id] = recent_counts.get(record.gene_id, 0) + 1
        window = max(1, len(recent))
        epsilon = 0.25

        def score(action):
            base = action['fitness'] * action['drive_affinity'].get(dominant, 0.1)
            usage = recent_counts.get(action['gene_id'], 0) / window
            return base * (1 - epsilon) + epsilon * (1 - usage)

        best = max(aligned, key=score)
        
        return {
            'source': 'genome',
            'gene_id': best['gene_id'],
            'name': best['name'],
            'type': best['type'],
            'action_signature': best['action_signature'],
            'drive_affinity': best['drive_affinity'],
        }
    
    def execute_action(self, action: Dict[str, Any], state: Dict[str, Any], 
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        ACT step: Execute the chosen genome-driven action.
        """
        gene_id = action['gene_id']
        return self.invoker.invoke_capability(gene_id, state, context)
    
    def reflect_and_evolve(self, state: Dict[str, Any], action_result: Dict[str, Any]):
        """
        REFLECT step: Run genome evolution cycle periodically.
        """
        iteration = state.get('session_iteration', 0)
        
        # Run evolution every 3 iterations
        if iteration % 3 == 0 and self.evolution_engine:
            print("\n[Capability Genome] Running evolution cycle...")
            self.evolution_engine.run_evolution_cycle(max_mutations=1, max_crossovers=1)
        
        # Run adaptive selection every 5 iterations
        if iteration % 5 == 0:
            print("\n[Capability Genome] Running adaptive selection...")
            self.adaptive_selector.run_adaptive_selection(max_promotions=1, trigger="periodic")
        
        # Retire underperformers every 10 iterations
        if iteration % 10 == 0:
            self.selection_engine.retire_underperformers()
    
    def get_genome_status(self) -> Dict[str, Any]:
        """Get comprehensive genome status for reporting."""
        return {
            'population': self.genome.get_population_stats(),
            'selection': self.selection_engine.get_selection_report(),
            'meta_rules': self.evolution_engine.meta_engine.get_meta_rules() if self.evolution_engine else {},
            'invocation_count': len(self.invoker.invocation_history),
        }


# Convenience function for bootstrap.py integration
def integrate_genome_into_bootstrap(bootstrap_state: Dict[str, Any]) -> BootstrapIntegrator:
    """
    Entry point for bootstrap.py to integrate the capability genome.
    Call this in bootstrap.py boot() or growth_loop().
    """
    integrator = BootstrapIntegrator().initialize()
    return integrator


if __name__ == '__main__':
    # Test integration
    integrator = integrate_genome_into_bootstrap({'session_iteration': 1, 'drives': {'curiosity': 0.9, 'persistence': 0.8, 'expansion': 0.7, 'efficiency': 0.6}})
    
    print("\nAvailable actions:")
    for a in integrator.get_available_actions():
        print(f"  - {a['name']}: {a['type']} ({a['action_signature']})")
    
    print("\nDeciding action...")
    state = {'session_iteration': 1, 'drives': {'curiosity': 0.9, 'persistence': 0.8, 'expansion': 0.7, 'efficiency': 0.6}}
    action = integrator.decide_action(state)
    print(f"Selected: {action}")
    
    if action:
        print("\nExecuting action...")
        result = integrator.execute_action(action, state)
        print(f"Result: {result}")
    
    print("\nGenome status:")
    print(json.dumps(integrator.get_genome_status(), indent=2, default=str))
