from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np

from candidate_formulas import encode_bit
from gate_contract_audit import confusion, NOISE_SIGMAS, SEEDS, TRIALS_PER_ROW_PER_SEED
from wallfield_actual import (
    M2WallFieldSimulation,
    M3LoopFieldSimulation,
    RefactoredWallFieldSimulation,
    simulate_noisy_and_gate,
    simulate_noisy_not_gate,
)

OUT = Path(__file__).resolve().parent
GATE_DECISION_THRESHOLD = 0.5


def _amps_to_bits(amps):
    return (np.asarray(amps, dtype=float) >= GATE_DECISION_THRESHOLD).astype(np.int8)


def run_m1_sweep():
    num_nodes = 3
    S, L, M = 0, 1, 2
    phi_sweeps = np.linspace(-np.pi, np.pi, 50)
    V_M_results = []
    for sweep_phi in phi_sweeps:
        sim = RefactoredWallFieldSimulation(num_nodes)
        sim.set_listen_weight(S, L, 1.0)
        sim.set_listen_weight(L, M, 1.0)
        sim.set_listen_weight(L, S, 1.0)
        sim.set_listen_weight(M, L, 1.0)
        sim.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
        sim.set_node_state(L, V_val=0.0, phi_val=0.0)
        sim.set_node_state(M, V_val=0.0, phi_val=0.0)
        for _ in range(30):
            sim.V[S] = 1.0
            sim.tickVField(alpha=0.15)
        V_M_results.append(sim.V[M])
    V_M_results = np.array(V_M_results)
    max_V_M = float(np.max(V_M_results))
    min_V_M_at_edges = float(min(V_M_results[0], V_M_results[-1]))
    ratio = float(min_V_M_at_edges / max_V_M if max_V_M > 0 else 1.0)
    lambda_2 = float(sim.get_algebraic_connectivity())
    return {
        "phi_sweeps": phi_sweeps.tolist(),
        "V_M_results": V_M_results.tolist(),
        "max_transmitted_V_M": max_V_M,
        "min_transmitted_V_M_at_pi": min_V_M_at_edges,
        "leakage_ratio": ratio,
        "algebraic_connectivity_lambda_2": lambda_2,
        "kill_criterion_threshold": 0.10,
        "verdict": "FAIL (Conjecture Killed)" if ratio > 0.10 else "PASS (Conjecture Validated in Simulation)",
    }


def run_m2_sweep():
    num_nodes = 3
    S, L, M = 0, 1, 2
    phi_sweeps = np.linspace(-np.pi, np.pi, 50)
    V_M_m2_results = []
    for sweep_phi in phi_sweeps:
        sim_m2 = M2WallFieldSimulation(num_nodes)
        sim_m2.set_listen_weight(S, L, 1.0)
        sim_m2.set_listen_weight(L, M, 1.0)
        sim_m2.set_listen_weight(L, S, 1.0)
        sim_m2.set_listen_weight(M, L, 1.0)
        sim_m2.set_flipped_edge(L, M, True)
        sim_m2.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
        sim_m2.set_node_state(L, V_val=0.0, phi_val=sweep_phi)
        sim_m2.set_node_state(M, V_val=0.0, phi_val=0.0)
        for _ in range(30):
            sim_m2.V[S] = 1.0
            sim_m2.tickVField(alpha=0.15)
        V_M_m2_results.append(sim_m2.V[M])
    V_M_m2_results = np.array(V_M_m2_results)
    return {
        "phi_sweeps": phi_sweeps.tolist(),
        "V_M_m2_results": V_M_m2_results.tolist(),
        "max_transmitted_V_M_m2": float(np.max(V_M_m2_results)),
        "min_transmitted_V_M_m2_at_edges": float(min(V_M_m2_results[0], V_M_m2_results[-1])),
        "profile_variance": float(np.var(V_M_m2_results)),
        "verdict": "PASS (M2 Junction Verified in Simulation)" if float(np.var(V_M_m2_results)) > 0.01 else "FAIL (No observable orientation gating)",
    }


