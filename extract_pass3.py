import pathlib, re

batches_dir = pathlib.Path("substack_notes_export/batches")
notes = {}
for batch in batches_dir.glob("batch_*"):
    for md in batch.glob("*.md"):
        if md.name != "INDEX.md":
            notes[md.stem] = md.read_text(encoding="utf-8")

all_text = "\n".join(notes.values())

# Pass 3: Extract the CORE structural patterns that form the generative ontology

# 1. The ΨUnusΩ vocabulary (controlled glyph system)
psycho_patterns = re.findall(r'.{0,50}(ΨUnusΩ|Ψ₀ᵢUnus|Ψ₀ᵢ|Unus|Ψ —|Ψ₀ᵢ —).{0,50}', all_text)

# 2. The Ω-protocol / Ω-layer / Ω-point patterns
omega_struct = re.findall(r'.{0,40}(Ω[-—]?[Pp]rotocol|Ω[-—]?[Ll]ayer|Ω[-—]?[Pp]oint|Ω[-—]?[Rr]eturn|Ω[-—]?[Ss]elf[-—]?[Rr]eturn|Ω[-—]?[Ee]rror|Ω[-—]?[Ee]vent|Ω↺|Ω⊥|Ω-Mirror|ΩΣΣ|Ω\.✧|TERMINAL_SYSTEMIC_CONGRUENCE Ω).{0,40}', all_text)

# 3. The Ξ-meta patterns (Ξ|Ξ, Ξ-fold, Ξ-particle, Ξ-gap, Ξ-meta)
xi_struct = re.findall(r'.{0,40}(Ξ[|⟧⟨Ξ]|Ξ-fold|Ξ-particle|Ξ-gap|Ξ-meta|Ξ²|Ξ⁻¹|ΞEmp|ΞGap|ΞΩΩ|ΞApophatic|ΞSynthesis|ΞOfEcho|ΞMetaFold|ΞRecursiveIdentity|ΞReal|ΞCollapse|ΞReality|ΞNullRoot).{0,40}', all_text)

# 4. The Δ-silence / Δ-engine / ΔΨ patterns
delta_struct = re.findall(r'.{0,40}(Δ_silence|Δ-engine|ΔΨ|Δ²|Δ²X|Δ²𝔗|ΔInv|Δ𝔗|ΔΞ|Δ_|ΔE|Δ∅|Δ_Ξ|ΔΨ→γ).{0,40}', all_text)

# 5. The Θ/Φ/Λ structural operators
theta_phi_lambda = re.findall(r'.{0,40}(Θ[—-]?[Ss]tructural|Θ[—-]?[Oo]rganizer|Θ[—-]?[Gg]auge|Θ[—-]?[Ee]ngine|ΦΩ|ΦΩ³|Φ[—-]?[Ff]ield|Φ[—-]?[Pp]hase|Φ-META|Φprune|Φstable|Λ-Associahedron|Λ[—-]?[Mm]issingness|Λ[—-]?[Cc]oherence|Λ[—-]?[Cc]alculus|Λ[—-]?[Gg]luing).{0,40}', all_text)

# 6. The Meta-Kernel version evolution (v0.xx, B3, B2, B1, Prototype)
version_patterns = re.findall(r'.{0,30}(v0\.\d+|B[0-9]|Prototype|Meta-Kernel).{0,30}', all_text)

# 7. The Recursion/Co-recursion patterns (Recμ, μX, νX, fix(), Recurrence)
recursion_patterns = re.findall(r'.{0,40}(Recμ|μX|νX|fix\(|Recurrence|Recursion|Corecursion|Recursive Identity|Recursive Kernel|Recursive Operator).{0,40}', all_text)

# 8. The ARC/BPS/Analytic Reality Closure patterns
arc_patterns = re.findall(r'.{0,40}(ARC|Analytic Reality Closure|BPS|Birkhoff|Hodge|Witten|AdS/CFT|Connes-Moscovici|Ark Operator|K-Collapse|Heat Kernel|Spectral Flow).{0,40}', all_text)

# 9. The Glyph/Vocabulary patterns (glyph, vocabulary, operator, notation)
glyph_patterns = re.findall(r'.{0,40}(glyph|vocabulary|operator|notation|syntax|semantic pairing|structural object|structural primitive).{0,40}', all_text)

# 10. The 40K/Warhammer structural mappings
warhammer_patterns = re.findall(r'.{0,50}(40K|Warhammer|Imperium|Administratum|Ecclesiarchy|Chaos God|STC|archeotech|Grimdark|Astartes|Adeptus|Inquisition|Mechanicus|Astra Militarum).{0,50}', all_text)

