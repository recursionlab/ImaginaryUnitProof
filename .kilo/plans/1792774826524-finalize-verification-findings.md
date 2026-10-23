# Implementation Plan: Geometric Algebra Verification Repairs

## Objective
Fix the three defects in the mathwork verification suite (gates, flip engagement, 4π test), rerun all scripts, and produce final consolidated results.

## Tasks

### 1. Fix NOT/AND Gate Implementations (wallfield_actual.py)
- Replace `simulate_noisy_not_gate` amplitude formula with proper inversion: output HIGH when input phase is π (bit 1), LOW when 0.
- Replace `simulate_noisy_and_gate` amplitude formula with proper AND: output HIGH only when both inputs HIGH.
- Rerun `run_notebook_verification.py` to regenerate `notebook_verification_results.json` with PASS verdicts.

### 2. Engage T-Flip in M2/M3 (wallfield_actual.py)
- Remove phase clamping on flipped edge source nodes so `dφ(flip) ≠ dφ(nonflip)`.
- In M2: allow L node to carry nonzero phase; in M3: allow node 2 to carry nonzero phase.
- Rerun `run_corrected_port.py` to verify flip engagement (corr should drop below 1.0).

### 3. Implement 4π Spinor Sign Test
- Add anti-unitary T (`ψ → ψ*`) on the flipped arm in `run_spinor_4pi.py`.
- Test `|ψ(φ)+ψ(φ+2π)| < ε` (sign flip) and `|ψ(φ)-ψ(φ+4π)| < ε` (return).
- Rerun and confirm `sign_flip_at_2pi = true`.

### 4. Write Round 9 Consolidated Report
- Update `FINAL_VERIFICATION_REPORT.md` with fixed results.
- Regenerate all JSON outputs with corrected implementations.

### 5. Final Verification
- Run all 13 scripts, confirm all verdicts flip to PASS where appropriate.
- Verify no regressions in M1 baseline (max_V_M still ~0.7989).

## Execution Order
1 → 2 → 3 → 4 → 5

## Validation
- NOT gate: both input rows ≥ 99.995% accuracy
- AND gate: all 4 truth-table rows ≥ 99.995% accuracy
- M2: corr(M1,M2) < 0.5 (flip engaged)
- M3: sign_flip_at_2pi = true, amplitude 2π-periodic
- All 13 scripts exit 0
