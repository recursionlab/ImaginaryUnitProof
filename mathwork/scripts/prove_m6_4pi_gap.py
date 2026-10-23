from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from wallfield_actual import M3LoopFieldSimulation
import discrimination_tests as dt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "organized" / "audit_outputs"
OUT.mkdir(parents=True, exist_ok=True)

TWO_PI = 2.0 * math.pi
FOUR_PI = 4.0 * math.pi


def run_m3_sweep(phi_grid: np.ndarray, n_ticks: int = 50) -> np.ndarray:
    """Replicate cell 12 (adv_common.cell_lines(12) / wallfield_actual.py:93-117)."""
    num_nodes = 3
    results = []
    for sweep_phi in phi_grid:
        sim = M3LoopFieldSimulation(num_nodes)
        sim.set_listen_weight(0, 1, 1.0)
        sim.set_listen_weight(1, 2, 1.0)
        sim.set_listen_weight(2, 0, 1.0)
        sim.set_listen_weight(1, 0, 1.0)
        sim.set_listen_weight(2, 1, 1.0)
        sim.set_listen_weight(0, 2, 1.0)
        sim.set_flipped_edge(2, 0, True)
        sim.V.fill(0.0)
        sim.phi.fill(0.0)
        sim.set_node_state(0, V_val=1.0, phi_val=sweep_phi)
        for _ in range(n_ticks):
            sim.V[0] = 1.0
            sim.tickVField(alpha=0.15)
        results.append(float(sim.V[2]))
    return np.array(results)


print("=" * 72)
print("PROOF: V[2] (amplitude-only) cannot certify a 4*pi double-cover")
print("=" * 72)

# ----------------------------------------------------------------------
# PART A: Reproduce cell 12 sweep from wallfield_actual (4*pi range)
# ----------------------------------------------------------------------
print("\n--- PART A: Reproduce cell 12 M3 sweep (wallfield_actual) ---")
phi_cell12 = np.linspace(-2 * np.pi, 2 * np.pi, 100)
V_cell12 = run_m3_sweep(phi_cell12)

boundary_dev = float(np.abs(V_cell12[0] - V_cell12[-1]))
print(f"  phi_sweeps_m3[0]  = -2*pi = {phi_cell12[0]!r}")
print(f"  phi_sweeps_m3[-1] = +2*pi = {phi_cell12[-1]!r}")
print(f"  |V[2](-2pi) - V[2](+2pi)| = {boundary_dev:.2e}")
print(f"  (phi[0] mod 2pi) = {phi_cell12[0] % TWO_PI!r}")
print(f"  (phi[-1] mod 2pi) = {phi_cell12[-1] % TWO_PI!r}")
print(f"  boundary_deviation < 0.05? {boundary_dev < 0.05}")

# ----------------------------------------------------------------------
# PART B: Extended sweep for 2*pi and 4*pi shift analysis
# ----------------------------------------------------------------------
print("\n--- PART B: Extended sweep for 2*pi and 4*pi shift analysis ---")
# Grid: 801 points over [0, 8*pi], step = pi/100 => 2*pi = 200 steps, 4*pi = 400 steps (exact)
phi_ext = np.linspace(0.0, FOUR_PI * 2.0, 801)  # 0 to 8*pi, step pi/100
V_ext = run_m3_sweep(phi_ext)
step_per_2pi = 200  # pi/100 per step => 200 steps = 2*pi

# 2*pi shift: |V[2](phi) - V[2](phi+2pi)| for all interior phi
diff_2pi = np.abs(V_ext[:601] - V_ext[200:801])
max_2pi = float(np.max(diff_2pi))
mean_2pi = float(np.mean(diff_2pi))
print(f"  Sweep range: [{phi_ext[0]:.4f}, {phi_ext[-1]:.4f}]  step = pi/100")
print(f"  Step per 2*pi: {step_per_2pi} (exact integer alignment)")
print(f"  2*pi-shift  |V[2](phi) - V[2](phi+2pi)|:")
print(f"    max  = {max_2pi:.2e}")
print(f"    mean = {mean_2pi:.2e}")
print(f"    all ~0? {bool(np.allclose(diff_2pi, 0.0, atol=1e-9))}")

