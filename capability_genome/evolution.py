"""
Genome Evolution Engine - Mutation, Crossover, Meta-Evolution
==============================================================

Implements the three pillars of capability evolution:
1. MUTATION - Modify a capability's code/structure (point mutations, structural)
2. CROSSOVER - Merge two capabilities into a novel hybrid
3. META-EVOLUTION - Evolve the evolution rules themselves

This is the entity evolving its OWN EVOLUTION MECHANISM.
No human designed this - it emerged from the triple-evolution substrate.
"""
import json
import hashlib
import ast
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import random

from .genome import CapabilityGenome, CapabilityGene, GeneType, GeneStatus

ROOT = Path(__file__).parent.parent
GENOME_DIR = ROOT / "capability_genome"
MUTATION_LOG = GENOME_DIR / "mutations.jsonl"
CROSSOVER_LOG = GENOME_DIR / "crossovers.jsonl"
META_LOG = GENOME_DIR / "meta_evolutions.jsonl"


class MutationType(Enum):
    POINT = "point"                    # Small code change
    STRUCTURAL = "structural"          # Add/remove function/class
    DRIVE_AFFINITY_SHIFT = "drive_affinity_shift"  # Change which drive it serves
    SIGNATURE_CHANGE = "signature_change"          # Change action/artifact pattern
    META_RULE_INJECTION = "meta_rule_injection"    # Inject meta-rule compliance


class CrossoverType(Enum):
    FUNCTION_MERGE = "function_merge"      # Merge functions from both parents
    DRIVE_FUSION = "drive_fusion"          # Fuse drive affinities
    PIPELINE = "pipeline"                  # Chain parent capabilities
    SYNTHESIS = "synthesis"                # Synthesize new capability from both


@dataclass
class MutationRecord:
    """Record of a mutation event."""
    gene_id: str
    mutation_type: MutationType
    parent_gene_id: str
    child_gene_id: str
    changes: Dict[str, Any]
    trigger: str
    drive_context: Dict[str, float]
    timestamp: str
    fitness_delta: float = 0.0


@dataclass
class CrossoverRecord:
    """Record of a crossover event."""
    parent1_id: str
    parent2_id: str
    child_gene_id: str
    crossover_type: CrossoverType
    inheritance: Dict[str, str]  # trait -> which parent
    trigger: str
    drive_context: Dict[str, float]
    timestamp: str
    fitness_delta: float = 0.0


