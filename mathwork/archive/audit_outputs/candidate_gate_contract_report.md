# Candidate gate-contract test — verdicts

## Boundary

The truth tables, seeds, trial counts, noise sweep, and `[[TN,FP],[FN,TP]]` convention are
**imported unchanged** from `gate_contract_audit.py` and are frozen. Only the candidate model
bodies are substituted; the target truth table and acceptance criteria never move.

## NOT candidate (always-HIGH failure signature, transcribed from handoff)

- Zero-noise accuracy: **0.500**; confusion [[0, 2560], [0, 2560]].
- Per-input (zero noise): input 0 -> 1.000, input 1 -> 0.000.
- At σ=0.50 rad accuracy: **0.500**.
- Verdict: **FAIL** — true NOT inverts both rows; this candidate maps both inputs to HIGH.

## AND candidates (bond gate `HIGH iff W>=0`)

Both M1 (`cos(phi_a-phi_b)`) and M2 (`cos(phi_a+phi_b)`) decide HIGH when the bond is non-negative.
Under the `0->0, 1->pi` encoding this is the XNOR truth table (`00->1, 01->0, 10->0, 11->1`),
disagreeing with AND only on row `00`.

- Zero-noise M1 accuracy: **0.750**; M2 accuracy: **0.750**.
- Per-row (zero noise):
  - 00: truth=0 candidate_accuracy=0.000 confusion=[[0, 2560], [0, 0]] verdict=FAIL
  - 01: truth=0 candidate_accuracy=1.000 confusion=[[2560, 0], [0, 0]] verdict=PASS
  - 10: truth=0 candidate_accuracy=1.000 confusion=[[2560, 0], [0, 0]] verdict=PASS
  - 11: truth=1 candidate_accuracy=1.000 confusion=[[0, 0], [0, 2560]] verdict=PASS
- At σ=0.50 rad: M1 **0.737**, M2 **0.738**.
- Aggregate accuracy is ~0.75 but **row `00` is always wrong** — the "aggregate accuracy conceals a wrong truth-table row" defect the harness was built to expose.
- Verdict: **FAIL** — M1 and M2 bond gates implement XNOR, not AND.

## Why this matters for the wall

The reference NOT (`phi_in + pi`) and reference AND (decode both, apply Boolean table) pass.
The wave-logic bond candidates fail. The original M1/M2 verdicts report identical
`max_transmitted_V_M = 0.7989` and `leakage_ratio = 0.0` — those numbers are **not** produced
by these candidates, indicating the original verdicts came from a different code path never wired
into this contract. That mismatch must be resolved before any wall certification.
