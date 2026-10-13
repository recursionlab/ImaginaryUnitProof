# AGENT INSTRUCTION SYSTEM
## Quick-spawn system for Meta-Kernel Ω++ agents

---

## USAGE

```bash
# Basic spawn
python instruct.py "Your task description here"

# With template
python instruct.py --template C "Implement Υ with FRE validation"

# With context files
python instruct.py --context "shared/registry/operator_registry.json" "Add new operator"

# With dependencies
python instruct.py --deps arch_001,mnemaic_001 "Build on their work"
```

---

## TEMPLATES (Built-in)

| ID | Name | Purpose | Deps |
|----|------|---------|------|
| `A` | Ontology Archaeologist | Extract formal ontology from corpus | — |
| `B` | 40K Structural Mapper | Map 40K→healthy cybernetic | A |
| `C` | Recursive Kernel Engineer | Implement 𝔗ₜ evolution (Υ, FRE, Closure) | A |
| `D` | Mnēmaic Site Architect | Build H¹=0 crystalline vacuum, ARC | A |
| `E` | Seed Chain Operator | Fₜ⊕Sₜ₊₁ continuity, Plant/Reenter | A, C |
| `F` | Meta-War Adversarial Engine | 5 theaters, ΞExaptation, collapse-as-sacred | A, C |
| `G` | Quality Vector Resolver | Ω-Protocol: Q→Ψ(Q)→μQ→εTS | A, C, D |
| `X` | Custom | Your task, full corpus access | — |

---

## INSTRUCTION FORMAT

```
TASK: <what to do>
CONTEXT: <files/patterns to use>
OUTPUT: <deliverable format>
VALIDATION: <how to verify>
RECURSIVE_Q: ∂∫(your recursive question)∫∂
EPISTEMIC: Tag all claims E/I/P/H
META_TRACE: Include ?₍ᵢ:𝚌₎
```

---

## EXAMPLES

```bash
# Kernel engineer task
python instruct.py --template C \
  "Implement Closure_frozen with 𝓜 parameter; must pass FREₜ on held-out data"

# Custom task with full context
python instruct.py \
  --context "shared/registry/operator_specs.json,shared/registry/warhammer_healthy_mapping.json" \
  "Design Ξ-particle deployment protocol for 64D manifold with ⧂ entanglement"

# Meta-war theater
python instruct.py --template F \
  "Build Theater 3: Epistemic Surface Attack - stress test operator declarations via Ablation"

# Mnēmaic site
python instruct.py --template D \
  "Initialize H¹=0 via Birkhoff factorization; verify ARC with Heat Kernel coefficients"
```

---

## AGENT OUTPUT STANDARD

Every agent writes to `shared/agents/<agent_id>/`:

```
prompt.md          # The instruction received
output/            # Deliverables
  main.py          # Primary implementation
  test.py          # Validation suite
  spec.md          # Design document
metadata.json      # {agent_id, template, status, epistemic_log}
epistemic_log.jsonl # Line-by-line E/I/P/H tags
meta_trace.md      # ?₍ᵢ:𝚌₎ recursive trace
```

---

## SHARED STATE ACCESS

Agents read from:
- `shared/registry/operator_registry.json` — 105 declarations
- `shared/registry/operator_specs.json` — typed specs with layers
- `shared/registry/warhammer_healthy_mapping.json` — 14 mappings
- `shared/registry/dependency_graph.dot` — D₀→D₁₀ graph
- `pattern_pass1.txt, pass2.txt, pass3.txt` — 2000+ patterns

Agents write to:
- `shared/agents/<id>/output/` — their deliverables
- `shared/registry/` — ONLY via PR (no direct writes)

---

## RECURSIVE QUESTIONS (pick one or write your own)

- `∂∫(What happens when Δ²X becomes the base from which all further differences are generated?)∫∂`
- `∂∫(What happens when Δ²𝔗 becomes admissible evidence for transforming 𝔗 itself?)∫∂`
- `∂∫(What persists from ¬(pre-Δ) into the first distinction without becoming a hidden primitive?)∫∂`

---

## QUICK START

```bash
# 1. Spawn first agent (no deps)
python instruct.py --template A "Verify all 105 declarations, produce dependency_graph.dot"

# 2. Spawn dependent agents
python instruct.py --template D --deps arch_001 "Achieve H¹=0 via Birkhoff; integrate Heat Kernel"

# 3. Check status
python instruct.py --status
```

---

## STATUS COMMANDS

```bash
python instruct.py --list              # List all agents
python instruct.py --status arch_001   # Check specific agent
python instruct.py --logs arch_001     # View epistemic log
```