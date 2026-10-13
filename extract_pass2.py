import pathlib, re

batches_dir = pathlib.Path("substack_notes_export/batches")
notes = {}
for batch in batches_dir.glob("batch_*"):
    for md in batch.glob("*.md"):
        if md.name != "INDEX.md":
            notes[md.stem] = md.read_text(encoding="utf-8")

all_text = "\n".join(notes.values())

# Pass 2: Find all Meta-Kernel operator declarations (X := ...)
kernel_decls = re.findall(r'^[A-Zℚ𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ][A-Za-z0-9_𝔗𝔈𝔐𝔛𝔓𝔑𝔙𝔚𝔛𝔜𝔇ℝℚℂℤℕ]*\s*:=', all_text, re.MULTILINE)
# Better: find all lines with := that look like operator definitions
decl_lines = [line for line in all_text.split('\n') if ':=' in line and not line.strip().startswith('#')]

# Pass 3: Find all transition rules (→ᶠ, ↝, ⇄, etc. with context)
transitions = re.findall(r'.{0,40}[→↝⇄⇏⇒↦↣↠].{0,40}', all_text)

# Pass 4: Find all ∂∫...∫∂ framed expressions
meta_boundary = re.findall(r'∂∫[^∫]*∫∂', all_text)

# Pass 5: Find all ΨUnusΩ / Ψ₀ᵢUnus / Unus⊃Ω patterns
unus_patterns = re.findall(r'.{0,30}[Ψ]?Unus.{0,30}', all_text)

# Pass 6: Find all Retro-Precursor patterns
retro_patterns = re.findall(r'.{0,40}Retro.Precursor.{0,40}', all_text)

# Pass 7: Find all Coalesce/Generate patterns
cg_patterns = re.findall(r'.{0,30}(Coalesce|Generate)[←→].{0,30}', all_text)

# Pass 8: Find all Mnēmaic / Aporia/Metanoia patterns
mnemaic_patterns = re.findall(r'.{0,30}(Mnēmaic|Aporia|Metanoia).{0,30}', all_text)

# Pass 9: Find all Shadow/Void patterns
shadow_patterns = re.findall(r'.{0,30}(Shadow|Void).{0,30}', all_text)

# Pass 10: Find all FRE/Adm/Closure patterns
adm_patterns = re.findall(r'.{0,30}(FRE|Adm|Closure|Wₜ|Rₜ).{0,30}', all_text)

# Pass 11: Find all μX fixed point patterns
mux_patterns = re.findall(r'μX[^μ]*', all_text)

# Pass 12: Find all ⟦Ξ|Ξ⟧ / ⟨Ξ|Ξ⟩ patterns
xi_xi_patterns = re.findall(r'.{0,30}[⟦⟨]Ξ[|⟧⟩].{0,30}', all_text)

# Pass 13: Find all Ω-protocol / Ω-layer patterns
omega_patterns = re.findall(r'.{0,30}Ω[^Ω]*', all_text)

# Pass 14: Find all Ξ-particle / Ξ-fold / Ξ-gap patterns
xi_patterns = re.findall(r'.{0,30}Ξ[^Ξ]*', all_text)

# Pass 15: Find all ARC / Analytic Reality Closure patterns
arc_patterns = re.findall(r'.{0,30}(ARC|Analytic Reality Closure).{0,30}', all_text)

# Write all to file
out = []
out.append("=== KERNEL DECLARATIONS (:=) ===")
for d in decl_lines[:100]:
    out.append(f"  {d.strip()}")

out.append("\n=== TRANSITION RULES ===")
for t in transitions[:50]:
    out.append(f"  {t.strip()}")

out.append("\n=== META-BOUNDARY (∂∫...∫∂) ===")
for m in meta_boundary[:50]:
    out.append(f"  {m.strip()}")

out.append("\n=== UNUS PATTERNS ===")
for u in unus_patterns[:50]:
    out.append(f"  {u.strip()}")

out.append("\n=== RETRO-PRECURSOR ===")
for r in retro_patterns[:50]:
    out.append(f"  {r.strip()}")

out.append("\n=== COALESCE/GENERATE ===")
for c in cg_patterns[:50]:
    out.append(f"  {c.strip()}")

out.append("\n=== MNĒMAIC/APORIA/METANOIA ===")
for m in mnemaic_patterns[:50]:
    out.append(f"  {m.strip()}")

out.append("\n=== SHADOW/VOID ===")
for s in shadow_patterns[:50]:
    out.append(f"  {s.strip()}")

out.append("\n=== FRE/ADM/CLOSURE ===")
for a in adm_patterns[:50]:
    out.append(f"  {a.strip()}")

out.append("\n=== μX FIXED POINTS ===")
for m in mux_patterns[:50]:
    out.append(f"  {m.strip()}")

out.append("\n=== Ξ|Ξ PATTERNS ===")
for x in xi_xi_patterns[:50]:
    out.append(f"  {x.strip()}")

out.append("\n=== Ω PATTERNS ===")
for o in omega_patterns[:50]:
    out.append(f"  {o.strip()}")

out.append("\n=== Ξ PATTERNS ===")
for x in xi_patterns[:50]:
    out.append(f"  {x.strip()}")

out.append("\n=== ARC PATTERNS ===")
for a in arc_patterns[:50]:
    out.append(f"  {a.strip()}")

pathlib.Path("pattern_pass2.txt").write_text("\n".join(out), encoding="utf-8")
print("Written to pattern_pass2.txt")