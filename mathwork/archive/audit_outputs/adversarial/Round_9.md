# Round 9 — Lambda-2 Misattribution Self-Attack

**Status:** CRITICAL — the reported `lambda_2 = 1.0` is the static algebraic connectivity of the unweighted **path graph P3**, not a property of the phase-gated propagation in `tickVField`. The correct operator yields `0.8592` (symmetric gated Laplacian) or a non-Laplacian spectrum entirely.

**Method:** Reproduce adversarial_audit_prompts.md item 9 directly against `ImaginaryUnit.ipynb` cells 2–3 (`adv_common.cell_lines(2)`, `cell_lines(3)`) and `wallfield_actual.py`, computing the exact spectrum of each candidate operator at `sweep_phi = 0.7` (`phi[S]=0.7, phi[L]=phi[M]=0`).

---

## Step 1 — The operator that claims `lambda_2 = 1.0`

The verdict JSONs cite `algebraic_connectivity_lambda_2`:

| Source | File:line | Value |
|---|---|---|
| `scoring_verdict.json:15` | `"algebraic_connectivity_lambda_2": 0.9999999999999998` | **1.0** |
| `notebook_verification_results.json:113` | `"algebraic_connectivity_lambda_2": 0.9999999999999998` | **1.0** |
| `organized/audit_outputs/notebook_verification_results.json:113` | same | **1.0** |

This value is produced by `get_algebraic_connectivity` — present verbatim in **both** cell 2 (`ImaginaryUnit.ipynb`, L30) and cell 3 (L23), which is the class that actually runs (`wallfield_actual.py:46-51`).

### Cell 2 `get_algebraic_connectivity` (verbatim, `adv_common.cell_lines(2)`)

```
C2 L30:     def get_algebraic_connectivity(self):
C2 L31:         """
C2 L32:         Computes lambda_2 (algebraic connectivity) of the symmetric part of the Laplacian.
C2 L33:         """
C2 L34:         # For directed graphs, we typically look at the symmetric laplacian of the underlying undirected graph
C2 L35:         sym_weights = (self.weights + self.weights.T) / 2.0
C2 L36:         D = np.diag(np.sum(sym_weights, axis=1))
C2 L37:         L_sym = D - sym_weights
C2 L38:
C2 L39:         eigenvalues = np.sort(la.eigvalsh(L_sym))
C2 L40:         # lambda_2 is the second smallest eigenvalue
C2 L41:         if len(eigenvalues) > 1:
C2 L42:             return eigenvalues[1]
C2 L43:         return eigenvalues[0]
```

### Cell 3 `get_algebraic_connectivity` (verbatim, `adv_common.cell_lines(3)`)

```
C3 L23:     def get_algebraic_connectivity(self):
C3 L24:         sym_weights = (self.weights + self.weights.T) / 2.0
C3 L25:         D = np.diag(np.sum(sym_weights, axis=1))
C3 L26:         L_sym = D - sym_weights
C3 L27:         eigenvalues = np.sort(la.eigvalsh(L_sym))
C3 L28:         return eigenvalues[1] if len(eigenvalues) > 1 else eigenvalues[0]
```

**Critical observation:** `get_algebraic_connectivity` uses **only** `self.weights`. It never reads `self.phi`. The reported `lambda_2 = 1.0` is **phi-invariant** — confirmed empirically:

```
phi[S]=0.0:    lambda_2 = 1.0000
phi[S]=0.7:    lambda_2 = 1.0000
phi[S]=pi/4:   lambda_2 = 1.0000
phi[S]=pi/2:   lambda_2 = 1.0000
```

---

## Step 2 — Graph topology: P3 (path), not K3 (3-cycle)

The notebook cell 2 (L45–L59) constructs the graph with edges:

| Cell 2 line | Edge | Weight |
|---|---|---|
| L55 | S→L | 1.0 |
| L56 | L→M | 1.0 |
| L58 | L→S | 1.0 |
| L59 | M→L | 1.0 |

```
W = [[0, 1, 0],
     [1, 0, 1],
     [0, 1, 0]]
```

