# Round 3 — M3 boundary check is vacuous

## Self-attack target
Claim: `ImaginaryUnit.ipynb` cell 12 (M3 sweep) certifies a **4π double-cover**
("PASS (M3 4-pi Double-Cover Verified)") via the boundary check
`|V[0] - V[-1]| < 0.05`.

**Verdict: the check is vacuous.** The two endpoints it compares are the *same*
physical phase modulo 2π, so the test passes for *any* 2π-periodic system and for
*any* 4π-periodic system alike. It cannot certify 4π.

---

## 1. Cell-anchored evidence (verbatim, `ImaginaryUnit.ipynb` cell idx=12)

Source: `adv_common.cell_lines(12)` — 0-based index into `nb["cells"]`.

| cell line | role | verbatim |
|---|---|---|
| L24 | sweep definition | `phi_sweeps_m3 = np.linspace(-2 * np.pi, 2 * np.pi, 100)` |
| L52 | **the check** | `"periodicity_conforms_to_4pi": bool(np.abs(V_target_results[0] - V_target_results[-1]) < 0.05)` |
| L55 | verdict | `"status": "PASS (M3 4-pi Double-Cover Verified)" if np.abs(V_target_results[0] - V_target_results[-1]) < 0.05 else "FAIL (Loop boundary mismatch)"` |

From the frozen harness `run_notebook_verification.py:95-127` (re-run from
`wallfield_actual.py` verbatim):

```text
phi_sweeps_m3[0]  = -2*pi = -6.283185307179586
phi_sweeps_m3[-1] = +2*pi =  6.283185307179586
boundary_deviation            = 0.0
periodicity_conforms_to_4pi   = True
verdict                       = "PASS (M3 4-pi Double-Cover Verified)"
```

---

## 2. Assertion: `phi_sweeps_m3[0] == phi_sweeps_m3[-1] (mod 2π)`

```python
phi0 = -2*math.pi      # -6.283185307179586
phiN =  2*math.pi      #  6.283185307179586
(phiN - phi0) % (2*math.pi)   # == 0.0   (they differ by 4*pi, i.e. 2 full 2*pi turns)
phi0 % (2*math.pi)            # == 0.0
phiN % (2*math.pi)            # == 0.0
```

Both endpoints are congruent to `0 (mod 2π)`. They are the **same phase**.

