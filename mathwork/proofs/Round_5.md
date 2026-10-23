# Round 5 — Self-Audit: The Proposed M2 Correction (phi[L]=1.0, phi[M]=0) Fails to Engage the Flip

**Status:** CRITICAL — the correction that claims to engage the T-flip operator does not, and the variance change it produces is an artifact of background diffusion, not orientation-gate physics.

**Method:** Reproduce cell 9 via `wallfield_actual.M2WallFieldSimulation` (the verbatim class from notebook cell 8, confirmed at `wallfield_actual.py:69-90`), varying only `phi[L]` per the proposed correction. All other parameters identical to cell 9.

**Target:** The claim that setting `phi[L]=1.0` (nonzero on the flipped edge's source node) "engages" the T-flip operator on edge `L->M`, producing a variance distinct from the notebook's reported `0.0946` and thereby changing the M2 verdict.

---

## Step 1 — Cell 9's reported `0.0946` originates from `phi[L]=0` (inert)

Cell 9 (`adv_common.cell_lines(9)`) explicitly sets both intermediate nodes to phase zero:

| Cell 9 line | Role | Content |
|---|---|---|
| L9 | Phase sweep | `phi_sweeps = np.linspace(-np.pi, np.pi, 50)` — sweeps **only** `phi[S]` |
| L21 | Flip activation | `sim_m2.set_flipped_edge(L, M, True)` |
| **L25** | **Source-node phase** | `sim_m2.set_node_state(L, V_val=0.0, **phi_val=0.0**)` — `phi[L] = 0.0` |
| L26 | Target-node phase | `sim_m2.set_node_state(M, V_val=0.0, phi_val=0.0)` — `phi[M] = 0.0` |
| L48 | Variance criterion | `float(np.var(V_M_m2_results))` |
| L51 | Verdict | `"PASS" if np.var(...) > 0.01 else "FAIL"` |

The notebook's `scoring_verdict_m2.json` records `profile_variance = 0.0946449751161661` and verdict `PASS (M2 Junction Verified in Simulation)` with rationale: *"Variance in transmission amplitude demonstrates active phase gating across the flipped orientation boundary."*

**Reproduction** (from `round5_experiment.json`, run via `wallfield_actual.py` verbatim):

| Condition | var(V[M]) | corr(M1, M2) | Verdict |
|---|---|---|---|
| Cell 9 verbatim (phi_L=0, phi_M=0, flip L->M) | **0.09464497511616608** | 1.0 (pointwise identical to M1) | PASS (inert) |

The reported `0.0946` is reproduced exactly. The curve is **pointwise identical** to M1 (no flip), confirming the flipped edge `L->M` is structurally inert: `phi[L] = 0` and `phi[M] = 0`, so `d_phi(flip) = -0 - 0 = 0` and `d_phi(nonflip) = 0 - 0 = 0` — `cos(0) = 1` in both branches (`wallfield_actual.py:83-87`).

---

## Step 2 — Proposed correction: `phi[L]=1.0`, `phi[M]=0.0`

Replicating the cell-9 sweep with the single change `phi[L] = 1.0` (`M2WallFieldSimulation`, flip on `L->M`, `phi[M] = 0.0` unchanged):

| Metric | Value |
|---|---|
| `var(V_M_m2_results)` (M2 corrected) | **0.013638347755336662** |
| `corr(M1_uncorrected, M2_corrected)` | **0.3957259261747667** |
| `max(V_M_m2_results)` | 0.3036222071920645 |
| Notebook reported variance | 0.09464497511616608 |
| Verdict (var > 0.01) | **PASS** (0.0136 > 0.01, but barely) |

**The verdict does NOT change** — variance drops from `0.0946` to `0.0136`, but `0.0136 > 0.01` still yields `PASS`. The correction produces a number distinct from `0.0946`, but it does not flip the verdict.

---

## Step 3 — The flip is STILL inert: cos-evenness proof

The proposed correction changes `phi[L]` to `1.0` but leaves `phi[M] = 0.0`. Because the flip operator computes `d_phi = -phi[j] - phi[i]` and the non-flip computes `d_phi = phi[j] - phi[i]`, and the gating is `cos(d_phi)` — and **cosine is an even function** (`cos(-x) = cos(x)`):

| Condition | d_phi (flip) | d_phi (nonflip) | cos(d_phi) | Identical? |
|---|---|---|---|---|
| `phi_L=1.0, phi_M=0.0` (proposed correction) | `-1.0 - 0.0 = -1.0` | `1.0 - 0.0 = 1.0` | `0.5403023058681398` | **Yes** |
| `phi_L=0.0, phi_M=0.0` (cell 9) | `-0 - 0 = 0.0` | `0 - 0 = 0.0` | `1.0` | **Yes** |

From `round5_experiment.json` `"cos_evenness_proof_optionA"`:

```json
{
  "phi_L": 1.0,
  "phi_M": 0.0,
  "d_phi_flip_minus_phiL_minus_phiM": -1.0,
  "d_phi_nonflip_phiL_minus_phiM": 1.0,
  "gating_flip": 0.5403023058681398,
  "gating_nonflip": 0.5403023058681398,
  "gating_identical": true
}
```

**The T-flip on `L->M` remains byte-identical to the non-flip path.** Setting `phi[L] = 1.0` while `phi[M] = 0` cannot engage the flip because `cos(-phi_L - 0) = cos(phi_L - 0)`. The general inertness condition (proven in Round 2, §"Why all edges are inert"):

> A flipped edge `(j->i)` is **non-inert** iff `phi[j] != 0 AND phi[i] != 0`.

With `phi[M] = 0`, the flip is inert **regardless** of `phi[L]`.

**The variance change (0.0946 to 0.0136) is NOT caused by the flip.** It is caused by `phi[L] = 1.0` altering the background diffusion on the **non-flipped** edges `S->L`, `L->S`, and `M->L`, which changes the cos-shaped interference pattern inherited from M1's `cos(phi[S] - phi[M])` gating. The flip operator itself remains a no-op.

---

## Step 4 — What WOULD truly engage the flip

Setting `phi[L] != 0` **and** `phi[M] != 0` (with `phi[L] != phi[M]`) makes `cos(-phi_L - phi_M) != cos(phi_L - phi_M)`:

| phi_L | phi_M | d_phi_flip | d_phi_nonflip | cos(flip) | cos(nonflip) | Inert? |
|---|---|---|---|---|---|---|
| 1.0 | 0.0 (proposed) | -1.0 | 1.0 | 0.5403 | 0.5403 | **Yes** (cos even) |
| 1.0 | 0.5 (truly engaged) | -1.5 | 0.5 | 0.0707 | 0.8776 | **No** |
| 0.5 | 0.5 | -1.0 | 0.0 | 0.5403 | 1.0000 | **No** |
| 1.0 | -0.5 | -0.5 | 1.5 | 0.8776 | 0.0707 | **No** |

When the flip is **truly engaged** (`phi_L=1.0, phi_M=0.5`):

| Metric | Value |
|---|---|
| `var(V_M_m2_results)` | **0.00018936496413660234** |
| `corr(M1, M2)` | 0.3957259261747668 |
| flip-on vs flip-off corr | 0.9999 (nearly identical at network level) |
| flip-on vs flip-off MAE | 0.1834 |
| Verdict (var > 0.01) | **FAIL** (0.000189 < 0.01) |

**The truly-engaging case FAILS the variance criterion.** When the flip actually engages, the transmission profile flattens dramatically (max drops to ~0.036), variance collapses to 0.000189, and the verdict flips from PASS to FAIL. This is the opposite of what the correction intended — a real engagement would *destroy* the PASS verdict, not preserve it.

The proposed correction (phi_L=1.0, phi_M=0.0) keeps variance at 0.0136 — just barely above the 0.01 threshold — not because the flip engaged (it did not), but because phi_L=1.0 partially suppresses the cos-profile enough to shrink variance without killing it. This is a fragile, accidental PASS.

---

## Step 5 — The "opposite" argument: Was nonzero phi[L] intended? Latency-bug plausibility assessment

### The argument

> Cell 9 sets `phi[L] = 0.0` explicitly (L25). But the M2 test exists *specifically* to validate the T-flip operator on edge `L->M`. For that flip to be testable at all, the source node L must carry non-zero phase — otherwise the entire test is structurally vacuous (Round 2 proved this). The author may have copied cell 4's initialization verbatim (which also sets `phi[L]=0`) and **forgot** to activate a phase on L for the M2 test. This is a latent bug: the intended configuration had `phi[L] != 0`, and the `0.0946` PASS is an artifact of that forgotten phase.

### Plausibility assessment: Weak — several fatal cracks

**1. The "intended phi_L != 0" hypothesis does not match the author's evident design.**
Cell 4 (M1) and cell 9 (M2) use identical node initialization: `phi[L]=0, phi[M]=0`, sweep `phi[S]`. The author is testing whether **sweeping the source phase** reveals different profiles between M1 (no flip) and M2 (flip). The design is: *"same sweep, flip the edge, compare."* If the author intended to put phase on L, they would have had to also change M1's setup for comparability — but they did not. The `0.0946` PASS in cell 9 is *expected* to equal M1's result under this design; the author may have believed the cos-profile itself (inherited from S's sweep) was the "M2 signature."

**2. Even if the bug hypothesis were true, the proposed correction does not fix it.**
The task's correction sets `phi[L]=1.0` but leaves `phi[M]=0.0`. As proven in Step 3, this **still does not engage the flip** — `cos` is even, so `cos(-1.0 - 0.0) = cos(1.0 - 0.0)`. A notebook author who understood T-flip physics would know that *both* endpoints need non-zero phase. The fact that the "correction" keeps `phi[M]=0` means it does not even attempt the right fix.

**3. The truly-engaging case (`phi_L=1.0, phi_M=0.5`) is self-incriminating.**
If we charitably assume the notebook author *intended* the flip to engage, the natural correction (give L non-zero phase) would, if done correctly (both endpoints non-zero), produce `var = 0.000189` — **below** the 0.01 threshold, yielding **FAIL**, not PASS. The only way to preserve a PASS with the flip engaged is to tune `phi[L]` and `phi[M]` to very specific values that keep variance above 0.01 *and* different from M1 — a posteriori curve-fitting, not a principled test.

**4. The variance > 0.01 criterion is the real failure, not the phi values.**
Round 4 destroyed the `variance > 0.01` PASS criterion as vacuous: it cannot distinguish M1 from M2 (identical curves), cannot distinguish A from -A (opposite physics, same variance), and cannot distinguish flat-zero from cos (trivial non-degeneracy check). The `0.0946` is an artifact of the criterion, not of phi values. Fixing phi without fixing the criterion changes nothing substantive.

**5. Cell 9's comment confirms the sweep design is intentional, not a copy-paste bug.**
Cell 9 L23: `# Set states: Clamp V[S] = 1.0, and sweep phase at S`. The author *intentionally* designed the sweep to vary only `phi[S]`. The `phi[L]=0, phi[M]=0` initialization is consistent with M1's design and is a deliberate choice to isolate the *source-phase* effect, not a forgotten phase on L.

### Verdict on plausibility: LOW

The "latent bug" hypothesis (intended nonzero `phi[L]`) is **not plausible** as a rescue for cell 9's PASS verdict:

- The fix that the task proposes (phi_L=1.0, phi_M=0.0) does not engage the flip.
- A *correct* fix (both endpoints nonzero) makes the flip engage but causes the verdict to **FAIL** (var = 0.000189 < 0.01).
- The cos-evenness proof is a mathematical identity, not a configuration accident — it applies regardless of what nonzero value phi_L takes, as long as phi_M = 0.

---

## Summary of numerical results

| Condition | phi[L] | phi[M] | Flip engaged? | var(V[M]) | corr(M1, M2) | Verdict (>0.01) |
|---|---|---|---|---|---|---|
| Cell 9 (notebook) | 0.0 | 0.0 | No | 0.09464 | 1.0 | PASS |
| Task correction | 1.0 | 0.0 | No (cos even) | 0.01364 | 0.3957 | PASS |
| Truly engaged | 1.0 | 0.5 | Yes | 0.00019 | 0.3957 | FAIL |

---

## Evidence chain

- `wallfield_actual.py:69-90` — `M2WallFieldSimulation.tickVField`: the flip branch computes `d_phi = -phi[j] - phi[i]` (`wallfield_actual.py:84`), the non-flip branch `d_phi = phi[j] - phi[i]` (`wallfield_actual.py:86`); gating is `cos(d_phi)` in both (`wallfield_actual.py:87`).
- Cell 9 L25 — `phi_val=0.0` on node L (source of flipped edge L->M).
- Cell 9 L21 — `set_flipped_edge(L, M, True)`.
- Cell 9 L51 — verdict criterion `np.var(V_M_m2_results) > 0.01`.
- `scoring_verdict_m2.json:7` — notebook reported `profile_variance = 0.0946449751161661`.
- `round5_experiment.json` — full numerical output from this audit; `"cos_evenness_proof_optionA.gating_identical": true`; `"m2_inert_variance": 0.09464497511616608`; `"m2_corrA_variance": 0.013638347755336662`.
- `round5_supplement.py` — supplementary experiment confirming the truly-engaging case.
- Round 2 — general inertness condition `phi[source] = 0 OR phi[target] = 0`.
- Round 4 — destruction of the `variance > 0.01` PASS criterion as vacuous.

## Verdict

**FAIL — The proposed M2 correction does not engage the flip.**

Setting `phi[L]=1.0` while `phi[M]=0.0` is mathematically incapable of engaging the T-flip operator because `cos(-phi_L - 0) = cos(phi_L - 0)` (cosine is even). The resulting variance change (0.0946 to 0.0136) is an artifact of altered background diffusion on non-flipped edges, not of orientation-gate physics. The verdict remains PASS only because the variance happens to land at 0.0136 — just above the arbitrary 0.01 threshold.

The "opposite" argument (notebook intended nonzero phi on L) is **not plausible**: the proposed correction itself does not fix the underlying inertness, and a *correct* engaging configuration causes the variance to collapse to 0.000189, which would flip the verdict to FAIL. The notebook's `0.0946` PASS is sustained by a vacuous variance criterion (Round 4), not by an activatable flip that was merely forgotten.
