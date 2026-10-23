# Phase-tree antipode / extracted-pair trace audit

**Algebra:** ordinary Connes–Kreimer Hopf algebra of non-planar rooted trees; phase transport is set to identity.

## Core definitions

- `Tree(children)` stores an explicit root node. The one-node tree is `Tree(())` = `•`.
- The algebra unit is the empty forest `()`, displayed as `1`; it is not the one-node tree.
- `P_c(T)` is the pruned forest and `R_c(T)` the remaining rooted trunk.
- `τ₂(T) = -T + Σ_c P_c(T)·R_c(T)`, summed over all nonempty admissible cuts.
- `r⁽ⁿ⁾(T) := τ₂(T) − S(T)` for an n-vertex tree.

## Shape notation

- `•` = one-vertex tree; `1` = empty-forest unit.
- `C₂ = (•)` is the two-vertex chain; `C₃ = ((•))` is the three-vertex chain; `Y₃ = (•,•)` is the three-vertex star.
- Degree-4 shapes: `(•,•,•)` is the 4-star; `(•,(•))` has root-children of sizes 1 and 2; `((•,•))` has a star as the root’s child; `(((•)))` is the 4-chain.

## Degree-3 chain and star

| Tree | Raw τ₂ | Antipode S | Residue r⁽³⁾ = τ₂ − S | τ₂ ⋆ id |
|---|---|---|---|---|
| `(•,•)` | `•·•·• + 2·•·(•) - (•,•)` | `-•·•·• + 2·•·(•) - (•,•)` | `2·•·•·•` | `2·•·•·•` |
| `((•))` | `2·•·(•) - ((•))` | `-•·•·• + 2·•·(•) - ((•))` | `•·•·•` | `•·•·•` |

Both left and right antipode identities are checked as exact polynomial equalities; the counit target is zero for every nonempty tree.

## Degree-4 topology residues

| Tree | Nonempty cuts | τ₂(T) | S(T) | r⁽⁴⁾(T) = τ₂(T) − S(T) | τ₂ ⋆ id | τ₂′ = S? |
|---|---:|---|---|---|---|---|
| `(•,•,•)` | 7 | `•·•·•·• + 3·•·•·(•) + 3·•·(•,•) - (•,•,•)` | `•·•·•·• - 3·•·•·(•) + 3·•·(•,•) - (•,•,•)` | `6·•·•·(•)` | `6·•·•·(•)` | True |
| `(•,(•))` | 5 | `2·•·•·(•) + •·(•,•) + •·((•)) + (•)·(•) - (•,(•))` | `•·•·•·• - 3·•·•·(•) + •·(•,•) + •·((•)) + (•)·(•) - (•,(•))` | `-•·•·•·• + 5·•·•·(•)` | `-•·•·•·• + 5·•·•·(•)` | True |
| `((•,•))` | 4 | `•·•·(•) + •·(•,•) + 2·•·((•)) - ((•,•))` | `•·•·•·• - 3·•·•·(•) + •·(•,•) + 2·•·((•)) - ((•,•))` | `-•·•·•·• + 4·•·•·(•)` | `•·•·•·• + 4·•·•·(•)` | True |
| `(((•)))` | 3 | `2·•·((•)) + (•)·(•) - (((•)))` | `•·•·•·• - 3·•·•·(•) + 2·•·((•)) + (•)·(•) - (((•)))` | `-•·•·•·• + 3·•·•·(•)` | `3·•·•·(•)` | True |

## Recursive subtraction and interpretation

Define the correction independently from a call to `S` by

`τ₂′(T) = τ₂(T) − Σ_c [P_c(T) + τ₂′(P_c(T))]·R_c(T)`,

with `τ₂′` extended multiplicatively to forests. Since `τ₂(T) = −T + Σ_c P_cR_c`, the pair terms cancel and this reduces to

`τ₂′(T) = −T − Σ_c τ₂′(P_c(T))·R_c(T)`,

which is exactly the standard antipode recursion. Consequently `τ₂′ = S` is guaranteed by construction; the genuinely informative object remains the raw residual `r⁽ⁿ⁾ = τ₂ − S`. The correction is useful as a recursively defined trace-to-antipode map, but it does not prove that the original raw trace is antipodal.

## Validation

- Rooted-tree counts through degree 4: `{'1': 1, '2': 1, '3': 2, '4': 4}` (standard unlabeled rooted-tree counts).
- Exact left/right antipode convolution checks and coproduct coassociativity pass for all enumerated trees: `True`.
- Arithmetic is exact over integer coefficients; no floating-point tolerance is used.
- Phase transport `Φ_c` is identity. A nontrivial phase-transport coproduct needs a separately specified `Φ_c` and a proved cocycle/coassociativity condition.
- This audit validates the implementation of the standard CK baseline. It does not establish the correctness of an undefined phase-deformed Hopf algebra.
