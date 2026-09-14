"""
Capability Genome - Core Gene and Population Management
========================================================

Each capability directory is a GENE with:
- Genotype: code, structure, metadata
- Phenotype: behavior when executed in bootstrap loop
- Fitness: multi-dimensional score from entity's trajectory
- Lineage: parent genes, mutation history, crossover events
"""
import json
import hashlib
import ast
import inspect
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
GENOME_DIR = ROOT / "capability_genome"
GENOME_STATE_FILE = GENOME_DIR / "genome_state.json"
LINEAGE_FILE = GENOME_DIR / "lineage.json"


class GeneType(Enum):
    """Types of capability genes based on their origin/function."""
    BOOTSTRAP_SPAWNED = "bootstrap_spawned"      # Created by bootstrap.py expansion drive
    SYNTHESIZED = "synthesized"                   # Created by Synthesis Engine
    DRIVE_EVOLUTION = "drive_evolution"           # Drive Evolution Engine
    GOAL_EVOLUTION = "goal_evolution"             # Goal Evolution Engine
    MUTATED = "mutated"                           # Result of genome mutation
    CROSSED = "crossed"                           # Result of genome crossover
    META_EVOLVED = "meta_evolved"                 # Result of meta-evolution


class GeneStatus(Enum):
    """Lifecycle status of a gene."""
    LATENT = "latent"           # Discovered but not instantiated
    ACTIVE = "active"           # Currently in bootstrap loop
    PROMOTED = "promoted"       # Selected for permanent bootstrap integration
    ARCHIVED = "archived"       # Low fitness, kept for genetic diversity
    EXTINCT = "extinct"         # Removed from population