There is **no S↔M edge**. The topology is the **path graph P3** (S—L—M), a 2-edge chain — *not* the complete graph K3 (triangle/3-cycle), which would require `W[0,2] = W[2,0] = 1`.

---

## Step 3 — Spectra of the three candidate Laplacians

### (a) Unweighted 3-cycle K3 Laplacian (standard)

`K3` = complete graph on {S,L,M}; every pair connected, weight 1:

```
W_K3 = [[0,1,1],[1,0,1],[1,1,0]],   D = diag(2,2,2)
L_K3 = D - W_K3 = [[ 2,-1,-1],
                   [-1, 2,-1],
                   [-1,-1, 2]]
eigenvalues = [0, 3, 3]
lambda_2(K3) = 3.0
```

### (b) Notebook LISTEN-weighted directed graph Laplacian at `sweep_phi=0.7`

The notebook's `compute_listen_laplacian` (cell 2 L20–28, cell 3 L19–21) computes `L = D_out - W` with **raw** weights:

```
W = [[0,1,0],[1,0,1],[0,1,0]],   D = diag(1,2,1)
L = D - W = [[ 1,-1, 0],
             [-1, 2,-1],
             [ 0,-1, 1]]
eigenvalues = [0, 1, 3]
lambda_2(P3 directed) = 1.0
```

**Note:** `sweep_phi=0.7` does **not** enter this computation. `compute_listen_laplacian` uses `self.weights` directly — phi is irrelevant to the static Laplacian. The value 1.0 is read off the *structural* path P3, not from any phase-gated quantity.

### (c) Symmetrized weighted Laplacian `(W + W^T)/2`

`get_algebraic_connectivity` symmetrizes: `sym_weights = (W+W^T)/2`. Since W is already symmetric (`W = W^T`), symmetrization is a no-op:

```
W_sym = (W + W^T)/2 = W = [[0,1,0],[1,0,1],[0,1,0]]
D_sym = diag(1,2,1)
L_sym = D_sym - W_sym = [[ 1,-1, 0],
                         [-1, 2,-1],
                         [ 0,-1, 1]]
eigenvalues = [0, 1, 3]
lambda_2(P3 symmetrized) = 1.0
```

### Summary table

| Operator | Matrix | Eigenvalues | lambda_2 | Source |
|---|---|---|---|---|
| (a) K3 standard unweighted | D - W_K3 | [0, 3, 3] | **3.0** | hand computation |
| (b) Notebook directed D−W | D_out - W | [0, 1, 3] | **1.0** | cell 2 L20–28; cell 3 L19–21 |
| (c) Symmetrized D−(W+W^T)/2 | D - W_sym | [0, 1, 3] | **1.0** | cell 2 L30–43; cell 3 L23–28 |

---

## Step 4 — The phase-weighted operator gives a DIFFERENT value

The report's `lambda_2 = 1.0` is presented as a property of the **phase-gated** system. The genuinely phase-weighted operator replaces each weight with `W[i,j] * cos(phi[i] - phi[j])`:

### Phase-weighted symmetric Laplacian (phi[S]=0.7, phi[L]=phi[M]=0)

```
W_phase = W * cos(phi_i - phi_j) = [[0, 0.7648, 0],
                                    [0.7648, 0,    1.0],
                                    [0,     1.0,   0  ]]
D_phase = diag(0.7648, 1.7648, 1.0)
L_phase = D_phase - W_phase
eigenvalues = [0, 0.8592, 2.6705]
lambda_2(phase-weighted) = 0.8592   ≠ 1.0
```

The phase-gating reduces lambda_2 from 1.0 (unweighted path) to **0.8592** — the edge S↔L weakens to `cos(0.7)=0.7648`. This is the value a principled "phase-gated connectivity" would report, and it is **not** 1.0.

### Phase-weighted directed Laplacian

Since `W_phase` is symmetric (W symmetric + cos even), the directed Laplacian `D_out_phase - W_phase` is identical to the symmetric version: eigenvalues `[0, 0.8592, 2.6705]`, lambda_2 = 0.8592.

### Cross-check against `discrimination_results.json`

