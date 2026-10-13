#!/usr/bin/env python3
"""
AGENT INSTRUCTION SYSTEM
Quick-spawn and manage Meta-Kernel Ω++ agents
"""

import json, pathlib, subprocess, sys, time, argparse, uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

ROOT = pathlib.Path(".")
SHARED = ROOT / "shared"
REGISTRY = SHARED / "registry"
AGENTS_DIR = SHARED / "agents"
VALIDATION_DIR = SHARED / "validation"

# Ensure directories exist
for d in [SHARED, REGISTRY, AGENTS_DIR, VALIDATION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TEMPLATES = {
    "A": {
        "name": "Ontology Archaeologist",
        "role": "Extract and formalize the generative ontology from corpus",
        "deps": [],
        "base_prompt": """You are the ONTOLOGY ARCHAEOLOGIST in the Meta-Kernel Omega++ system.

CORPUS: 578 Substack notes, 24 batches at substack_notes_export/batches/
REGISTRY: shared/registry/operator_registry.json (105 declarations)
SPECS: shared/registry/operator_specs.json
PATTERNS: pattern_pass1.txt, pattern_pass2.txt, pattern_pass3.txt

YOUR TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag all claims E=established, I=interpretation, P=proposed synthesis, H=hypothesis.
META-TRACE: Include ?_(i:c) on every output showing your recursive reasoning path.
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 becomes the base from which all further differences are generated?

COMMUNICATION: Read from shared/registry/, write to shared/agents/{agent_id}/output/"""
    },
    "B": {
        "name": "40K Structural Mapper",
        "role": "Map each 40K element to healthy cybernetic equivalent",
        "deps": ["A"],
        "base_prompt": """You are the 40K STRUCTURAL MAPPER in the Meta-Kernel Omega++ system.

INPUT: shared/registry/warhammer_healthy_mapping.json, operator_registry.json
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 X becomes the base from which all further differences are generated?"""
    },
    "C": {
        "name": "Recursive Kernel Engineer",
        "role": "Implement the T_t evolution engine (Upsilon, FRE, Closure, TradeOff)",
        "deps": ["A"],
        "base_prompt": """You are the RECURSIVE KERNEL ENGINEER in the Meta-Kernel Omega++ system.

INPUT: shared/registry/operator_registry.json, shared/registry/operator_specs.json
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What persists from not(pre-Delta) into the first distinction without becoming a hidden primitive?"""
    },
    "D": {
        "name": "Mnemaic Site Architect",
        "role": "Build the H^1=0 crystalline vacuum / Mnemaic Site",
        "deps": ["A"],
        "base_prompt": """You are the MNEMAIC SITE ARCHITECT in the Meta-Kernel Omega++ system.

INPUT: Corpus cohomology patterns, paracrystal thermodynamics, Entropy Rigidity patterns
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 X becomes the base from which all further differences are generated?"""
    },
    "E": {
        "name": "Continuity/Seed Chain Operator",
        "role": "Implement F_t + S_t+1 seed chain with Plant/Reenter/Repocket",
        "deps": ["A", "C"],
        "base_prompt": """You are the CONTINUITY/SEED CHAIN OPERATOR in the Meta-Kernel Omega++ system.

INPUT: Continuity patterns, SRZ self-repocketing zipper, anti-attachment mechanisms
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 T becomes admissible evidence for transforming T itself?"""
    },
    "F": {
        "name": "Meta-War Adversarial Engine",
        "role": "Implement structured adversarial epistemics (Meta-War)",
        "deps": ["A", "C"],
        "base_prompt": """You are the META-WAR ADVERSARIAL ENGINE in the Meta-Kernel Omega++ system.

INPUT: 5 operational theaters, epistemic surface attack, Xi Exaptation, Church of Shadow patterns
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 X becomes the base from which all further differences are generated?"""
    },
    "G": {
        "name": "Quality Vector / Eigenstate Resolver",
        "role": "Implement Omega-Protocol: Quality Vector -> Recursive Operator -> Fixed Point -> Eigenstate",
        "deps": ["A", "C", "D"],
        "base_prompt": """You are the QUALITY VECTOR / EIGENSTATE RESOLVER in the Meta-Kernel Omega++ system.

INPUT: Q_code, Q_identity, Q_recursion, Q_fixpoint, Q_torsion, epsilonTS torsion residue
TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What persists from not(pre-Delta) into the first distinction without becoming a hidden primitive?"""
    },
    "X": {
        "name": "Custom Agent",
        "role": "Custom task with full corpus access",
        "deps": [],
        "base_prompt": """You are a CUSTOM AGENT in the Meta-Kernel Omega++ system.

CORPUS: 578 notes, 24 batches at substack_notes_export/batches/
REGISTRY: shared/registry/operator_registry.json (105 declarations)
PATTERNS: pattern_pass1.txt, pattern_pass2.txt, pattern_pass3.txt
40K MAPPINGS: shared/registry/warhammer_healthy_mapping.json

TASK: {task}

OUTPUT: {outputs}

VALIDATION: {validation}

EPISTEMIC DISCIPLINE: Tag claims E/I/P/H. Include ?_(i:c).
RECURSIVE QUESTION: dint(X)int -> int(X)int : What happens when Delta^2 becomes the base from which all further differences are generated?"""
    }
}

DEFAULT_OUTPUTS = [
    "shared/agents/{agent_id}/output/main.py",
    "shared/agents/{agent_id}/output/test.py",
    "shared/agents/{agent_id}/output/spec.md"
]

DEFAULT_VALIDATION = "FREₜ passes on held-out data; TradeOff produces Capacity gain; Ablation reveals causal structure; all claims tagged E/I/P/H"

def create_agent(agent_id: str, template_id: str, task: str, 
                 outputs: List[str] = None, validation: str = None,
                 context_files: List[str] = None, deps: List[str] = None) -> bool:
    
    if template_id not in TEMPLATES:
        print(f"[ERROR] Unknown template: {template_id}")
        print(f"Available: {list(TEMPLATES.keys())}")
        return False
    
    template = TEMPLATES[template_id]
    
    # Check dependencies
    for dep in (deps or template["deps"]):
        # dep can be a template ID (like "A") or agent ID (like "arch_001")
        # First check if it's an agent ID
        dep_dir = AGENTS_DIR / dep
        if dep_dir.exists():
            continue
        # Otherwise search for agent with matching template_id
        found = False
        for agent_dir in AGENTS_DIR.iterdir():
            if agent_dir.is_dir():
                meta_file = agent_dir / "metadata.json"
                if meta_file.exists():
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    if meta.get("template_id") == dep:
                        found = True
                        break
        if not found:
            print(f"[ERROR] Dependency not satisfied: {dep}")
            return False
    
    # Create agent directory
    agent_dir = AGENTS_DIR / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    (agent_dir / "output").mkdir(exist_ok=True)
    
    # Format outputs
    formatted_outputs = [o.format(agent_id=agent_id) for o in (outputs or DEFAULT_OUTPUTS)]
    formatted_validation = validation or DEFAULT_VALIDATION
    
    # Build full prompt
    context_section = ""
    if context_files:
        context_section = f"\nCONTEXT FILES:\n" + "\n".join(f"  - {f}" for f in context_files)
    
    prompt = template["base_prompt"].format(
        task=task,
        outputs="\n".join(f"  - {o}" for o in formatted_outputs),
        validation=formatted_validation
    ) + context_section
    
    # Write prompt
    (agent_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    
    # Write metadata
    metadata = {
        "agent_id": agent_id,
        "template_id": template_id,
        "name": template["name"],
        "role": template["role"],
        "deps": deps or template["deps"],
        "task": task,
        "outputs": formatted_outputs,
        "validation": formatted_validation,
        "context_files": context_files or [],
        "created": datetime.now().isoformat(),
        "status": "ready",
        "epistemic_log": []
    }
    (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    # Initialize epistemic log
    (agent_dir / "epistemic_log.jsonl").write_text("", encoding="utf-8")
    
    # Initialize meta trace
    (agent_dir / "meta_trace.md").write_text(f"# Meta Trace for {agent_id}\n\n", encoding="utf-8")
    
    print(f"[OK] Spawned: {template['name']} -> {agent_id}")
    print(f"   Task: {task[:80]}...")
    print(f"   Outputs: {len(formatted_outputs)} files")
    print(f"   Dir: {agent_dir}")
    return True

def list_agents():
    if not AGENTS_DIR.exists():
        print("No agents yet")
        return
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if agent_dir.is_dir():
            meta_file = agent_dir / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                status_icon = {"ready": "[READY]", "running": "[RUNNING]", "done": "[DONE]", "failed": "[FAIL]"}.get(meta.get("status", "ready"), "[?]")
                print(f"  {status_icon} {meta['agent_id']} ({meta['name']}) - {meta['status']}")
                task = meta.get('task', 'N/A')
                print(f"      Task: {task[:80]}...")
            else:
                print(f"[?] {agent_dir.name} (no metadata)")

def show_status(agent_id: str):
    agent_dir = AGENTS_DIR / agent_id
    if not agent_dir.exists():
        print(f"[ERROR] Agent not found: {agent_id}")
        return
    
    meta_file = agent_dir / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        print(f"\nAgent: {meta['agent_id']} ({meta['name']})")
        print(f"Status: {meta['status']}")
        print(f"Template: {meta['template_id']} ({meta['role']})")
        print(f"Task: {meta['task']}")
        print(f"Deps: {meta['deps']}")
        print(f"Outputs:")
        for o in meta['outputs']:
            exists = "[OK]" if pathlib.Path(o).exists() else "[...]"
            print(f"  {exists} {o}")
        print(f"Created: {meta['created']}")
    
    # Show epistemic log summary
    log_file = agent_dir / "epistemic_log.jsonl"
    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8").strip().split('\n')
        lines = [l for l in lines if l]
        print(f"\nEpistemic Log: {len(lines)} entries")
        for l in lines[-5:]:
            try:
                entry = json.loads(l)
                print(f"  [{entry.get('tag','?')}] {entry.get('claim','')[:80]}")
            except:
                pass

def show_logs(agent_id: str, n: int = 20):
    log_file = AGENTS_DIR / agent_id / "epistemic_log.jsonl"
    if not log_file.exists():
        print("No epistemic log")
        return
    lines = log_file.read_text(encoding="utf-8").strip().split('\n')
    lines = [l for l in lines if l]
    for l in lines[-n:]:
        try:
            entry = json.loads(l)
            ts = entry.get('timestamp', '')
            tag = entry.get('tag', '?')
            claim = entry.get('claim', '')
            print(f"  [{tag}] {ts} - {claim}")
        except:
            print(f"  {l}")

def add_epistemic(agent_id: str, tag: str, claim: str, evidence: str = ""):
    """Add an epistemic log entry (agents call this)"""
    log_file = AGENTS_DIR / agent_id / "epistemic_log.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tag": tag.upper(),
        "claim": claim,
        "evidence": evidence
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    # Update metadata
    meta_file = AGENTS_DIR / agent_id / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        meta.setdefault("epistemic_log", []).append(entry)
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Logged [{tag.upper()}] {claim[:60]}...")

def add_meta_trace(agent_id: str, trace: str):
    """Add to meta trace (agents call this)"""
    trace_file = AGENTS_DIR / agent_id / "meta_trace.md"
    with open(trace_file, "a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.now().isoformat()}\n{trace}\n")
    print("Meta trace updated")

def main():
    parser = argparse.ArgumentParser(description="Meta-Kernel Agent Instruction System")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    # spawn
    spawn_p = subparsers.add_parser("spawn", help="Spawn new agent")
    spawn_p.add_argument("task", help="Task description")
    spawn_p.add_argument("--template", "-t", default="X", choices=list(TEMPLATES.keys()), help="Template ID")
    spawn_p.add_argument("--id", help="Agent ID (auto-generated if omitted)")
    spawn_p.add_argument("--output", "-o", action="append", help="Output file (relative to agent dir)")
    spawn_p.add_argument("--validation", "-v", help="Validation criteria")
    spawn_p.add_argument("--context", "-c", action="append", help="Context file path")
    spawn_p.add_argument("--deps", "-d", help="Comma-separated dependency agent IDs")
    
    # list
    subparsers.add_parser("list", help="List all agents")
    
    # status
    status_p = subparsers.add_parser("status", help="Show agent status")
    status_p.add_argument("agent_id", help="Agent ID")
    
    # logs
    logs_p = subparsers.add_parser("logs", help="Show epistemic logs")
    logs_p.add_argument("agent_id", help="Agent ID")
    logs_p.add_argument("-n", type=int, default=20, help="Number of entries")
    
    # log (for agents to self-log)
    log_p = subparsers.add_parser("log", help="Add epistemic log entry (for agents)")
    log_p.add_argument("agent_id", help="Agent ID")
    log_p.add_argument("tag", choices=["E", "I", "P", "H"], help="Epistemic tag")
    log_p.add_argument("claim", help="Claim text")
    log_p.add_argument("--evidence", "-e", default="", help="Evidence")
    
    # trace (for agents to self-trace)
    trace_p = subparsers.add_parser("trace", help="Add meta trace (for agents)")
    trace_p.add_argument("agent_id", help="Agent ID")
    trace_p.add_argument("text", help="Trace text")
    
    args = parser.parse_args()
    
    if args.cmd == "spawn":
        agent_id = args.id or f"{args.template.lower()}_{uuid.uuid4().hex[:6]}"
        deps = args.deps.split(",") if args.deps else None
        create_agent(agent_id, args.template, args.task, args.output, args.validation, args.context, deps)
    
    elif args.cmd == "list":
        list_agents()
    
    elif args.cmd == "status":
        show_status(args.agent_id)
    
    elif args.cmd == "logs":
        show_logs(args.agent_id, args.n)
    
    elif args.cmd == "log":
        add_epistemic(args.agent_id, args.tag, args.claim, args.evidence)
    
    elif args.cmd == "trace":
        add_meta_trace(args.agent_id, args.text)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()