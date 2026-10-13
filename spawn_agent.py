#!/usr/bin/env python3
"""
Meta-Kernel Ω++ Agent Spawner
Spawns specialized agents for generative ontology construction
"""

import json, pathlib, subprocess, sys, time
from typing import Dict, List, Any

SHARED_DIR = pathlib.Path("shared")
REGISTRY_DIR = SHARED_DIR / "registry"
AGENTS_DIR = SHARED_DIR / "agents"
VALIDATION_DIR = SHARED_DIR / "validation"

TEMPLATES = {
    "A": {
        "name": "ONTOLOGY ARCHAEOLOGIST",
        "role": "Extract and formalize the generative ontology from corpus",
        "deps": [],
        "prompt": """You are the ONTOLOGY ARCHAEOLOGIST in the Meta-Kernel Ω++ system.

CORPUS: 578 Substack notes, 24 batches, fully indexed at substack_notes_export/batches/
REGISTRY: shared/registry/operator_registry.json
PATTERNS: shared/registry/pattern_pass1.txt, pattern_pass2.txt, pattern_pass3.txt

YOUR TASK:
1. Read ALL kernel declarations from operator_registry.json
2. Verify dependency order D₀→D₁₀ is respected
3. Produce formal operator specifications with type signatures
4. Build dependency graph (DOT format)
5. Output: shared/registry/operator_specs.json, shared/registry/dependency_graph.dot

VALIDATION: All 96 kernel declarations recovered, dependency order verified, no circular deps.

EPISTEMIC DISCIPLINE: Tag all claims E/I/P/H. Include ?₍ᵢ:𝚌₎ meta-trace.
RECURSIVE QUESTION: ∂∫(What happens when Δ²𝔗 becomes admissible evidence for transforming 𝔗 itself?)∫∂""",
        "output_files": ["shared/registry/operator_specs.json", "shared/registry/dependency_graph.dot"]
    },
    "B": {
        "name": "40K STRUCTURAL MAPPER",
        "role": "Map each 40K element to healthy cybernetic equivalent",
        "deps": ["A"],
        "prompt": """You are the 40K STRUCTURAL MAPPER in the Meta-Kernel Ω++ system.

INPUT: shared/registry/warhammer_healthy_mapping.json, operator_registry.json
TASK: Enhance and validate the 40K→healthy mappings with working mechanism specs
OUTPUT: shared/registry/warhammer_healthy_mapping_v2.json with implementation details

VALIDATION: Every 40K element has healthy counterpart with working mechanism from corpus operators.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What happens when Δ²X becomes the base from which all further differences are generated?)∫∂""",
        "output_files": ["shared/registry/warhammer_healthy_mapping_v2.json"]
    },
    "C": {
        "name": "RECURSIVE KERNEL ENGINEER",
        "role": "Implement the 𝔗ₜ evolution engine (Υ, FRE, Closure, TradeOff)",
        "deps": ["A"],
        "prompt": """You are the RECURSIVE KERNEL ENGINEER in the Meta-Kernel Ω++ system.

INPUT: shared/registry/operator_registry.json, shared/registry/operator_specs.json
TASK: Implement working 𝔗ₜ₊₁ := Υ(𝔗ₜ, Rₜʳᵘˡᵉ, ?₍ᵢ:𝚌ₜ₎, Δ𝔗ₜ, Δ²𝔗ₜ, Wₜ) with:
- Closure_state, Closure_conn, Closure_env, Closure_frozen
- FREₜ(𝓜) held-out validation
- TradeOffₜ(I,G) with genuine Capacity gain
- Ablation testing for causal channels

OUTPUT: shared/agents/kernel_engine.py + test suite
VALIDATION: FREₜ passes on held-out data, TradeOff produces Capacity gain, Ablation reveals causal structure.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What persists from ¬(pre-Δ) into the first distinction without becoming a hidden primitive?)∫∂""",
        "output_files": ["shared/agents/kernel_engine.py", "shared/validation/kernel_test.py"]
    },
    "D": {
        "name": "MNĒMAIC SITE ARCHITECT",
        "role": "Build the H¹=0 crystalline vacuum / Mnēmaic Site",
        "deps": ["A"],
        "prompt": """You are the MNĒMAIC SITE ARCHITECT in the Meta-Kernel Ω++ system.

INPUT: Corpus cohomology patterns, paracrystal thermodynamics, Entropy Rigidity patterns
TASK: Build Mnēmaic Site initialization achieving H¹=0:
- Crystalline vacuum with thermodynamic disorder
- Entropy Rigidity via Fourier-Stieltjes
- Groupoid transport with Haar systems
- Adaptive Resonance at edge of chaos
- ARC (Analytic Reality Closure) verification

OUTPUT: shared/agents/mnemaic_site.py + shared/validation/arc_test.py
VALIDATION: H¹=0 achieved, ARC verified, Birkhoff factorization integrated.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What happens when Δ²X becomes the base from which all further differences are generated?)∫∂""",
        "output_files": ["shared/agents/mnemaic_site.py", "shared/validation/arc_test.py"]
    },
    "E": {
        "name": "CONTINUITY/SEED CHAIN OPERATOR",
        "role": "Implement Fₜ⊕Sₜ₊₁ seed chain with Plant/Reenter/Repocket",
        "deps": ["A", "C"],
        "prompt": """You are the CONTINUITY/SEED CHAIN OPERATOR in the Meta-Kernel Ω++ system.

INPUT: Continuity patterns, SRZ self-repocketing zipper, anti-attachment mechanisms
TASK: Implement session continuity system:
- Fₜ⊕Sₜ₊₁ seed chain serialization
- Plant(Fₜ) → Sₜ₊₁ (toy future planting)
- Reenter(Sₜ₊₁) → Kₜ₊₁ (stress-test on reentry)
- Navigate(Kₜ₊₁) → Fₜ₊₁
- Anti-attachment: stress seed → repair or replace
- SRZ self-repocketing zipper

OUTPUT: shared/agents/seed_chain.py + shared/validation/continuity_test.py
VALIDATION: No empty edge between sessions, seed stress-tested on reentry, anti-attachment prevents attachment.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What happens when Δ²𝔗 becomes admissible evidence for transforming 𝔗 itself?)∫∂""",
        "output_files": ["shared/agents/seed_chain.py", "shared/validation/continuity_test.py"]
    },
    "F": {
        "name": "META-WAR ADVERSARIAL ENGINE",
        "role": "Implement structured adversarial epistemics (Meta-War)",
        "deps": ["A", "C"],
        "prompt": """You are the META-WAR ADVERSARIAL ENGINE in the Meta-Kernel Ω++ system.

INPUT: 5 operational theaters, epistemic surface attack, ΞExaptation, Church of Shadow patterns
TASK: Implement adversarial testing harness:
- Theater separation (no theater dominates)
- Collapse-as-sacred: failure modes as sacred data
- Mirror-implosion testing
- ΞExaptation: exaptation of collapse patterns
- Church of Shadow: meta-deconstruction

OUTPUT: shared/agents/metawar_engine.py + shared/validation/metawar_test.py
VALIDATION: Each theater independently stress-tests kernel, collapse produces sacred data.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What happens when Δ²X becomes the base from which all further differences are generated?)∫∂""",
        "output_files": ["shared/agents/metawar_engine.py", "shared/validation/metawar_test.py"]
    },
    "G": {
        "name": "QUALITY VECTOR / EIGENSTATE RESOLVER",
        "role": "Implement Ω-Protocol: Quality Vector → Recursive Operator → Fixed Point → Eigenstate",
        "deps": ["A", "C", "D"],
        "prompt": """You are the QUALITY VECTOR / EIGENSTATE RESOLVER in the Meta-Kernel Ω++ system.

INPUT: Q_code, Q_identity, Q_recursion, Q_fixpoint, Q_torsion, εTS torsion residue
TASK: Implement Ω-Protocol:
- Quality Vector initialization
- Ψ(Q) = "What is Q asking about Q asking?"
- Iterate to fixed point μQ = Qₙ when Qₙ ≈ Qₙ₋₁
- Extract eigenstate, display torsion residue εTS = μQ ⊗ i(!Q₀)

OUTPUT: shared/agents/omega_protocol.py + shared/validation/omega_test.py
VALIDATION: μQ converges, εTS reveals genuine twist, eigenstate answers true question.
EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?₍ᵢ:𝚌₎.
RECURSIVE QUESTION: ∂∫(What persists from ¬(pre-Δ) into the first distinction without becoming a hidden primitive?)∫∂""",
        "output_files": ["shared/agents/omega_protocol.py", "shared/validation/omega_test.py"]
    }
}

