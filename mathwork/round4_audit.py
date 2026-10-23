from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from wallfield_actual import (
    RefactoredWallFieldSimulation,
    M2WallFieldSimulation,
)
from run_notebook_verification import run_m1_sweep, run_m2_sweep

OUT = Path(__file__).resolve().parent


def compute_curve_stats(label, curve):
    arr = np.asarray(curve, dtype=float)
    var = float(np.var(arr))
    return {
        f"V_{label}": arr.tolist(),
        f"var({label})": var,
        f"max_{label}": float(np.max(arr)),
        f"min_{label}": float(np.min(arr)),
    }


def main():
    m1 = run_m1_sweep()
    m2 = run_m2_sweep()

    V_M = np.array(m1["V_M_results"])
    V_M_m2 = np.array(m2["V_M_m2_results"])

    var_M1 = float(np.var(V_M))
    var_M2 = float(np.var(V_M_m2))
    corr_M1_M2 = float(np.corrcoef(V_M, V_M_m2)[0, 1])
    mean_abs_diff = float(np.mean(np.abs(V_M - V_M_m2)))

    print("=== STEP 1: wallfield_actual M1 vs M2 ===")
    print(f"  var(M1) = {var_M1}")
    print(f"  var(M2) = {var_M2}")
    print(f"  var(M1) == var(M2): {np.isclose(var_M1, var_M2)}")
    print(f"  corr(M1, M2) = {corr_M1_M2}")
    print(f"  mean |M1 - M2| = {mean_abs_diff}")
    print(f"  M1 == M2 (pointwise): {bool(np.allclose(V_M, V_M_m2))}")

    A = V_M
    B = -A

    var_A = float(np.var(A))
    var_B = float(np.var(B))
    corr_A_B = float(np.corrcoef(A, B)[0, 1])

    print("\n=== STEP 2: B = -A (negation) ===")
    print(f"  A = V_M (M1 transmission curve)")
    print(f"  B = -A (negated)")
    print(f"  var(A) = {var_A}")
    print(f"  var(B) = {var_B}")
    print(f"  var(A) == var(B): {np.isclose(var_A, var_B)}")
    print(f"  corr(A, B) = {corr_A_B}")
    print(f"  variance threshold 0.01: A passes={var_A > 0.01}, B passes={var_B > 0.01}")

    phi_full = np.linspace(-np.pi, np.pi, 50)
    cos_curve = np.cos(phi_full) / 2.0 + 0.5
    flat_zero = np.zeros_like(cos_curve)

    var_cos = float(np.var(cos_curve))
    var_flat = float(np.var(flat_zero))

    print("\n=== STEP 3: Flat-zero vs cos curve ===")
    print(f"  Flat-zero curve: var = {var_flat}")
    print(f"    Passes variance>0.01: {var_flat > 0.01}  (trivially flat, no structure)")
    print(f"  Cos curve: var = {var_cos}")
    print(f"    Passes variance>0.01: {var_cos > 0.01}  (non-flat, passes threshold)")
    print(f"    corr(flat-zero, cos) = {float(np.corrcoef(flat_zero, cos_curve)[0,1])}")

    cell9_verdict = "PASS (M2 Junction Verified in Simulation)"
    cell9_rationale = "Variance in transmission amplitude demonstrates active phase gating across the flipped orientation boundary."
    print("\n=== STEP 4: Cell 9 verdict line ===")
    print(f"  Cell 9 verdict: {cell9_verdict}")
    print(f"  Cell 9 rationale: {cell9_rationale}")

    results = {
        "step1": {
            "description": "M1 and M2 sweeps from wallfield_actual.py via run_notebook_verification",
            "V_M": V_M.tolist(),
            "V_M_m2": V_M_m2.tolist(),
            "var_M1": var_M1,
            "var_M2": var_M2,
            "var_M1_equals_var_M2": bool(np.isclose(var_M1, var_M2)),
            "corr_M1_M2": corr_M1_M2,
            "mean_abs_diff_M1_M2": mean_abs_diff,
            "pointwise_identical": bool(np.allclose(V_M, V_M_m2)),
        },
        "step2": {
            "description": "B = -A negation: var(A) = var(B), corr(A,B) = -1.0",
            "var_A": var_A,
            "var_B": var_B,
            "var_equal": bool(np.isclose(var_A, var_B)),
            "corr_A_B": corr_A_B,
            "variance_threshold_0_01": {
                "A_passes": bool(var_A > 0.01),
                "B_passes": bool(var_B > 0.01),
                "note": "Both pass the >0.01 criterion despite corr(A,B)=-1.0 (opposite physical sign)",
            },
        },
        "step3": {
            "description": "Flat-zero curve (var=0) vs cos curve (var>0.01)",
            "flat_zero_variance": var_flat,
            "cos_curve_variance": var_cos,
            "flat_passes_threshold": bool(var_flat > 0.01),
            "cos_passes_threshold": bool(var_cos > 0.01),
        },
        "step4": {
            "cell_9_verdict_line": cell9_verdict,
            "cell_9_rationale": cell9_rationale,
            "cell_9_source": "ImaginaryUnit.ipynb cell 9 (M2 sweep, run_notebook_verification.py:91)",
            "cell_9_pass_criterion": "float(np.var(V_M_m2_results)) > 0.01",
        },
    }

    out_path = OUT / "round4_audit_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()
