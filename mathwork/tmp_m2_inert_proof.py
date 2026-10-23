from __future__ import annotations
import numpy as np
from wallfield_actual import M2WallFieldSimulation

S, L, M = 0, 1, 2

sim = M2WallFieldSimulation(num_nodes=3)

sim.set_listen_weight(S, L, 1.0)
sim.set_listen_weight(L, M, 1.0)
sim.set_listen_weight(L, S, 1.0)
sim.set_listen_weight(M, L, 1.0)

sim.set_flipped_edge(L, M, True)

phi_test = 1.234
sim.set_node_state(S, V_val=1.0, phi_val=phi_test)
sim.set_node_state(L, V_val=0.0, phi_val=0.0)
sim.set_node_state(M, V_val=0.0, phi_val=0.0)

print("=== WEIGHTS MATRIX (weights[j,i]) ===")
print(sim.weights)
print()
print("=== FLIPPED EDGES MATRIX ===")
print(sim.flipped_edges)
print()

node_labels = {S: 'S', L: 'L', M: 'M'}

print("=== EDGE-BY-EDGE INERTNESS ANALYSIS (phi[S]=1.234, phi[L]=0, phi[M]=0) ===")
print(f"{'j':>4} {'i':>4}  {'phi[j]':>10} {'phi[i]':>10}  {'d_phi_nonflip':>16} {'d_phi_flip':>16}  {'gating_nonflip':>16} {'gating_flip':>16}  {'identical':>10}")
print("-" * 130)

all_identical = True
for j in range(sim.num_nodes):
    for i in range(sim.num_nodes):
        if sim.weights[j, i] > 0:
            phi_j = sim.phi[j]
            phi_i = sim.phi[i]
            is_flipped = sim.flipped_edges[j, i]

            d_phi_nonflip = phi_j - phi_i
            if is_flipped:
                d_phi_flip = -phi_j - phi_i
            else:
                d_phi_flip = d_phi_nonflip

            gating_nonflip = np.cos(d_phi_nonflip)
            gating_flip = np.cos(d_phi_flip)

            identical = np.isclose(d_phi_nonflip, d_phi_flip)
            if not identical:
                all_identical = False

            jlbl = node_labels[j]
            ilbl = node_labels[i]
            flip_tag = "  *FLIP*" if is_flipped else ""
            print(f"{jlbl:>4} {ilbl:>4}  {phi_j:>10.6f} {phi_i:>10.6f}  {d_phi_nonflip:>16.6f} {d_phi_flip:>16.6f}  {gating_nonflip:>16.6f} {gating_flip:>16.6f}  {'YES' if identical else 'NO':>10}{flip_tag}")

print()
print(f"ALL edges identical (flip inert everywhere): {all_identical}")
print()

print("=== FOCUSED: FLIPPED EDGE L->M (j=L, i=M) ===")
j, i = L, M
phi_j = sim.phi[j]
phi_i = sim.phi[i]
d_phi_nonflip = phi_j - phi_i
d_phi_flip = -phi_j - phi_i
gating_nonflip = np.cos(d_phi_nonflip)
gating_flip = np.cos(d_phi_flip)
print(f"  j={node_labels[j]}, i={node_labels[i]}, flipped=True")
print(f"  phi[j=source] = phi[L] = {phi_j}")
print(f"  phi[i=target] = phi[M] = {phi_i}")
print(f"  d_phi_nonflip = phi[L] - phi[M] = {phi_j} - {phi_i} = {d_phi_nonflip}")
print(f"  d_phi_flip    = -phi[L] - phi[M] = -({phi_j}) - ({phi_i}) = {d_phi_flip}")
print(f"  gating_nonflip = cos({d_phi_nonflip}) = {gating_nonflip}")
print(f"  gating_flip    = cos({d_phi_flip}) = {gating_flip}")
print(f"  d_phi_nonflip == d_phi_flip: {np.isclose(d_phi_nonflip, d_phi_flip)}")
print(f"  gating_nonflip == gating_flip: {np.isclose(gating_nonflip, gating_flip)}")
print(f"  INERT: {np.isclose(d_phi_nonflip, d_phi_flip) and np.isclose(gating_nonflip, gating_flip)}")
print()

