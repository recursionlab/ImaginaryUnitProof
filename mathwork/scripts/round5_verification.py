from __future__ import annotations
import json
import numpy as np
from wallfield_actual import (
    M2WallFieldSimulation,
    RefactoredWallFieldSimulation,
)

S, L, M = 0, 1, 2
PHI = np.linspace(-np.pi, np.pi, 50)
TICKS = 30
ALPHA = 0.15


def build(sim_cls, phi_L, phi_M, flip_edge=None):
    """Faithful to cell 9 weights + states; optional corrected phi/flip."""
    sim = sim_cls(num_nodes=3)
    sim.set_listen_weight(S, L, 1.0)
    sim.set_listen_weight(L, M, 1.0)
    sim.set_listen_weight(L, S, 1.0)
    sim.set_listen_weight(M, L, 1.0)
    if flip_edge is not None:
        sim.set_flipped_edge(*flip_edge, True)
    sim.set_node_state(S, V_val=1.0, phi_val=0.0)
    sim.set_node_state(L, V_val=0.0, phi_val=phi_L)
    sim.set_node_state(M, V_val=0.0, phi_val=phi_M)
    return sim


def sweep(sim_cls, phi_L, phi_M, flip_edge=None):
    out = []
    for sp in PHI:
        sim = build(sim_cls, phi_L, phi_M, flip_edge)
        sim.set_node_state(S, V_val=1.0, phi_val=sp)
        for _ in range(TICKS):
            sim.V[S] = 1.0
            sim.tickVField(alpha=ALPHA)
        out.append(sim.V[M])
    return np.array(out)


def stats(name, v):
    return {
        "name": name,
        "max": float(np.max(v)),
        "min": float(np.min(v)),
        "variance": float(np.var(v)),
    }


# 1. M1 baseline (no flip) - cell 4 layout, phi_L=phi_M=0
m1 = sweep(RefactoredWallFieldSimulation, phi_L=0.0, phi_M=0.0, flip_edge=None)

# 2. M2 INERT - cell 9 verbatim: flip L->M, phi_L=0, phi_M=0
m2_inert = sweep(M2WallFieldSimulation, phi_L=0.0, phi_M=0.0, flip_edge=(L, M))

# 3. M2 CORRECTED-A (task option A): phi_L=1.0, phi_M=0 still, flip L->M
m2_corr_A = sweep(M2WallFieldSimulation, phi_L=1.0, phi_M=0.0, flip_edge=(L, M))

# 4. M2 CORRECTED-B (task option B): flip edge whose source is S -> flip S->L, phi_L=0, phi_M=0
m2_corr_B = sweep(M2WallFieldSimulation, phi_L=0.0, phi_M=0.0, flip_edge=(S, L))

# 5. M2 TRULY-ENGAGED control: flip L->M with phi_L=1.0 AND phi_M=0.5 -> flip differs from nonflip
m2_engaged_flip = sweep(M2WallFieldSimulation, phi_L=1.0, phi_M=0.5, flip_edge=(L, M))
m2_noengaged_noflip = sweep(M2WallFieldSimulation, phi_L=1.0, phi_M=0.5, flip_edge=None)


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


report = {
    "note": "wallfield_actual.py M2WallFieldSimulation; cell 9 setup preserved except the phi/flip variation under test.",
    "layout": {"S": 0, "L": 1, "M": 2, "ticks": TICKS, "alpha": ALPHA, "n_points": 50},
    "baseline_0_0946_reproduced": float(np.var(m2_inert)),
    "experiments": [],
}


def add(variant, v, cmp_base, label):
    report["experiments"].append({
        "variant": variant,
        "label": label,
        "stats": stats(variant, v),
        "corr_with_base": (None if cmp_base is None else corr(cmp_base, v)),
        "mae_with_base": (None if cmp_base is None else mae(cmp_base, v)),
    })