**Consequence:** any observable that is a function of phase alone satisfies
`V(-2π) == V(+2π)` *by definition* whenever the observable is 2π-periodic.
The check `|V[0]-V[-1]|<0.05` is therefore satisfied identically by a 2π-periodic
system — which is exactly what the M3 loop actually is (see §6 of
`notebook_verification_results.json`: `m3_flip_basis` — the flipped edge `2->0`
is driven by a source node clamped to `phi=0`, making its dφ equal to the
non-flipped edge's dφ, so the flip never engages).

---

## 3. Explicit 4π-periodic function `f` with `f(-2π) == f(2π)` — the check still passes

Take the spinor/cosine-half observable

```
f(phi) = cos(phi / 2)
```

**4π-periodic (genuinely, not 2π):**
```
f(phi + 4π) = cos((phi+4π)/2) = cos(phi/2 + 2π) = cos(phi/2) = f(phi).   ✓ 4π-periodic
f(phi + 2π) = cos(phi/2 + π)  = -cos(phi/2)      ≠ f(phi).                ✗ not 2π-periodic
```

**Endpoints agree (the check passes):**
```
f(-2π) = cos(-π) = -1.0
f(+2π) = cos(+π) = -1.0
|f(-2π) - f(+2π)| = 0.0  < 0.05   →  check PASSES
```

So even a **genuinely** 4π-periodic function satisfies the notebook's boundary
test. And:

**A 2π-periodic function satisfies it too (counterexample → vacuity):**
```
g(phi) = cos(phi)
g(-2π) = cos(-2π) = 1.0
g(+2π) = cos(+2π) = 1.0
|g(-2π) - g(+2π)| = 0.0  < 0.05   →  check PASSES
```

**Conclusion.** `V[0] == V[-1]` is *necessary* for 4π-periodicity but is **not
sufficient**: it holds for the 2π-periodic `g` as well. The test certifies
neither 4π nor distinguishes 2π from 4π; it is a structural null
(`phi[0] ≡ phi[-1] (mod 2π)`), exactly the `m3_boundary_coincidence` finding
recorded in `notebook_verification_results.json:671`.

---

## 4. Minimal alternative phase set that WOULD distinguish 2π from 4π

The defect is that the two sampled points are **4π apart and 0 mod 2π
coincident** — i.e. useless for separating the periods.

**Fix.** Sample points `phi` and `phi + 2π` that *both lie inside*
`[-2π, +2π]` (so `phi ∈ [-2π, 0]`). A 2π-periodic system is invariant under
every such 2π-shift; a (non-2π) 4π-periodic system must differ at *some*
such pair.

Minimal phase set (5 points):

```
Φ = { -2π, -π, 0, π, 2π }
```

Form the three interior 2π-separated pairs and require the **existence** of a
break:

```
P1 = |V(-2π) - V(0)|      # phi=-2π  vs phi+2π=0
P2 = |V(-π)  - V(π)|      # phi=-π   vs phi+2π=π
P3 = |V(0)    - V(2π)|    # phi=0    vs phi+2π=2π
```

**Distinguishing predicate (existence test):**

```
4π-cert  :  max(P1, P2, P3) > 0.05   AND   |V(-2π) - V(2π)| < 0.05   (endpoint closure still holds)
2π       :  all(P1, P2, P3) < 0.05   (no 2π-shift breaks invariance)
```

**Check on `f(phi) = cos(phi/2)`:**
```
P1 = |f(-2π) - f(0)|   = |(-1) - 1|  = 2.0000  > 0.05   → distinguishes
P2 = |f(-π)  - f(π)|   = |0    - 0|  = 0.0000  <= 0.05  (coincidental zero; P1/P3 catch it)
P3 = |f(0)   - f(2π)|  = |1    -(-1)| = 2.0000  > 0.05   → distinguishes
```

With the current M3 observable `V[2]` the *actual* simulation yields
`boundary_deviation = 0.0` and (per the inert-flip analysis) the curve is
effectively 2π-periodic, so `P1 ≈ P2 ≈ P3 ≈ 0` — correctly classifying it as
**2π (not 4π)** under the predicate above.

---

## 5. Spinor sign-flip variant (the real SU(2) double-cover signature)

The notebook reasons in **intensity** `|ψ|²`, which is invariant under
`ψ → -ψ` and therefore blind to the double-cover. The true 4π signature of an
SU(2)/spinor system is a **sign flip** at 2π and **restoration** at 4π:

```
ψ(φ + 2π) = -ψ(φ)      # sign flip (the double cover)
ψ(φ + 4π) = +ψ(φ)      # restored
```

**Predicate (complex-amplitude / spinor test):**

```
∃ phi interior :  |ψ(φ) + ψ(φ+2π)| < ε   AND   |ψ(φ) - ψ(φ+2π)| > ε
AND            :  |ψ(φ) + ψ(φ+4π)| < ε   (restoration)
```

Equivalently on a real-valued proxy of the *same* observable: a genuine
double-cover system has `V(φ+2π) == -V(φ)` for some φ (the amplitude, not
`|amplitude|²`, carries the sign). The notebook's `V[2]` is clamped to an
amplitude but the recorded metric is `|V[2]|`-style intensity dynamics with no
phase-sign degree of freedom, so it can **never** satisfy the spin-flip
predicate — confirming the `phase_model_prediction` layer verdict in
`scoring_verdict_m1_m2_m3_layered.json` (M3 physical_interpretation: "OPEN").

---

## Summary
- `phi_sweeps_m3[0] = -2π` and `phi_sweeps_m3[-1] = +2π` are **identical mod 2π**
  (both ≡ 0).
- The check `|V[0]-V[-1]|<0.05` (cell L52) passes trivially for **any** 2π-periodic
  system and for any genuinely 4π-periodic `f` (e.g. `cos(φ/2)`), by construction.
- Real M3 `boundary_deviation = 0.0` is the *expected* output of the inert (2π)
  loop, not evidence of 4π.
- A distinguishing sweep must compare `V(φ)` vs `V(φ+2π)` for interior φ
  (minimal set `{-2π,-π,0,π,2π}`) or, for a true SU(2) check, measure the
  **sign flip** `ψ(φ+2π) = -ψ(φ)` on a complex amplitude.
