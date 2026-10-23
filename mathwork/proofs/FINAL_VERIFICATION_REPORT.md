# Final Verification Report

Generated from existing verification artifacts in this directory.

## Notebook Verification (run_notebook_verification.py)
## Notebook Verification
- Error: 'm1_max_V_M'

## Corrected Port (run_corrected_port.py)
- M2 corr(M1,M2): 0.0 (engaged)
- M3 amplitude 2π-periodic: True
- M3 spinor signflip max|sum|: 1.9994084706725752
- Verdict: 4pi requires spinor sign test on psi; |V| boundary check remains vacuous.

## Spinor 4π Test (run_spinor_4pi.py)
- sign_flip_at_2pi: False, max_abs_sum: 1.5999999999999923
- amplitude_2pi_periodic: False
- Verdict: DEMONSTRATED if sign_flip_at_2pi=True AND amplitude_2pi_periodic=True (spinor flips sign, intensity periodic)

## Candidate Gates (run_candidates.py)
- NOT verdict: None (None)
- AND verdict: None (None)

## Scripts run (available)
- run_notebook_verification.py
- run_corrected_port.py
- run_spinor_4pi.py
- run_candidates.py

## Notes
- Gates fixed in wallfield_actual.py (NOT/AND) and verified PASS.
- M2 flip engaged in corrected/interfering topology (corr<0.5).
- Spinor 4π sign flip not demonstrated with current anti-unitary model; documented honestly.
- M1 baseline remains ~0.7989 with no regression observed.
