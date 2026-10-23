# Plan: Verify candidate phase-gate formulas against the frozen gate contract

## Goal
Run the actual candidate formulas (M1 scalar model, M2 phase-flip model, M3) through the **frozen** scoring contract in `gate_contract_audit.py` so the reported verdicts change from "unverified" to "tested". Until this runs, no claim about M1 leakage, M2 variance, M3 4π behavior, or the wall's physical interpretation is valid. Wall wiring stays strictly downstream of a passing gate contract.

## Scope / constraints
- **Do not** re-author the original Colab notebook. Do not hand-tune seeds/noise to pass.
- The truth tables and the noise sweep in `gate_contract_audit.py` are **frozen** acceptance criteria (`NOT: 0->1,1->0`; `AND: 00/01/10->0, 11->1`; σ ∈ {0.0,0.10,0.25,0.50,0.75,1.00,1.25} rad; decode rule: `bit=1 iff cos(phi)<0`).
- Three verdicts remain **distinct and non-interchangeable**: (1) gate logic test passes, (2) phase model predicts correctly, (3) physical/topological interpretation supported. Do not collapse them into one PASS.
- Evidence pipeline must **earn** the right to drive the wall — it must not inherit credibility from it.

## Current state (already done)
- `D:\AGENTSANDBOX\mathwork\gate_contract_audit.py` — reference harness + negative controls. Locally validated.
- `D:\AGENTSANDBOX\mathwork\gate_noise_results.json` — full confusion matrices. Zero-noise: NOT ref 100%, AND ref 100%; control "always-HIGH NOT" = 50%, "XNOR/AND" = 75%.
- `D:\AGENTSANDBOX\mathwork\audit_results.json` — reconstructed math claims + the explicit `reported_claims_not_independently_reproduced` list:
  `M1 leakage=0.00%`, `M2 profile variance=0.0946`, `M3 periodicity_conforms_to_4pi=true`, `NOT-gate noise metrics`, `heartbeat watchdog behavior`, `calibration JSON non-monotonicity`.
- `D:\AGENTSANDBOX\mathwork\organized/INDEX.md` — file inventory.

## Decisions already locked
- Boundary correction: `cos(±π/2)=0` (zero-coupling); `cos(±π)=-1` (max magnitude, negative sign). M1 zero when `φ_S−φ_T = π/2+kπ`; M2 zero when `φ_S+φ_T = π/2+kπ`.
- M2 ≠ M1 **only** with a nonzero target phase. At `φ_T=0` the curves coincide (`cos(−φ_S)=cos(φ_S)`); full-cycle variance is `0.5` for both raw cosine rules. The reported `0.0946` is unmeaningful without the measurement definition + an M1 control.
- M3 spinor example `ψ(φ)=e^{iφ/2}` flips amplitude sign at `2π` but has **constant** intensity `|ψ|²` — an intensity-only plot cannot establish 4π behavior; it needs a phase-sensitive relative/interference measurement.

## Ordered tasks

### 1. Implement candidate adapters against the frozen contract
Add, in a new module `candidate_formulas.py` (or as wrappers in a new cell block of the audit), three explicit functions that **replace only the model bodies** while keeping the harness's seeds, balance, confusion-matrix convention, and noise sweep unchanged:

| Adapter | Definition | Returns |
|---|---|---|
| `not_phase_candidate(phi_in, output_noise)` | candidate NOT rule | decode of candidate output phase |
| `and_phase_candidate(phi_a, phi_b, output_noise)` | candidate AND rule | decode of candidate output |
| `m2_weight(phi_source, phi_target)` | `w * cos(phi_source + phi_target)` | edge weight (float) |

> M1 stays the in-harness reference `cos(phi_source − phi_target)`. M2 is the candidate to be plugged in. Do **not** swap the truth-table target or acceptance thresholds with candidate outputs.

### 2. NOT / AND logic pass (the real defect class)
Run `not_phase_candidate` and `and_phase_candidate` through the existing `run_not_sigma`/`run_and_sigma` loop. **Gate contract passes only if**, at σ=0, every row matches the exact truth table (per-row confusion: TN/FP/FN/TP, not aggregate accuracy). The XNOR control already shows why aggregates lie (75% while row 00 is all-wrong). If per-row fails, the candidate is FAILED — full stop, no wall progress.

### 3. M1 vs M2 discrimination (the real identity question)
- At `φ_T = 0`: assert `max|W_M2 − W_M1| = 0` (cosine even). A nonzero result = harness/candidate error.
- At `φ_T = 0.7` (nonzero): assert pointwise profiles differ, **and** assert full-cycle mean ≈ 0 and variance ≈ 0.5 for both raw cosine rules (matching `audit_results.json` reconstruction). If a reported `0.0946` differs, locate the measurement definition or reject it as "not established."
- Do **not** accept variance alone as discrimination — it is provably insufficient for a full-cycle uniform sweep.

