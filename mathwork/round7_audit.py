from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from wallfield_actual import RefactoredWallFieldSimulation
from run_notebook_verification import run_m1_sweep

S, L, M = 0, 1, 2
ROOT = Path(__file__).resolve().parent


def edge_gatings(phi_S: float, phi_L: float = 0.0, phi_M: float = 0.0) -> dict:
    phi = {S: phi_S, L: phi_L, M: phi_M}
    out = {}
    for j, i, name in [(S, L, "S->L"), (L, M, "L->M"), (L, S, "L->S"), (M, L, "M->L")]:
        d_phi = phi[j] - phi[i]
        out[name] = {
            "weight": 1.0,
            "d_phi": float(d_phi),
            "gating": float(np.cos(d_phi)),
        }
    return out


def run_at(sweep_phi: float, clip: bool = True) -> dict:
    sim = RefactoredWallFieldSimulation(num_nodes=3)
    sim.set_listen_weight(S, L, 1.0)
    sim.set_listen_weight(L, M, 1.0)
    sim.set_listen_weight(L, S, 1.0)
    sim.set_listen_weight(M, L, 1.0)
    sim.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
    sim.set_node_state(L, V_val=0.0, phi_val=0.0)
    sim.set_node_state(M, V_val=0.0, phi_val=0.0)
    if not clip:
        def tick(self, alpha=0.15):
            nV = np.copy(self.V)
            for i in range(self.num_nodes):
                ds = 0.0
                for j in range(self.num_nodes):
                    if self.weights[j, i] > 0:
                        ds += self.weights[j, i] * np.cos(self.phi[j] - self.phi[i]) * self.V[j]
                nV[i] = self.V[i] + alpha * (ds - np.sum(self.weights[i, :]) * self.V[i])
            self.V = nV
        sim.tickVField = tick.__get__(sim, RefactoredWallFieldSimulation)
    for _ in range(30):
        sim.V[S] = 1.0
        sim.tickVField(alpha=0.15)
    return {"phi_S": float(sweep_phi), "V": sim.V.tolist(), "phi": sim.phi.tolist()}


def linear_fixed_point_phi_pi() -> dict:
    """Closed-form linear (unclipped) fixed point of the 3-node M1 lattice at phi_S=pi.
    V[M](pi) = - w_SL * w_LM / (w_ML * w_LS)  ->  -1.0 at unit weights.
    Derived from  sum_j w[j,i] cos(phi[j]-phi[i]) V[j] = outdeg(i) V[i],  V[S]=1.
    """
    w_SL, w_LM, w_LS, w_ML = 1.0, 1.0, 1.0, 1.0
    # i=L: -w_SL*1 + w_ML*V[M] = (w_LS+w_LM)*V[L]
    # i=M:  w_LM*V[L]           = w_ML*V[M]  => V[L] = (w_ML/w_LM)*V[M]
    vm = -w_SL * w_LM / (w_ML * w_LS)
    return {"V_M_fixed_point": float(vm), "formula": "V[M](pi) = -w_SL*w_LM/(w_ML*w_LS)"}


def run_4node(sweep_phi: float) -> float:
    """4-node lattice: original 4 edges + independent clamped source C->M.
    S->L gating at phi_S=pi is cos(pi)=-1 (identical to M1); the extra C->M (+cos 0=+1)
    breaks the cancellation so V[M](pi) != 0.
    """
    N = 4
    C = 3
    sim = RefactoredWallFieldSimulation(num_nodes=N)
    sim.set_listen_weight(S, L, 1.0)
    sim.set_listen_weight(L, M, 1.0)
    sim.set_listen_weight(L, S, 1.0)
    sim.set_listen_weight(M, L, 1.0)
    sim.set_listen_weight(C, M, 1.0)
    sim.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
    sim.set_node_state(L, V_val=0.0, phi_val=0.0)
    sim.set_node_state(M, V_val=0.0, phi_val=0.0)
    sim.set_node_state(C, V_val=1.0, phi_val=0.0)
    for _ in range(30):
        sim.V[S] = 1.0
        sim.V[C] = 1.0
        sim.tickVField(alpha=0.15)
    return float(sim.V[M])


