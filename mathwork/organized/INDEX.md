# Organized Project Files Index

Generated: 2026-10-23

## Folder Structure

```
organized/
├── core_proofs/           # Main proof documents
├── scoring_verdicts/      # Layer-separated verdicts for M1, M2, M3 stages
├── phase_data/            # Phase calibration data
├── csv_data/              # All CSV tables and data exports
├── architecture/          # Architecture docs, audits, decision locks
├── audit_outputs/         # Standalone audit results (generated, runnable locally)
├── wall_config/           # Wall/monitor configuration JSON
└── notebooks/             # Jupyter notebooks (when added)
```

## File Inventory

### core_proofs/
- `proof-set.md` — Main proof set v0.1 (The Imaginary Unit, Straightened)
- `proof-set (1).md` — Duplicate copy of proof set

### scoring_verdicts/
- `scoring_verdict_m1_m2_m3_layered.json` — **Active**: layered per-layer verdicts from ACTUAL notebook code (logic_test / phase_model_prediction / physical_interpretation kept SEPARATE). Verdicts:
  - Logic gates (NOT/AND, cell 27): **FAIL** — NOT outputs HIGH for both inputs (no inversion); AND reduces to XNOR (row `00` always wrong).
  - M1: logic PASS (coherent), phase-model PARTIAL (leakage=0 is a dynamic result; cos(±π)=−1, not 0), physical **OPEN**.
  - M2: logic **FAIL (degenerate/null effect)** — flipped edge L→M joins two zero-phase nodes, so gating is identical to M1; corr(M1,M2)=1.0, mean abs diff=0.0, var(M1)=var(M2)=0.09464. phase-model PARTIAL (variance reproduced but identical to M1; >0.01 criterion is non-discriminatory). physical **NOT ESTABLISHED (vacuous)**.
  - M3: logic **FAIL (vacuous criterion)** — boundary check compares V(−2π) vs V(+2π), which are the same phase mod 2π, so it cannot distinguish 2π from 4π. phase-model PARTIAL. physical OPEN.
- `scoring_verdict.json`, `scoring_verdict_m2.json`, `scoring_verdict_m3.json` — Original single combined `PASS` verdicts (preserved as superseded; conflated layers and contradicted by actual-code reproduction).

### phase_data/
- `phase_c_calibration.json` — Phase C calibration values

### csv_data/
- `architecture_deformation_residue_map.csv` — Deformation residue mapping
- `phase_tree_degree4_residues.csv` — Phase tree degree 4 residues
- `PHASE_PLAN.csv` — Phase plan with workstreams and deliverables
- `Comparative Analysis of Technical and Research Frameworks - Table 1 (1).csv` — Framework comparison
- `Patterns of Symmetry Breaking and Topological Condensation - Table 1 (1).csv` — Symmetry breaking patterns
- `Properties and Types of Syntactic Merge and Structural Claims - Table 1.csv` — Syntactic merge properties
- `Provenance Trace Index for Syntactic Merge and Geometric Latent Spaces - Table 1 (1).csv` — Provenance trace index
- `Identity as a Limit of α-Variation - Table 1 (6).csv` — Identity variation table
- `Quantum Toric Geometry, Noncommutative Instantons, and Latent Spaces - Table 1 (2).csv` — Quantum toric geometry (part 2)
- `Quantum Toric Geometry, Noncommutative Instantons, and Latent Spaces - Table 1 (3).csv` — Quantum toric geometry (part 3)
- `Recursive Spectral Transport Reconstruction and Mathematical Foundations - Table 1 (3).csv` — Recursive spectral transport
- `tree_trace_comparison.csv` — Tree trace comparison data

### architecture/
- `BLIND_SEER_ADJUDICATION_HANDOFF.md` — Review queue adjudication
- `blind_seer_next_research_choices.md` — Next research priorities
- `BLIND_SEER_ROOT_CAUSE_ACCOUNTABILITY_PROMPT.md` — Root cause investigation
- `kink_energy_audit (1).md` — Fractional kink energy audit
- `OMEGA_DIVISOR_DECISION_LOCK.md` — Omega divisor decisions
- `phase_tree_audit.md` — Phase-tree antipode audit
- `VACUUM_SUBTRACTION_AUDIT.md` — Vacuum subtraction audit