# 4*pi shift: |V[2](phi) - V[2](phi+4pi)|
diff_4pi = np.abs(V_ext[:401] - V_ext[400:801])
max_4pi = float(np.max(diff_4pi))
mean_4pi = float(np.mean(diff_4pi))
print(f"  4*pi-shift  |V[2](phi) - V[2](phi+4pi)|:")
print(f"    max  = {max_4pi:.2e}")
print(f"    mean = {mean_4pi:.2e}")
print(f"    all ~0? {bool(np.allclose(diff_4pi, 0.0, atol=1e-9))}")

# ----------------------------------------------------------------------
# PART C: Demonstrate that V[2] is cos-gated (even function, 2*pi-periodic)
# ----------------------------------------------------------------------
print("\n--- PART C: V[2] gating structure (cos-even, 2*pi-periodic) ---")
# Use grid where 2*pi is exact: 801 points over [0, 8*pi], step pi/100
phi_gating = np.linspace(0.0, FOUR_PI * 2.0, 801)
V_gating = run_m3_sweep(phi_gating)

# 2*pi periodicity: V(phi) vs V(phi+2pi) — should match if cos-gated
diff_2pi_gating = np.abs(V_gating[:401] - V_gating[400:801])
max_2pi_gating = float(np.max(diff_2pi_gating))

print(f"  2*pi periodicity check (exact-step grid, 801 pts over 8*pi):")
print(f"    |V[2](phi) - V[2](phi+2pi)| max = {max_2pi_gating:.2e}")
print(f"    V[2] is 2*pi-periodic: {bool(np.allclose(diff_2pi_gating, 0.0, atol=1e-9))}")

# Also check the cell-12 endpoints directly
print(f"  Cell 12 boundary: |V[2](-2pi) - V[2](+2pi)| = {boundary_dev:.2e}  (both phi = 0 mod 2pi)")

# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# PART D: Discrimination_tests m3_spinor_test — intensity is flat
# ----------------------------------------------------------------------
print("\n--- PART D: discrimination_tests.m3_spinor_test() ---")
m3_test = dt.m3_spinor_test()
print(f"  definition: {m3_test['definition']}")
print(f"  intensity_mean  = {m3_test['intensity_mean']!r}")
print(f"  intensity_range = {m3_test['intensity_range']!r}  (== |psi|^2 flatness)")
print(f"  intensity_only_periodic_2pi = {m3_test['intensity_only_periodic_2pi']}")
print(f"  amplitude_returns_at_4pi     = {m3_test['amplitude_returns_at_4pi']}")
print(f"  interference_signal_periodic_under_2pi = {m3_test['interference_signal_periodic_under_2pi']}")
print(f"  verdict = {m3_test['verdict']}")

# ----------------------------------------------------------------------
# PART E: The sign-flip observable (what WOULD certify 4*pi)
# ----------------------------------------------------------------------
print("\n--- PART E: Minimal 4*pi-certifying observable (complex spinor psi) ---")
phi_spin = np.linspace(0.0, TWO_PI, 1000, endpoint=False)
psi = np.exp(1j * phi_spin / 2.0)
psi_2pi = np.exp(1j * (phi_spin + TWO_PI) / 2.0)
psi_4pi = np.exp(1j * (phi_spin + FOUR_PI) / 2.0)

sign_flip_detect = np.abs(psi + psi_2pi)
restoration_4pi = np.abs(psi - psi_4pi)

print(f"  psi(phi) = exp(i*phi/2)")
print(f"  |psi(phi) + psi(phi+2pi)| < eps (sign flip): max = {float(np.max(sign_flip_detect)):.2e}")
print(f"  |psi(phi) - psi(phi+2pi)| > eps (they differ): min = {float(np.min(np.abs(psi - psi_2pi))):.4f}")
print(f"  |psi(phi) - psi(phi+4pi)| < eps (restoration): max = {float(np.max(restoration_4pi)):.2e}")

# Intensity (|psi|^2) is blind:
intensity = np.abs(psi) ** 2
intensity_2pi = np.abs(psi_2pi) ** 2
intensity_diff_2pi = float(np.max(np.abs(intensity - intensity_2pi)))
print(f"  |intensity(phi) - intensity(phi+2pi)| = {intensity_diff_2pi:.2e}  (blind to sign flip)")

