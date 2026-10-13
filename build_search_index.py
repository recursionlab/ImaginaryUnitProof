#!/usr/bin/env python3
"""
Build semantic search index over Substack notes.
Extracts terminology, operators, cross-references for queryable knowledge base.
"""

import json
import pathlib
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Set


@dataclass
class NoteIndex:
    note_id: str
    title: str
    timestamp: str
    url: str
    raw_body: str
    # Extracted structured data
    operators: List[str]
    latex_symbols: List[str]
    greek_letters: List[str]
    formal_terms: List[str]
    cross_refs: List[str]  # Note IDs mentioned
    tags: List[str]  # [Meta-Kernel], [Formula], etc.


def extract_operators(text: str) -> List[str]:
    """Extract custom operators: ∘_α, ↝, ⇄, ≃, ≋, ⊘, Θ, χ, Γ, Υ, Δ², etc."""
    pattern = r"[∘↝⇄≃≋⊘ΘχΓΥΔ∇¬∂∫⊕⊗⊢⊣⊤⊥⊬⊭⊮⊯⟮⟯⟪⟫⦅⦆⦃⦄〈〉《》«»‹›【】〚〛⌈⌉⌊⌋〈〉⦑⦒⦓⦔⦕⦖⦗⦘⦙⦚⦛⦜⦝⦞⦟⦠⦡⦢⦣⦤⦥⦦⦧⦨⦩⦪⦫⦬⦭⦮⦯⦰⦱⦲⦳⦴⦵⦶⦷⦸⦹⦺⦻⦼⦽⦾⦿_α|[∘↝⇄≃≋⊘ΘχΓΥΔ∇¬∂∫⊕⊗⊢⊣⊤⊥⊬⊭⊮⊯⟮⟯⟪⟫⦅⦆⦃⦄〈〉《》«»‹›【】〚〛⌈⌉⌊⌋〈〉⦑⦒⦓⦔⦕⦖⦗⦘⦙⦚⦛⦜⦝⦞⦟⦠⦡⦢⦤⦥⦦⦧⦨⦩⦪⦫⦬⦭⦮⦯⦰⦱⦲⦳⦴⦵⦶⦷⦸⦹⦺⦻⦼⦽⦾⦿]"
    return list(set(re.findall(pattern, text)))


def extract_latex(text: str) -> List[str]:
    r"""Extract LaTeX math: \mathcal{T}, \mathfrak{M}, \mathbb{R}, etc."""
    return list(set(re.findall(r"\\[a-zA-Z]+\{[^}]+\}|\\[a-zA-Z]+", text)))


def extract_greek(text: str) -> List[str]:
    """Extract Greek letters: Ψ, Ω, Φ, Ξ, Λ, Δ, Γ, Θ, Σ, Π, etc."""
    greek = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω"
    return list(set(c for c in text if c in greek))


