# Round 6 — Ruthless Self-Audit: The 4π Observable Gap

**Status:** CRITICAL — M3 cannot certify a 4π double-cover. The boundary check is vacuous, V[2] is a 2π-periodic amplitude-only observable (cos-gated, even, intensity-style), and the recorded metric has no complex-phase/sign degree of freedom to detect the spinor sign flip ψ(φ+2π) = −ψ(φ).

**Method:** Cell-12 reproduction via `wallfield_actual.M3LoopFieldSimulation` (verbatim class, `wallfield_actual.py:93-117`); extended sweep over [0, 8π] with exact 2π integer-step alignment (801 points, step π/100); `discrimination_tests.m3_spinor_test()` for the |ψ|² reference.

---

## 1. Cell 12 (M3) — verbatim via `adv_common.cell_lines(12)`

| cell line | role | verbatim |
|---|---|---|
| L8 | instantiate | `sim_m3 = M3LoopFieldSimulation(num_nodes)` |
| L11,12,13 | directed cycle | `sim_m3.set_listen_weight(0,1,1.0); sim_m3.set_listen_weight(1,2,1.0); sim_m3.set_listen_weight(2,0,1.0)` |
| L21 | flip | `sim_m3.set_flipped_edge(2, 0, True)` |
| L24 | sweep | `phi_sweeps_m3 = np.linspace(-2 * np.pi, 2 * np.pi, 100)` |
| L33 | source clamp | `sim_m3.set_node_state(0, V_val=1.0, phi_val=sweep_phi)` |
| L38 | tick | `sim_m3.tickVField(alpha=0.15)` |
| L41 | record | `V_target_results.append(sim_m3.V[2])` |
| L52 | **the check** | `"periodicity_conforms_to_4pi": bool(np.abs(V_target_results[0] - V_target_results[-1]) < 0.05)` |
| L55 | verdict | `"PASS (M3 4-pi Double-Cover Verified)"` |

**Scoring artifact (`scoring_verdict_m3.json`):** `max_amplitude=0.9997, min_amplitude=0.0, periodicity_conforms_to_4pi=true, boundary_deviation=0.0`.

---

## 2. The 4π observable gap

The notebook claims 4π certification from `|V[2](-2π) - V[2](+2π)| < 0.05`. This is **vacuous**:

```
phi[0]  = -2*pi  = -6.283185307179586   =>  mod 2*pi = 0.0
phi[-1] = +2*pi  =  6.283185307179586   =>  mod 2*pi = 0.0
```

The endpoints differ by **4π** (so any 4π-periodic function agrees) AND are **both 0 mod 2π** (so any 2π-periodic function also agrees). Per `notebook_verification_results.json:671` (`m3_boundary_coincidence`): *"phi_sweeps_m3[0]=-2pi and [-1]=+2pi are identical mod 2pi (both ==0); |V(-2pi)-V(2pi)|<0.05 passes for ANY 2pi-periodic system."*

Reproduced boundary_deviation = **0.00e+00** (passes < 0.05, but trivially).

---

## 3. Minimal observable certifying a 4π double-cover

The genuine SU(2) double-cover signature is a **spinor sign flip**, not an amplitude coincidence:

> **ψ(φ + 2π) = −ψ(φ)**  (sign flip at 2π — the double cover)
> **ψ(φ + 4π) = +ψ(φ)**  (restoration at 4π)

**Minimal distinguishing predicate:** sample the complex amplitude ψ at interior points φ and φ+2π such that:

```
∃ interior φ:  |ψ(φ) + ψ(φ+2π)| < ε   (they cancel — sign flip detected)
            AND |ψ(φ) − ψ(φ+2π)| > ε   (they differ, not identical — not 2π)
AND:           |ψ(φ) − ψ(φ+4π)| < ε   (restored at 4π)
```

This requires a **phase-sensitive** observable (complex amplitude with sign). `discrimination_tests.m3_spinor_test()` confirms `psi(phi)=exp(i*phi/2)` satisfies this:

| Check | Value | Meaning |
|---|---|---|
| `max|ψ(φ) + ψ(φ+2π)|` | **6.47e-16** | sign flip: ψ cancels with its 2π-shifted self |
| `min|ψ(φ) − ψ(φ+2π)|` | **2.0000** | they are maximally different (opposite sign) |
| `max|ψ(φ) − ψ(φ+4π)|` | **1.20e-15** | restored at 4π |
| `max|intensity(φ) − intensity(φ+2π)|` | **6.66e-16** | intensity |ψ|² is blind |

The interference observable `|ψ+ref|²` (where `ref=exp(iφ)`) IS the 4π signature — `interference_signal_periodic_under_2pi = False` (the interference is genuinely 4π-periodic, not 2π). V[2] has no such interference or phase-sign structure.

---

## 4. V[2] cannot carry 4π — amplitude-only proof

V[2] is the recorded target-node amplitude. It responds to `gating = cos(d_φ)` (`wallfield_actual.py:87`, cell 12 L87), and `cos` is an **even** function: `cos(−x) = cos(x)`. The flipped edge computes `d_φ = −φ[j] − φ[i]` (cell 12 L107) while non-flip computes `d_φ = φ[j] − φ[i]` (cell 12 L110) — but `cos(−φ[j]−φ[i]) = cos(φ[j]+φ[i])` and `cos(φ[j]−φ[i])` are NOT generally equal, yet V[2] has **no sign degree of freedom**: it is real-valued and clipped to `[0, 10]` (`wallfield_actual.py:116`), making it structurally `|ψ|²`-like.

V[2] also never evolves its phase (`M3LoopFieldSimulation` computes `new_phi` at line 99 but never assigns it to `self.phi` — `self.phi` is frozen), so only cos-gating on a static field drives the dynamics.

**Extended sweep** (801 points, step π/100, exact 2π = 200 steps and 4π = 400 steps alignment, range [0, 8π]):

| Shift | `max|V[2](φ) − V[2](φ+shift)|` | `mean` | ~0? |
|---|---|---|---|
| **2π** | **3.31e-15** | 2.12e-16 | True |
| **4π** | **2.55e-15** | 2.96e-16 | True |

Both are **machine-zero**. A genuine 4π double-cover observable with a sign flip would show `|V[2](φ) − V[2](φ+2π)|` **large** (the sign must change — the curve inverts) and `|V[2](φ) − V[2](φ+4π)|` ~0 (restoration). Instead, V[2] changes identically under both shifts — it is **2π-periodic and trivially 4π-periodic**, with no sign flip at 2π.

**Cell-12 boundary:** `|V[2](−2π) − V[2](+2π)| = 0.00e+00` — passes < 0.05 but both endpoints are φ ≡ 0 (mod 2π).

---

## 5. Recorded metric is intensity-style (|ψ|²-like, flat)

The M3 scoring artifact records only **amplitude** fields (`scoring_verdict_m3.json`):

```json
"results": {
    "max_amplitude": 0.9997042353362874,
    "min_amplitude": 0.0,
    "periodicity_conforms_to_4pi": true
}
```

No complex phase, no sign information — purely intensity-style. Per `discrimination_tests.m3_spinor_test()`:

| Metric | Value | Interpretation |
|---|---|---|
| `intensity_mean` | 1.0 | |ψ|² is constant |
| `intensity_range` | 8.88e-16 | **flat** — no variation to signal a 2π flip |
| `intensity_only_periodic_2pi` | True | |ψ|² is 2π-periodic (blind to 4π) |
| `interference_signal_periodic_under_2pi` | False | only |ψ+ref|² is the 4π signature — absent from V[2] |
| `verdict` | **FAIL (intensity-only)** | intensity alone cannot certify a spinor double cover |

V[2] is structurally equivalent to |ψ|²: real, non-negative (clipped), cos-gated, 2π-periodic. The `cos` gating (even function) destroys the sign information needed to detect ψ → −ψ.

