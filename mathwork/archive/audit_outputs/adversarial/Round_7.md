# Round 7 — Self-Audit: The `leakage_ratio = 0` Kill Criterion Confuses a Cancellation Artifact with a Physical Blockade

**Status:** CRITICAL — the kill criterion cannot distinguish its own two logical hypotheses, because it mistakes a fine-tuned destructive-interference zero for a zero-coupling blockade. The `leakage_ratio = 0` that sustains the M1 PASS is numerically reproduced from the *actual* S→L coupling `cos(pi) = -1` (negative, **not zero**), and a structurally different but equally `cos(pi) = -1` lattice produces a large nonzero `V[M](pi)`. The metric is therefore unsound as a discriminator.

**Method:** Reproduce cells 4–5 of `ImaginaryUnit.ipynb` exactly through `wallfield_actual.RefactoredWallFieldSimulation` (verbatim from cell 3 / `wallfield_actual.py:28-66`), instrumenting (a) the four edge gatings at `sweep_phi = pi`, (b) the unclipped linear fixed point, and (c) a minimal 4-node counterexample Laplacian that keeps `S->L` coupling at `cos(pi) = -1` but breaks the cancellation so `V[M](pi) != 0`. Numerical results persisted in `round7_audit_results.json` (source: `round7_audit.py`).

**Target:** Cell 5 kill criterion, `ImaginaryUnit.ipynb` cell 5 line 14:

> `"kill_criterion": "If V[M] at delta_phi = +/- pi exceeds 10% of V[M] at delta_phi = 0, the operator-i phase-gating conjecture is KILLED."`

i.e. the reported `leakage_ratio = 0` (`scoring_verdict.json:14`) is read as evidence that the `H_operator` conjecture holds — specifically, as evidence of a genuine *zero-coupling* blockade at anti-alignment. That reading is a false premise: at `sweep_phi = pi` the S→L edge is not uncoupled, it is anti-coupled (`cos(pi) = -1`).

---

## Step 1 — `V[M](phi=pi) = 0` reproduced, with `S->L` coupling = -1 (not 0)

Re-running cell 4 (`ImaginaryUnit.ipynb` cell 4; `adv_common.cell_lines(4)`) verbatim through `wallfield_actual.RefactoredWallFieldSimulation` — identical 4 edges (`S->L, L->M, L->S, M->L`, each weight 1.0), `phi[S] = sweep_phi`, `phi[L] = phi[M] = 0`, 30 ticks, `alpha = 0.15` —

| Quantity | Value | Source |
|---|---|---|
| `max_V_M` (at `phi ~= 0`) | `0.7989364408479221` | `run_notebook_verification.py:49` |
| `V[M](phi = -pi)` | `0.0` | cell 4 line 21 (phi state) + sweep |
| `V[M](phi = pi)` | `0.0` | cell 4 line 21 |
| `min_transmitted_V_M_at_pi` | `0.0` | `scoring_verdict.json:13` |
| `leakage_ratio` | `0.0` | `scoring_verdict.json:14` |
| Verdict (`leakage_ratio <= 0.10`) | **PASS** | `run_notebook_verification.py:61` |

This matches the notebook's artifact exactly. Now the edge gatings at `sweep_phi = pi` (where `phi[S] = pi`, `phi[L] = phi[M] = 0`):

| Edge | `weights[j,i]` | `d_phi = phi[j] - phi[i]` | Gating `cos(d_phi)` | Sign |
|---|---|---|---|---|
| S→L | 1.0 | `pi - 0 = +pi` | `-1.000000` | **negative (anti-coupled)** |
| L→S | 1.0 | `0 - pi = -pi` | `-1.000000` | **negative (anti-coupled)** |
| L→M | 1.0 | `0 - 0 = 0` | `+1.000000` | positive |
| M→L | 1.0 | `0 - 0 = 0` | `+1.000000` | positive |