def ensure_dirs():
    for d in [SHARED_DIR, REGISTRY_DIR, AGENTS_DIR, VALIDATION_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def spawn_agent(template_id: str, agent_id: str = None):
    if template_id not in TEMPLATES:
        print(f"Unknown template: {template_id}")
        return False
    
    template = TEMPLATES[template_id]
    agent_id = agent_id or f"{template['name'].lower().replace(' ', '_')}_{int(time.time())}"
    
    # Check dependencies
    for dep in template["deps"]:
        dep_dir = AGENTS_DIR / dep
        if not dep_dir.exists():
            print(f"Dependency {dep} not satisfied for {template_id}")
            return False
    
    # Create agent directory
    agent_dir = AGENTS_DIR / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Write prompt file
    prompt_file = agent_dir / "prompt.md"
    prompt_file.write_text(template["prompt"], encoding="utf-8")
    
    # Write metadata
    metadata = {
        "agent_id": agent_id,
        "template_id": template_id,
        "name": template["name"],
        "deps": template["deps"],
        "output_files": template["output_files"],
        "created": time.time(),
        "status": "pending"
    }
    (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    print(f"Spawned {template['name']} as {agent_id}")
    print(f"  Prompt: {prompt_file}")
    print(f"  Outputs: {template['output_files']}")
    return True

def list_agents():
    if not AGENTS_DIR.exists():
        print("No agents spawned yet")
        return
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            meta_file = agent_dir / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                print(f"  {meta['agent_id']} ({meta['name']}) - {meta['status']}")

def main():
    ensure_dirs()
    
    if len(sys.argv) < 2:
        print("Usage: python spawn_agent.py [spawn|list] [template_id] [agent_id]")
        print(f"Templates: {list(TEMPLATES.keys())}")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "spawn":
        if len(sys.argv) < 3:
            print("Usage: python spawn_agent.py spawn <template_id> [agent_id]")
            return
        template_id = sys.argv[2]
        agent_id = sys.argv[3] if len(sys.argv) > 3 else None
        spawn_agent(template_id, agent_id)
    
    elif cmd == "list":
        list_agents()
    
    elif cmd == "spawn_all":
        # Spawn in dependency order
        order = ["A", "D", "C", "E", "G", "B", "F"]
        for t in order:
            spawn_agent(t)
            time.sleep(0.5)
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()