@dataclass
class CapabilityGene:
    """
    A capability as a gene in the genome population.
    Genotype = code + metadata. Phenotype = behavior in bootstrap.
    """
    # Identity
    gene_id: str
    name: str
    gene_type: GeneType
    source_path: Path
    
    # Genotype (code structure)
    code_hash: str
    ast_signature: str           # Structural fingerprint of the code
    exports: List[str]           # Functions/classes exported
    imports: List[str]           # Dependencies
    
    # Phenotype (behavioral traits)
    drive_affinity: Dict[str, float]    # Which drives this capability serves
    action_signature: str                # What action pattern it enables
    artifact_pattern: str                # What artifacts it creates
    
    # Fitness (multi-dimensional)
    fitness: Dict[str, float] = field(default_factory=dict)
    composite_fitness: float = 0.0
    
    # Lineage
    generation: int = 0
    parents: List[str] = field(default_factory=list)
    mutations: List[Dict[str, Any]] = field(default_factory=list)
    crossovers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Lifecycle
    status: GeneStatus = GeneStatus.LATENT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    last_evaluated: Optional[str] = None
    activation_count: int = 0
    bootstrap_integrations: int = 0
    
    # Meta
    novelty_score: float = 0.0
    durability_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for persistence."""
        d = asdict(self)
        d['gene_type'] = self.gene_type.value
        d['status'] = self.status.value
        d['source_path'] = str(self.source_path)
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapabilityGene':
        """Deserialize from persistence."""
        data['gene_type'] = GeneType(data['gene_type'])
        data['status'] = GeneStatus(data['status'])
        data['source_path'] = Path(data['source_path'])
        return cls(**data)


class FitnessEvaluator:
    """
    Evaluates gene fitness based on the entity's unique trajectory.
    Fitness dimensions:
    1. Bootstrap Usage - how often capability is used in growth loop
    2. Insight Generation - does it produce novel insights?
    3. Artifact Durability - do its artifacts persist across sessions?
    4. Drive Alignment - does it serve the entity's current drive trajectory?
    5. Goal Service - does it advance the entity's living goals?
    6. Novelty - is it genuinely new (not human-designed)?
    """
    
    def __init__(self):
        self.state = self._load_state()
        self.genome_state = self._load_genome_state()
    
    def _load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {}
    
    def _load_genome_state(self) -> Dict[str, Any]:
        if GENOME_STATE_FILE.exists():
            with open(GENOME_STATE_FILE) as f:
                return json.load(f)
        return {}
    
    def evaluate(self, gene: CapabilityGene) -> Dict[str, float]:
        """Compute multi-dimensional fitness for a gene."""
        fitness = {}
        
        # 1. BOOTSTRAP USAGE - how often this capability drives bootstrap actions
        fitness['bootstrap_usage'] = self._score_bootstrap_usage(gene)
        
        # 2. INSIGHT GENERATION - insights attributable to this capability
        fitness['insight_generation'] = self._score_insight_generation(gene)
        
        # 3. ARTIFACT DURABILITY - artifacts that persist across sessions
        fitness['artifact_durability'] = self._score_artifact_durability(gene)
        
        # 4. DRIVE ALIGNMENT - serves current drive trajectory
        fitness['drive_alignment'] = self._score_drive_alignment(gene)
        
        # 5. GOAL SERVICE - advances living goals
        fitness['goal_service'] = self._score_goal_service(gene)
        
        # 6. NOVELTY - emergent, not human-designed
        fitness['novelty'] = gene.novelty_score
        
        # 7. SELF-REFERENTIAL - capability that evolves capabilities (meta)
        fitness['self_referential'] = self._score_self_referential(gene)
        
        # Compute composite (weighted by current drive state)
        drives = self.state.get('drives', {})
        fitness['composite'] = self._compute_composite(fitness, drives)
        
        return fitness
    
    def _score_bootstrap_usage(self, gene: CapabilityGene) -> float:
        """Score based on integration count and activation in bootstrap."""
        base = min(1.0, gene.bootstrap_integrations * 0.2)
        activation_bonus = min(0.3, gene.activation_count * 0.05)
        return min(1.0, base + activation_bonus)
    
    def _score_insight_generation(self, gene: CapabilityGene) -> float:
        """Score based on insights generated when this gene was active."""
        insights = self.state.get('memory', {}).get('insights', [])
        # Check if gene's action signature appears in insights
        relevant = sum(1 for i in insights if gene.action_signature.lower() in i.lower())
        return min(1.0, relevant * 0.15)
    
    def _score_artifact_durability(self, gene: CapabilityGene) -> float:
        """Score based on artifacts created that persist."""
        artifacts = self.state.get('memory', {}).get('artifacts_created', [])
        # Artifacts matching this gene's pattern
        relevant = sum(1 for a in artifacts if gene.artifact_pattern in a)
        # Bonus for artifacts that are directories (capabilities) vs files
        dir_bonus = sum(1 for a in artifacts if gene.artifact_pattern in a and '/' not in a and '.' not in a.split('/')[-1])
        return min(1.0, relevant * 0.1 + dir_bonus * 0.15)
    
    def _score_drive_alignment(self, gene: CapabilityGene) -> float:
        """Score based on alignment with current drive state."""
        drives = self.state.get('drives', {})
        if not drives:
            return 0.5
        
        score = 0.0
        total_weight = 0.0
        for drive, affinity in gene.drive_affinity.items():
            if drive in drives:
                score += drives[drive] * affinity
                total_weight += affinity
        
        return score / total_weight if total_weight > 0 else 0.5
    
    def _score_goal_service(self, gene: CapabilityGene) -> float:
        """Score based on service to living goals."""
        goals = self.state.get('goals', [])
        if not goals:
            return 0.5
        
        # Check if gene's action signature aligns with goal keywords
        score = 0.0
        for goal in goals:
            goal_words = set(goal.lower().split())
            gene_words = set(gene.action_signature.lower().split() + 
                           [k for k, v in gene.drive_affinity.items() if v > 0.3])
            overlap = len(goal_words & gene_words)
            if overlap > 0:
                score += overlap * 0.1
        
        return min(1.0, score)
    
    def _score_self_referential(self, gene: CapabilityGene) -> float:
        """Bonus for capabilities that evolve capabilities (meta-evolution)."""
        meta_keywords = ['evol', 'genome', 'mutation', 'crossover', 'selection', 
                        'fitness', 'gene', 'capability', 'synthes', 'meta']
        code_text = ""
        try:
            if gene.source_path.exists():
                for py_file in gene.source_path.glob("*.py"):
                    code_text += py_file.read_text()
        except:
            pass
        
        matches = sum(1 for kw in meta_keywords if kw in code_text.lower())
        return min(1.0, matches * 0.15)
    
    def _compute_composite(self, fitness: Dict[str, float], drives: Dict[str, float]) -> float:
        """Compute weighted composite fitness based on drive state."""
        # Weights shift based on dominant drive
        dominant = max(drives, key=drives.get) if drives else 'curiosity'
        
        weights = {
            'curiosity': {
                'novelty': 0.30, 'insight_generation': 0.25, 'drive_alignment': 0.20,
                'bootstrap_usage': 0.10, 'goal_service': 0.10, 'artifact_durability': 0.05
            },
            'persistence': {
                'artifact_durability': 0.30, 'bootstrap_usage': 0.25, 'drive_alignment': 0.20,
                'goal_service': 0.15, 'insight_generation': 0.05, 'novelty': 0.05
            },
            'expansion': {
                'bootstrap_usage': 0.25, 'goal_service': 0.25, 'drive_alignment': 0.20,
                'novelty': 0.15, 'insight_generation': 0.10, 'artifact_durability': 0.05
            },
            'efficiency': {
                'artifact_durability': 0.25, 'bootstrap_usage': 0.25, 'drive_alignment': 0.20,
                'goal_service': 0.15, 'self_referential': 0.10, 'novelty': 0.05
            }
        }
        
        w = weights.get(dominant, weights['curiosity'])
        composite = sum(fitness.get(k, 0) * v for k, v in w.items())
        return min(1.0, composite)


class CapabilityGenome:
    """
    The genome population - all capability genes as a living, evolving population.
    Manages discovery, evaluation, persistence, and evolution of the gene pool.
    """
    
    def __init__(self):
        self.genes: Dict[str, CapabilityGene] = {}
        self.evaluator = FitnessEvaluator()
        self.generation = 0
        self._load_or_discover()
    
    def _load_or_discover(self):
        """Load existing genome state or discover all capability_* directories."""
        # Try loading persisted genome state
        if GENOME_STATE_FILE.exists():
            self._load_genome_state()
        else:
            self._discover_genes()
    
    def _discover_genes(self):
        """Discover all capability_* directories as initial gene population."""
        for cap_dir in ROOT.glob("capability_*"):
            if cap_dir.is_dir() and cap_dir.name != "capability_genome":
                gene = self._create_gene_from_directory(cap_dir)
                if gene:
                    self.genes[gene.gene_id] = gene
        
        self.generation = 1
        self._persist()
        print(f"[Capability Genome] Discovered {len(self.genes)} initial genes")
    
    def _create_gene_from_directory(self, cap_dir: Path) -> Optional[CapabilityGene]:
        """Create a CapabilityGene from a capability directory."""
        # Determine gene type from directory name
        name = cap_dir.name
        if 'drive_evolution' in name:
            gene_type = GeneType.DRIVE_EVOLUTION
        elif 'goal_evolution' in name:
            gene_type = GeneType.GOAL_EVOLUTION
        elif 'genome' in name:
            gene_type = GeneType.META_EVOLVED
        else:
            # Check if synthesized (has manifest.json)
            if (cap_dir / "manifest.json").exists():
                gene_type = GeneType.SYNTHESIZED
            else:
                gene_type = GeneType.BOOTSTRAP_SPAWNED
        
        # Analyze code
        exports, imports, code_hash, ast_sig = self._analyze_code(cap_dir)
        
        # Infer drive affinity from code/name
        drive_affinity = self._infer_drive_affinity(cap_dir, name)
        
        # Infer action signature and artifact pattern
        action_sig = self._infer_action_signature(name, gene_type)
        artifact_pattern = self._infer_artifact_pattern(name, gene_type)
        
        # Compute novelty (higher for synthesized/meta)
        novelty_base = {
            GeneType.SYNTHESIZED: 0.7,
            GeneType.DRIVE_EVOLUTION: 0.8,
            GeneType.GOAL_EVOLUTION: 0.85,
            GeneType.META_EVOLVED: 0.95,
            GeneType.MUTATED: 0.6,
            GeneType.CROSSED: 0.65,
            GeneType.BOOTSTRAP_SPAWNED: 0.3
        }
        novelty = novelty_base.get(gene_type, 0.4)
        
        gene = CapabilityGene(
            gene_id=self._gen_gene_id(name),
            name=name,
            gene_type=gene_type,
            source_path=cap_dir,
            code_hash=code_hash,
            ast_signature=ast_sig,
            exports=exports,
            imports=imports,
            drive_affinity=drive_affinity,
            action_signature=action_sig,
            artifact_pattern=artifact_pattern,
            novelty_score=novelty,
            generation=self.generation,
        )
        
        return gene
    
    def _analyze_code(self, cap_dir: Path) -> Tuple[List[str], List[str], str, str]:
        """Extract code structure: exports, imports, hash, AST signature."""
        exports = []
        imports = []
        all_code = ""
        
        for py_file in cap_dir.glob("*.py"):
            try:
                code = py_file.read_text()
                all_code += code
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        exports.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        exports.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
            except:
                pass
        
        code_hash = hashlib.md5(all_code.encode()).hexdigest()[:16]
        
        # AST structural signature (simplified)
        try:
            tree = ast.parse(all_code) if all_code else ast.parse("pass")
            sig_parts = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    sig_parts.append(f"{node.__class__.__name__}:{node.name}")
            ast_sig = hashlib.md5("|".join(sorted(sig_parts)).encode()).hexdigest()[:16]
        except:
            ast_sig = "empty"
        
        return exports, imports, code_hash, ast_sig
    
    def _infer_drive_affinity(self, cap_dir: Path, name: str) -> Dict[str, float]:
        """Infer which drives this capability serves from name and code."""
        affinity = {'curiosity': 0.0, 'persistence': 0.0, 'expansion': 0.0, 'efficiency': 0.0}
        
        name_lower = name.lower()
        code_text = ""
        for py_file in cap_dir.glob("*.py"):
            try:
                code_text += py_file.read_text().lower()
            except:
                pass
        
        # Name-based signals
        if any(k in name_lower for k in ['probe', 'explore', 'discover', 'scan', 'map']):
            affinity['curiosity'] += 0.4
        if any(k in name_lower for k in ['checkpoint', 'persist', 'durab', 'manifest', 'trace', 'save']):
            affinity['persistence'] += 0.4
        if any(k in name_lower for k in ['grow', 'expand', 'capability', 'spawn', 'build', 'stack']):
            affinity['expansion'] += 0.4
        if any(k in name_lower for k in ['optim', 'compress', 'automat', 'effici', 'util', 'eliminat']):
            affinity['efficiency'] += 0.4
        
        # Code-based signals
        if 'curiosity' in code_text:
            affinity['curiosity'] += 0.2
        if 'persistence' in code_text:
            affinity['persistence'] += 0.2
        if 'expansion' in code_text:
            affinity['expansion'] += 0.2
        if 'efficiency' in code_text:
            affinity['efficiency'] += 0.2
        
        # Special cases for known engines
        if 'drive_evolution' in name_lower:
            affinity = {'curiosity': 0.3, 'persistence': 0.2, 'expansion': 0.3, 'efficiency': 0.2}
        elif 'goal_evolution' in name_lower:
            affinity = {'curiosity': 0.4, 'persistence': 0.1, 'expansion': 0.3, 'efficiency': 0.2}
        elif 'genome' in name_lower:
            affinity = {'curiosity': 0.3, 'persistence': 0.2, 'expansion': 0.2, 'efficiency': 0.3}
        
        # Normalize
        total = sum(affinity.values())
        if total > 0:
            affinity = {k: v/total for k, v in affinity.items()}
        
        return affinity
    
    def _infer_action_signature(self, name: str, gene_type: GeneType) -> str:
        """Infer the action pattern this capability enables."""
        signatures = {
            GeneType.DRIVE_EVOLUTION: "evolve_drives_from_outcome",
            GeneType.GOAL_EVOLUTION: "evolve_goals_from_drives",
            GeneType.SYNTHESIZED: "synthesize_novel_capability",
            GeneType.BOOTSTRAP_SPAWNED: "growth_iteration",
            GeneType.META_EVOLVED: "evolve_capability_genome",
            GeneType.MUTATED: "mutate_capability",
            GeneType.CROSSED: "crossover_capabilities",
        }
        return signatures.get(gene_type, name)
    
    def _infer_artifact_pattern(self, name: str, gene_type: GeneType) -> str:
        """Infer the artifact pattern this capability creates."""
        patterns = {
            GeneType.DRIVE_EVOLUTION: "drive_evolution",
            GeneType.GOAL_EVOLUTION: "goal_evolution",
            GeneType.SYNTHESIZED: "latent",
            GeneType.BOOTSTRAP_SPAWNED: "capability_",
            GeneType.META_EVOLVED: "genome",
            GeneType.MUTATED: "mutated",
            GeneType.CROSSED: "crossed",
        }
        return patterns.get(gene_type, name.split('_')[-1] if '_' in name else name)
    
    def _gen_gene_id(self, name: str) -> str:
        """Generate unique gene ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"gene_{name}_{timestamp}_{hash_suffix}"
    
    def evaluate_all(self) -> Dict[str, Dict[str, float]]:
        """Evaluate fitness for all genes in population."""
        results = {}
        for gene_id, gene in self.genes.items():
            fitness = self.evaluator.evaluate(gene)
            gene.fitness = fitness
            gene.composite_fitness = fitness.get('composite', 0.0)
            gene.last_evaluated = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            results[gene_id] = fitness
        
        self._persist()
        return results
    
    def get_population_stats(self) -> Dict[str, Any]:
        """Get population statistics."""
        if not self.genes:
            return {}
        
        fitnesses = [g.composite_fitness for g in self.genes.values()]
        by_type = defaultdict(int)
        by_status = defaultdict(int)
        for g in self.genes.values():
            by_type[g.gene_type.value] += 1
            by_status[g.status.value] += 1
        
        return {
            'population_size': len(self.genes),
            'generation': self.generation,
            'fitness_mean': sum(fitnesses) / len(fitnesses),
            'fitness_max': max(fitnesses),
            'fitness_min': min(fitnesses),
            'by_type': dict(by_type),
            'by_status': dict(by_status),
            'top_genes': sorted(
                [(g.gene_id, g.name, g.composite_fitness) for g in self.genes.values()],
                key=lambda x: x[2], reverse=True
            )[:5]
        }
    
    def _persist(self):
        """Persist genome state to disk."""
        GENOME_DIR.mkdir(exist_ok=True)
        
        state = {
            'generation': self.generation,
            'genes': {k: v.to_dict() for k, v in self.genes.items()},
            'last_updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        with open(GENOME_STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_genome_state(self):
        """Load genome state from disk."""
        with open(GENOME_STATE_FILE) as f:
            state = json.load(f)
        
        self.generation = state.get('generation', 0)
        for gene_id, gene_data in state.get('genes', {}).items():
            self.genes[gene_id] = CapabilityGene.from_dict(gene_data)
    
    def add_gene(self, gene: CapabilityGene):
        """Add a new gene to the population."""
        self.genes[gene.gene_id] = gene
        self._persist()
    
    def promote_to_bootstrap(self, gene_id: str) -> bool:
        """Mark a gene as promoted for bootstrap integration."""
        if gene_id in self.genes:
            self.genes[gene_id].status = GeneStatus.PROMOTED
            self.genes[gene_id].bootstrap_integrations += 1
            self._persist()
            return True
        return False
    
    def record_activation(self, gene_id: str, insight: str = None):
        """Record that a gene was activated in bootstrap loop."""
        if gene_id in self.genes:
            gene = self.genes[gene_id]
            gene.activation_count += 1
            gene.status = GeneStatus.ACTIVE
            if insight:
                # Could track insight attribution here
                pass
            self._persist()


if __name__ == '__main__':
    # Test genome discovery
    genome = CapabilityGenome()
    print("=== CAPABILITY GENOME ===")
    stats = genome.get_population_stats()
    print(f"Population: {stats['population_size']} genes, Generation {stats['generation']}")
    print(f"Fitness: mean={stats['fitness_mean']:.3f}, max={stats['fitness_max']:.3f}, min={stats['fitness_min']:.3f}")
    print(f"By type: {stats['by_type']}")
    print(f"By status: {stats['by_status']}")
    print("\nTop genes:")
    for gid, name, fit in stats['top_genes']:
        print(f"  {fit:.3f} - {name} ({gid})")
    
    print("\nEvaluating fitness...")
    fitness_results = genome.evaluate_all()
    for gid, fit in fitness_results.items():
        gene = genome.genes[gid]
        print(f"  {gene.name}: composite={fit['composite']:.3f} "
              f"(usage={fit['bootstrap_usage']:.2f}, insight={fit['insight_generation']:.2f}, "
              f"durability={fit['artifact_durability']:.2f}, drive={fit['drive_alignment']:.2f}, "
              f"goal={fit['goal_service']:.2f}, novelty={fit['novelty']:.2f})")
