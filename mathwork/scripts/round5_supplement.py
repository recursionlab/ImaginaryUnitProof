from __future__ import annotations
import json
import numpy as np
from wallfield_actual import M2WallFieldSimulation, RefactoredWallFieldSimulation

S, L, M = 0, 1, 2
PHI = np.linspace(-np.pi, np.pi, 50)
TICKS = 30
ALPHA = 0.15


def build(sim_cls, phi_L, phi_M, flip_edge=None):
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


def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1])


m1 = sweep(RefactoredWallFieldSimulation, 0.0, 0.0, None)
m2_inert = sweep(M2WallFieldSimulation, 0.0, 0.0, flip_edge=(L, M))
m2_corr_A = sweep(M2WallFieldSimulation, 1.0, 0.0, flip_edge=(L, M))

m2_truly_engaged_flip = sweep(M2WallFieldSimulation, 1.0, 0.5, flip_edge=(L, M))
m2_truly_engaged_noflip = sweep(M2WallFieldSimulation, 1.0, 0.5, flip_edge=None)

print("=" * 70)
print("SUPPLEMENT: truly engaging the flip (phi_L=1.0, phi_M=0.5)")
print("=" * 70)
print(f"corr(M1, m2_inert):           {corr(m1, m2_inert)}")
print(f"var(m2_inert):                {np.var(m2_inert)}")
print()
print(f"corr(M1, m2_corr_A phiL=1,phiM=0): {corr(m1, m2_corr_A)}")
print(f"var(m2_corr_A):                        {np.var(m2_corr_A)}")
print()
print(f"corr(M1, m2_truly_engaged_flip):     {corr(m1, m2_truly_engaged_flip)}")
print(f"var(m2_truly_engaged_flip):          {np.var(m2_truly_engaged_flip)}")
print()
print(f"flip-on vs flip-off (truly engaged):")
print(f"  corr: {corr(m2_truly_engaged_flip, m2_truly_engaged_noflip)}")
print(f"  mae:  {float(np.mean(np.abs(m2_truly_engaged_flip - m2_truly_engaged_noflip)))}")
print(f"  var_gap: {float(np.var(m2_truly_engaged_flip) - np.var(m2_truly_engaged_noflip))}")

for phi_L, phi_M in [(1.0, 0.0), (1.0, 0.5), (0.5, 0.5), (1.0, -0.5)]:
    d_flip = -phi_L - phi_M
    d_nonflip = phi_L - phi_M
    gf = np.cos(d_flip)
    gn = np.cos(d_nonflip)
    inert = np.isclose(gf, gn)
    print(f"phi_L={phi_L}, phi_M={phi_M}: d_flip={d_flip:.4f} d_nonflip={d_nonflip:.4f} "
          f"gating_flip={gf:.6f} gating_nonflip={gn:.6f} inert={inert}")