add("M1_baseline_noFlip", m1, None, "cell-4 layout; no flip; phi_L=phi_M=0")
add("M2_INERT_cell9", m2_inert, m1, "cell 9 verbatim: flip L->M, phi_L=0, phi_M=0")
add("M2_CORRECTED_phiL1_phiM0", m2_corr_A, m1, "task option A: phi_L=1.0, phi_M=0, flip L->M")
add("M2_CORRECTED_flipS_L", m2_corr_B, m1, "task option B: flip S->L, phi_L=0, phi_M=0")
add("M2_ENGAGED_phiL1_phiM05", m2_engaged_flip, m1, "control: phi_L=1.0, phi_M=0.5, flip L->M (flip ON)")
add("M2_ENGAGED_noflip", m2_noengaged_noflip, m1, "control: phi_L=1.0, phi_M=0.5, NO flip")

report["engagement_check"] = {
    "description": "Does the flip operator actually engage (differ from non-flip) at phi_L=1.0, phi_M=0.5?",
    "flip_on_vs_off_corr": corr(m2_engaged_flip, m2_noengaged_noflip),
    "flip_on_vs_off_mae": mae(m2_engaged_flip, m2_noengaged_noflip),
    "flip_on_vs_off_variance_gap": float(np.var(m2_engaged_flip) - np.var(m2_noengaged_noflip)),
}

# cos-evenness proof for the corrected-A case
fl = 1.0
fm = 0.0
d_flip = -fl - fm
d_nonflip = fl - fm
report["cos_evenness_proof_optionA"] = {
    "phi_L": fl, "phi_M": fm,
    "d_phi_flip_minus_phiL_minus_phiM": d_flip,
    "d_phi_nonflip_phiL_minus_phiM": d_nonflip,
    "gating_flip": float(np.cos(d_flip)),
    "gating_nonflip": float(np.cos(d_nonflip)),
    "gating_identical": bool(np.isclose(np.cos(d_flip), np.cos(d_nonflip))),
}

with open("round5_experiment.json", "w") as f:
    json.dump(report, f, indent=2)

# Console summary
print("=" * 70)
print("M2 SELF-AUDIT: flip engagement under cell-9 layout variations")
print("=" * 70)
print("Reproduced M2 inert profile_variance (cell 9):", report["baseline_0_0946_reproduced"])
print()
hdr = "%-42s %18s %12s %10s %12s" % ("variant", "max(V[M])", "variance", "corr(M1)", "MAE(M1)")
print(hdr)
print("-" * len(hdr))
for e in report["experiments"]:
    s = e["stats"]
    cw = e["corr_with_base"] if e["corr_with_base"] is not None else float("nan")
    mw = e["mae_with_base"] if e["mae_with_base"] is not None else float("nan")
    print("%-42s %18.10f %12.8f %10.6f %12.8f" % (
        e["variant"], s["max"], s["variance"], cw, mw))
print()
ec = report["engagement_check"]
print("ENGAGEMENT (phi_L=1.0, phi_M=0.5): flip_on vs flip_off -> corr=%.6f  MAE=%.6f  var_gap=%.8f" % (
    ec["flip_on_vs_off_corr"], ec["flip_on_vs_off_mae"], ec["flip_on_vs_off_variance_gap"]))
cp = report["cos_evenness_proof_optionA"]
print("COS-EVEN PROOF option A (phi_L=1, phi_M=0): gating_flip=%.10f gating_nonflip=%.10f identical=%s" % (
    cp["gating_flip"], cp["gating_nonflip"], cp["gating_identical"]))

key = {
    "m2_inert_variance": stats("M2_INERT_cell9", m2_inert)["variance"],
    "m2_inert_corr_with_m1": corr(m1, m2_inert),
    "m2_corrA_corr_with_m1": corr(m1, m2_corr_A),
    "m2_corrA_variance": stats("M2_CORRECTED_phiL1_phiM0", m2_corr_A)["variance"],
    "m2_corrB_corr_with_m1": corr(m1, m2_corr_B),
    "m2_corrB_variance": stats("M2_CORRECTED_flipS_L", m2_corr_B)["variance"],
    "engagement_flip_on_vs_off_corr": ec["flip_on_vs_off_corr"],
    "engagement_flip_on_vs_off_mae": ec["flip_on_vs_off_mae"],
}
print()
print("KEY:", json.dumps(key, indent=2))
