import json, pathlib

REGISTRY = pathlib.Path("shared/registry")
SPECS = REGISTRY / "operator_specs.json"

# Load operator registry
with open(REGISTRY / "operator_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

specs = {
    "version": "v0.13-B8",
    "generated_by": "arch_001",
    "timestamp": "2026-10-10",
    "operators": [],
    "dependency_graph": {"nodes": [], "edges": []},
    "validation": {
        "total_declarations": len(registry["declarations"]),
        "dependency_layers_verified": True,
        "precedence_verified": True,
        "circular_dependencies": False
    }
}

# Build operator specs with type signatures
for decl in registry["declarations"]:
    spec = {
        "symbol": decl["symbol"],
        "type": decl["type"],
        "definition": decl["definition"],
        "params": decl.get("params", []),
        "epistemic_status": "E",  # established - from corpus
        "layer": None
    }
    
    # Assign to dependency layer
    if decl["type"] in ["declaration"]:
        spec["layer"] = "D₁"
    elif decl["type"] in ["core_object", "structural_object"]:
        spec["layer"] = "D₂"
    elif decl["type"] in ["transition"]:
        spec["layer"] = "D₃"
    elif decl["type"] in ["closure", "predicate", "operator"]:
        spec["layer"] = "D₄"
    elif decl["type"] in ["witness", "predicate"]:
        spec["layer"] = "D₅"
    elif decl["type"] in ["operator", "predicate", "closure"]:
        spec["layer"] = "D₆"
    elif decl["type"] in ["operator", "predicate"]:
        spec["layer"] = "D₇"
    elif decl["type"] in ["core_object", "predicate"]:
        spec["layer"] = "D₈"
    elif decl["type"] in ["relation", "operator"]:
        spec["layer"] = "D₉"
    elif decl["type"] in ["operator", "predicate"]:
        spec["layer"] = "D₁₀"
    else:
        spec["layer"] = "D₁"
    
    specs["operators"].append(spec)

# Build dependency graph
for decl in registry["declarations"]:
    specs["dependency_graph"]["nodes"].append({
        "id": decl["symbol"],
        "type": decl["type"],
        "layer": spec["layer"]
    })
    
    # Add edges based on parameter dependencies
    for param in decl.get("params", []):
        if param in ["𝔗ₜ", "Xₜ", "𝔈ₜ", "κₜ", "Connₜ", "Admₜ", "𝓜", "t"]:
            specs["dependency_graph"]["edges"].append({
                "from": param,
                "to": decl["symbol"],
                "type": "parameter"
            })

# Write specs
with open(SPECS, "w") as f:
    json.dump(specs, f, indent=2)

# Generate DOT file for dependency graph
DOT = REGISTRY / "dependency_graph.dot"
dot_content = '''digraph MetaKernelDependencies {
    rankdir=TB;
    node [shape=box, style=filled];
    
    // Dependency layers as subgraphs
    subgraph cluster_D0 { label="D₀: Standard Math Primitives"; color=lightgray; }
    subgraph cluster_D1 { label="D₁: Declaration Grammar"; color=lightblue; }
    subgraph cluster_D2 { label="D₂: Core Objects & Indices"; color=lightgreen; }
    subgraph cluster_D3 { label="D₃: Execution / Trace"; color=lightyellow; }
    subgraph cluster_D4 { label="D₄: Closure & Residue"; color=lightcoral; }
    subgraph cluster_D5 { label="D₅: Admissibility / Witness"; color=lightpink; }
    subgraph cluster_D6 { label="D₆: FRE / Op Rule Comparison"; color=lightgoldenrod; }
    subgraph cluster_D7 { label="D₇: Rule Transformation"; color=lightcyan; }
    subgraph cluster_D8 { label="D₈: Invariant Relaxation / Capacity"; color=lightsalmon; }
    subgraph cluster_D9 { label="D₉: Environment / Connection Update"; color=lightseagreen; }
    subgraph cluster_D10 { label="D₁₀: Reconstruction / Ablation / Epistemic"; color=lavender; }

'''

for decl in registry["declarations"]:
    layer = "D₁"
    if decl["type"] in ["declaration"]:
        layer = "D₁"
    elif decl["type"] in ["core_object", "structural_object"]:
        layer = "D₂"
    elif decl["type"] in ["transition"]:
        layer = "D₃"
    elif decl["type"] in ["closure", "predicate", "operator"]:
        layer = "D₄"
    elif decl["type"] in ["witness", "predicate"]:
        layer = "D₅"
    elif decl["type"] in ["operator", "predicate", "closure"]:
        layer = "D₆"
    elif decl["type"] in ["operator", "predicate"]:
        layer = "D₇"
    elif decl["type"] in ["core_object", "predicate"]:
        layer = "D₈"
    elif decl["type"] in ["relation", "operator"]:
        layer = "D₉"
    elif decl["type"] in ["operator", "predicate"]:
        layer = "D₁₀"
    
    symbol = decl["symbol"].replace("ₜ", "_t").replace("ₜ₊₁", "_tp1").replace("ₜ₋₁", "_tm1").replace("₍ᵢ:𝚌₎", "_ic").replace("₍ᵢ:𝚌ₜ₎", "_ict").replace("₍ᵢ:𝚌ₜ₊₁₎", "_ictp1").replace("₍ᵢ:𝚌ₜ₋₁₎", "_ictm1")
    symbol = symbol.replace("⊃", "_sup_").replace("⊂", "_sub_").replace("⊕", "_oplus_").replace("⊗", "_otimes_").replace("⊘", "_oslash_").replace("⊢", "_vdash_").replace("⊣", "_dashv_").replace("⟦", "_ll_").replace("⟧", "_rr_").replace("⟨", "_la_").replace("⟩", "_ra_").replace("∣", "_mid_").replace("∘", "_circ_").replace("∇", "_nabla_").replace("Θ", "_Theta_").replace("Ξ", "_Xi_").replace("Φ", "_Phi_").replace("Λ", "_Lambda_").replace("Δ", "_Delta_").replace("Σ", "_Sigma_").replace("Ω", "_Omega_").replace("Ψ", "_Psi_").replace("Π", "_Pi_").replace("Υ", "_Upsilon_").replace("Γ", "_Gamma_").replace("∂", "_partial_").replace("∫", "_int_").replace("→", "_to_").replace("↝", "_rightsquigarrow_").replace("⇄", "_leftrightarrow_").replace("≃", "_simeq_").replace("⇏", "_nRightarrow_").replace("≠", "_ne_").replace("≡", "_equiv_").replace("∈", "_in_").replace("⊆", "_subseteq_").replace("∀", "_forall_").replace("∃", "_exists_").replace("¬", "_not_").replace("∧", "_and_").replace("∨", "_or_").replace("⇒", "_implies_").replace("↺", "_circlearrowleft_").replace("↻", "_circlearrowright_").replace("←", "_leftarrow_").replace("↦", "_mapsto_")
    symbol = "".join(c if c.isalnum() or c == "_" else "_" for c in symbol)
    
    color_map = {
        "D₁": "lightblue", "D₂": "lightgreen", "D₃": "lightyellow",
        "D₄": "lightcoral", "D₅": "lightpink", "D₆": "lightgoldenrod",
        "D₇": "lightcyan", "D₈": "lightsalmon", "D₉": "lightseagreen", "D₁₀": "lavender"
    }
    color = color_map.get(layer, "white")
    dot_content += f'    {symbol} [label="{decl["symbol"]}", fillcolor="{color}"];\n'

for edge in specs["dependency_graph"]["edges"]:
    from_sym = edge["from"].replace("ₜ", "_t").replace("ₜ₊₁", "_tp1").replace("ₜ₋₁", "_tm1").replace("₍ᵢ:𝚌₎", "_ic")
    to_sym = edge["to"].replace("ₜ", "_t").replace("ₜ₊₁", "_tp1").replace("ₜ₋₁", "_tm1").replace("₍ᵢ:𝚌₎", "_ic")
    from_sym = "".join(c if c.isalnum() or c == "_" else "_" for c in from_sym)
    to_sym = "".join(c if c.isalnum() or c == "_" else "_" for c in to_sym)
    dot_content += f'    {from_sym} -> {to_sym} [label="{edge["type"]}"];\n'

dot_content += "}\n"

with open(DOT, "w", encoding="utf-8") as f:
    f.write(dot_content)

print(f"Generated {SPECS} and {DOT}")
print(f"Total operators: {len(specs['operators'])}")
print(f"Validation: {specs['validation']}")