### audit_outputs/
- `audit_results.json` — Handoff transcription of the mathematical audit (NOT reproduced from notebook source)
- `gate_noise_results.json` — Handoff transcription of gate noise sweep (full confusion matrices)
- `audit_report.md` — Handoff transcription of phase-gating audit report
- `gate_contract_report.md` — Handoff transcription of gate contract audit report
- `gate_contract_audit.py` — **Frozen** reference harness + negative controls (reproduces NOT ref 1.0, XNOR control 0.75, σ=0.5 NOT 0.9736, AND 0.9974).
- `candidate_formulas.py` — Transcribed candidate adapters (M1/M2 weight rules; NOT always-HIGH; AND bond-gate candidates M1/M2).
- `run_candidates.py` — Wires candidates into the frozen contract (unchanged seeds/truth tables/noise/confusion).
- `candidate_gate_results.json` — Per-row + confusion-matrix results for the candidates vs frozen contract.
- `candidate_gate_contract_report.md` — Candidate verdicts.
- `candidate_gate_vs_reference.png` — NOT + AND candidates vs reference accuracy vs noise.
- `discrimination_tests.py` — M1/M2 profile reproduction, M3 4π phase-sensitive test.
- `discrimination_results.json` — Handoff-transcription numbers (used as a cross-check target, NOT the source of truth).
- `discrimination_audit.png` — Four-panel comparison (M1/M2 profiles; M3 intensity-only vs interference).
- `wallfield_actual.py` — **Verbatim port** of notebook cells (`RefactoredWallFieldSimulation.tickVField`, `M2WallFieldSimulation`, `M3LoopFieldSimulation`, cell-27 gate functions) + `GATE_DECISION_THRESHOLD = 0.5`.
- `run_notebook_verification.py` — Reproduces M1/M2/M3 sweeps and gate tests through the frozen contract using `wallfield_actual.py`.
- `notebook_verification_results.json` — **Source of truth**: actual-code reproduced metrics (max_transmitted_V_M=0.7989, leakage_ratio=0.0, λ₂=1.0; M2 variance=0.0946 identical to M1; M3 boundary_deviation=0.0 comparing same-phase-mod-2π points; NOT input-1 acc=0.0; AND row 00 acc=0.0).
- `notebook_m1_m2_m3_verification.png` — Plot: M1 curve == M2 curve (null flip effect); M3 boundary points coincide mod 2π.

### wall_config/
- `memory_array_1792658841801.json` — Wall monitor configuration

## Verification status (from ACTUAL notebook source)

- **Reproduced from source**: `wallfield_actual.py` (verbatim notebook port) + `run_notebook_verification.py` + `notebook_verification_results.json` are the authoritative artifacts. The handoff-transcription files (`audit_results.json`, `discrimination_results.json`, `gate_noise_results.json`) are retained only as cross-check targets.
- **Logic test**: candidates FAIL. NOT outputs HIGH for both inputs (50%, no inversion); AND candidates M1/M2 reduce to XNOR (row `00` always wrong, 75%). Reference contract unaffected.
- **Phase-model prediction**: PARTIAL. Weight-rule algebra reproduced; the reported M2 variance `0.0946` is reproduced BUT is identical to M1's variance (M2 is a null effect on the flipped zero-phase edge, corr=1.0). The reported `cos(π)=−1` boundary is confirmed (NOT zero).
- **Physical interpretation**: OPEN / NOT ESTABLISHED. Orientation-flip as independent physical DOF, one-way topological barriers, perfect destructive interference, and 4π double-cover are not established. M3 requires the phase-sensitive interference observable (intensity-only is flat).
- **Smuggling flag**: `true` (confirmed from source). M1 and M2 produce byte-identical transmission curves; the M2 verdict's PASS rests on a variance number M1 satisfies identically while the flipped edge has zero observable effect.

## Notes

- The audit outputs in `audit_outputs/` were generated from the conversation context, not reproduced from original Colab artifacts.
- `wallfield_actual.py` and `run_notebook_verification.py` are newly authored here to reproduce the **notebook cell source** (`ImaginaryUnit.ipynb` cells 3/4/5/8/9/11/12 and cell 27), not the handoff equations.
- Original notebook files (`ImaginaryUnit.ipynb`, `Self_Conjugation.ipynb`) and plot images are present at `mathwork/` root; they need to be added into `notebooks/` from the source Colab environment.
- PDF files referenced in conversation (Comprehensive_Phase_B_Wave_Logic_Report.pdf, Geometric_Algebra_of_Time_and_Symmetry.pdf, Prime-Resonance_Hilbert-Pólya_Operator.pdf) are present at `mathwork/` root but not copied into `organized/`.
