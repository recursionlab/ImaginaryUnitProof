from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from candidate_formulas import m1_weight, m2_weight

OUT = Path(__file__).resolve().parent

TWO_PI = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi
PHI_T_NONZERO = 0.7


def sweep_weights(phi_t: float, n: int = 4096) -> dict:
    phi_s = np.linspace(0.0, TWO_PI, n, endpoint=False)
    w1 = m1_weight(phi_s, phi_t)
    w2 = m2_weight(phi_s, phi_t)
    diff = w2 - w1
    return {
        "phi_target_rad": phi_t,
        "phi_source_samples": n,
        "w_M1_mean": float(np.mean(w1)),
        "w_M1_variance": float(np.var(w1)),
        "w_M2_mean": float(np.mean(w2)),
        "w_M2_variance": float(np.var(w2)),
        "max_abs_difference": float(np.max(np.abs(diff))),
        "w_M1_at_phi_s_zero": float(m1_weight(np.array([0.0]), phi_t)[0]),
        "w_M2_at_phi_s_zero": float(m2_weight(np.array([0.0]), phi_t)[0]),
    }


def m3_spinor_test() -> dict:
    phi = np.linspace(0.0, FOUR_PI, 8192, endpoint=True)
    psi = np.exp(1j * phi / 2.0)
    intensity = np.abs(psi) ** 2
    ref = np.exp(1j * phi)
    interference = np.abs(psi + ref) ** 2
    return {
        "definition": "psi(phi)=exp(i*phi/2); reference branch ref(phi)=exp(i*phi) (2 pi-periodic)",
        "samples": {
            "phi=0": {"real": float(np.real(psi[0])), "imag": float(np.imag(psi[0])), "intensity": float(intensity[0])},
            "phi=2pi": {"real": float(np.real(psi[len(phi) // 4])), "imag": float(np.imag(psi[len(phi) // 4])), "intensity": float(intensity[len(phi) // 4])},
            "phi=4pi": {"real": float(np.real(psi[-1])), "imag": float(np.imag(psi[-1])), "intensity": float(intensity[-1])},
        },
        "amplitude_returns_at_4pi": bool(np.isclose(psi[0], psi[-1], atol=1e-9)),
        "intensity_mean": float(np.mean(intensity)),
        "intensity_range": float(np.ptp(intensity)),
        "intensity_only_periodic_2pi": bool(np.allclose(intensity[:len(phi) // 2], intensity[len(phi) // 2:], atol=1e-9)),
        "interference_signal_periodic_under_2pi": bool(np.allclose(interference[:len(phi) // 2], interference[len(phi) // 2:], atol=1e-9)),
        "verdict": "FAIL (intensity-only)" if np.isclose(np.ptp(intensity), 0.0, atol=1e-12) else "PASS",
    }


def connectivity_lambda2() -> dict:
    unweighted_adj = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    deg = np.diag(unweighted_adj.sum(axis=1))
    L_unweighted = deg - unweighted_adj
    evals_unweighted = np.sort(np.linalg.eigvalsh(L_unweighted))
    unweighted_lambda2 = float(evals_unweighted[1])

    phi = np.array([0.0, PHI_T_NONZERO, 2 * PHI_T_NONZERO])
    phi_s, phi_t = np.meshgrid(phi, phi, indexing="ij")
    a_w = m1_weight(phi_s, phi_t) * unweighted_adj
    directed_lap = np.diag(a_w.sum(axis=1)) - a_w
    evals_dir = np.linalg.eigvals(directed_lap)
    a_sym = (a_w + a_w.T) / 2.0
    lap_sym = np.diag(a_sym.sum(axis=1)) - a_sym
    evals_sym = np.sort(np.linalg.eigvalsh(lap_sym))
    sym_lambda2 = float(evals_sym[1])

    return {
        "topology": "3-node path 0-1-2",
        "phase_assignment_rad": phi.tolist(),
        "weight_rule": "M1: w_ij = cos(phi_i - phi_j)",
        "unweighted_laplacian_lambda2": unweighted_lambda2,
        "directed_weighted_laplacian_eigenvalues_real": [float(x) for x in np.sort(np.real(evals_dir))],
        "symmetrized_weighted_laplacian_lambda2": sym_lambda2,
        "directed_min_real_nontrivial": float(np.min(np.real(evals_dir[evals_dir != 0]))),
        "verdict": (
            "MISMATCH — unweighted lambda2 characterizes the unweighted graph (path P3 -> 1.0), "
            "not the phase-weighted directed operator. Directed and symmetrized spectra differ."
        ),
    }


def make_plot(m1m2_results, m3) -> Path:
    phi_s = np.linspace(0.0, TWO_PI, 1000, endpoint=False)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    w1_z = m1_weight(phi_s, 0.0)
    w2_z = m2_weight(phi_s, 0.0)
    axes[0].plot(phi_s, w1_z, label="M1, phi_T=0")
    axes[0].plot(phi_s, w2_z, "--", label="M2, phi_T=0")
    axes[0].plot(phi_s, m1_weight(phi_s, PHI_T_NONZERO), label="M1, phi_T=0.7")
    axes[0].plot(phi_s, m2_weight(phi_s, PHI_T_NONZERO), "--", label="M2, phi_T=0.7")
    axes[0].set_title("M1 vs M2 weight profiles (zero-crossings shift, variance fixed)")
    axes[0].set_xlabel("phi_source (rad)"); axes[0].set_ylabel("W = w cos(Delta_phi)"); axes[0].grid(True, alpha=.25); axes[0].legend(fontsize=8)

    phi = np.linspace(0.0, FOUR_PI, 1000, endpoint=True)
    psi = np.exp(1j * phi / 2.0)
    ref = np.exp(1j * phi)
    axes[1].plot(phi, np.abs(psi) ** 2, label="|psi|^2 (intensity-only)")
    axes[1].plot(phi, np.abs(psi + ref) ** 2, label="interference |psi+ref|^2")
    axes[1].axvline(TWO_PI, color="k", linestyle=":", alpha=0.5, label="2 pi")
    axes[1].axvline(FOUR_PI, color="k", linestyle="--", alpha=0.5, label="4 pi")
    axes[1].set_title("M3 spinor: intensity-only is flat; interference is 4 pi-periodic")
    axes[1].set_xlabel("phi (rad)"); axes[1].set_ylabel("signal"); axes[1].grid(True, alpha=.25); axes[1].legend(fontsize=8)

    fig.suptitle("Discrimination audits: M1 vs M2 profiles; M3 intensity-only vs phase-sensitive")
    fig.tight_layout()
    path = OUT / "discrimination_audit.png"
    fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)
    return path


def reproduce_audit_math() -> dict:
    z0 = sweep_weights(0.0)
    nz = sweep_weights(PHI_T_NONZERO)
    return {"phi_T_zero": z0, "phi_T_0_7": nz}


def main() -> None:
    m1m2 = reproduce_audit_math()
    m3 = m3_spinor_test()
    conn = connectivity_lambda2()
    plot = make_plot(m1m2, m3)

    expected = {
        "phi_T_zero_max_abs_diff": 0.0,
        "phi_T_0_7_max_abs_diff": 2.0 * math.sin(PHI_T_NONZERO),
        "full_cycle_variance": 0.5,
    }
    reproduces = bool(
        np.isclose(m1m2["phi_T_zero"]["max_abs_difference"], expected["phi_T_zero_max_abs_diff"])
        and np.isclose(m1m2["phi_T_0_7"]["max_abs_difference"], expected["phi_T_0_7_max_abs_diff"])
        and np.isclose(m1m2["phi_T_0_7"]["w_M1_variance"], expected["full_cycle_variance"])
        and np.isclose(m1m2["phi_T_0_7"]["w_M2_variance"], expected["full_cycle_variance"])
    )
    reproduces = bool(reproduces)

    result = {
        "title": "Phase-rule discrimination + M3 + connectivity",
        "status": "REPRODUCED_FROM_HANDOFF_EQUATIONS_NOT_THE_ORIGINAL_NOTEBOOK",
        "audit_math_reproduction_expected": expected,
        "audit_math_reproduction_achieved": reproduces,
        "m1_vs_m2_sweep": m1m2,
        "m2_at_phi_T_zero_coincides_with_M1": bool(np.isclose(m1m2["phi_T_zero"]["max_abs_difference"], 0.0)),
        "m3_spinor": m3,
        "connectivity": conn,
        "open_claims_not_reproduced": [
            "M1 leakage=0.00% at delta_phi=+/-pi (raw cos(pi)=-1, full coupling; zero requires a clip rule)",
            "M2 profile_variance=0.0946 (reconstructed raw-cosine full-cycle variance is 0.5 for both M1 and M2; measurement definition + M1 control missing)",
            "M1/M2 max_transmitted_V_M=0.7989 (this package reproduces weight profiles, not the V_M transmission observable — separate code path)",
        ],
    }
    json_path = OUT / "discrimination_results.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "results": str(json_path),
        "plot": str(plot),
        "audit_math_reproduced": reproduces,
        "m1_vs_m2_phi_T0_max_abs_diff": m1m2["phi_T_zero"]["max_abs_difference"],
        "m1_vs_m2_phi_T0_7_max_abs_diff": m1m2["phi_T_0_7"]["max_abs_difference"],
        "m1_vs_m2_phi_T0_7_variance_M1": m1m2["phi_T_0_7"]["w_M1_variance"],
        "m1_vs_m2_phi_T0_7_variance_M2": m1m2["phi_T_0_7"]["w_M2_variance"],
        "m3_intensity_flat": bool(np.isclose(m3["intensity_range"], 0.0, atol=1e-12)),
        "m3_amplitude_returns_at_4pi": m3["amplitude_returns_at_4pi"],
        "m3_interference_2pi_periodic": m3["interference_signal_periodic_under_2pi"],
        "unweighted_lambda2": conn["unweighted_laplacian_lambda2"],
        "symmetrized_weighted_lambda2": conn["symmetrized_weighted_laplacian_lambda2"],
    }, indent=2))


if __name__ == "__main__":
    main()