The file `discrimination_results.json:70–75` computes the same phase-weighted Laplacian with a different phi gradient `[0.0, 0.7, 1.4]` and obtains eigenvalues `[0, 0.7648, 2.2945]` — confirming the phase-weighted operator's spectrum is gradient-dependent and **never equals the unweighted [0, 1, 3]**. (Reproduced: `np.sort(eigvalsh(L_phase))` = `[0, 0.7648, 2.2945]` at phi=`[0, 0.7, 1.4]`. ✓)

---

## Step 5 — The ACTUAL `tickVField` operator is NOT a Laplacian at all

The phase-gated propagation does **not** use the Laplacian eigenvalues. It uses `tickVField` (cell 3 L36–55; `wallfield_actual.py:56–66` for the base, `wallfield_actual.py:77–90` for M2):

```
C3 L46:                 if self.weights[j, i] > 0:
C3 L47:                     d_phi = self.phi[j] - self.phi[i]
C3 L48:                     # Gating factor: cos(d_phi) models how phase alignment affects signal flow
C3 L49:                     gating = np.cos(d_phi)
C3 L50:                     diffusion_sum += self.weights[j, i] * gating * self.V[j]
C3 L53:             new_V[i] = self.V[i] + alpha * (diffusion_sum - np.sum(self.weights[i, :]) * self.V[i])
```

The effective generator `M` (where `dV/dt = M·V`) at `phi=[0.7,0,0]`:

```
M = [[-1.0,   0.7648,  0    ],
     [ 0.7648,-2.0,   1.0   ],
     [ 0,      1.0,  -1.0   ]]
M @ [1,1,1] = [-0.2352, -0.2352, 0.0]   ← NOT zero
eigenvalues(M) = [-2.8546, -1.0, -0.1454]
```

**Two fatal problems:**

1. `M` has **no zero eigenvalue** — `M·ones ≠ 0`. The leak term uses the *unweighted* out-degree (`np.sum(self.weights[i, :])`, line 53 / `wallfield_actual.py:65,89`) while the inflow uses *phase-weighted* weights. Rows do **not** sum to zero, so `M` is **not a Laplacian**. The diffusion is non-conservative — total amplitude leaks at a rate depending on phi.

2. The eigenvalue `-1.0` that appears in `M`'s spectrum is a **numerical coincidence**, not algebraic connectivity. It arises from the asymmetric structure of the non-Laplacian generator, not from the graph's static connectivity. Sorting `M`'s eigenvalues gives `[-2.8546, -1.0, -0.1454]` — there is no meaningful "second smallest" in the Laplacian sense because there is no zero eigenvalue to define the spectral gap.

The proper "effective Laplacian" `-M` has eigenvalues `[0.1454, 1.0, 2.8546]` — but even this lacks a true zero eigenvalue (`-M)·ones = [0.2352, 0.2352, 0] ≠ 0`), confirming `tickVField` does not conserve the DC component and is not a graph Laplacian in any standard sense.

---

## Step 6 — The misattribution, identified

**Which operator yields 1.0?** — Operators (b) and (c): the **static, unweighted** Laplacians of the **path graph P3**. Computed by `get_algebraic_connectivity` (cell 2 L30–43 / cell 3 L23–28) and `compute_listen_laplacian` (cell 2 L20–28 / cell 3 L19–21), neither of which references `phi`.

**Is it the phase-weighted operator actually used in `tickVField`?** — **No, on both counts:**

| Claim in report | Reality |
|---|---|
| `lambda_2 = 1.0` characterizes "phase-gated connectivity" | 1.0 is the **unweighted** static algebraic connectivity of P3; `get_algebraic_connectivity` never reads phi (cell 2 L35, cell 3 L24 only use `self.weights`) |
| tickVField's operator has lambda_2 = 1.0 | tickVField's generator `M` is **not a Laplacian** (no zero eigenvalue, non-conservative rows); its spectrum is `[-2.8546, -1.0, -0.1454]`; the `-1.0` is coincidental |
| Phase-gated lambda_2 | The genuinely phase-weighted Laplacian yields **0.8592** at sweep_phi=0.7 — different from 1.0 |

**K3 (the 3-cycle) gives 3.0**, confirming that lambda_2 is a **graph-topology** quantity: it distinguishes P3 (path, 1.0) from K3 (triangle, 3.0). The report's "1.0" is nothing more than the notebook having built **P3 and called it the connectivity of the phase-gated system**. The phase is absent from the operator entirely.