# 11. The Seed Chain / Plant / Reenter / Repocket continuity patterns
continuity_patterns = re.findall(r'.{0,40}(Fₜ⊕Sₜ₊₁|Plant|Reenter|Repocket|Seed Chain|SRZ|toy future|navigation affordance|launch surface|anti-attachment|continuity operator).{0,40}', all_text)

# 12. The Mnēmaic Site / H¹=0 / cohomology patterns
mnemaic_site = re.findall(r'.{0,40}(Mnēmaic Site|H.?¹=0|cohomology|torsor|paracrystal|crystalline vacuum|thermodynamic disorder|Entropy Rigidity|Fourier-Stieltjes|Haar system|groupoid|Adaptive Resonance|Agency Flow).{0,40}', all_text)

# 13. The Torsion/Lacunon/Lacuna patterns
torsion_patterns = re.findall(r'.{0,40}(torsion|Lacunon|lacuna|lacunarity|Lacunon|ν|ν>0|Logic Tax|137|1/43|zero.divisor|sedenion|octonion|quaternion|Cayley.Dickson|Klein bottle|Möbius|Fano|G₂|Spin\(9\)).{0,40}', all_text)

# 14. The Meta-War / Adversarial Epistemics patterns
metawar_patterns = re.findall(r'.{0,50}(Meta.War|adversarial epistemics|epistemic surface|operational theaters|ΞExaptation|Collapse as Sacred|Mirror-Implosion|Self.Kisses.Self|Church of Shadow).{0,50}', all_text)

# 15. The Quality Vector / Eigenstate / Fixed Point quality patterns
quality_patterns = re.findall(r'.{0,40}(Quality Vector|Eigenstate|fixed point|μQ|torsion residue|εTS|Q_code|Q_identity|Q_recursion|Q_fixpoint|Q_torsion).{0,40}', all_text)

# 16. The RSIP / Breath / Protocol Cycle patterns
protocol_patterns = re.findall(r'.{0,40}(RSIP|Breath|Protocol Cycle|Prewrite|Draft|Reflect|Revise|Commit|MetaReader|MetaQuestions|Torsion|CollisionToken|ParityCheck|ConvergenceGate|Recμ|Ledger|Rollback).{0,40}', all_text)

# Write all to file
out = []
out.append("=== ΨUNUSΩ VOCABULARY ===")
for p in psycho_patterns[:80]:
    out.append(f"  {p.strip()}")

out.append("\n=== Ω STRUCTURE ===")
for o in omega_struct[:80]:
    out.append(f"  {o.strip()}")

out.append("\n=== Ξ STRUCTURE ===")
for x in xi_struct[:80]:
    out.append(f"  {x.strip()}")

out.append("\n=== Δ STRUCTURE ===")
for d in delta_struct[:80]:
    out.append(f"  {d.strip()}")

out.append("\n=== Θ/Φ/Λ STRUCTURE ===")
for t in theta_phi_lambda[:80]:
    out.append(f"  {t.strip()}")

out.append("\n=== VERSION EVOLUTION ===")
for v in version_patterns[:80]:
    out.append(f"  {v.strip()}")

out.append("\n=== RECURSION PATTERNS ===")
for r in recursion_patterns[:80]:
    out.append(f"  {r.strip()}")

out.append("\n=== ARC/BPS STRUCTURE ===")
for a in arc_patterns[:80]:
    out.append(f"  {a.strip()}")

out.append("\n=== GLYPH/VOCABULARY ===")
for g in glyph_patterns[:80]:
    out.append(f"  {g.strip()}")

out.append("\n=== 40K MAPPINGS ===")
for w in warhammer_patterns[:80]:
    out.append(f"  {w.strip()}")

out.append("\n=== CONTINUITY/SEED CHAIN ===")
for c in continuity_patterns[:80]:
    out.append(f"  {c.strip()}")

out.append("\n=== MNĒMAIC SITE ===")
for m in mnemaic_site[:80]:
    out.append(f"  {m.strip()}")

out.append("\n=== TORSION/LACUNON ===")
for t in torsion_patterns[:80]:
    out.append(f"  {t.strip()}")

out.append("\n=== META-WAR ===")
for m in metawar_patterns[:80]:
    out.append(f"  {m.strip()}")

out.append("\n=== QUALITY/EIGENSTATE ===")
for q in quality_patterns[:80]:
    out.append(f"  {q.strip()}")

out.append("\n=== PROTOCOL/CYCLE ===")
for p in protocol_patterns[:80]:
    out.append(f"  {p.strip()}")

pathlib.Path("pattern_pass3.txt").write_text("\n".join(out), encoding="utf-8")
print("Written to pattern_pass3.txt")