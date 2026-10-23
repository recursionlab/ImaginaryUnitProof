# Round 10 — Ruthless Self-Audit: Census of Uncited Assumptions

## Scope

Audited cells (0-indexed into `ImaginaryUnit.ipynb["cells"]` per `adv_common.cell_lines`):
**2, 3, 5, 8, 9, 12, 27**.

Line numbers are 1-based within each cell, matching `ac.cell_lines(idx)` enumeration.

External references cited for contrast (NOT audited cells):
- `gate_contract_audit.py` — defines SEEDS, decode rule, threshold, XNOR control.
- `wallfield_actual.py` — defines `GATE_DECISION_THRESHOLD = 0.5`.
- `run_notebook_verification.py` — applies seeds + threshold externally.
- `round8_audit.py` — applies seeds + threshold externally.

## Assumption Census

| # | Assumption | Status | Cell:Line (commitment in audited cells) |
|---|-----------|--------|----------------------------------------|
| 1 | truth-table decode: bit=1 iff cos(phi)<0 | METHODOLOGY_HOLE | **None** in audited cells |
| 2 | GATE_DECISION_THRESHOLD=0.5 | METHODOLOGY_HOLE | **None** in audited cells |
| 3 | seeds / seed handling | METHODOLOGY_HOLE | **None** in audited cells |
| 4 | noise distribution (Gaussian, `np.random.normal`) | CITED | 27:6, 27:7, 27:12 |
| 5 | alpha=0.15 | CITED | 9:31, 12:38 |
| 6 | 30 ticks | CITED (contradiction) | 9:29 (commits to 30); 12:36 commits to **50** |
| 7 | 50/100 sweep points | CITED | 9:9 (50 pts), 12:24 (100 pts) |
| 8 | lambda2 > 1e-5 health bar | CITED | 2:68 |
| 9 | 10% leakage threshold | CITED | 5:28 (textual precommit: 5:14) |
| 10 | variance > 0.01 for M2 | CITED | 9:51 |

## Summary

| Metric | Count |
|--------|-------|
| Assumptions audited | 10 |
| CITED | 7 (4, 5, 6*, 7, 8, 9, 10) |
| METHODOLOGY_HOLE | **3** (1, 2, 3) |
| CITED with contradiction | 1 (#6: cell 12 uses 50 ticks, not 30) |

* #6 is cited (cell 9:29) but a contradiction exists (cell 12:36 uses 50). Counted as cited.

## METHODOLOGY_HOLE Details

### HOLE 1 — truth-table decode: bit=1 iff cos(phi)<0

**No audited cell commits to this rule.**

The audited cells use `np.cos` in two distinct roles — neither is the declared decode:
- **Gating factor** (multiplicative signal transmission): cell 3:49 `gating = np.cos(d_phi)`,
  cell 8:29 `gating = np.cos(d_phi)`.
- **Amplitude formula** (computing |amplitude| in [0,1]): cell 27:8
  `output_amplitude = 0.5 * (np.cos(path1_phase) + np.cos(path2_phase + np.pi))`,
  cell 27:13 `output_amplitude = np.cos(d_phi / 2.0)`.

Neither is the read-back rule `bit = 1 iff cos(phi) < 0` (i.e. the phase half-plane decoder).
That exact rule exists **only** in `gate_contract_audit.py:44` (`return (np.cos(wrap_phase(phi)) < 0.0).astype(np.int8)`)
and its prose at `gate_contract_audit.py:221`. It is absent from cells 2, 3, 5, 8, 9, 12, 27.

**Impact**: The notebook never decodes phases to bits internally. Truth-table correctness is
inherited from an external harness, not established in-cell.

### HOLE 2 — GATE_DECISION_THRESHOLD=0.5

**No audited cell commits to a 0.5 amplitude threshold.**

Cell 27's gate functions return raw clipped amplitudes:
`np.clip(np.abs(output_amplitude), 0.0, 1.0)` (cell 27:9, 27:14). No `>= 0.5` comparison
appears inside cell 27 or any other audited cell.

The three `0.5` substrings found in audited cells are **not** the threshold:
- cell 5:58, 9:66, 12:72 — `plt.grid(..., alpha=0.5)` (matplotlib grid transparency).
- cell 27:8 — `0.5 * (...)` (constant scaling factor in the NOT amplitude formula).

The threshold `0.5` lives **only** in `wallfield_actual.py:6`
(`GATE_DECISION_THRESHOLD = 0.5`) and is applied **only** externally in
`round8_audit.py:34` (`amp >= GATE_DECISION_THRESHOLD`) and
`run_notebook_verification.py:23,27`.

**Impact**: Amplitude-to-bit discretization is an uncited external dependency. Gate
truth tables are never evaluated inside the audited notebook cells.

### HOLE 3 — seeds / seed handling

**No audited cell sets, declares, or passes a seed.**

Cell 27's gate functions accept no seed parameter and call `np.random.normal` on the
**global** numpy RNG:
- cell 27:6  `input_phase + np.random.normal(0, noise_std)`
- cell 27:7  `-input_phase - np.pi + np.random.normal(0, noise_std)`
- cell 27:12 `(phase_a + np.random.normal(0, noise_std)) - (phase_b + np.random.normal(0, noise_std))`

A grep for `seed`, `np.random.seed`, and `default_rng` across cells 2, 3, 5, 8, 9, 12, 27
returns **zero** matches. The deterministic M1/M2/M3 sweep cells (3, 5, 8, 9, 12) have no
randomness to seed; cell 2 is eigenvalue-based.

Seeds are defined **only** in `gate_contract_audit.py:29`
(`SEEDS = (73129, 84221, 95317, 106487, 117503)`) and consumed **only** externally in
`round8_audit.py:57` (`rng = np.random.default_rng(seed)`) and
`run_notebook_verification.py:144,161`.

**Impact**: The notebook's native gate stress test (cell 27) is fully non-reproducible.
Every invocation produces different outputs; the "1000 runs / stress metrics" reported by
cell 27 cannot be reproduced from the notebook source alone.

## Additional Finding (contradiction — cited but inconsistent, NOT a hole)

### Finding 6b — 30 ticks vs 50 ticks

| Cell | Model | Commits to | Line |
|------|-------|-----------|------|
| 9 | M2 sweep | `range(30)` | 9:29 |
| 12 | M3 loop | `range(50)` | 12:36 |

Assumption #6 ("30 ticks") is **cited** at cell 9:29, but cell 12:36 commits to **50** ticks
for the M3 model. This is a parameter inconsistency across models — not an uncited
assumption, but a latent reproducibility/consistency defect.

## Final Count

- **Total assumptions audited**: 10
- **METHODOLOGY_HOLE (uncited)**: 3 — assumptions **#1**, **#2**, **#3**