---

## Conclusion

**`lambda_2 = 1.0` characterizes the unweighted, undirected path graph P3 (S—L—M), NOT the phase-gated propagation.**

- K3 (complete 3-cycle) → lambda_2 = 3.0 — a different topology gives a different value.
- The notebook's graph is P3, so its static Laplacian gives lambda_2 = 1.0 regardless of phi.
- `get_algebraic_connectivity` is phi-invariant: it symmetrizes the raw weight matrix and reads the second eigenvalue. It does not see the phase-gating that `tickVField` applies.
- The truly phase-weighted Laplacian gives lambda_2 = 0.8592 (at sweep_phi=0.7) — not 1.0.
- The actual `tickVField` operator is not a Laplacian at all: its generator has no zero eigenvalue, non-conservative rows, and a spectrum `[-2.8546, -1.0, -0.1454]` in which `-1.0` is a coincidence — the unweighted-out-degree leak term (`wallfield_actual.py:65,89` / cell 3 L53) breaks Laplacian conservation.

Citing `lambda_2 = 1.0` as evidence of "phase-gated connectivity" is a **layer violation**: a static topological invariant is being read out to validate a dynamic, phi-dependent propagation claim. The static Laplacian and the `tickVField` generator operate on different matrices; the reported value is the wrong operator for the claimed physical interpretation. The report should either (i) compute the phase-weighted Laplacian's spectrum (0.8592 at sweep_phi=0.7) as the "phase-gated connectivity," or (ii) acknowledge that the static P3 connectivity tells us nothing about orientation-gated propagation.

---

## Evidence chain

- `ImaginaryUnit.ipynb` cell 2 L30–43 — original `get_algebraic_connectivity` (phi-invariant symmetrized Laplacian)
- `ImaginaryUnit.ipynb` cell 3 L23–28 — identical `get_algebraic_connectivity` in the class actually used
- `ImaginaryUnit.ipynb` cell 2 L20–28 — `compute_listen_laplacian` (`L = D - W`, raw weights, phi-blind)
- `ImaginaryUnit.ipynb` cell 2 L45–L59 — graph construction: edges S→L, L→M, L→S, M→L (path P3, no S↔M)
- `ImaginaryUnit.ipynb` cell 3 L36–55 — `tickVField`: phase-weighted gating on inflow, **unweighted** out-degree leak on the diagonal
- `wallfield_actual.py:42–51` — `compute_listen_laplacian` + `get_algebraic_connectivity` (verbatim re-implementation, phi-blind)
- `wallfield_actual.py:56–66` — base `tickVField` (unweighted diagonal leak)
- `wallfield_actual.py:77–90` — M2 `tickVField` (flip adds phi only to inflow gating, not to leak)
- `scoring_verdict.json:15` — cited `algebraic_connectivity_lambda_2 = 0.999...`
- `notebook_verification_results.json:113` — cited `algebraic_connectivity_lambda_2 = 0.999...`
- `organized/audit_outputs/audit_results.json:89–92` — P3 lambda_2 = 1.0, K3 lambda_2 = 3.0 (the audit itself records the distinction but the report did not enforce it)
- `discrimination_results.json:61–77` — phase-weighted directed/symmetrized spectra (0.7648/0.7648 at phi=[0,0.7,1.4]); verdict: "MISMATCH — unweighted lambda2 characterizes the unweighted graph (path P3 → 1.0), not the phase-weighted directed operator"
- Adversarial_audit_prompts.md item 9 — this Round's directive

## Verdict

**FAIL — Lambda-2 is misattributed.** The reported `lambda_2 = 1.0` is the algebraic connectivity of the static **unweighted path P3** (the notebook's actual topology, not K3 which would give 3.0). It is computed by `get_algebraic_connectivity`, which is **phi-blind**. The phase-weighted Laplacian gives **0.8592**, and the actual `tickVField` generator is **not a Laplacian** (no zero eigenvalue, non-conservative leak). `lambda_2 = 1.0` characterizes graph topology, not phase-gated propagation.
