import json, pathlib, re

# Load all note bodies
batches_dir = pathlib.Path("substack_notes_export/batches")
notes = {}
for batch in batches_dir.glob("batch_*"):
    for md in batch.glob("*.md"):
        if md.name != "INDEX.md":
            notes[md.stem] = md.read_text(encoding="utf-8")

print(f"Loaded {len(notes)} notes")

# Extract ALL symbolic operators/patterns from the corpus itself
all_text = "\n".join(notes.values())

# Find all unicode operators and symbolic patterns
operators = set(re.findall(r'[∂∫∘⇄↝⊃⊂⊕⊗⊘⊢⊣⟦⟧⟨⟩∇ΘΥΣΩΨΞΦΛΔΓΞΠ∇∂∫∮∯∰∴∵≃≋≠≡⇏⊢⊣⊤⊥⊤⊥∀∃∈⊆⊇⊂⊃⊄⊅∪∩∧∨¬⇒⇔↑↓←→↔⇄↕↗↘↙↖↚↛↞↠↝↜↷↶↻↺]', all_text))
# Write all output to file to avoid encoding issues
out_lines = []
out_lines.append(f"Unique unicode operators: {len(operators)}")
for op in sorted(operators):
    out_lines.append(f"  {op}")

# Find all function-like patterns: Name(args) or Name[args]
func_patterns = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*\([^)]*\)', all_text))
out_lines.append(f"\nFunction-like patterns: {len(func_patterns)}")
for f in sorted(func_patterns)[:50]:
    out_lines.append(f"  {f}")

# Find all subscripted/indexed patterns
indexed = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*₍[^₎]*₎', all_text))
out_lines.append(f"\nIndexed patterns: {len(indexed)}")
for i in sorted(indexed)[:30]:
    out_lines.append(f"  {i}")

# Find all bracketed/angle patterns
bracketed = set(re.findall(r'⟦[^⟧]*⟧|⟨[^⟩]*⟩|\[[^\[\]]*\]', all_text))
out_lines.append(f"\nBracketed patterns: {len(bracketed)}")
for b in sorted(bracketed)[:30]:
    out_lines.append(f"  {b}")

# Find all patterns like X := Y (definitions)
definitions = set(re.findall(r'[A-Za-z_𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ][A-Za-z0-9_𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ]*\s*:=', all_text))
out_lines.append(f"\nDefinitions (:=): {len(definitions)}")
for d in sorted(definitions)[:30]:
    out_lines.append(f"  {d}")

# Find all patterns with arrows/transitions
arrows = set(re.findall(r'[A-Za-z_𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ][A-Za-z0-9_𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ]*\s*[→↝⇄↦↣↠↢↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪⇫⇬⇭⇮⇯⇰⇱⇲⇳⇴⇵⇶⇷⇸⇹⇺⇻⇼⇽⇾⇿]', all_text))
out_lines.append(f"\nArrow patterns: {len(arrows)}")
for a in sorted(arrows)[:30]:
    out_lines.append(f"  {a}")

# Find all greek letter + subscript combos
greek_subscript = set(re.findall(r'[ΘΥΣΩΨΞΦΛΔΓΞΠΘΩΨΞΦΛΔΓΞΠ][₀₁₂₃₄₅₆₇₈₉ₜₓᵧᵢⱼₖₗₘₙₒₚqᵣₛₜᵤᵥwₓᵧz]+', all_text))
out_lines.append(f"\nGreek subscript patterns: {len(greek_subscript)}")
for g in sorted(greek_subscript)[:30]:
    out_lines.append(f"  {g}")

# Write to file
out_path = pathlib.Path("pattern_inventory.txt")
out_path.write_text("\n".join(out_lines), encoding="utf-8")
print(f"Written to {out_path}")