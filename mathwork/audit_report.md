# Phase-gating audit — reconstructed checks

## Scope and evidence status

This audit was generated from the equations and reported values in the supplied handoff. The original Colab notebook, source cells, raw outputs, six original plots, and calibration/verdict JSONs were not present in the active working directory. **This is not a reproduction of those artifacts and does not independently validate their reported verdicts.**

## Verified mathematical results

1. **M1/M2 at zero target phase:** max absolute difference over the tested sweep = `0`. The curves must overlap because `cos(-phi_s) = cos(phi_s)`.
2. **M1/M2 at target phase 0.7:** the profiles differ pointwise (max absolute difference `1.2884`), but their uniform full-cycle means and variances remain equal (variances `0.500000` and `0.500000`). A single reported variance such as `0.0946` is not evidence of an orientation flip without a matched comparator and a definition of the statistic.
3. **Cosine boundary:** `cos(pi) = -1`, not 0. For the signed rule `w*cos(Delta phi)`, the weight at `Delta phi=pi` is `-w`; zero occurs at `Delta phi=pi/2 + k*pi`. If the implementation clips negative weights to zero, that is a different rule and must be stated explicitly.
4. **M3 4π example:** `psi(phi)=exp(i*phi/2)` changes sign at `2π` and returns at `4π`, while intensity remains constant. An intensity-only trace cannot show the sign reversal; a phase-sensitive relative/interference measurement is needed. This example does not validate the original notebook's M3 simulation.
5. **Logic gates:** the generated table shows the distinct truth tables for NOT, AND, and XNOR. This is a reference specification, not evidence that the original noisy analog gate implements them.
6. **Graph lambda2:** the standard undirected 3-node path `P3` gives lambda2=`1`, and the complete graph `K3` gives lambda2=`3`. These values describe different graphs; graph symmetrization can change the operator being measured.

## Original claims still unverified

The following require the original code or raw artifacts: M1 leakage `0.00%`; M2 profile variance `0.0946`; M3 `periodicity_conforms_to_4pi=true`; the NOT-gate noise metrics; watchdog behavior; and the calibration JSON's claimed non-monotonicity.

## Minimal next falsification steps

- Make M1 and M2 explicit functions and test a nonzero target phase; report both pointwise profile difference and full-cycle statistics.
- Decide whether weights are signed cosine weights or rectified conductances; align equations, code, plots, and boundary claims.
- Test M3 with a phase-sensitive observable over one and two complete turns.
- Exercise all four two-input truth-table rows and both NOT inputs, then assess noisy distributions against predefined acceptance thresholds.
- Compute connectivity from the same graph/operator actually used in propagation; label whether directed, symmetrized, weighted, or unweighted.