**The S→L coupling at anti-alignment is `cos(pi) = -1.0`, not `0.0`.** Every weight is `1.0` (nonzero); `wallfield_actual.py:40` (`set_listen_weight`) never drops a weight, and cell 4 lines 12–16 set all four edges to `1.0`. There is no zero weight anywhere. The `leakage_ratio = 0` therefore does **not** come from a zero-coupling blockade.

---

## Step 2 — `V[M](pi) = 0` emerges from destructive diffusion among the 4 edges, not from zero coupling

The clipping in `wallfield_actual.py:66` (`np.clip(new_V, 0.0, 10.0)`) hides the physics. Removing the clip (same `tickVField` recurrence, `wallfield_actual.py:56-66`, only the `np.clip` removed) reveals the **linear fixed point** at `phi_S = pi`. With `V[S]` clamped to `1.0` and free nodes `{L, M}`, the fixed-point condition `sum_j w[j,i] cos(phi[j]-phi[i]) V[j] = outdeg(i) V[i]` gives, at unit weights:

```
i = L :  (-1)*V[S] + (+1)*V[M] = 2*V[L]   =>   V[M] - 1 = 2*V[L]
i = M :  (+1)*V[L]          = 1*V[M]       =>   V[L] = V[M]
```

Substituting: `V[M] - 1 = 2*V[M]`  =>  **`V[M](pi) = -1.0`** (and `V[L] = -1.0`).

The general closed form (arbitrary edge weights, all positive, `phi[S]=pi, phi[L]=phi[M]=0`) is

> **`V[M](pi) = - w_{SL} * w_{LM} / (w_{ML} * w_{LS})`**

which at unit weights is exactly `-1`. Two independent confirmations:

1. **No-clip trajectory at `phi = pi`** (alpha 0.15, 30 ticks) converges toward the `-1` fixed point:

| tick | `V[L]` | `V[M]` |
|---|---|---|
| 1 | -0.150000 | +0.000000 |
| 2 | -0.255000 | -0.022500 |
| 3 | -0.331875 | -0.057375 |
| 28 | -0.861316 | -0.775605 |
| 29 | -0.869262 | -0.788461 |
| 30 | -0.876752 | -0.800581 |

   `V[M]` marches steadily **negative** (toward `-1`), proving the dynamics are *actively* pushing the target amplitude negative — i.e. the two `cos = -1` anti-couplings (S→L and L→S) are *driving* the system, not disconnecting it.

2. **The clip is what manufactures the zero.** `V[M]` reaches `-1` (negative), and `wallfield_actual.py:66` clips the state to `[0, 10]`, mapping `-1 -> 0`. So `V[M](pi) = 0` is the **clipped image of an active negative fixed point produced by destructive diffusion among the four edges** (the two `-1` anti-couplings on S↔L oppose the `+1` L↔M cycle and the S source, summing to a net negative drive at M).

**Conclusion of Step 2:** `leakage_ratio = 0` is a *cancellation artifact* (negative coupling driven to a negative fixed point, then hard-clipped to zero) — not a *zero-coupling blockade*. The "zero coupling" reading of the kill criterion rested on a false premise.

---

## Step 3 — A different Laplacian with the SAME `cos(pi) = -1` on S→L but `V[M](pi) != 0`

To show the cancellation is contingent (and therefore that `leakage_ratio = 0` cannot certify the conjecture), construct a **different, minimal Laplacian** that preserves the S→L anti-coupling `cos(pi) = -1` but breaks the four-edge cancellation by adding an independent, uncanceled positive drive into M.

**4-node lattice** (`num_nodes = 4`, `S=0, L=1, M=2, C=3`):
- Edges (all weight 1.0): `S->L`, `L->M`, `L->S`, `M->L` (the original 4), **plus `C->M`**.
- States: `phi[S] = phi[L] = phi[M] = phi[C] = 0`; `V[S] = V[C] = 1.0` (both clamped sources); `phi[S]` swept.
- At `sweep_phi = pi`: the S→L gating is `cos(phi[S]-phi[L]) = cos(pi) = -1.0` — **identical negative coupling** to the 3-node M1 lattice. The added `C->M` edge has gating `cos(0) = +1` and feeds M from an independent clamped source, so the negative cascade through L can no longer zero M.