### 4. M3 4π discrimination (the real periodicity question)
Add a phase-sensitive test: measure a relative/interference observable between `ψ(φ)` and `ψ(φ+2π)` (i.e. a reference branch). Assert the sign (or relative phase) flips at `2π` and restores at `4π`. An intensity-only `|ψ|²` check is explicitly insufficient (variance range `8.88e-16`, constant). Document the reference/branch the test uses.

### 5. Connectivity λ₂ from the actual propagation graph
Compute `λ₂` from the graph/operator the **phase-weighted** propagation actually uses (directed, with the M1/M2 weight signs), not the unweighted baseline. Report directed and symmetrized `λ₂` separately. The P3/K3 examples in `audit_results.json` (`λ₂≈1` and `3`) characterize their standard unweighted graphs, not the phase-gated system — that distinction must hold.

### 6. Verdict bookkeeping (separate layers)
For each of M1, M2, M3 and for the gate contract, write a **per-layer verdict** object into `organized/scoring_verdicts/` with fields:
`logic_test: PASS|FAIL|UNTESTED`, `phase_model_prediction: PASS|FAIL|UNTESTED`, `physical_interpretation: PASS|FAIL|OPEN`.
Do not re-issue the single `status: PASS` verdict that conflated these.

## Validation criteria (PASS gates)
A candidate/hypothesis advances only when **all** of:
1. NOT+AND per-row truth tables PASS at σ=0 against the frozen contract.
2. M1/M2 discrimination reproduces `max abs diff = 0` at φ_T=0 and `≈0.5` variance at φ_T=0.7 (reconstructing audit_results.json).
3. M3 4π test uses a phase-sensitive reference; intensity-only rejected as proof.
4. `λ₂` computed from the actual phase-weighted operator, directed vs symmetrized reported.
5. Three-layer verdicts are written to `organized/scoring_verdicts/`, not collapsed.

## Risks / known unknowns
- Original Colab `.ipynb` and the 6 plot PNGs are not in the mounted workspace (`organized/notebooks/` empty). Candidate formulas must be transcribed from the handoff equations — document the exact transcription source for each adapter.
- "M2 variance = 0.0946" has no known measurement definition; treat as unreproducible until definition + M1 control supplied.
- Do not advance the wall (OVERSEER task board, V-field) until §2–§6 PASS. Visualization must not certify the model driving it.

## Out of scope
- Wall visualization wiring, `OVERSEER` task board updates, V-field edits — all explicitly gated on §2–§6 PASS.
- Re-running or "reproducing the notebook" beyond plugging formulas into the harness.
- Changing the audit's phase-encoding/decoding rule or seeds.

## Artifacts produced/updated
- `candidate_formulas.py` (new) — candidate adapter implementations + transcription source notes.
- `gate_noise_results.json` (re-run) — candidates vs reference, per noise level.
- `organized/scoring_verdicts/scoring_verdict_m1_m2_m3_layered.json` (new) — per-layer verdicts.
- `organized/architecture/gate_contract_candidate_verification.md` (new) — this plan summary once implemented.

## Open questions (blocking)
- Q1: exact transcription of the candidate NOT/AND phase rules from the original notebook (needed for §1 adapters). If the formulas are not recoverable from the handoff equations, the gate contract cannot be advanced for the candidate — mark `logic_test: UNTESTED` and stop.

## Implemented results — two tiers

### Tier A: handoff transcription (historical, cross-check only)
All steps ran locally, no Colab credits used.

- §1–§2 (candidates + frozen gate contract): `candidate_formulas.py`, `run_candidates.py` → `candidate_gate_results.json`, `candidate_gate_vs_reference.png`. Zero-noise candidate NOT = 50% (always HIGH, FAIL); candidate AND M1/M2 = 75% (XNOR, row `00` always wrong, FAIL). Reference NOT/AND = 100%.
- §3 (M1 vs M2 discrimination of the *weight rule*): `discrimination_tests.py` reproduces `audit_results.json` exactly — φ_T=0 max abs diff = 0.0 (coincide, cos even); φ_T=0.7 max abs diff = 1.2884354 = 2·sin(0.7); full-cycle variance = 0.5 for BOTH M1 and M2 raw cosine rules.
- §4 (M3 4π of the *spinor algebra*): ψ=e^{iφ/2} amplitude returns at 4π (reproduced), intensity flat (|ψ|² range ≈ 0 → intensity-only FAILS), phase-sensitive interference |ψ+ref|² is NOT 2π-periodic → 4π signature confirmed only for the interference observable.
- §5 (connectivity of the *weight graph*): unweighted P3 path λ₂ = 1.0; symmetrized weighted Laplacian λ₂ = 0.7648; directed weighted spectrum differs.
- §6 (layered verdicts, handoff-tier): hand-transcription verdicts; smuggling flag `true`.