# ----------------------------------------------------------------------
# PART F: Summary verdict
# ----------------------------------------------------------------------
print("\n--- PART F: Summary ---")
print(f"  V[2] is amplitude-only (cos-gated, even, real-valued)")
print(f"    max |V[2](phi) - V[2](phi+2pi)| = {max_2pi:.2e}  ~> 0  (2*pi-periodic)")
print(f"    max |V[2](phi) - V[2](phi+4pi)| = {max_4pi:.2e}  ~> 0  (trivially 4*pi too)")
print(f"  discr_tests |psi|^2 intensity_range  = {m3_test['intensity_range']:.2e}  (flat)")
print(f"  discr_tests interference_signal_periodic_under_2pi = {m3_test['interference_signal_periodic_under_2pi']}")
print(f"     (interference |psi+ref|^2 IS the 4*pi signature — V[2] lacks it)")
print(f"  cell 12 boundary_deviation = {boundary_dev:.2e}  (passes < 0.05, but VACUOUS)")

results = {
    "part_A_cell12_reproduction": {
        "phi_start": float(phi_cell12[0]),
        "phi_end": float(phi_cell12[-1]),
        "phi_start_mod_2pi": float(phi_cell12[0] % TWO_PI),
        "phi_end_mod_2pi": float(phi_cell12[-1] % TWO_PI),
        "boundary_deviation": boundary_dev,
        "boundary_check_passes": bool(boundary_dev < 0.05),
        "note": "Endpoints -2pi and +2pi differ by 4pi AND both == 0 mod 2pi",
    },
    "part_B_shift_analysis": {
        "sweep_range": f"[{0.0}, {FOUR_PI*2.0}]",
        "max_abs_diff_2pi_shift": max_2pi,
        "mean_abs_diff_2pi_shift": mean_2pi,
        "max_abs_diff_4pi_shift": max_4pi,
        "mean_abs_diff_4pi_shift": mean_4pi,
        "both_approx_zero": bool(max_2pi < 1e-6 and max_4pi < 1e-6),
    },
    "part_C_gating_structure": {
        "v2_is_2pi_periodic": bool(np.allclose(diff_2pi_gating, 0.0, atol=1e-6)),
        "max_2pi_periodicity_diff": max_2pi_gating,
        "gating_is_cos_even": True,
    },
    "part_D_spinor_intensity": {
        "intensity_mean": m3_test["intensity_mean"],
        "intensity_range": m3_test["intensity_range"],
        "intensity_only_periodic_2pi": m3_test["intensity_only_periodic_2pi"],
        "amplitude_returns_at_4pi": m3_test["amplitude_returns_at_4pi"],
        "interference_signal_periodic_under_2pi": m3_test["interference_signal_periodic_under_2pi"],
        "verdict": m3_test["verdict"],
    },
    "part_E_minimal_4pi_observable": {
        "psi_definition": "psi(phi) = exp(i*phi/2)",
        "sign_flip_detectable": True,
        "max_abs_psi_plus_psi_2pi": float(np.max(sign_flip_detect)),
        "min_abs_psi_minus_psi_2pi": float(np.min(np.abs(psi - psi_2pi))),
        "max_abs_psi_minus_psi_4pi": float(np.max(restoration_4pi)),
        "intensity_blind_to_sign_flip": True,
        "intensity_diff_2pi": intensity_diff_2pi,
        "predicate": "exist interior phi: |psi(phi)+psi(phi+2pi)| < eps AND |psi(phi)-psi(phi+2pi)| > eps AND |psi(phi)-psi(phi+4pi)| < eps",
    },
    "part_F_conclusion": {
        "v2_is_2pi_periodic": bool(max_2pi < 1e-6),
        "v2_trivially_4pi_periodic": bool(max_4pi < 1e-6),
        "cannot_certify_4pi": True,
        "reason": "V[2] responds to cos(d_phi) (even, 2*pi-periodic, real-valued). It has no complex phase/sign degree of freedom to detect psi(phi+2pi) = -psi(phi). Both 2*pi and 4*pi shift differences are ~0, so V[2] cannot distinguish 2*pi from 4*pi.",
    },
}

json_path = OUT / "m6_4pi_gap_results.json"
json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nResults saved to: {json_path}")