| Lattice | S→L gating at `phi=pi` | `V[M](phi=0)` | `V[M](phi=pi)` | `leakage_ratio` | Verdict (>0.10) |
|---|---|---|---|---|---|
| 3-node M1 (cell 4) | `-1.000000` | `0.798936` | `0.0` | `0.0` | PASS |
| **4-node (+C→M)** | `-1.000000` | `2.476270` | **`0.992369`** | **`0.400752`** | **FAIL** |

The 4-node lattice has the **same** S→L coupling sign-flip (`cos` from `+1` at `phi=0` to `-1` at `phi=pi`) as M1, yet its `V[M](pi)` is large (`0.992`) and its `leakage_ratio` is `0.400752` (40.08%) — which would **FAIL** the very kill criterion that declared M1 a PASS.

> Note (honesty about "drop one edge"): a naive single-edge deletion in the 3-node graph does **not** break the zero — dropping `M->L` or `L->S` still yields `V[M](pi) = 0`, because the negative S→L cascade still drives L (and hence M) below zero and the clip (`wallfield_actual.py:66`) still zeros it. That the cancellation survives single-edge deletion only *strengthens* the diagnosis: the original zero is the clip of a robustly-negative fixed point, not a structural zero-coupling. A positive drive into M (the 4-node extension) is what finally restores a nonzero `V[M](pi)` while keeping `cos(pi) = -1`.

---

## Step 4 — `leakage_ratio = 0` cannot distinguish the two hypotheses → the kill criterion is unsound

The kill criterion treats `V[M](pi) = 0` as falsifiable evidence. But `V[M](pi) = 0` under this model is **equally consistent with two logically distinct hypotheses**:

- **Hypothesis A (the FALSE premise embedded in the verdict):** *S→L coupling is zero at `phi = pi`, so nothing flows and `V[M] = 0` trivially.* — **False by construction.** The S→L gating is `cos(pi) = -1.0` (cell 4 line 19 sweeps `phi` at S; step 2 shows `cos = -1`, weights are all `1.0`). There is no zero weight (`set_listen_weight`, `wallfield_actual.py:39-40`) and no zero coupling (`gating = np.cos(d_phi)`, `wallfield_actual.py:63`).

- **Hypothesis B (the TRUE mechanism):** *S→L coupling is `-1` (maximally anti-aligned) and `V[M] = 0` is the clipped residue of destructive diffusion among the four edges, producing a negative fixed point `V[M] = -1` that the hard clip at `wallfield_actual.py:66` maps to `0`.* — Verified numerically in Steps 1–3.

The reported metric `leakage_ratio = 0` (cell 5 line 37: `"leakage_ratio": float(ratio)`; `scoring_verdict.json:14`) is **identical under both hypotheses** — it is `0` whether the underlying physics is "zero coupling" (A) or "negative-coupling cancellation" (B). Crucially, the 4-node counterexample demonstrates a state of **identical S→L coupling** (`cos(pi) = -1`, same as M1) for which `leakage_ratio` is `0.40`, not `0`. Therefore:

1. `leakage_ratio = 0` is **not** a necessary consequence of the `cos(pi) = -1` coupling (the 4-node lattice violates it with the very same coupling).
2. `leakage_ratio = 0` is **not** diagnostic of "zero coupling" (coupling is `-1`, not `0`, in the lattice that produces it).
3. The metric cannot tell A from B — it is `0` in both cases that the rule is meant to certify, yet A is false and B is true.