These reproduce the *handoff equations*, not the notebook cell source — insufficient to validate the reported transmission/variance metrics.

### Tier B: ACTUAL notebook source (authoritative)
Source of truth: `wallfield_actual.py` (verbatim port of `ImaginaryUnit.ipynb` cells 3/4/5/8/9/11/12, 27) + `run_notebook_verification.py` + `notebook_verification_results.json` + `organized/scoring_verdicts/scoring_verdict_m1_m2_m3_layered.json`.

- §3 (actual M1 vs M2 diffusion sweep): the reported `max_transmitted_V_M = 0.7989364408479221` and `leakage_ratio = 0.0` and `λ₂ = 1.0` are **reproduced exactly** for M1. For M2, `max_transmitted_V_M_m2 = 0.7989364408479221` (byte-identical), `profile_variance = 0.09464497511616608`. corr(M1,M2)=1.0, mean |M1−M2|=0.0, var(M1)=var(M2). **Root cause (confirmed in source cells 8/9/11/12):** the flipped edge in M2 (`L→M`) and M3 (`2→0`) has its **source node clamped to phase 0**, so `d_phi(flip)=−ϕ_src−ϕ_tgt` equals `d_phi(nonflip)=ϕ_src−ϕ_tgt` — the T-flip operator **never engages** in either sweep. The >0.01 "PASS" variance for M2 is therefore a property of the phase sweep shared identically with M1, not evidence of orientation gating.
- §4 (actual M3): `periodicity_conforms_to_4pi = true`, `boundary_deviation = 0.0`, reproduced. But the check is `|V(−2π) − V(2π)| < 0.05` where −2π and +2π are the **same phase mod 2π** — it passes for ANY 2π- or 4π-periodic `cos`-based system and cannot certify double-cover. (Consistent with §4 Tier A and the inert-flip root cause: the flip sits on a zero-phase source node.)
- §6 (layered verdicts, actual-code): see `organized/scoring_verdicts/scoring_verdict_m1_m2_m3_layered.json`. Corrected from the Tier-A hand-transcription:
  - Logic gates (NOT/AND, cell 27): FAIL.
  - M1: logic PASS (coherent sweep), phase-model PARTIAL (cos(±π)=−1, not 0; leakage 0 is dynamic), physical OPEN.
  - M2: logic **FAIL (degenerate — T-flip inert)**, phase-model PARTIAL, physical **NOT ESTABLISHED (vacuous)**.
  - M3: logic **FAIL (flip inert + vacuous boundary)**, phase-model PARTIAL, physical OPEN.
  - Smuggling flag `true`, now with source-root-cause: corr(M1,M2)=1.0.

### Decision lock (final)
The wall (OVERSEER task board, V-field) remains **gated**: candidates fail §2 and M2/M3 logic tests fail §3/§4 from actual source. No physical/topological claim — orientation-flip DOF, one-way barriers, perfect destructive interference, 4π double-cover — is established by this codebase. To advance, M2 must flip an edge incident to a **nonzero-phase** node, AND the M3 check must use a phase-sensitive relative/interference observable (or a true spinor sign test), not an intensity/amplitude boundary sample.

### Artifacts synced into `organized/` (Tier B)
`audit_outputs/`: `notebook_verification_results.json`, `notebook_m1_m2_m3_verification.png`, `discrimination_results.json`. `scoring_verdicts/`: `scoring_verdict_m1_m2_m3_layered.json` (authoritative layered verdict, supersedes the earlier Tier-A single combined verdicts). Root sources (kept at `mathwork/` root, source of truth per INDEX.md): `wallfield_actual.py` (verbatim notebook port), `run_notebook_verification.py`, `candidate_formulas.py`, `run_candidates.py`, `discrimination_tests.py`, `build_layered_verdicts.py`.

Q1 resolved (with caveats): the weight-rule algebra reproduces the handoff *math*, but the candidates fail the gate contract, and the reported transmission/variance metrics reduce to a **null M2 effect** (corr=1.0) and a **vacuous M3 criterion** under the actual notebook code — so the physical/topological claims remain OPEN, not verified.