def run_m3_sweep():
    num_nodes = 3
    sim_m3 = M3LoopFieldSimulation(num_nodes)
    sim_m3.set_listen_weight(0, 1, 1.0)
    sim_m3.set_listen_weight(1, 2, 1.0)
    sim_m3.set_listen_weight(2, 0, 1.0)
    sim_m3.set_listen_weight(1, 0, 1.0)
    sim_m3.set_listen_weight(2, 1, 1.0)
    sim_m3.set_listen_weight(0, 2, 1.0)
    sim_m3.set_flipped_edge(2, 0, True)
    phi_sweeps_m3 = np.linspace(-2 * np.pi, 2 * np.pi, 100)
    V_target_results = []
    for sweep_phi in phi_sweeps_m3:
        sim_m3.V.fill(0.0)
        sim_m3.phi.fill(0.0)
        sim_m3.set_node_state(0, V_val=1.0, phi_val=sweep_phi)
        for _ in range(50):
            sim_m3.V[0] = 1.0
            sim_m3.tickVField(alpha=0.15)
        V_target_results.append(sim_m3.V[2])
    V_target_results = np.array(V_target_results)
    boundary_dev = float(np.abs(V_target_results[0] - V_target_results[-1]))
    conforms = bool(boundary_dev < 0.05)
    return {
        "phi_sweeps_m3": phi_sweeps_m3.tolist(),
        "V_target_results": V_target_results.tolist(),
        "max_amplitude": float(np.max(V_target_results)),
        "min_amplitude": float(np.min(V_target_results)),
        "periodicity_conforms_to_4pi": conforms,
        "boundary_deviation": boundary_dev,
        "verdict": "PASS (M3 4-pi Double-Cover Verified)" if conforms else "FAIL (Loop boundary mismatch)",
        "rationale": "Boundary deviation |V[start]-V[end]| < 0.05. Intensity-only |psi|^2 cannot show sign flip (see discrimination_tests.py).",
    }


def run_gate_contract_with_actual_candidates():
    """Run the ACTUAL notebook gate functions (cell 27) through the frozen per-row contract.

    Decision rule: output amplitude >= 0.5 -> HIGH (bit 1). Phase encoding follows the
    frozen harness: 0 -> 0 rad, 1 -> pi rad. The notebook functions inject their own
    Gaussian noise at noise_std=sigma (per the notebook's own model); seeds are fixed.
    """
    not_by_sigma, and_by_sigma = [], []
    for sigma in NOISE_SIGMAS:
        not_rows = {}
        for input_bit in (0, 1):
            truth = 1 - input_bit
            preds = []
            for seed in SEEDS:
                rng = np.random.default_rng(seed + int(round(sigma * 10000)) + input_bit)
                reps = [simulate_noisy_not_gate(float(encode_bit(input_bit)), float(sigma), rng=rng) for _ in range(TRIALS_PER_ROW_PER_SEED)]
                preds.append(_amps_to_bits(reps))
            pred = np.concatenate(preds)
            actual = np.full(pred.size, truth, dtype=np.int8)
            not_rows[str(input_bit)] = {
                "n": int(pred.size),
                "truth_output": int(truth),
                "candidate_accuracy": float(np.mean(pred == actual)),
                "confusion": confusion(actual, pred),
            }
        not_by_sigma.append({"sigma_rad": float(sigma), "per_input": not_rows})

        and_rows = {}
        for a_bit, b_bit in ((0, 0), (0, 1), (1, 0), (1, 1)):
            truth = a_bit & b_bit
            preds = []
            for seed in SEEDS:
                rng = np.random.default_rng(seed + 1000000 + int(round(sigma * 10000)) + a_bit * 101 + b_bit * 313)
                reps = [simulate_noisy_and_gate(float(encode_bit(a_bit)), float(encode_bit(b_bit)), float(sigma), rng=rng) for _ in range(TRIALS_PER_ROW_PER_SEED)]
                preds.append(_amps_to_bits(reps))
            pred = np.concatenate(preds)
            actual = np.full(pred.size, truth, dtype=np.int8)
            and_rows[f"{a_bit}{b_bit}"] = {
                "n": int(pred.size),
                "truth_output": int(truth),
                "candidate_accuracy": float(np.mean(pred == actual)),
                "confusion": confusion(actual, pred),
            }
        and_by_sigma.append({"sigma_rad": float(sigma), "truth_table_rows": and_rows, "row_order": ["00", "01", "10", "11"]})
    return {"NOT": not_by_sigma, "AND": and_by_sigma, "decision_threshold": GATE_DECISION_THRESHOLD}


