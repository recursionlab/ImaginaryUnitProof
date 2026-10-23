from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
ORGANIZED = OUT / "organized"
(ORGANIZED / "scoring_verdicts").mkdir(parents=True, exist_ok=True)


def build() -> dict:
    nb = json.loads((OUT / "notebook_verification_results.json").read_text(encoding="utf-8"))
    disc = json.loads((OUT / "discrimination_results.json").read_text(encoding="utf-8"))
    m1_orig = json.loads((OUT / "scoring_verdict.json").read_text(encoding="utf-8"))
    m2_orig = json.loads((OUT / "scoring_verdict_m2.json").read_text(encoding="utf-8"))
    m3_orig = json.loads((OUT / "scoring_verdict_m3.json").read_text(encoding="utf-8"))

    m1_curve = np.array(nb["m1_sweep_verdict"]["V_M_results"])
    m2_curve = np.array(nb["m2_sweep_verdict"]["V_M_m2_results"])
    m3_first_phase = nb["m3_sweep_verdict"]["phi_sweeps_m3"][0]
    m3_last_phase = nb["m3_sweep_verdict"]["phi_sweeps_m3"][-1]

    verdict = {
        "title": "Layered verdicts from ACTUAL notebook code (wallfield_actual.py verbatim) — logic / phase-model / physical kept separate",
        "status": "VERIFIED_FROM_NOTEBOOK_SOURCE_NOT_TRANSCRIBED_APPROXIMATION",
        "layer_definitions": {
            "logic_test": "Is the test mechanism coherent and non-degenerate? (Does it actually vary the variable it claims to vary?)",
            "phase_model_prediction": "Do the reproduced numbers (V[M] curves, leakage, variance, lambda2, M3 boundary) match the reported claims, and are they interpreted at the right mathematical layer?",
            "physical_interpretation": "Does the evidence establish the physical claim (independent orientation DOF, one-way barrier, 4 pi double cover) or only an algebraic coincidence?",
        },
        "layers": {
            "logic_gates_NOT_AND": {
                "source": "ImaginaryUnit.ipynb cell 27 (simulate_noisy_not_gate, simulate_noisy_and_gate), run through the frozen per-row truth-table contract with amplitude>=0.5 -> HIGH",
                "logic_test": {
                    "verdict": "FAIL",
                    "basis": (
                        "NOT candidate: input 0 row accuracy 1.0 (correct), input 1 row accuracy 0.0 (always HIGH) -> "
                        "the input-1 row is wrong 100%; no inversion. "
                        "AND candidate amplitude = |cos((phi_a-phi_b)/2)| => XNOR truth table: row 00 (truth=0) predicted HIGH at 0.0 accuracy (always wrong), rows 01/10/11 correct. "
                        "Aggregate 50%/75% hides the exact broken rows."
                    ),
                    "reference_verdict": "Reference NOT/AND gates = 100% (contract intact); only the wave-logic candidates fail.",
                },
                "phase_model_prediction": "N/A — cell-27 candidates are amplitude gates, not the weight-rule sweep.",
                "physical_interpretation": "N/A",
            },
            "M1": {
                "source": "ImaginaryUnit.ipynb cells 3,4,5 (RefactoredWallFieldSimulation.tickVField; 30 ticks, alpha=0.15; 50 phase points)",
                "logic_test": {
                    "verdict": "PASS (coherent)",
                    "basis": "The M1 sweep is a non-degenerate phase-gating sweep; V[M] at +/-pi reaches 0.0 (min at edges).",
                },
                "phase_model_prediction": {
                    "verdict": "PARTIAL",
                    "basis": (
                        "Reproduces max_transmitted_V_M=0.7989364408479221, leakage_ratio=0.0, lambda_2=1.0 EXACTLY (matches scoring_verdict.json). "
                        "But the reported '0% leakage at +/-pi' is a DYNAMIC diffusion result, not weight=0: gating=cos(pi)=-1 (full negative coupling), "
                        "and V[M]=0 emerges because negative S->L flux cancels at M under the 30-tick dynamics. "
                        "The hypothesis text claims 'V[M] drops to 0 when delta_phi approaches +/- pi' and conflates this with zero coupling; "
                        "the boundary cos(pi)=-1 (not 0) is confirmed in discrimination_results.json. Leakage=0 is consistent with the dynamics but is NOT evidence that cos(±pi)=0."
                    ),
                    "reproduced_max_V_M": nb["m1_sweep_verdict"]["max_transmitted_V_M"],
                    "reproduced_leakage_ratio": nb["m1_sweep_verdict"]["leakage_ratio"],
                    "reproduced_lambda_2": nb["m1_sweep_verdict"]["algebraic_connectivity_lambda_2"],
                },
                "physical_interpretation": {
                    "verdict": "OPEN",
                    "basis": "Phase alignment gated diffusion is an algebraic/numerical observation in this scalar diffusion model. Whether it corresponds to a physical orientation degree of freedom or a topological blockade requires the independent symmetry/dynamical conditions noted in the audit; the simulation alone does not establish it.",
                },
            },
            "M2": {
                "source": "ImaginaryUnit.ipynb cells 8,9,11,12 (M2WallFieldSimulation/M3LoopFieldSimulation; flip edge L<->M)",
                "logic_test": {
                    "verdict": "FAIL (degenerate / null effect)",
                    "basis": (
                        "In the M2 sweep the flipped edge is L->M, but BOTH L and M are clamped to phase 0 "
                        "while only S is swept. The flip formula gives d_phi = -phi_L - phi_M = 0, identical to "
                        "the M1 formula phi_L - phi_M = 0, so gating = cos(0) = 1 on the flipped edge in BOTH cases. "
                        "Empirical check: corr(V_M_results, V_M_m2_results) = 1.0, mean |M1-M2| = 0.0, "
                        "var(M1)=var(M2)=0.09464497511616608, max(M1)=max(M2)=0.7989364408479221. "
                        "The orientation-flip operator has ZERO observable effect on V[M] in this configuration."
                    ),
                    "m1_m2_correlation": float(np.corrcoef(m1_curve, m2_curve)[0, 1]),
                    "m1_m2_mean_abs_diff": float(np.mean(np.abs(m1_curve - m2_curve))),
                    "m1_variance": float(np.var(m1_curve)),
                    "m2_variance": float(np.var(m2_curve)),
                },
                "phase_model_prediction": {
                    "verdict": "PARTIAL (reproduced, but meaningless as discrimination)",
                    "basis": (
                        "The reported profile_variance=0.0946 IS reproduced (0.09464497511616608) from the actual code. "
                        "However that same variance is also M1's variance; the >0.01 PASS criterion is satisfied identically by M1 and M2. "
                        "Variance>0.01 is true of any non-flat curve, so it cannot certify 'active phase gating across the flipped orientation boundary.'"
                    ),
                },
                "physical_interpretation": {
                    "verdict": "NOT ESTABLISHED (vacuous)",
                    "basis": (
                        "M2 does not produce a different transmission profile from M1 (pointwise identical). "
                        "A null-effect test cannot establish that orientation is an independent physical degree of freedom, "
                        "that destructive interference is 'perfect,' or that one-way topological barriers exist. "
                        "The PASS is smuggling: M2 is certified on a variance number M1 satisfies identically while the transmission it claims to gate is byte-identical."
                    ),
                },
            },
            "M3": {
                "source": "ImaginaryUnit.ipynb cells 11,12 (M3LoopFieldSimulation; closed 3-cycle 0-1-2-0; 1 flip on edge 2->0; 50 ticks; phi in [-2pi, 2pi])",
                "logic_test": {
                    "verdict": "FAIL (vacuous criterion)",
                    "basis": (
                        f"The periodicity check is |V(phi={m3_first_phase:.4f}) - V(phi={m3_last_phase:.4f})| < 0.05. "
                        f"But {m3_first_phase:.4f} and {m3_last_phase:.4f} are the SAME phase modulo 2*pi "
                        f"(both == 0 mod 2*pi), so this check PASSES for ANY 2*pi-periodic OR 4*pi-periodic system. "
                        f"boundary_deviation = {nb['m3_sweep_verdict']['boundary_deviation']}. "
                        f"It cannot distinguish 2*pi from 4*pi periodicity."
                    ),
                    "periodicity_conforms_to_4pi_reported": nb["m3_sweep_verdict"]["periodicity_conforms_to_4pi"],
                },
                "phase_model_prediction": {
                    "verdict": "PARTIAL",
                    "basis": "Reproduces periodicity_conforms_to_4pi=True/boundary_deviation=0.0 from the actual code. But the spinor sign-flip (the real 4*pi signature) is invisible to V[2], an amplitude. See discrimination_tests.py: |psi|^2 is flat; only the phase-sensitive interference observable |psi+ref|^2 is non-2*pi-periodic.",
                },
                "physical_interpretation": {
                    "verdict": "OPEN",
                    "basis": "4 pi double-cover / quaternionic SU(2) claims require a sign-flip observable. The amplitude-only boundary check is structurally incapable of detecting them.",
                },
            },
        },
        "smuggling_summary": {
            "M1_M2_transmission_identical": bool(np.isclose(m1_curve.max(), m2_curve.max())),
            "M1_M2_curves_correlation": float(np.corrcoef(m1_curve, m2_curve)[0, 1]),
            "M1_M2_variances_identical": bool(np.isclose(np.var(m1_curve), np.var(m2_curve))),
            "verdict": "M2 PASSes a variance>0.01 test that M1 satisfies identically, while its flipped edge has zero observable effect (the flip is on a zero-phase-to-zero-phase link).",
        },
    }
    return verdict


def main() -> None:
    v = build()
    path = OUT.parent / "organized" / "scoring_verdicts" / "scoring_verdict_m1_m2_m3_layered.json"
    path = ORGANIZED / "scoring_verdicts" / "scoring_verdict_m1_m2_m3_layered.json"
    path.write_text(json.dumps(v, indent=2), encoding="utf-8")
    print(json.dumps({
        "verdicts": str(path),
        "logic_gates": v["layers"]["logic_gates_NOT_AND"]["logic_test"]["verdict"],
        "M1": {k: v["layers"]["M1"][k]["verdict"] for k in ("logic_test", "phase_model_prediction", "physical_interpretation")},
        "M2": {k: v["layers"]["M2"][k]["verdict"] for k in ("logic_test", "phase_model_prediction", "physical_interpretation")},
        "M3": {k: v["layers"]["M3"][k]["verdict"] for k in ("logic_test", "phase_model_prediction", "physical_interpretation")},
        "M1_M2_correlation": v["smuggling_summary"]["M1_M2_curves_correlation"],
    }, indent=2))


if __name__ == "__main__":
    main()
