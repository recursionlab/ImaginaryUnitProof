# Round 4 — Self-Audit: The `variance > 0.01` PASS Criterion Cannot Certify M2 Orientation Gating

**Status:** CRITICAL — criterion destroyed
**Method:** Direct numerical reproduction from `wallfield_actual.py` via `run_notebook_verification.py`
**Target:** Cell 9 verdict line — `PASS (M2 Junction Verified in Simulation)` / `Variance in transmission amplitude demonstrates active phase gating across the flipped orientation boundary.`

---

## Step 1 — wallfield_actual: M1 vs M2 over the full sweep

Loaded `wallfield_actual.py` (verbatim source) through `run_notebook_verification.py`.
Ran `run_m1_sweep()` and `run_m2_sweep()` with identical initial conditions except for
the M2 flipped edge (`set_flipped_edge(L, M, True)`).

| Metric | Value |
|---|---|
| `var(M1)` | `0.09464497511616608` |
| `var(M2)` | `0.09464497511616608` |
| `var(M1) == var(M2)` | **True** |
| `corr(M1, M2)` | **1.0** |
| `mean |M1 - M2|` | **0.0** |
| Pointwise identical | **True** |

The M1 and M2 transmission curves `V[M]` are **pointwise identical** across all 50 phase
samples. The flipped orientation edge in M2 has **zero observable effect** because its source
node (L) is clamped to phase 0, making `d_phi(flip) = -phi_L - phi_M = 0` equal to
`d_phi(nonflip) = phi_L - phi_M = 0`. `cos(0) = 1` in both branches — the T-flip operator is
byte-identical to the non-flipped path (see `notebook_verification_results.json` lines 666–667).

---

## Step 2 — Construct `B = -A`: identical variance, opposite physical meaning

Let `A = V_M` (the M1/M2 transmission curve, cos-shaped and physically interpretable as
constructive→destructive interference). Construct `B = -A` (the exact negation — physically,
this would represent the **opposite** interference signature: destructive everywhere A is
constructive).

| Metric | Value |
|---|---|
| `A` (M1/M2 curve) | cos-shaped, peaks at 0.799 |
| `B = -A` | cos-shaped, **inverted**, troughs at -0.799 |
| `var(A)` | `0.09464497511616608` |
| `var(B)` | `0.09464497511616608` |
| `var(A) == var(B)` | **True** |
| `corr(A, B)` | **-1.0** |
| `A passes variance > 0.01` | **True** |
| `B passes variance > 0.01` | **True** |

**Proof by contradiction:** `A` and `B = -A` are physically opposite — if `A` represents
"gate opens at phase alignment," then `B` represents "gate closes at phase alignment." They
carry **opposite physical meaning**. Yet `var(A) = var(B)` exactly and `corr(A, B) = -1.0`.
Both pass the >0.01 criterion. A variance threshold of 0.01 **cannot distinguish** a curve
from its exact physical negation. If variance > 0.01 certified "active orientation gating,"
it would certify both `A` and `B` — which are mutually contradictory physical claims.
Therefore, variance > 0.01 is **logically incapable** of certifying orientation gating.

---

## Step 3 — Flat-zero vs cos curve: variance measures non-flatness, not physics

Constructed two canonical curves over the same 50-point sweep `phi in [-pi, pi]`:

| Curve | Description | `var` | Passes `> 0.01`? |
|---|---|---|---|
| **Flat-zero** | `V = 0` everywhere (no transmission — fully "inactive") | `0.0` | **False** |
| **Cos** | `V = cos(phi)/2 + 0.5` (non-flat — appears "active") | `0.12739999999999999` | **True** |

The flat-zero curve has `var = 0` and correctly fails the threshold. The cos curve has
`var = 0.12739999999999999` and passes the threshold. But the cos curve's passing is **not** evidence
of orientation gating — it simply reflects that the curve is non-flat. This is exactly what
happens in M2: the curve that passes `variance > 0.01` is **identical to M1** (Step 1), and the
flipped edge is inert. The variance is inherited from M1's `cos(phi_S - phi_M)` phase-gating
dynamics, not from any orientation-flip effect.

A variance threshold of 0.01 separates "flat" from "non-flat" — it is a **trivial
non-degeneracy check**, not a discriminator of orientation physics.

---

## Step 4 — Conclusion: `variance > 0.01` is true of any non-flat curve

The `variance > 0.01` criterion:

1. **Cannot distinguish M1 from M2** — they are pointwise identical (`var = 0.09464497511616608`,
   `corr = 1.0`), yet M1 is the baseline and M2 is claimed to add orientation
   gating. If the criterion passes for both, it certifies nothing new about M2.
2. **Cannot distinguish A from -A** — two curves with identical variance (0.09464497511616608) and
   opposite physical meaning both pass. A criterion that cannot separate contradictory
   physical claims is vacuous.
3. **Cannot distinguish flat-zero from cos** — one is genuinely inactive (`var = 0`, fails),
   the other passes but its passing is purely a measure of non-flatness, not of active
   orientation gating. M2 falls in the "passes but inert" category.

**The criterion is a necessary-but-not-sufficient test for non-flatness, not a test for
orientation gating.** It passes for M2 not because the T-flip engages, but because M2 is
numerically identical to M1 and inherits its non-flat, cos-shaped transmission profile.
The flipped edge's source node is clamped to phase 0, so the orientation operator never
acts — and the variance > 0.01 PASS criterion is satisfied regardless.

### Citation — Cell 9 verdict line

From `ImaginaryUnit.ipynb` cell 9 (M2 sweep), as reproduced in `run_notebook_verification.py:91`:

> `PASS (M2 Junction Verified in Simulation)`

And from `scoring_verdict_m2.json`:

> `PASS (M2 Junction Verified in Simulation)`  
> `Variance in transmission amplitude demonstrates active phase gating across the flipped orientation boundary.`

This verdict is **invalid**. The variance > 0.01 criterion is satisfied identically by M1
(the baseline with no flip) and by the negated curve `B = -A` (opposite physical meaning).
Cell 9's PASS certifies a non-flatness artifact, not orientation gating.

---

## Evidence chain

- `wallfield_actual.py` — source of `M2WallFieldSimulation.tickVField` (lines 77–90): the flip
  branch computes `d_phi = -phi[j] - phi[i]`, but with both L and M clamped to `phi = 0`,
  this equals the non-flip branch's `d_phi = phi[j] - phi[i] = 0`.
- `run_notebook_verification.py:91` — the `variance > 0.01` PASS criterion.
- `notebook_verification_results.json:222–226` — M1 max = M2 max = 0.7989364408479221, identical.
- `notebook_verification_results.json:666–669` — M2 and M3 flip inert basis (source node clamped to phase 0).
- `scoring_verdict_m1_m2_m3_layered.json:42–55` — M2 logic_test verdict: FAIL (degenerate / null effect);
  physical_interpretation verdict: NOT ESTABLISHED (vacuous).
- `round4_audit.py` — this audit's computational source.
- `round4_audit_results.json` — numerical output.

---

## Verdict

**FAIL — The `variance > 0.01` PASS criterion is destroyed as evidence of M2 orientation gating.**

M2's T-flip is inert (source node clamped to phase 0, `cos(0) = 1` in both branches).
The curve that passes the threshold is pointwise identical to M1. Variance > 0.01 is true of
any non-flat curve — including the negated curve `B = -A` with opposite physical meaning.
It is a non-degeneracy check masquerading as a physics test.