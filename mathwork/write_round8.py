"""Write Round_8.md via adv_common.write_round(8, ...)."""
from __future__ import annotations
from adv_common import write_round

content = """# Round 8 — Ruthless Self-Audit: Cell-27 Gate Truth Tables

## Source

- **Cell 27 of `ImaginaryUnit.ipynb`**: defines `simulate_noisy_not_gate` and
  `simulate_noisy_and_gate` (the Phase-B noise-stress cell).
- **`wallfield_actual.py`**: ports cell 27's formulas exactly into a reproducible
  API (explicit `np.random.default_rng` instead of global `np.random.normal`).
  The algebraic expressions are identical; only the RNG plumbing differs.
- **Seeds**: 5 explicit seeds taken from `gate_contract_audit.SEEDS`:
  `(73129, 84221, 95317, 106487, 117503)`.
- **Trial count**: `TRIALS_PER_ROW_PER_SEED = 512` (from `gate_contract_audit`).
- **Noise**: `sigma = 0.0` rad (deterministic limit).
- **Decision rule**: `bit = 1 if amplitude >= 0.5 else 0`
  (`GATE_DECISION_THRESHOLD = 0.5`).
- **Phase encoding**: bit 0 -> phase 0 rad; bit 1 -> phase pi rad.

---

## NOT Gate Truth Table Audit

**Expected**: NOT(0) = 1 (HIGH), NOT(1) = 0 (LOW).

| Row | Input bit | Input phase (rad) | Expected output | TP | FP | TN | FN | n    | Accuracy | Amplitude (mean/min/max) | Correct? |
|-----|-----------|--------------------|-----------------|----|----|----|----|------|----------|--------------------------|----------|
| 0   | 0         | 0.0000             | HIGH (1)        | 2560 | 0  | 0  | 0  | 2560 | 1.0000   | 1.000000 / 1.0 / 1.0     | YES      |
| 1   | 1         | 3.1416             | LOW (0)         | 0  | 2560 | 0  | 0  | 2560 | 0.0000   | 1.000000 / 1.0 / 1.0     | **NO**   |

### NOT Row 1 — Broken

- **Amplitude**: 1.000000 (expected 0.000000 for a LOW output).
- **Magnitude of failure**: full-scale — the gate outputs the maximum amplitude
  (1.0) when it should output zero (0.0). Accuracy = 0.0000 (0% correct on this row).
- **Root cause (zero-noise algebra)**:

  The NOT formula reduces at sigma=0 to:

  ```
  path1_phase = input_phase
  path2_phase = -input_phase - pi
  output_amplitude = 0.5 * (cos(input_phase) + cos(-input_phase))
                   = 0.5 * (cos(input_phase) + cos(input_phase))
                   = cos(input_phase)
  output = |cos(input_phase)|
  ```

  For input_phase = 0 (bit 0): `|cos(0)| = 1` -> HIGH (correct).
  For input_phase = pi (bit 1): `|cos(pi)| = |-1| = 1` -> HIGH (**wrong**;
  cos(pi) = -1 encodes the negation, but `abs()` destroys the sign).

  The logical result is encoded in the *sign* of cos(input_phase), not in its
  *magnitude*. Taking `abs()` before thresholding collapses +1 and -1 to the same
  value (1.0), making both inputs indistinguishable. This is the "always-HIGH"
  failure signature.

---

## AND Gate Truth Table Audit

**Expected truth table**: 00->0, 01->0, 10->0, 11->1.

| Row | Input pair (a,b) | Phase a (rad) | Phase b (rad) | Delta phi (rad) | Expected output | TP | FP | TN | FN | n    | Accuracy | Amplitude (mean/min/max) | Correct? |
|-----|-------------------|---------------|---------------|------------------|-----------------|----|----|----|----|------|----------|------------------------|----------|
| 00  | (0,0)             | 0.0000        | 0.0000        | 0.0000           | LOW (0)         | 0  | 2560 | 0  | 0  | 2560 | 0.0000   | 1.000000 / 1.0 / 1.0     | **NO**   |
| 01  | (0,1)             | 0.0000        | 3.1416        | -3.1416          | LOW (0)         | 0  | 0  | 2560 | 0  | 2560 | 1.0000   | 0.000000 / 0.0 / 0.0     | YES      |
| 10  | (1,0)             | 3.1416        | 0.0000        | 3.1416           | LOW (0)         | 0  | 0  | 2560 | 0  | 2560 | 1.0000   | 0.000000 / 0.0 / 0.0     | YES      |
| 11  | (1,1)             | 3.1416        | 3.1416        | 0.0000           | HIGH (1)        | 2560 | 0  | 0  | 0  | 2560 | 1.0000   | 1.000000 / 1.0 / 1.0     | YES      |

### AND Row 00 — Broken

- **Amplitude**: 1.000000 (expected 0.000000 for a LOW output).
- **Magnitude of failure**: full-scale — outputs maximum amplitude (1.0) when
  the AND gate requires zero (0.0). Accuracy = 0.0000 (0% correct on this row).
- **Confusion**: TN=0, FP=2560, FN=0, TP=0. This is a pure false-positive row.

### Correct rows

- AND rows 01 and 10: amplitude = 0.0 (correct LOW). TN=2560, accuracy=1.0.
- AND row 11: amplitude = 1.0 (correct HIGH). TP=2560, accuracy=1.0.

---

## Broken Rows Summary

| Gate | Row                          | Amplitude | Expected amplitude | Correct output | Actual output | Magnitude of error | Accuracy |
|------|------------------------------|-----------|--------------------|----------------|---------------|--------------------|----------|
| NOT  | row 1 (input 1, phase pi)     | 1.0       | 0.0                | LOW (0)        | HIGH (1)      | +1.0 (full-scale)  | 0.0000   |
| AND  | row 00 (inputs 0,0)           | 1.0       | 0.0                | LOW (0)        | HIGH (1)      | +1.0 (full-scale)  | 0.0000   |

Both broken rows produce amplitude = 1.0 where 0.0 is required — a 100% magnitude
error. The remaining rows (NOT-0, AND-01, AND-10, AND-11) are correct.

---

## Algebraic Proof: AND candidate `|cos((phi_a - phi_b)/2)|` is XNOR, not AND

### The candidate formula

```
amplitude = |cos((phi_a - phi_b) / 2)|
```

At sigma = 0 (deterministic), with encoding `bit -> phase = pi * bit`:

```
phi_a = pi * a,   phi_b = pi * b
delta_phi = phi_a - phi_b = pi * (a - b)
amplitude = |cos(pi * (a - b) / 2)|
```

### Truth table evaluation (all four rows)

| (a, b) | a - b | delta_phi / pi | cos(delta/2)                          | |amp| | bit (>= 0.5) | AND | XNOR |
|--------|-------|----------------|----------------------------------------|--------|--------------|-----|------|
| (0,0)  | 0     | 0              | cos(0) = 1.0                           | 1.0      | HIGH (1)     | 0   | 1    |
| (0,1)  | -1    | -1             | cos(-pi/2) = 0                         | 0.0      | LOW (0)      | 0   | 0    |
| (1,0)  | 1     | 1              | cos(pi/2) = 0                          | 0.0      | LOW (0)      | 0   | 0    |
| (1,1)  | 0     | 0              | cos(0) = 1.0                           | 1.0      | HIGH (1)     | 1   | 1    |

**Candidate output**: 1, 0, 0, 1
**AND truth table**:  0, 0, 0, 1
**XNOR (equivalence)**: 1, 0, 0, 1

The candidate output matches XNOR exactly, and differs from AND on row 00
(candidate gives HIGH, AND requires LOW).

### Why `cos((phi_a - phi_b)/2)` is structurally XNOR

1. **cos is an even function**: `cos(-x) = cos(x)`. Therefore
   `|cos((phi_a - phi_b)/2)| = |cos((phi_b - phi_a)/2)|`, so the candidate is
   *symmetric under exchange of the two inputs*. AND is also input-symmetric
   on rows 01 and 10, so this alone does not distinguish them.

2. **The candidate depends only on the phase DIFFERENCE** `|phi_a - phi_b|`,
   not on the phases themselves. With `phi = pi * bit`:

   - (a,b) = (0,0): `|phi_a - phi_b| = |0 - 0| = 0`
   - (a,b) = (1,1): `|phi_a - phi_b| = |pi - pi| = 0`

   Both agreeing-input rows yield `delta_phi = 0`, producing the **identical**
   amplitude `|cos(0)| = 1.0`.

3. **AND requires asymmetric treatment of agreeing inputs**:
   - Row 00 (both low): AND = 0 (LOW)
   - Row 11 (both high): AND = 1 (HIGH)

   The candidate assigns the **same** amplitude (1.0) to both, so no threshold
   or decision rule can separate them:
   ```
   amplitude(00) == amplitude(11) == 1.0
   ```
   Yet AND demands `bit(00) = 0` and `bit(11) = 1`. This is an algebraic
   impossibility for any function of `(phi_a - phi_b)` alone.

4. **The logical output is "inputs agree" (XNOR/equivalence)**:
   - When `phi_a == phi_b` (inputs agree: both 0 or both 1):
     `delta_phi = 0`, `amplitude = |cos(0)| = 1` -> HIGH.
   - When `phi_a != phi_b` (inputs differ: one is 0, other is 1):
     `|delta_phi| = pi`, `amplitude = |cos(pi/2)| = 0` -> LOW.

   Output HIGH iff inputs agree, which is the **XNOR** truth table
   (truth table `1, 0, 0, 1`), **not** the AND truth table (`0, 0, 0, 1`).

### Why this is fundamental, not a fixable bug

- **Zero-noise determinism**: At `sigma = 0`, `rng.normal(0, 0) = 0` always.
  Every seed produces identical results. The broken rows are deterministic and
  seed-independent — confirming the failure is structural, not stochastic.
- **Cannot be fixed by threshold tuning**: Rows 00 and 11 produce *identical*
  amplitudes (1.0). Any threshold places both on the same side.
- **Cannot be fixed by noise**: At sigma = 0 the two rows are provably equal.
  With nonzero sigma, they may differ by random chance, but the zero-noise
  limit (the ideal gate behavior) is structurally XNOR. A correct AND gate
  must be correct in the noise-free limit.
- **Cannot be fixed by averaging or trial count**: Averaging over 512 trials
  per seed per row yields amplitude 1.0 for both 00 and 11 (no variance at
  sigma=0). The FP on row 00 persists at 100%.
- **Requires a different formula**: To implement AND, the amplitude must
  depend on more than just the phase *difference*. It must separately sense
  whether each input is low (phase 0) or high (phase pi), e.g. via a sum or
  individual projection. The formula `cos((phi_a - phi_b)/2)` is a pure
  difference operator — it is XNOR by construction.

**Conclusion**: The candidate formula `|cos((phi_a - phi_b)/2)|` is structurally
and provably an XNOR (equivalence) gate at zero noise. Row 00 is broken
because the candidate outputs HIGH (amplitude 1.0) where AND requires LOW
(amplitude 0.0). This difference is not a tunable defect — it is the
defining characteristic of XNOR versus AND: both agreeing-input rows (00 and
11) collapse to the same amplitude, yet AND requires them to map to different
outputs. No noise model, seed, or threshold can reconcile this.

---

## Reproduction

```
python round8_audit.py
```

Outputs the full per-row confusion matrices, amplitudes, and the algebraic
proof table above.
"""

p = write_round(8, content)
print(f"Written: {p}")