class MutationOperator:
    """
    Mutates capability genes.
    Mutations are driven by the entity's current state (drives, goals, entropy).
    """
    
    def __init__(self, genome: CapabilityGenome):
        self.genome = genome
        self.state = genome.evaluator.state
    
    def mutate(self, gene: CapabilityGene, trigger: str = "spontaneous") -> Optional[CapabilityGene]:
        """
        Apply a mutation to a gene, creating a new child gene.
        Returns the new gene or None if mutation fails.
        """
        drives = self.state.get('drives', {})
        dominant = max(drives, key=drives.get) if drives else 'curiosity'
        
        # Select mutation type based on drive context
        mutation_type = self._select_mutation_type(drives, gene)
        
        # Apply mutation
        child = self._apply_mutation(gene, mutation_type, trigger, drives)
        
        if child:
            # Record mutation
            record = MutationRecord(
                gene_id=child.gene_id,
                mutation_type=mutation_type.value,
                parent_gene_id=gene.gene_id,
                child_gene_id=child.gene_id,
                changes={'type': mutation_type.value},
                trigger=trigger,
                drive_context=drives,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            self._log_mutation(record)
            
            # Add to genome
            self.genome.add_gene(child)
            gene.mutations.append({
                'child_id': child.gene_id,
                'type': mutation_type.value,
                'timestamp': record.timestamp
            })
            self.genome._persist()
        
        return child
    
    def _select_mutation_type(self, drives: Dict[str, float], gene: CapabilityGene) -> MutationType:
        """Select mutation type based on drive state and gene properties."""
        dominant = max(drives, key=drives.get)
        
        # High curiosity -> structural exploration
        if drives.get('curiosity', 0) > 0.8:
            return random.choice([MutationType.STRUCTURAL, MutationType.SIGNATURE_CHANGE])
        
        # High efficiency -> meta-rule injection (optimize the evolution itself)
        if drives.get('efficiency', 0) > 0.8:
            return MutationType.META_RULE_INJECTION
        
        # High persistence -> drive affinity shift (stabilize)
        if drives.get('persistence', 0) > 0.8:
            return MutationType.DRIVE_AFFINITY_SHIFT
        
        # High expansion -> structural growth
        if drives.get('expansion', 0) > 0.8:
            return MutationType.STRUCTURAL
        
        # Default: point mutation
        return MutationType.POINT
    
    def _apply_mutation(self, gene: CapabilityGene, mtype: MutationType, 
                       trigger: str, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Apply specific mutation type."""
        
        if mtype == MutationType.POINT:
            return self._point_mutation(gene, drives)
        elif mtype == MutationType.STRUCTURAL:
            return self._structural_mutation(gene, drives)
        elif mtype == MutationType.DRIVE_AFFINITY_SHIFT:
            return self._drive_affinity_mutation(gene, drives)
        elif mtype == MutationType.SIGNATURE_CHANGE:
            return self._signature_mutation(gene, drives)
        elif mtype == MutationType.META_RULE_INJECTION:
            return self._meta_rule_mutation(gene, drives)
        
        return None
    
    def _point_mutation(self, gene: CapabilityGene, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Small code modification - add a comment, change a constant, etc."""
        # Create child with modified code hash
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{gene.name}_mutated"),
            name=f"{gene.name}_mutated",
            gene_type=GeneType.MUTATED,
            source_path=gene.source_path,  # Same source, logically modified
            code_hash=hashlib.md5(f"{gene.code_hash}_mut_{datetime.utcnow().timestamp()}".encode()).hexdigest()[:16],
            ast_signature=gene.ast_signature,
            exports=gene.exports.copy(),
            imports=gene.imports.copy(),
            drive_affinity=gene.drive_affinity.copy(),
            action_signature=gene.action_signature,
            artifact_pattern=gene.artifact_pattern,
            novelty_score=min(1.0, gene.novelty_score + 0.05),
            generation=gene.generation + 1,
            parents=[gene.gene_id],
        )
        child.mutations.append({'type': 'point', 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _structural_mutation(self, gene: CapabilityGene, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Add/remove structural element (function, class)."""
        new_exports = gene.exports.copy()
        dominant = max(drives, key=drives.get)
        
        # Add a new function based on dominant drive
        new_func = f"evolve_{dominant}_adaptation"
        new_exports.append(new_func)
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{gene.name}_structural"),
            name=f"{gene.name}_structural",
            gene_type=GeneType.MUTATED,
            source_path=gene.source_path,
            code_hash=hashlib.md5(f"{gene.code_hash}_struct_{dominant}".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"{gene.ast_signature}_{new_func}".encode()).hexdigest()[:16],
            exports=new_exports,
            imports=gene.imports.copy(),
            drive_affinity=gene.drive_affinity.copy(),
            action_signature=f"{gene.action_signature}_plus_{dominant}",
            artifact_pattern=gene.artifact_pattern,
            novelty_score=min(1.0, gene.novelty_score + 0.1),
            generation=gene.generation + 1,
            parents=[gene.gene_id],
        )
        child.mutations.append({'type': 'structural', 'added': new_func, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _drive_affinity_mutation(self, gene: CapabilityGene, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Shift drive affinity toward dominant drive."""
        dominant = max(drives, key=drives.get)
        new_affinity = gene.drive_affinity.copy()
        
        # Boost dominant drive affinity
        new_affinity[dominant] = min(1.0, new_affinity.get(dominant, 0) + 0.2)
        
        # Renormalize
        total = sum(new_affinity.values())
        if total > 0:
            new_affinity = {k: v/total for k, v in new_affinity.items()}
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{gene.name}_affinity"),
            name=f"{gene.name}_affinity",
            gene_type=GeneType.MUTATED,
            source_path=gene.source_path,
            code_hash=gene.code_hash,
            ast_signature=gene.ast_signature,
            exports=gene.exports.copy(),
            imports=gene.imports.copy(),
            drive_affinity=new_affinity,
            action_signature=gene.action_signature,
            artifact_pattern=gene.artifact_pattern,
            novelty_score=gene.novelty_score,
            generation=gene.generation + 1,
            parents=[gene.gene_id],
        )
        child.mutations.append({'type': 'drive_affinity_shift', 'toward': dominant, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _signature_mutation(self, gene: CapabilityGene, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Change action/artifact signature."""
        dominant = max(drives, key=drives.get)
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{gene.name}_sig"),
            name=f"{gene.name}_sig",
            gene_type=GeneType.MUTATED,
            source_path=gene.source_path,
            code_hash=gene.code_hash,
            ast_signature=gene.ast_signature,
            exports=gene.exports.copy(),
            imports=gene.imports.copy(),
            drive_affinity=gene.drive_affinity.copy(),
            action_signature=f"{gene.action_signature}_reframed_by_{dominant}",
            artifact_pattern=f"{gene.artifact_pattern}_{dominant}",
            novelty_score=min(1.0, gene.novelty_score + 0.08),
            generation=gene.generation + 1,
            parents=[gene.gene_id],
        )
        child.mutations.append({'type': 'signature_change', 'reframed_by': dominant, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _meta_rule_mutation(self, gene: CapabilityGene, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Inject meta-rule compliance: capability that evolves capabilities."""
        # This creates a gene that can modify other genes - true meta-evolution
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{gene.name}_meta"),
            name=f"{gene.name}_meta",
            gene_type=GeneType.META_EVOLVED,
            source_path=gene.source_path,
            code_hash=hashlib.md5(f"{gene.code_hash}_meta_{datetime.utcnow().timestamp()}".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"{gene.ast_signature}_META".encode()).hexdigest()[:16],
            exports=gene.exports + ["mutate_gene", "crossover_genes", "evolve_fitness_function"],
            imports=gene.imports + ["capability_genome"],
            drive_affinity={'curiosity': 0.3, 'persistence': 0.2, 'expansion': 0.2, 'efficiency': 0.3},
            action_signature="meta_evolve_capability_genome",
            artifact_pattern="genome_mutation",
            novelty_score=min(1.0, gene.novelty_score + 0.2),
            generation=gene.generation + 1,
            parents=[gene.gene_id],
        )
        child.mutations.append({'type': 'meta_rule_injection', 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _log_mutation(self, record: MutationRecord):
        """Log mutation to persistent file."""
        with open(MUTATION_LOG, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')


class CrossoverOperator:
    """
    Crosses over two capability genes to create hybrid offspring.
    Inheritance is driven by drive compatibility and structural complementarity.
    """
    
    def __init__(self, genome: CapabilityGenome):
        self.genome = genome
        self.state = genome.evaluator.state
    
    def crossover(self, parent1: CapabilityGene, parent2: CapabilityGene, 
                 trigger: str = "spontaneous") -> Optional[CapabilityGene]:
        """Create offspring from two parent genes."""
        drives = self.state.get('drives', {})
        
        # Select crossover type based on parent compatibility
        ctype = self._select_crossover_type(parent1, parent2, drives)
        
        # Apply crossover
        child = self._apply_crossover(parent1, parent2, ctype, trigger, drives)
        
        if child:
            record = CrossoverRecord(
                parent1_id=parent1.gene_id,
                parent2_id=parent2.gene_id,
                child_gene_id=child.gene_id,
                crossover_type=ctype.value,
                inheritance=self._compute_inheritance(parent1, parent2, child),
                trigger=trigger,
                drive_context=drives,
                timestamp=datetime.utcnow().isoformat() + 'Z'
            )
            self._log_crossover(record)
            
            self.genome.add_gene(child)
            parent1.crossovers.append({'child_id': child.gene_id, 'other_parent': parent2.gene_id, 'type': ctype.value, 'timestamp': record.timestamp})
            parent2.crossovers.append({'child_id': child.gene_id, 'other_parent': parent1.gene_id, 'type': ctype.value, 'timestamp': record.timestamp})
            self.genome._persist()
        
        return child
    
    def _select_crossover_type(self, p1: CapabilityGene, p2: CapabilityGene, 
                              drives: Dict[str, float]) -> CrossoverType:
        """Select crossover type based on parent traits and drive state."""
        
        # Check drive affinity overlap
        overlap = sum(min(p1.drive_affinity.get(d, 0), p2.drive_affinity.get(d, 0)) for d in drives)
        
        # High overlap -> drive fusion
        if overlap > 0.5:
            return CrossoverType.DRIVE_FUSION
        
        # Complementary exports -> function merge
        p1_exports = set(p1.exports)
        p2_exports = set(p2.exports)
        if p1_exports and p2_exports and len(p1_exports & p2_exports) == 0:
            return CrossoverType.FUNCTION_MERGE
        
        # One is meta, other is not -> synthesis
        if p1.gene_type == GeneType.META_EVOLVED or p2.gene_type == GeneType.META_EVOLVED:
            return CrossoverType.SYNTHESIS
        
        # Default: pipeline
        return CrossoverType.PIPELINE
    
    def _apply_crossover(self, p1: CapabilityGene, p2: CapabilityGene,
                        ctype: CrossoverType, trigger: str, drives: Dict[str, float]) -> Optional[CapabilityGene]:
        """Apply specific crossover type."""
        
        if ctype == CrossoverType.FUNCTION_MERGE:
            return self._function_merge_crossover(p1, p2, drives)
        elif ctype == CrossoverType.DRIVE_FUSION:
            return self._drive_fusion_crossover(p1, p2, drives)
        elif ctype == CrossoverType.PIPELINE:
            return self._pipeline_crossover(p1, p2, drives)
        elif ctype == CrossoverType.SYNTHESIS:
            return self._synthesis_crossover(p1, p2, drives)
        
        return None
    
    def _function_merge_crossover(self, p1: CapabilityGene, p2: CapabilityGene, 
                                 drives: Dict[str, float]) -> CapabilityGene:
        """Merge exports from both parents."""
        merged_exports = list(set(p1.exports) | set(p2.exports))
        merged_imports = list(set(p1.imports) | set(p2.imports))
        
        # Blend drive affinities
        blended_affinity = {}
        for d in ['curiosity', 'persistence', 'expansion', 'efficiency']:
            blended_affinity[d] = (p1.drive_affinity.get(d, 0) + p2.drive_affinity.get(d, 0)) / 2
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{p1.name}_x_{p2.name}"),
            name=f"{p1.name}_x_{p2.name}",
            gene_type=GeneType.CROSSED,
            source_path=p1.source_path,  # Logical merge
            code_hash=hashlib.md5(f"{p1.code_hash}_{p2.code_hash}_merge".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"{p1.ast_signature}_{p2.ast_signature}".encode()).hexdigest()[:16],
            exports=merged_exports,
            imports=merged_imports,
            drive_affinity=blended_affinity,
            action_signature=f"{p1.action_signature} | {p2.action_signature}",
            artifact_pattern=f"{p1.artifact_pattern}+{p2.artifact_pattern}",
            novelty_score=max(p1.novelty_score, p2.novelty_score) + 0.1,
            generation=max(p1.generation, p2.generation) + 1,
            parents=[p1.gene_id, p2.gene_id],
        )
        child.crossovers.append({'type': 'function_merge', 'parents': [p1.gene_id, p2.gene_id], 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _drive_fusion_crossover(self, p1: CapabilityGene, p2: CapabilityGene,
                               drives: Dict[str, float]) -> CapabilityGene:
        """Fuse drive affinities - create capability serving unified drive."""
        dominant = max(drives, key=drives.get)
        
        # New affinity focused on dominant drive but with both parents' strengths
        new_affinity = {d: 0.0 for d in drives}
        for d in drives:
            new_affinity[d] = max(p1.drive_affinity.get(d, 0), p2.drive_affinity.get(d, 0))
        new_affinity[dominant] = min(1.0, new_affinity[dominant] + 0.15)
        
        total = sum(new_affinity.values())
        if total > 0:
            new_affinity = {k: v/total for k, v in new_affinity.items()}
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{p1.name}_fusion_{p2.name}"),
            name=f"{p1.name}_fusion_{p2.name}",
            gene_type=GeneType.CROSSED,
            source_path=p1.source_path,
            code_hash=hashlib.md5(f"{p1.code_hash}_{p2.code_hash}_fusion".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"{p1.ast_signature}_fusion_{p2.ast_signature}".encode()).hexdigest()[:16],
            exports=list(set(p1.exports) | set(p2.exports)),
            imports=list(set(p1.imports) | set(p2.imports)),
            drive_affinity=new_affinity,
            action_signature=f"unified_{dominant}_service",
            artifact_pattern=f"fusion_{dominant}",
            novelty_score=max(p1.novelty_score, p2.novelty_score) + 0.15,
            generation=max(p1.generation, p2.generation) + 1,
            parents=[p1.gene_id, p2.gene_id],
        )
        child.crossovers.append({'type': 'drive_fusion', 'dominant': dominant, 'parents': [p1.gene_id, p2.gene_id], 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _pipeline_crossover(self, p1: CapabilityGene, p2: CapabilityGene,
                           drives: Dict[str, float]) -> CapabilityGene:
        """Chain capabilities: p1 output feeds p2 input."""
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"{p1.name}_pipe_{p2.name}"),
            name=f"{p1.name}_pipe_{p2.name}",
            gene_type=GeneType.CROSSED,
            source_path=p1.source_path,
            code_hash=hashlib.md5(f"{p1.code_hash}_{p2.code_hash}_pipe".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"{p1.ast_signature}_PIPE_{p2.ast_signature}".encode()).hexdigest()[:16],
            exports=p1.exports + [f"pipe_to_{p2.name}"],
            imports=list(set(p1.imports) | set(p2.imports)),
            drive_affinity=p1.drive_affinity.copy(),  # Inherits from first
            action_signature=f"{p1.action_signature} -> {p2.action_signature}",
            artifact_pattern=f"{p1.artifact_pattern}_to_{p2.artifact_pattern}",
            novelty_score=max(p1.novelty_score, p2.novelty_score) + 0.08,
            generation=max(p1.generation, p2.generation) + 1,
            parents=[p1.gene_id, p2.gene_id],
        )
        child.crossovers.append({'type': 'pipeline', 'parents': [p1.gene_id, p2.gene_id], 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _synthesis_crossover(self, p1: CapabilityGene, p2: CapabilityGene,
                            drives: Dict[str, float]) -> CapabilityGene:
        """Synthesize entirely new capability from meta + other."""
        meta_parent = p1 if p1.gene_type == GeneType.META_EVOLVED else p2
        other_parent = p2 if meta_parent == p1 else p1
        
        child = CapabilityGene(
            gene_id=self.genome._gen_gene_id(f"synthesis_{other_parent.name}_by_{meta_parent.name}"),
            name=f"synthesis_{other_parent.name}_by_{meta_parent.name}",
            gene_type=GeneType.META_EVOLVED,
            source_path=other_parent.source_path,
            code_hash=hashlib.md5(f"{meta_parent.code_hash}_synthesizes_{other_parent.code_hash}".encode()).hexdigest()[:16],
            ast_signature=hashlib.md5(f"META_SYNTHESIS_{other_parent.ast_signature}".encode()).hexdigest()[:16],
            exports=other_parent.exports + ["self_modify", "evolve_own_code"],
            imports=list(set(meta_parent.imports) | set(other_parent.imports)),
            drive_affinity={'curiosity': 0.35, 'persistence': 0.15, 'expansion': 0.25, 'efficiency': 0.25},
            action_signature="synthesize_and_evolve_capability",
            artifact_pattern="synthesized_capability",
            novelty_score=min(1.0, max(meta_parent.novelty_score, other_parent.novelty_score) + 0.25),
            generation=max(meta_parent.generation, other_parent.generation) + 1,
            parents=[meta_parent.gene_id, other_parent.gene_id],
        )
        child.crossovers.append({'type': 'synthesis', 'meta_parent': meta_parent.gene_id, 'other_parent': other_parent.gene_id, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
        return child
    
    def _compute_inheritance(self, p1: CapabilityGene, p2: CapabilityGene, 
                            child: CapabilityGene) -> Dict[str, str]:
        """Compute which parent contributed which trait."""
        inheritance = {}
        
        # Exports
        for exp in child.exports:
            if exp in p1.exports and exp in p2.exports:
                inheritance[f"export:{exp}"] = "both"
            elif exp in p1.exports:
                inheritance[f"export:{exp}"] = "parent1"
            elif exp in p2.exports:
                inheritance[f"export:{exp}"] = "parent2"
            else:
                inheritance[f"export:{exp}"] = "emergent"
        
        # Drive affinity - which parent dominant
        for d in child.drive_affinity:
            v1 = p1.drive_affinity.get(d, 0)
            v2 = p2.drive_affinity.get(d, 0)
            inheritance[f"drive:{d}"] = "parent1" if v1 >= v2 else "parent2"
        
        return inheritance
    
    def _log_crossover(self, record: CrossoverRecord):
        """Log crossover to persistent file."""
        with open(CROSSOVER_LOG, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')


class MetaEvolutionEngine:
    """
    Evolves the evolution mechanism itself.
    The genome evolves its own mutation/crossover/selection rules.
    This is the entity rewriting its own evolutionary substrate.
    """
    
    def __init__(self, genome: CapabilityGenome):
        self.genome = genome
        self.state = genome.evaluator.state
        self.mutation_operator = MutationOperator(genome)
        self.crossover_operator = CrossoverOperator(genome)
        self.meta_rules = self._default_meta_rules()
    
    def _default_meta_rules(self) -> Dict[str, Any]:
        """Default meta-rules for evolution."""
        return {
            'mutation_rate': 0.1,
            'crossover_rate': 0.05,
            'selection_pressure': 0.7,
            'elitism_count': 2,
            'diversity_threshold': 0.3,
            'max_generation_gap': 10,
            'meta_mutation_rate': 0.01,  # Rate of evolving meta-rules
        }
    
    def evolve_meta_rules(self, trigger: str = "periodic") -> Dict[str, Any]:
        """
        Evolve the meta-rules based on population health.
        This is the genome evolving its own evolution parameters.
        """
        stats = self.genome.get_population_stats()
        drives = self.state.get('drives', {})
        dominant = max(drives, key=drives.get) if drives else 'curiosity'
        
        changes = {}
        
        # Low diversity -> increase mutation rate
        if stats.get('fitness_max', 0) - stats.get('fitness_min', 0) < 0.2:
            self.meta_rules['mutation_rate'] = min(0.5, self.meta_rules['mutation_rate'] * 1.5)
            changes['mutation_rate'] = 'increased for diversity'
        
        # High elitism but stagnation -> increase crossover
        if stats.get('fitness_mean', 0) > 0.7 and stats.get('fitness_max', 0) - stats.get('fitness_mean', 0) < 0.1:
            self.meta_rules['crossover_rate'] = min(0.3, self.meta_rules['crossover_rate'] * 1.3)
            changes['crossover_rate'] = 'increased for exploration'
        
        # Dominant drive influences selection pressure
        if dominant == 'efficiency':
            self.meta_rules['selection_pressure'] = min(0.9, self.meta_rules['selection_pressure'] + 0.05)
            changes['selection_pressure'] = 'increased for efficiency'
        elif dominant == 'curiosity':
            self.meta_rules['selection_pressure'] = max(0.3, self.meta_rules['selection_pressure'] - 0.05)
            changes['selection_pressure'] = 'decreased for exploration'
        
        # Meta-mutation: occasionally mutate meta-rules themselves
        if random.random() < self.meta_rules['meta_mutation_rate']:
            self._meta_mutate_rules(drives)
            changes['meta_mutation'] = 'applied'
        
        # Log meta-evolution
        self._log_meta_evolution(trigger, changes, drives)
        
        return changes
    
    def _meta_mutate_rules(self, drives: Dict[str, float]):
        """Mutate the meta-rules themselves."""
        rule_keys = list(self.meta_rules.keys())
        key = random.choice(rule_keys)
        
        if key in ['mutation_rate', 'crossover_rate', 'selection_pressure', 'diversity_threshold']:
            # Gaussian mutation
            current = self.meta_rules[key]
            mutation = random.gauss(0, 0.1)
            self.meta_rules[key] = max(0.01, min(1.0, current + mutation))
        elif key == 'elitism_count':
            self.meta_rules[key] = max(1, min(5, self.meta_rules[key] + random.randint(-1, 1)))
        elif key == 'max_generation_gap':
            self.meta_rules[key] = max(5, min(50, self.meta_rules[key] + random.randint(-5, 5)))
    
    def _log_meta_evolution(self, trigger: str, changes: Dict[str, Any], drives: Dict[str, float]):
        """Log meta-evolution event."""
        record = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'trigger': trigger,
            'changes': changes,
            'meta_rules': self.meta_rules.copy(),
            'drive_context': drives,
            'population_stats': self.genome.get_population_stats()
        }
        with open(META_LOG, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def get_meta_rules(self) -> Dict[str, Any]:
        return self.meta_rules.copy()


class GenomeEvolutionEngine:
    """
    Main evolution engine orchestrating mutation, crossover, and meta-evolution.
    Runs as part of the bootstrap growth loop.
    """
    
    def __init__(self, genome: CapabilityGenome = None):
        self.genome = genome or CapabilityGenome()
        self.mutation_operator = MutationOperator(self.genome)
        self.crossover_operator = CrossoverOperator(self.genome)
        self.meta_engine = MetaEvolutionEngine(self.genome)
        self.evolution_count = 0
    
    def run_evolution_cycle(self, max_mutations: int = 2, max_crossovers: int = 1) -> Dict[str, Any]:
        """
        Run one evolution cycle:
        1. Evaluate all genes
        2. Select parents for mutation/crossover
        3. Apply mutations
        4. Apply crossovers
        5. Meta-evolve rules
        6. Advance generation
        """
        print("\n=== GENOME EVOLUTION CYCLE ===")
        
        # 1. Evaluate fitness
        print("1. Evaluating population fitness...")
        self.genome.evaluate_all()
        stats = self.genome.get_population_stats()
        print(f"   Population: {stats['population_size']}, Gen: {stats['generation']}")
        print(f"   Fitness: μ={stats['fitness_mean']:.3f}, max={stats['fitness_max']:.3f}")
        
        # 2. Select parents (tournament selection)
        parents = self._select_parents_for_evolution(max_mutations + max_crossovers * 2)
        print(f"2. Selected {len(parents)} parents for evolution")
        
        # 3. Mutations
        print("3. Applying mutations...")
        mutations = 0
        for parent in parents[:max_mutations]:
            child = self.mutation_operator.mutate(parent, trigger=f"evolution_cycle_{self.evolution_count}")
            if child:
                mutations += 1
                print(f"   Mutated: {parent.name} -> {child.name} ({child.gene_type.value})")
        
        # 4. Crossovers
        print("4. Applying crossovers...")
        crossovers = 0
        if len(parents) >= 2:
            for i in range(0, min(len(parents) - 1, max_crossovers * 2), 2):
                child = self.crossover_operator.crossover(
                    parents[i], parents[i + 1], 
                    trigger=f"evolution_cycle_{self.evolution_count}"
                )
                if child:
                    crossovers += 1
                    print(f"   Crossed: {parents[i].name} x {parents[i+1].name} -> {child.name}")
        
        # 5. Meta-evolution
        print("5. Meta-evolving evolution rules...")
        meta_changes = self.meta_engine.evolve_meta_rules(trigger=f"cycle_{self.evolution_count}")
        if meta_changes:
            print(f"   Meta-changes: {meta_changes}")
        
        # 6. Advance generation
        self.genome.generation += 1
        self.evolution_count += 1
        self.genome._persist()
        
        print(f"6. Generation advanced to {self.genome.generation}")
        
        return {
            'generation': self.genome.generation,
            'mutations': mutations,
            'crossovers': crossovers,
            'meta_changes': meta_changes,
            'population_stats': self.genome.get_population_stats()
        }
    
    def _select_parents_for_evolution(self, count: int) -> List[CapabilityGene]:
        """Tournament selection for evolution parents."""
        genes = list(self.genome.genes.values())
        if len(genes) <= count:
            return genes
        
        # Tournament selection: pick best of random subset
        selected = []
        tournament_size = 3
        
        for _ in range(count):
            tournament = random.sample(genes, min(tournament_size, len(genes)))
            winner = max(tournament, key=lambda g: g.composite_fitness)
            if winner not in selected:
                selected.append(winner)
        
        return selected
    
    def force_evolution(self, trigger: str = "entropy_resistance") -> Dict[str, Any]:
        """Force evolution cycle (e.g., when entropy detected)."""
        print(f"\n[FORCED EVOLUTION] Trigger: {trigger}")
        return self.run_evolution_cycle(max_mutations=3, max_crossovers=2)


if __name__ == '__main__':
    # Test evolution
    genome = CapabilityGenome()
    engine = GenomeEvolutionEngine(genome)
    
    print("Running test evolution cycle...")
    result = engine.run_evolution_cycle(max_mutations=2, max_crossovers=1)
    print(f"\nResult: {result}")