The kill criterion (`ImaginaryUnit.ipynb` cell 5 line 14) reasons: `leakage_ratio = 0` ⟹ `V[M] = 0 at anti-alignment` ⟹ `H_operator` phase-gating validated ⟹ PASS. Step 2 shows the first arrow is a false-premise (coupling is `-1`, not `0`); Step 3 shows the last two arrows are not entailed (the same `cos(pi)=-1` coupling yields a large nonzero `V[M]` in a different Laplacian). **The criterion is consistent with both "zero coupling" and "negative-coupling cancellation" and therefore cannot distinguish them — it certifies a cancellation artifact as if it were a zero-coupling blockade.**

---

## Evidence chain

- `ImaginaryUnit.ipynb` cell 4 (M1 sweep) — `adv_common.cell_lines(4)`: line 5 `phi_sweeps = np.linspace(-np.pi, np.pi, 50)`; line 19 `phi[S] = sweep_phi`; lines 20–21 `phi[L] = phi[M] = 0.0`; lines 12–16 set all four edges to weight `1.0`; line 27 `tickVField(alpha=0.15)`, 30 ticks (cell 4 line 24 `for _ in range(30)`).
- `ImaginaryUnit.ipynb` cell 5 (kill criterion) — `adv_common.cell_lines(5)`: **line 14 `kill_criterion`** = "If V[M] at delta_phi = +/- pi exceeds 10% of V[M] at delta_phi = 0, the operator-i phase-gating conjecture is KILLED."; line 12 H_operator "V[M] drops to 0 when delta_phi approaches +/- pi"; **line 37 `leakage_ratio`** = `float(ratio)`.
- `wallfield_actual.py:39-40` `set_listen_weight` (no weight is ever zero); `:56-66` `tickVField` with `:63` `gating = np.cos(d_phi)` and `:66` `np.clip(new_V, 0.0, 10.0)`; `:42-44` `compute_listen_laplacian` `L = D - W`.
- `run_notebook_verification.py:30-62` `run_m1_sweep()` (verbatim M1 cell 4); `:61` verdict `PASS` when `ratio <= 0.10`.
- `scoring_verdict.json:14` `leakage_ratio: 0.0`; `:13` `min_transmitted_V_M_at_pi: 0.0`; `:19` rationale "0.00%, below the 10.0% threshold".
- `round7_audit.py` — this audit's computational source (M1 reproduction, edge gatings at `phi=pi`, unclipped fixed point `V[M]=-1`, 4-node counterexample, drop-edge variants); `round7_audit_results.json` — numerical output (`SL_gating_at_pi = -1.0`, `leakage_ratio = 0.0`, `counterexample_4node.V_M_at_pi = 0.992369`, `counterexample_4node.leakage_ratio = 0.400752`).
- `notebook_verification_results.json` — M1 `max_transmitted_V_M = 0.7989364408479221`; M1/M2 pointwise identical (`m1_sweep_verdict`/`m2_sweep_verdict`).
- Round 4 — established `variance > 0.01` as vacuous (M1 == M2, corr = 1.0); same null-flip regime.

---

## Verdict

**FAIL — the `leakage_ratio = 0` kill criterion is unsound.**

At `sweep_phi = pi` the S→L edge is not uncoupled: its gating is `cos(pi) = -1.0` (negative, anti-aligned), all four edge weights are `1.0`, and the `V[M](pi) = 0` reported as a PASS derives from a **destructive-diffusion fixed point `V[M] = -1`** that the hard clip at `wallfield_actual.py:66` maps to `0` — not from any zero coupling. The metric `leakage_ratio = 0` is numerically identical under the false "zero coupling" hypothesis and the true "negative-coupling cancellation" hypothesis, so it cannot discriminate between them. This is demonstrated decisively by the 4-node counterexample: the **same** S→L `cos(pi) = -1` coupling yields `V[M](pi) = 0.992` and `leakage_ratio = 0.400752` (FAIL). The kill criterion therefore admits a cancellation artifact as proof of a zero-coupling blockade; the M1 PASS stands on a false premise and an unsound metric.