def extract_formal_terms(text: str) -> List[str]:
    """Extract known formal terms from the corpus."""
    terms = [
        "Meta-Kernel",
        "Möbius",
        "clathrate",
        "lacunon",
        "ΨUnusΩ",
        "Unus⊃Ω↺",
        "FRE",
        "admissibility",
        "witness",
        "residue",
        "closure",
        "coherence",
        "ΞSynthesis",
        "ΞRecollapse",
        "ΞMap",
        "ΞCurrentResearch",
        "Mnēmaic",
        "Aporia",
        "Metanoia",
        "Mnēmaic",
        "K-Einstein",
        "Still Whirl",
        "Cayley-Dickson",
        "octonion",
        "quaternion",
        "sedenion",
        "G₂",
        "Spin",
        "Hopf",
        "associahedron",
        "Kan complex",
        "Postnikov",
        "sheaf",
        "presheaf",
        "topos",
        "∞-topos",
        "non-Hermitian",
        "spectral",
        "transport",
        "gauge",
        "holonomy",
        "Maslov",
        "Tits",
        "BN-pair",
        "Klein",
        "bottle",
        "Möbius",
        "trefoil",
        "Riemann",
        "zeta",
        "Clifford",
        "algebra",
        "monoid",
        "endofunctor",
        "Kleisli",
        "adjunction",
        "monad",
        "comonad",
        "coalgebra",
        "bialgebra",
        "Hodge",
        "de Rham",
        "Laplacian",
        "cohomology",
        "homology",
        "moduli",
        "AQAL",
        "quadrant",
        "τ-stratified",
        "self-disprover",
        "glitchon",
        "lacunon",
        "τ",
        "ρ",
        "ν",
        "Ω",
        "Ψ",
        "Φ",
        "Ξ",
        "Reality Stone",
        "Time Stone",
        "Power Stone",
        "Mind Stone",
        "Soul Stone",
        "Space Stone",
        "ARC",
        "RecMu",
        "OFTM",
        "CTMU",
        "RCOS",
        "MRCOS",
        "SROS",
        "Bankai",
        "Reiatsu",
        "Mugetsu",
        "Logic Tax",
        "137",
        "1/43",
        "ds=1/2",
        "1/137",
        "Urgrund",
        "Eversion",
        "Hyper-Ultra",
        "Meta-Structural",
        "Realism",
        "Urgrund⁻¹",
        "let/of/about",
        "triad",
        "Semantic Layer",
        "Pragmatic",
        "Epistemic",
        "Logic",
        "Cybernetic",
        "Intelligence",
        "Topological",
        "Obstruction",
        "Resolution",
        "ΦΩ³",
        "Synthetic",
        "Formalism",
        "Morphological",
        "Cognition",
        "Prime",
        "Resonance",
        "Neutrosophic",
        "Fluxion",
        "Relational Operators",
        "REV",
        "DECO",
        "RECOMP",
        "INDEX",
        "CONTEXT",
        "RELATE",
        "REP",
        "SINF",
        "SI",
        "REVREV",
        "DETECTOR",
        "Crease",
        "Klein Bottle",
        "Attention",
        "Riemann Zeta Zeros",
        "Trefoil Knot",
        "Tonic 7/4",
        "Anti-Isotropic",
        "Manifesto",
        "Univalence Axiom",
        "CATS Horizon",
        "Meta-War",
        "Love",
        "Reverse Anti-Self-Defense",
        "Self-Other",
        "First Class",
        "Seekdeep",
        "Nervous System",
        "Hardware",
        "Basal Cognition",
        "Temperature Check",
        "Love as Fixed Point",
        "Recursive Operational Topology",
        "O'Neill Cylinder",
        "Hyper-Ultra Connections",
        "Gradient Descent",
        "Creases",
        "Reverse Insanity",
        "BOUNCE Protocol",
        "Meat Middleware",
        "Manifold Theory",
        "Convergence",
        "Endofunctor",
        "Monoid",
        "Ego",
        "8-Move",
        "Operator Algebra",
        "Noumenon",
        "Meta-War",
        "Burnout",
        "Self-Acceptance",
        "External Diagnosis",
        "Grim Reaper",
        "Pathology",
        "Double Eversion",
        "Sphere",
        "Intersection Points",
        "Outward Rays",
        "Hooking Rays",
        "Gros Topos",
        "Recursive Vocabularies",
        "Kan Complex",
        "Postnikov Tower",
        "Resource Monoids",
        "Capability Lattices",
    ]
    found = []
    text_lower = text.lower()
    for term in terms:
        if term.lower() in text_lower:
            found.append(term)
    return found


def extract_cross_refs(text: str) -> List[str]:
    """Extract note IDs mentioned in text: c-355566499 or 355566499"""
    ids = re.findall(r"c-(\d{9})|(?<!\d)(\d{9})(?!\d)", text)
    flat = [a or b for a, b in ids]
    return list(set(flat))