def drop_edge_variant(sweep_phi: float, drop_edge: tuple) -> float:
    sim = RefactoredWallFieldSimulation(num_nodes=3)
    base = [(S, L, 1.0), (L, M, 1.0), (L, S, 1.0), (M, L, 1.0)]
    for (j, i, w) in base:
        if (j, i) == drop_edge:
            continue
        sim.set_listen_weight(j, i, w)
    sim.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
    sim.set_node_state(L, V_val=0.0, phi_val=0.0)
    sim.set_node_state(M, V_val=0.0, phi_val=0.0)
    for _ in range(30):
        sim.V[S] = 1.0
        sim.tickVField(alpha=0.15)
    return float(sim.V[M])


def main() -> None:
    phi_sweeps = np.linspace(-np.pi, np.pi, 50)
    res = run_m1_sweep()

    idx_pi = int(np.argmin(np.abs(phi_sweeps - np.pi)))
    idx_0 = int(np.argmin(np.abs(phi_sweeps)))

    gatings_pi = edge_gatings(np.pi)
    fixed = linear_fixed_point_phi_pi()
    noclip = run_at(np.pi, clip=False)

    four_pi = run_4node(np.pi)
    four_0 = run_4node(phi_sweeps[idx_0])

    # 4-node leakage ratio across the full sweep
    four_full = np.array([run_4node(sp) for sp in phi_sweeps])
    four_max = float(np.max(four_full))
    four_min_edge = float(min(four_full[0], four_full[-1]))
    four_ratio = four_min_edge / four_max if four_max > 0 else 1.0

    drop_ml = drop_edge_variant(np.pi, (M, L))
    drop_ls = drop_edge_variant(np.pi, (L, S))

    out = {
        "m1_reproduction": {
            "max_V_M": res["max_transmitted_V_M"],
            "V_M_at_pi": res["V_M_results"][idx_pi],
            "V_M_at_neg_pi": res["V_M_results"][idx_negpi] if (idx_negpi := int(np.argmin(np.abs(phi_sweeps + np.pi)))) >= 0 else res["V_M_results"][0],
            "min_transmitted_V_M_at_pi": res["min_transmitted_V_M_at_pi"],
            "leakage_ratio": res["leakage_ratio"],
            "verdict": res["verdict"],
        },
        "edge_gatings_at_phi_pi": gatings_pi,
        "SL_gating_at_pi_is_negative_not_zero": bool(gatings_pi["S->L"]["gating"] < 0),
        "all_weights_nonzero": True,
        "linear_fixed_point_unclipped": fixed,
        "no_clip_trajectory_final": {"V_L": noclip["V"][L], "V_M": noclip["V"][M]},
        "clip_source": "wallfield_actual.py:66 np.clip(new_V, 0.0, 10.0)",
        "interpretation": "V[M](pi)=0 is the clipped image of V[M] = -1 (active NEGATIVE fixed point); NOT zero coupling.",
        "counterexample_4node": {
            "description": "3-node M1 + independent clamped source C->M (cos(0)=+1). S->L gating at pi still cos(pi)=-1.",
            "SL_gating_at_pi": float(np.cos(np.pi)),
            "V_M_at_0": four_0,
            "V_M_at_pi": four_pi,
            "leakage_ratio": four_ratio,
            "verdict": "FAIL" if four_ratio > 0.10 else "PASS",
        },
        "drop_edge_variants_at_pi": {
            "drop_M->L": drop_ml,
            "drop_L->S": drop_ls,
            "note": "Still 0 because negative S->L cascade drives L (and thus M) below zero; clip zeros them.",
        },
    }
    out_path = ROOT / "round7_audit_results.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"\nWROTE: {out_path}")


if __name__ == "__main__":
    main()
