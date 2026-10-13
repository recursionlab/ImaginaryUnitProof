# Self-Conjugation Master Meta-Draft

**Primary artifact:** `self_conjugation_master_meta_draft.pdf`  
**Editable source:** `self_conjugation_master_meta_draft.tex`  
**Status:** Scope/architecture draft, not a proof-complete or publication-ready paper.

## Scope

The paper integrates four connected workstreams:

1. **Self-Conjugation:** typed transform, invariant, residue, retained information, reconstruction, and external constraints.
2. **8D alternative-slice compiler:** exact Cayley–Dickson reference operations, explicit subalgebra closure, typed morphisms, and verified partial composition.
3. **Structural topological meta-fields:** a platform-neutral intermediate representation (IR) with operators, relations, invariants, provenance, and evidence.
4. **Generator-hub integration:** first a narrow Perchance import/embed/share-link proof of concept, then a generic adapter contract for other hubs.

It also maps a candidate non-tautological symmetry/entropy research program, independent cold-start verification, phase gates, a portfolio priority matrix, and links to MRMD and Case Xi-001.

## Key corrections preserved in this draft

- `-r log(r)` is not a Shannon entropy when `r` can exceed 1; the earlier `dim(Aut(A))/dim(A)` ratio can do so for octonions.
- The preliminary value `dim Aut(sedenions) = 3` is not retained as fact. Standard-construction literature reports `Aut(S) ~= G2 x S3`; because `S3` is finite, this group has Lie dimension 14. Verify conventions against the chosen algebra implementation before freezing data.
- A vector with at most eight active coordinates is not automatically inside a closed 8D octonion subalgebra. The compiler must test embeddings and closure.
- Octonion multiplication is nonassociative. Composition of functions/morphisms can be associative, but the paper's proposed partial category must prove identities and associativity for its declared composition.
- Algebraic/structural entropy is not thermodynamic entropy. A physical bridge requires its own model, units, state variables, and evidence.
- Missing source Word/Excel files must not be reconstructed from fragments and then treated as originals. The paper can be produced from the supplied context; original docket/register mutation requires the authoritative files.

## Build

```bash
pdflatex self_conjugation_master_meta_draft.tex
pdflatex self_conjugation_master_meta_draft.tex
```

The second run resolves the table of contents and internal links. References are embedded in the LaTeX source.

## Important boundary

The linked Colab notebook could not be inspected directly in this session. This draft uses the notebook output pasted in the conversation plus checked public references. It does **not** claim that the original Colab notebook, Word docket, Excel register, or live Perchance project was modified.