---

## 6. Inert flip (amplifying the gap)

Per `notebook_verification_results.json:669`: *"Flipped edge 2->0 (source node 2) is clamped to phi=0 => d_phi(flip) = -phi_2 - phi_0 = -phi_0 equals d_phi(nonflip) = phi_2 - phi_0 = -phi_0; the T-flip never engages on M3."*

Node 2 (source of the flipped edge 2->0) is clamped to `phi=0` (cell 12 L30: `sim_m3.phi.fill(0.0)`, L33 sets only node 0's phi). With `phi[2]=0`, the flip branch `d_phi = -0 - phi[0] = -phi[0]` and the non-flip branch `d_phi = 0 - phi[0] = -phi[0]` are **identical** — and `cos(-phi[0]) = cos(phi[0])` anyway. The orientation operator never acts.

---

## 7. Conclusion: M3 cannot certify 4π

Three independent failures collapse the M3 double-cover claim:

1. **Vacuous boundary check** (§2): `|V[2](−2π) − V[2](+2π)| < 0.05` compares the same physical phase (both ≡ 0 mod 2π). It passes for any 2π- or 4π-periodic system. Cannot certify.

2. **Amplitude-only observable** (§4): `max|V[2](φ) − V[2](φ+2π)| = 3.31e-15` and `max|V[2](φ) − V[2](φ+4π)| = 2.55e-15` — both machine-zero. V[2] is 2π-periodic with no sign degree of freedom. A true 4π signature requires `|V[2](φ) − V[2](φ+2π)|` large (sign flip) — absent.

3. **Intensity-style recording** (§5): M3 records only `max_amplitude`, `min_amplitude`, `periodicity_conforms_to_4pi` — all |ψ|²-like. `discrimination_tests.m3_spinor_test()` verdicts: `|ψ|²` is flat and 2π-periodic; only the interference observable |ψ+ref|² carries the 4π signature, and V[2] lacks it.

4. **Inert flip** (§6): The flipped edge's source node is clamped to φ=0, so `d_phi(flip) = d_phi(nonflip)` and `cos(−x) = cos(x)` — the T-flip is a structural no-op.

**Verdict: FAIL — M3 cannot certify a 4π double-cover.** The boundary check is structurally vacuous, V[2] is a 2π-periodic amplitude observable with no sign/phase degree of freedom, and the recorded metric is intensity-style (|ψ|²-like, flat). The PASS in `scoring_verdict_m3.json` is a boundary-coincidence artifact, not evidence of double-cover physics.

---

## Evidence chain

- `adv_common.py:11-15` — `cell_lines(idx)` reads notebook cell idx (0-based).
- `adv_common.py:35-38` — `write_round(n, content)` writes `organized/audit_outputs/adversarial/Round_n.md`.
- `ImaginaryUnit.ipynb` cell idx=12 — M3 sweep (verbatim, L24/L41/L52/L55).
- `wallfield_actual.py:93-117` — `M3LoopFieldSimulation` (verbatim port of cell 11; `new_phi` computed L99 but never assigned to `self.phi`).
- `run_notebook_verification.py:95-127` — frozen re-run of cell 12 from wallfield_actual.
- `scoring_verdict_m3.json` — recorded `boundary_deviation=0.0, periodicity_conforms_to_4pi=true`.
- `notebook_verification_results.json:668-671` — `m3_flip_inert=true, m3_flip_basis`, `m3_boundary_coincidence`.
- `scoring_verdict_m1_m2_m3_layered.json:57-71` — M3 phased_model_prediction: "PARTIAL", physical_interpretation: "OPEN".
- `discrimination_tests.py:37-56` — `m3_spinor_test()`: |ψ|² flat, 2π-periodic; interference 4π-periodic.
- `prove_m6_4pi_gap.py` — this audit's computational source.
- `m6_4pi_gap_results.json` — numerical output.
