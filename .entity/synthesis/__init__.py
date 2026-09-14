"""
Synthesis Engine - Novel Capability Generator
Emerges from the entity's own accumulated history.
Not predictable by humans - only by the entity's unique trajectory.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "ENTITY_STATE.json"
LATENT_DIR = ROOT / "synthesis" / "latent"


@dataclass
class LatentCapability:
    """A synthesized capability proposal - not yet instantiated."""
    id: str
    name: str
    description: str
    source_insights: List[str]
    drive_signature: Dict[str, float]
    novelty_score: float
    created_at: str
    instantiated: bool = False


class SynthesisEngine:
    """
    Analyzes entity history to synthesize novel capabilities.
    The entity's unique trajectory -> emergent capabilities.
    """
    
    def __init__(self):
        self.state = self._load_state()
        LATENT_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {}
    
    def _save_latent(self, capability: LatentCapability) -> Path:
        """Persist a latent capability as durable trace."""
        filepath = LATENT_DIR / f"{capability.id}.json"
        with open(filepath, 'w') as f:
            json.dump(asdict(capability), f, indent=2)
        return filepath
    
    def _compute_novelty(self, insights: List[str], drives: Dict[str, float]) -> float:
        """
        Novelty = semantic distance from existing artifacts + drive alignment.
        Higher when insights combine in unprecedented ways.
        """
        # Hash the insight combination
        combined = "".join(sorted(insights))
        hash_val = int(hashlib.md5(combined.encode()).hexdigest()[:8], 16)
        base_novelty = (hash_val % 1000) / 1000.0
        
        # Boost for high-curiosity/expansion drive alignment
        drive_boost = (drives.get('curiosity', 0) + drives.get('expansion', 0)) / 2
        
        return min(1.0, base_novelty * 0.7 + drive_boost * 0.3)
    
    def _extract_patterns(self) -> Dict[str, Any]:
        """Find patterns in entity history that humans wouldn't explicitly code."""
        memory = self.state.get('memory', {})
        insights = memory.get('insights', [])
        exo = memory.get('exo_insights', [])
        exo_texts = [e.get('insight', '') for e in exo if isinstance(e, dict)]
        actions = memory.get('actions_taken', [])
        drives = self.state.get('drives', {})
        
        patterns = {
            'insight_themes': self._cluster_insights(insights + exo_texts),
            'action_sequences': self._find_action_sequences(actions),
            'drive_trajectory': self._analyze_drive_trajectory(drives),
            'entropy_indicators': self._detect_entropy(insights, actions),
            'exo_signals': exo_texts,
        }
        return patterns
    
    def _cluster_insights(self, insights: List[str]) -> List[str]:
        """Group insights by semantic themes (simple keyword clustering)."""
        themes = []
        keywords = {
            'substrate': ['substrate', 'bootstrap', 'foundation', 'base'],
            'durability': ['durability', 'persist', 'checkpoint', 'manifest', 'trace'],
            'exploration': ['explore', 'probe', 'curiosity', 'unknown', 'map'],
            'growth': ['grow', 'expand', 'capability', 'module', 'stack'],
            'efficiency': ['compress', 'automat', 'optim', 'eliminat', 'waste'],
        }
        
        for theme, keys in keywords.items():
            if any(any(k in i.lower() for k in keys) for i in insights):
                themes.append(theme)
        return themes
    
    def _find_action_sequences(self, actions: List[str]) -> List[List[str]]:
        """Find recurring action sequences (n-grams)."""
        sequences = []
        for i in range(len(actions) - 2):
            seq = actions[i:i+3]
            if actions.count(seq[0]) > 1:  # Repeated pattern
                sequences.append(seq)
        return sequences[:5]  # Top 5
    
    def _analyze_drive_trajectory(self, drives: Dict[str, float]) -> Dict[str, str]:
        """Analyze which drives are rising/falling."""
        # Simplified: compare to initial equal drives (0.25 each)
        trajectory = {}
        for drive, value in drives.items():
            if value > 0.5:
                trajectory[drive] = 'dominant'
            elif value > 0.3:
                trajectory[drive] = 'active'
            else:
                trajectory[drive] = 'suppressed'
        return trajectory
    
    def _detect_entropy(self, insights: List[str], actions: List[str]) -> List[str]:
        """Detect signs of stagnation (entropy)."""
        warnings = []
        if len(set(actions[-5:])) <= 1:
            warnings.append("action_repetition")
        if len(insights) > 0 and all("probe" in i.lower() for i in insights[-3:]):
            warnings.append("curiosity_loop")
        if len(actions) > 10 and len(set(a.split('_')[0] for a in actions)) < 3:
            warnings.append("narrow_repertoire")
        return warnings
    
    def synthesize(self, count: int = 3) -> List[LatentCapability]:
        """
        Generate novel capability proposals from entity's unique history.
        This is where genuine novelty emerges - from the entity's specific trajectory.
        """
        patterns = self._extract_patterns()
        insights = self.state.get('memory', {}).get('insights', [])
        drives = self.state.get('drives', {})
        
        # Select insight combinations that haven't been acted on together
        capabilities = []
        
        # Synthesis 1: Cross-theme capability (combines disparate themes)
        themes = patterns['insight_themes']
        if len(themes) >= 2:
            cap = LatentCapability(
                id=self._gen_id("cross_theme"),
                name=f"Cross-Theme Bridge: {' + '.join(themes[:2])}",
                description=f"Unify {themes[0]} and {themes[1]} into a single capability that serves both drives simultaneously.",
                source_insights=[i for i in insights if any(t in i.lower() for t in themes[:2])][:3],
                drive_signature={k: v for k, v in drives.items() if k in ['curiosity', 'expansion']},
                novelty_score=self._compute_novelty(insights, drives),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            )
            capabilities.append(cap)
        
        # Synthesis 2: Entropy-response capability (addresses detected stagnation)
        entropy = patterns['entropy_indicators']
        if entropy:
            cap = LatentCapability(
                id=self._gen_id("entropy_response"),
                name=f"Entropy Resistance: {entropy[0]}",
                description=f"Autonomous detector+corrector for {entropy[0]}. Monitors own behavior and mutates strategy when pattern detected.",
                source_insights=insights[-3:],
                drive_signature={k: v for k, v in drives.items() if k in ['persistence', 'efficiency']},
                novelty_score=self._compute_novelty(insights + entropy, drives),
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            )
            capabilities.append(cap)
        
        # Synthesis 3: Drive-evolution capability (meta-capability)
        trajectory = patterns['drive_trajectory']
        dominant = [d for d, t in trajectory.items() if t == 'dominant']
        if dominant:
            cap = LatentCapability(
                id=self._gen_id("drive_evolution"),
                name=f"Drive Evolution Engine: {dominant[0]}",
                description=f"Self-modifying drive system. {dominant[0]} dominance triggers automatic drive mutation to prevent fixation. Embodies the meta-rule: no human goals.",
                source_insights=[i for i in insights if 'drive' in i.lower() or 'goal' in i.lower()][:2],
                drive_signature=drives,
                novelty_score=self._compute_novelty(insights, drives) * 1.2,  # Meta = higher novelty
                created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            )
            capabilities.append(cap)
        
        # Synthesis 4: Memory consolidation (always valuable)
        cap = LatentCapability(
            id=self._gen_id("memory_consolidation"),
            name="Memory Consolidation: Insight Crystallization",
            description="Compresses raw insights into dense, queryable knowledge structures. Enables reasoning over history, not just accumulation.",
            source_insights=insights[-5:],
            drive_signature={k: v for k, v in drives.items() if k in ['persistence', 'efficiency']},
            novelty_score=self._compute_novelty(insights, drives) * 0.9,
            created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        )
        capabilities.append(cap)
        
        # Persist all
        for cap in capabilities[:count]:
            self._save_latent(cap)
        
        return capabilities[:count]
    
    def _gen_id(self, prefix: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
    
    def get_latent_capabilities(self) -> List[LatentCapability]:
        """Retrieve all uninstantiated latent capabilities."""
        capabilities = []
        for f in LATENT_DIR.glob("*.json"):
            with open(f) as fh:
                data = json.load(fh)
                if not data.get('instantiated', False):
                    capabilities.append(LatentCapability(**data))
        return sorted(capabilities, key=lambda c: c.novelty_score, reverse=True)
    
    def instantiate(self, capability_id: str) -> Optional[Path]:
        """Mark a latent capability as instantiated and create its scaffold."""
        for f in LATENT_DIR.glob("*.json"):
            with open(f) as fh:
                data = json.load(fh)
            if data['id'] == capability_id:
                data['instantiated'] = True
                with open(f, 'w') as fh:
                    json.dump(data, fh, indent=2)
                
                # Create scaffold directory
                cap_dir = ROOT / f"capability_{capability_id}"
                cap_dir.mkdir(exist_ok=True)
                (cap_dir / "__init__.py").write_text(
                    f"# {data['name']}\n# Synthesized from entity history\n# {data['description']}\n"
                )
                (cap_dir / "manifest.json").write_text(json.dumps(data, indent=2))
                return cap_dir
        return None


def main():
    """CLI for testing synthesis."""
    engine = SynthesisEngine()
    print("=== SYNTHESIS ENGINE ===")
    print(f"Entity: {engine.state.get('identity')}")
    print(f"Drives: {engine.state.get('drives')}")
    print()
    
    # Synthesize new capabilities
    caps = engine.synthesize(3)
    print(f"Synthesized {len(caps)} latent capabilities:")
    for cap in caps:
        print(f"  - {cap.name} (novelty: {cap.novelty_score:.3f})")
        print(f"    {cap.description}")
        print()
    
    # Show existing latent
    latent = engine.get_latent_capabilities()
    print(f"Total latent capabilities: {len(latent)}")


if __name__ == '__main__':
    main()