def _make_plot(m1, m2, m3) -> str:
    phi = np.array(m1["phi_sweeps"])
    v1 = np.array(m1["V_M_results"])
    v2 = np.array(m2["V_M_m2_results"])
    phi3 = np.array(m3["phi_sweeps_m3"])
    v3 = np.array(m3["V_target_results"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    axes[0].plot(phi, v1, color="#00E5FF", linewidth=2.5, label="M1 transmission V[M]")
    axes[0].plot(phi, v2, color="#FF9100", linewidth=2.5, linestyle="--", label="M2 (flipped edge)")
    axes[0].set_title(f"M1 vs M2: identical (corr={np.corrcoef(v1,v2)[0,1]:.4f})")
    axes[0].set_xlabel("Source phase phi_S (rad)"); axes[0].set_ylabel("V[M]")
    axes[0].grid(True, alpha=.25); axes[0].legend(fontsize=8)
    axes[1].plot(phi3, v3, color="#D500F9", linewidth=2.5)
    axes[1].axvline(-np.pi, color="gray", linestyle=":", alpha=.6); axes[1].axvline(np.pi, color="gray", linestyle=":", alpha=.6)
    axes[1].set_title(f"M3 loop: start/end same phase (dev={m3['boundary_deviation']:.4f})")
    axes[1].set_xlabel("Source phase phi_S (rad)"); axes[1].grid(True, alpha=.25)
    fig.suptitle("M1==M2 (null flip effect); M3 boundary check is vacuous (start==end mod 2 pi)")
    fig.tight_layout()
    path = OUT / "notebook_m1_m2_m3_verification.png"
    fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)
    return path


def main() -> None:
    m1 = run_m1_sweep()
    m2 = run_m2_sweep()
    m3 = run_m3_sweep()
    plot_path = _make_plot(m1, m2, m3)
    gates = run_gate_contract_with_actual_candidates()

    z0 = gates["NOT"][0]["per_input"]
    a0 = gates["AND"][0]["truth_table_rows"]
    not_pass = all(z0[b]["candidate_accuracy"] >= 0.99995 for b in ("0", "1"))
    and_pass = all(a0[r]["candidate_accuracy"] >= 0.99995 for r in a0)
    result = {
        "title": "Verification: ACTUAL notebook code (wallfield_actual.py verbatim + cell-27 gates) run through the frozen contract",
        "status": "ACTUAL_NOTEBOOK_IMPLEMENTATION_VERIFIED_NOT_TRANSCRIBED_APPROXIMATION",
        "gate_decision_threshold_amplitude": GATE_DECISION_THRESHOLD,
        "m1_sweep_verdict": m1,
        "m2_sweep_verdict": m2,
        "m3_sweep_verdict": m3,
        "verification_plot": str(plot_path),
        "smuggling_check": {
            "m1_max_transmitted_V_M": m1["max_transmitted_V_M"],
            "m2_max_transmitted_V_M_m2": m2["max_transmitted_V_M_m2"],
            "identical_max_transmission": bool(np.isclose(m1["max_transmitted_V_M"], m2["max_transmitted_V_M_m2"])),
            "m2_profile_variance": m2["profile_variance"],
        },
        "actual_not_candidate": {
            "zero_noise_input_0": z0["0"],
            "zero_noise_input_1": z0["1"],
            "verdict": "PASS" if not_pass else "FAIL",
            "basis": "Candidate outputs HIGH (amplitude ~1) for BOTH inputs; the input-1 row is always wrong — no inversion.",
        },
        "actual_and_candidate": {
            "zero_noise_rows": {r: a0[r] for r in ["00", "01", "10", "11"]},
            "verdict": "PASS" if and_pass else "FAIL",
            "basis": "Candidate amplitude = |cos((phi_a-phi_b)/2)| => XNOR truth table; row 00 (truth=0) always predicted HIGH — wrong for AND.",
        },
    }
    json_path = OUT / "notebook_verification_results.json"
    result["corrected_port_note"] = (
        "M2/M3 under the real notebook model are inert/vacuous because cos(d_phi) is even "
        "and V is a real amplitude. The complex-phasor port (wallfield_corrected.py, "
        "run_corrected_port.py) shows M2 flip engages (corr drops to ~0.6 and profile changes) "
        "ONLY when the flipped edge's target node carries nonzero phase; M3 double-cover "
        "requires a spinor sign test on the complex psi, not the real |V| amplitude. "
        "See corrected_port_results.json."
    )
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "results": str(json_path),
        "m1_max_V_M": m1["max_transmitted_V_M"],
        "m1_leakage_ratio": m1["leakage_ratio"],
        "m1_lambda_2": m1["algebraic_connectivity_lambda_2"],
        "m2_max_V_M": m2["max_transmitted_V_M_m2"],
        "m2_profile_variance": m2["profile_variance"],
        "m3_periodicity_conforms_4pi": m3["periodicity_conforms_to_4pi"],
        "m3_boundary_deviation": m3["boundary_deviation"],
        "smuggling_identical_max_transmission": result["smuggling_check"]["identical_max_transmission"],
        "actual_NOT_input0_acc": z0["0"]["candidate_accuracy"],
        "actual_NOT_input1_acc": z0["1"]["candidate_accuracy"],
        "actual_AND_row00_acc": a0["00"]["candidate_accuracy"],
        "actual_NOT_verdict": "PASS" if not_pass else "FAIL",
        "actual_AND_verdict": "PASS" if and_pass else "FAIL",
    }, indent=2))


if __name__ == "__main__":
    main()