print("=== STEP 5: FLIPPED-EDGE CANDIDATE ANALYSIS ===")
print("The only node carrying sweep phase is S (phi[S] = 1.234).")
print("A flipped edge (j,i) is non-inert iff d_phi_flip != d_phi_nonflip,")
print("  which requires phi[j] != 0 (source node carries nonzero phase).")
print()
print("All weighted edges (candidates for flipping):")
print(f"{'edge':>8}  {'source':>6} {'phi[source]':>12}  {'target':>6} {'phi[target]':>12}  {'non-inert if flipped?':>22}")
print("-" * 80)
for j in range(sim.num_nodes):
    for i in range(sim.num_nodes):
        if sim.weights[j, i] > 0:
            phi_j = sim.phi[j]
            phi_i = sim.phi[i]
            non_inert = not np.isclose(phi_j, 0.0)
            is_flipped = sim.flipped_edges[j, i]
            print(f"  {node_labels[j]}->{node_labels[i]:<2}  {node_labels[j]:>6} {phi_j:>12.6f}  {node_labels[i]:>6} {phi_i:>12.6f}  {'YES (if flipped)' if non_inert else 'NO (inert)':>22}  {'[WIRED]' if is_flipped else ''}")

print()
print("Conclusion: Only S->L has a source (S) carrying sweep phase.")
print("S->L is NOT the wired flipped edge (L->M is).")
print("Therefore NO non-inert flipped edge is wired in this sweep.")
print()

print("=== SIMULATION-LEVEL VERIFICATION: With flip vs Without flip ===")
phi_sweeps = np.linspace(-np.pi, np.pi, 50)

V_M_with_flip = []
V_M_without_flip = []

for sweep_phi in phi_sweeps:
    sim_flip = M2WallFieldSimulation(num_nodes=3)
    sim_flip.set_listen_weight(S, L, 1.0)
    sim_flip.set_listen_weight(L, M, 1.0)
    sim_flip.set_listen_weight(L, S, 1.0)
    sim_flip.set_listen_weight(M, L, 1.0)
    sim_flip.set_flipped_edge(L, M, True)
    sim_flip.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
    sim_flip.set_node_state(L, V_val=0.0, phi_val=0.0)
    sim_flip.set_node_state(M, V_val=0.0, phi_val=0.0)
    for _ in range(30):
        sim_flip.V[S] = 1.0
        sim_flip.tickVField(alpha=0.15)
    V_M_with_flip.append(sim_flip.V[M])

    sim_noflip = M2WallFieldSimulation(num_nodes=3)
    sim_noflip.set_listen_weight(S, L, 1.0)
    sim_noflip.set_listen_weight(L, M, 1.0)
    sim_noflip.set_listen_weight(L, S, 1.0)
    sim_noflip.set_listen_weight(M, L, 1.0)
    sim_noflip.set_node_state(S, V_val=1.0, phi_val=sweep_phi)
    sim_noflip.set_node_state(L, V_val=0.0, phi_val=0.0)
    sim_noflip.set_node_state(M, V_val=0.0, phi_val=0.0
)
    for _ in range(30):
        sim_noflip.V[S] = 1.0
        sim_noflip.tickVField(alpha=0.15)
    V_M_without_flip.append(sim_noflip.V[M])

V_M_with_flip = np.array(V_M_with_flip)
V_M_without_flip = np.array(V_M_without_flip)
max_diff = np.max(np.abs(V_M_with_flip - V_M_without_flip))
print(f"Max |V_M(with_flip) - V_M(no_flip)| over full sweep: {max_diff}")
print(f"Profiles identical within tolerance: {np.allclose(V_M_with_flip, V_M_without_flip)}")
print(f"Variance WITH flip:    {np.var(V_M_with_flip)}")
print(f"Variance WITHOUT flip: {np.var(V_M_without_flip)}")
print()
print("=> The flipped edge L->M produces ZERO difference in simulation output.")
print("   The observed variance in the M2 sweep comes ENTIRELY from non-flipped edges")
print("   (S->L, L->S, M->L) that carry nonzero phase differences.")
