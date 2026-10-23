# Gate-contract audit — standalone reference harness

## Purpose and boundary

This run executes locally with no Colab credits. It implements an explicit phase-bit encoding and checks the exact Boolean contracts under a declared noise sweep. **It does not reproduce or validate the missing original Colab notebook.** The negative controls demonstrate recognizable failure modes; their behavior must not be presented as the exact legacy implementation unless its source formula is supplied.

## Contract

- Encoding: bit 0 → phase 0; bit 1 → phase π.
- Decode: bit 1 iff `cos(phase) < 0`.
- NOT: apply a π phase shift, then decode after output-channel noise.
- AND: decode both input phases, apply the exact Boolean AND truth table, encode output, then decode after output-channel noise. This is a **logic reference**, not evidence for a new physical phase-coupling mechanism.
- Negative control for NOT: always outputs HIGH, matching the reported failure signature of both inputs producing HIGH.
- Negative control for AND: threshold `cos((phi_a - phi_b)/2) >= 0.5`, a phase-agreement/XNOR-like rule.

AND rows are balanced independently: `00`, `01`, `10`, `11` each receive 2560 trials per noise level. NOT inputs are balanced. Each noise level is rerun using the fixed, predeclared seeds in the JSON. Noise is Gaussian phase perturbation on each input and output phase.

## Key checks

- At zero noise, NOT reference accuracy: **1.000**; always-HIGH control accuracy: **0.500**.
- At zero noise, AND reference accuracy: **1.000**; cosine/XNOR negative-control accuracy against AND: **0.750**.
- At σ = 0.50 rad, NOT reference accuracy: **0.974**; always-HIGH control accuracy: **0.500**.
- At σ = 0.50 rad, AND reference accuracy: **0.997**; cosine/XNOR negative-control accuracy: **0.714**.
- Zero-noise AND candidate output correctness by row: 00: 1.000, 01: 1.000, 10: 1.000, 11: 1.000.

## Confusion matrices

Matrix convention is `[[TN, FP], [FN, TP]]`; rows are actual output labels (0 then 1), columns are predicted output labels (0 then 1). Full matrices at every noise level are in `gate_noise_results.json`.

### Zero-noise NOT

Reference: `[[2560, 0], [0, 2560]]`

Always-HIGH failure control: `[[0, 2560], [0, 2560]]`

### Zero-noise AND

Reference: `[[7680, 0], [0, 2560]]`

Cosine/XNOR negative control: `[[5120, 2560], [0, 2560]]`

## Verdict

**Reference-contract checks pass; legacy implementation remains unverified.** The test harness distinguishes a correct Boolean gate from explicit failure controls and produces full confusion matrices under noise. This is the smallest local proof that the testing machinery can detect the named defects. The original notebook's formulas, seeds, plots, and verdicts must still be plugged into this harness before any claim about the original implementation can change from unverified to tested.

## Integration adapter points

Replace the implementations of `not_phase_reference` and `and_truth_table_reference` with wrappers around the actual candidate functions once those source cells are available. Do not replace the truth-table target or acceptance criteria with candidate outputs. Preserve row balance, fixed seeds, confusion matrix convention, and the noise sweep.