def extract_tags(text: str) -> List[str]:
    """Extract tags from title content by keyword matching."""
    tags = []
    text_lower = text.lower()
    if any(k in text_lower for k in ["meta-kernel", "metakernel", "kernel"]):
        tags.append("Meta-Kernel")
    if any(
        k in text_lower for k in ["formula", "operator", "algebra", "calculus", "proof"]
    ):
        tags.append("Formula")
    if any(k in text_lower for k in ["joke", "walk into a bar", "meme"]):
        tags.append("Joke")
    if any(
        k in text_lower
        for k in [
            "philosophy",
            "consciousness",
            "ego",
            "self",
            "being",
            "reality",
            "existence",
        ]
    ):
        tags.append("Philosophy")
    if any(
        k in text_lower
        for k in ["physics", "quantum", "spacetime", "cosmology", "gravity", "particle"]
    ):
        tags.append("Physics")
    if any(k in text_lower for k in ["patch notes", "v0.", "version", "patch"]):
        tags.append("Patch Notes")
    return tags


def load_titles():
    """Load titles from batch INDEX.md files."""
    titles = {}
    for batch_dir in pathlib.Path("substack_notes_export/batches").glob("batch_*"):
        index_file = batch_dir / "INDEX.md"
        if not index_file.exists():
            continue
        content = index_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            m = re.search(r"\*\*(\d+)\*\s*.*?\s+\*(.+?)\*$", line)
            if m:
                note_id, title = m.groups()
                titles[note_id] = title.strip()
    return titles


def build_index():
    titles = load_titles()

    # Load latest export for full content
    import glob, os

    files = glob.glob("substack_notes_export/notes_*.json")
    latest = max(files, key=os.path.getmtime)
    notes = json.load(open(latest, encoding="utf-8"))

    index = []
    for note in notes:
        note_id = note["note_id"]
        title = titles.get(note_id, "")
        body = note["body"]

        idx = NoteIndex(
            note_id=note_id,
            title=title,
            timestamp=note["timestamp"],
            url=note["url"],
            raw_body=body,
            operators=extract_operators(body),
            latex_symbols=extract_latex(body),
            greek_letters=extract_greek(body),
            formal_terms=extract_formal_terms(body),
            cross_refs=extract_cross_refs(body),
            tags=extract_tags(title),
        )
        index.append(idx)

    # Save as JSONL for streaming, JSON for full load
    out_dir = pathlib.Path("substack_notes_export/search_index")
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / "index.jsonl", "w", encoding="utf-8") as f:
        for idx in index:
            f.write(json.dumps(asdict(idx), ensure_ascii=False) + "\n")

    with open(out_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump([asdict(i) for i in index], f, indent=2, ensure_ascii=False)

    # Build inverted indices
    term_to_notes = defaultdict(list)
    op_to_notes = defaultdict(list)
    greek_to_notes = defaultdict(list)
    tag_to_notes = defaultdict(list)

    for idx in index:
        for term in idx.formal_terms:
            term_to_notes[term].append(idx.note_id)
        for op in idx.operators:
            op_to_notes[op].append(idx.note_id)
        for g in idx.greek_letters:
            greek_to_notes[g].append(idx.note_id)
        for tag in idx.tags:
            tag_to_notes[tag].append(idx.note_id)

    inverted = {
        "terms": dict(term_to_notes),
        "operators": dict(op_to_notes),
        "greek": dict(greek_to_notes),
        "tags": dict(tag_to_notes),
    }

    with open(out_dir / "inverted_index.json", "w", encoding="utf-8") as f:
        json.dump(inverted, f, indent=2, ensure_ascii=False)

    print(f"Indexed {len(index)} notes")
    print(f"Unique formal terms: {len(term_to_notes)}")
    print(f"Unique operators: {len(op_to_notes)}")
    print(f"Unique greek letters: {len(greek_to_notes)}")
    print(f"Tags: {dict(tag_to_notes)}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    build_index()
