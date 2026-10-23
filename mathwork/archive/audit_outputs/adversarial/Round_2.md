# Round 2 - M2 Flipped Edge L->M Is Inert Under Fixed-Phase Configuration

## Setup

Built via `wallfield_actual.M2WallFieldSimulation` (verbatim port of notebook cell 8,
confirmed via `adv_common.cell_lines(8)`).

**Weights** (4 edges): S->L, L->M, L->S, M->L, all = 1.0
**Phases**: phi[S] = 1.234, phi[L] = 0, phi[M] = 0
**Flipped edge**: L->M (`set_flipped_edge(L, M, True)`)

## Cell 8 (verbatim, `adv_common.cell_lines(8)`)

```
1: # 2. Refactor simulation to include M2 flipped edge operator

2: class M2WallFieldSimulation(RefactoredWallFieldSimulation):

3:     def __init__(self, num_nodes):

4:         super().__init__(num_nodes)

5:         # Keep track of which connections are 'flipped' (orientation flip)

6:         # If flipped_edges[j, i] is True, the edge j -> i acts under time-reversal (orientation reversal)

7:         self.flipped_edges = np.zeros((num_nodes, num_nodes), dtype=bool)

8: 

9:     def set_flipped_edge(self, source, target, is_flipped=True):

10:         self.flipped_edges[source, target] = is_flipped

11: 

12:     def tickVField(self, alpha=0.1):

13:         """

14:         Overridden tickVField that accounts for flipped edges (anti-unitary/orientation flip T).

15:         If an edge is flipped, the incoming signal phase undergoes a sign inversion:

16:         d_phi = -phi_j - phi_i (instead of phi_j - phi_i).

17:         """

18:         new_V = np.copy(self.V)

19:         for i in range(self.num_nodes):

20:             diffusion_sum = 0.0

21:             for j in range(self.num_nodes):

22:                 if self.weights[j, i] > 0:

23:                     if self.flipped_edges[j, i]:

24:                         # Flip operator application: reverses phase contribution direction

25:                         d_phi = -self.phi[j] - self.phi[i]

26:                     else:

27:                         d_phi = self.phi[j] - self.phi[i]

28: 

29:                     gating = np.cos(d_phi)

30:                     diffusion_sum += self.weights[j, i] * gating * self.V[j]

31: 

32:             # Apply diffusion equation

33:             new_V[i] = self.V[i] + alpha * (diffusion_sum - np.sum(self.weights[i, :]) * self.V[i])

34: 

35:         self.V = np.clip(new_V, 0.0, 10.0)

36: 

37: # Test connectivity and print initialization of M2 class

38: m2_sim = M2WallFieldSimulation(num_nodes=3)

39: m2_sim.set_listen_weight(0, 1, 1.0)

40: m2_sim.set_flipped_edge(0, 1, True)

41: print("M2 simulation initialized. Flipped edge matrix defined:")

42: print(m2_sim.flipped_edges)
```

## Cell 9 (verbatim, `adv_common.cell_lines(9)`)

```
1: import numpy as np

2: import matplotlib.pyplot as plt

3: import json

4: 

5: # --- 1. Initialize M2 (Orientation Flip) Simulation Sweep ---

6: num_nodes = 3

7: S, L, M = 0, 1, 2

8: 

9: phi_sweeps = np.linspace(-np.pi, np.pi, 50)

10: V_M_m2_results = []

11: 

12: for sweep_phi in phi_sweeps:

13:     # Initialize M2 simulation

14:     sim_m2 = M2WallFieldSimulation(num_nodes)

15:     sim_m2.set_listen_weight(S, L, 1.0)

16:     sim_m2.set_listen_weight(L, M, 1.0)

17:     sim_m2.set_listen_weight(L, S, 1.0)

18:     sim_m2.set_listen_weight(M, L, 1.0)

19: 

20:     # Flip the edge between L and M to introduce the orientation flip operator (T)

21:     sim_m2.set_flipped_edge(L, M, True)

22: 

23:     # Set states: Clamp V[S] = 1.0, and sweep phase at S

24:     sim_m2.set_node_state(S, V_val=1.0, phi_val=sweep_phi)

25:     sim_m2.set_node_state(L, V_val=0.0, phi_val=0.0)

26:     sim_m2.set_node_state(M, V_val=0.0, phi_val=0.0)

27: 

28:     # Run simulation ticks

29:     for _ in range(30):

30:         sim_m2.V[S] = 1.0

31:         sim_m2.tickVField(alpha=0.15)

32: 

33:     V_M_m2_results.append(sim_m2.V[M])

34: 

35: # --- 2. Evaluate M2 Hypotheses & Scoring ---

36: # Standard scalar prediction expects no phase dependency, or a symmetrical profile depending on model

37: max_V_M_m2 = np.max(V_M_m2_results)

38: min_V_M_m2 = np.min(V_M_m2_results)

39: 

40: # For M2, we check if the orientation flip shifts the transmission profile as predicted by H_operator

41: # Let's save a structured scoring verdict JSON

42: m2_scoring_artifact = {

43:     "test_id": "M2_JUNCTION_FLIP_STAGE_2",

44:     "purpose": "Verify if the orientation flip operator (T) successfully alters transmission profiles under phase sweeps.",

45:     "results": {

46:         "max_transmitted_V_M_m2": float(max_V_M_m2),

47:         "min_transmitted_V_M_m2_at_edges": float(min(V_M_m2_results[0], V_M_m2_results[-1])),

48:         "profile_variance": float(np.var(V_M_m2_results))

49:     },

50:     "verdict": {

51:         "status": "PASS (M2 Junction Verified in Simulation)" if np.var(V_M_m2_results) > 0.01 else "FAIL (No observable orientation gating)",

52:         "rationale": "Variance in transmission amplitude demonstrates active phase gating across the flipped orientation boundary."

53:     }

54: }

55: 

56: with open('/content/scoring_verdict_m2.json', 'w') as f:

57:     json.dump(m2_scoring_artifact, f, indent=2)

58: 

59: # --- 3. Plot M2 Junction Gating Map ---

60: plt.figure(figsize=(9, 5.5))

61: plt.plot(phi_sweeps, V_M_m2_results, label='H_operator (M2 Flipped: T-operator active)', color='orange', linewidth=2.5)

62: plt.plot(phi_sweeps, V_M_results, label='M1 Reference (No Flip)', color='cyan', linestyle=':', linewidth=2)

63: plt.title('Stage 2 (M2 Junction): Orientation Flip Transmission Profile')

64: plt.xlabel('Source Phase Offset \Delta\phi_S (rad)')

65: plt.ylabel('Observed Target Amplitude V[M]')

66: plt.grid(True, linestyle='--', alpha=0.5)

67: plt.legend(loc='upper right')

68: plt.savefig('/content/m2_junction_profile.png', dpi=150)

69: plt.show()

70: 

71: print(json.dumps(m2_scoring_artifact, indent=2))
```

## Node state

| Node | phi | V (initial) |
|------|-----|-------------|
| S | 1.234 | 1.0 |
| L | 0.0 | 0.0 |
| M | 0.0 | 0.0 |

## Edge-by-edge gating comparison

For every edge (j->i), the non-flip branch computes `d_phi = phi[j] - phi[i]` and the flip
branch computes `d_phi = -phi[j] - phi[i]`. The gating factor is `cos(d_phi)` in both
branches. If the two gating values are equal, flipping that edge has **zero effect** on the
diffusion update - the edge is **inert**.

| Edge (j->i) | phi[j] | phi[i] | d_phi_nonflip | d_phi_flip | gating_nonflip | gating_flip | identical |
|------------|--------|--------|---------------|------------|----------------|-------------|-----------|
| S->L | 1.234000 | 0.000000 | 1.234000 | -1.234000 | 0.330465 | 0.330465 | True |
| L->M | 0.000000 | 0.000000 | 0.000000 | -0.000000 | 1.000000 | 1.000000 | True |
| L->S | 0.000000 | 1.234000 | -1.234000 | -1.234000 | 0.330465 | 0.330465 | True |
| M->L | 0.000000 | 0.000000 | 0.000000 | -0.000000 | 1.000000 | 1.000000 | True |

## Proof: flipped edge L->M is inert

The only edge with `flipped_edges[j,i] = True` is L->M (j=L, i=M).

- **d_phi_nonflip** = phi[L] - phi[M] = 0.0 - 0.0 = **0.0**
- **d_phi_flip** = -phi[L] - phi[M] = -0.0 - 0.0 = **0.0**
- **gating_nonflip** = cos(0.0) = **1.0**
- **gating_flip** = cos(0.0) = **1.0**
- **identical** = **True**

Both branches yield d_phi = 0, so the T-flip operator applies `cos(-0 - 0) = cos(0) = 1`,
which is byte-identical to the non-flip branch. The source node L carries **phase 0**, so
the orientation-flip operator never engages. **L->M is provably inert.**

## Simulation-level confirmation (30 ticks, alpha=0.15)

Ran the full `tickVField` loop with the flipped edge ON vs OFF (all other parameters identical).

| Metric | Value |
|--------|-------|
| V[M] final, flip off | 0.26456419277573023 |
| V[M] final, flip on | 0.26456419277573023 |
| max |V_flip - V_noflip| over 30 ticks | **0.0** |
| mean |V_flip - V_noflip| | **0.0** |
| Pointwise identical | **True** |

The flipped edge produces **zero divergence** in the observed amplitude V[M] across all 30
time steps. This is the direct numerical confirmation of inertness: the T-flip on L->M is
observably absent.

## Why all edges are inert in this configuration

The general condition for a flipped edge (j->i) to be **non-inert** (i.e.
`cos(phi[j]-phi[i]) != cos(-phi[j]-phi[i])`) is:

> **phi[source] != 0 AND phi[target] != 0**

This follows from the identity `cos(a) = cos(b)` iff `a = b (mod 2pi)` or `a = -b (mod 2pi)`:
- a = phi[j] - phi[i], b = -(phi[j] + phi[i])
- a = b  =>  phi[j] = 0
- a = -b  =>  phi[i] = 0

So the flip is inert whenever **either endpoint has phase 0**.

In our setup, phi[L] = 0 and phi[M] = 0, so the flipped L->M is inert by the source-is-zero
condition. Furthermore, **all four edges** are inert because every edge has at least one
endpoint at phase 0. This is confirmed in the table above: `identical = True` for every edge.

## Candidate enumeration: edges that COULD be non-inert

A flipped edge **could** be non-inert when its **source node carries phase**
(phi[source] != 0). In this configuration, only **S** carries non-zero phase (phi[S] = 1.234).

All possible directed edges among S, L, M where the source carries phase:

| Candidate edge | phi[source] != 0? | phi[target] != 0? | Could be non-inert? | Wired? |
|----------------|-------------------|-------------------|----------------------|--------|
| S->S | Yes (1.234) | Yes (1.234) | **Yes** (both non-zero) | No (weight=0) |
| **S->L** | Yes (1.234) | No (0.0) | **No** (target=0 - cos even) | **Yes** (weight=1.0) |
| S->M | Yes (1.234) | No (0.0) | **No** (target=0 - cos even) | No (weight=0) |
| L->M (actual flip) | No (0.0) | No (0.0) | **No** (source=0) | Yes |
| L->S | No (0.0) | Yes (1.234) | No | Yes |
| M->L | No (0.0) | No (0.0) | No | Yes |

**Key result**: The only wired candidate whose source carries phase is **S->L**. But S->L is
**still inert** because phi[target=L] = 0 and cos is an even function:

- d_phi_nonflip = 1.234 - 0 = 1.234 -> cos = 0.330465
- d_phi_flip = -1.234 - 0 = -1.234 -> cos = 0.330465

The d_phi *values* differ (1.234 vs -1.234), but `cos(1.234) = cos(-1.234)` - the gating
factor is identical - so S->L is inert.

**No wired edge in this configuration can be non-inert.** S is the sole phase-carrying
node, and all of S's wired outgoing edges terminate at zero-phase nodes, collapsing the flip
to `cos(-x) = cos(x)`.

### Contrast: a genuinely non-inert configuration (for reference)

If phi[L] were 0.5 instead of 0.0, the S->L edge would become non-inert:

| Edge | phi[j] | phi[i] | d_phi_nonflip | d_phi_flip | gating_nonflip | gating_flip | identical |
|------|--------|--------|---------------|------------|----------------|-------------|-----------|
| S->L (hypothetical, phi[L]=0.5) | 1.234 | 0.5 | 0.734 | -1.734 | 0.7425 | -0.1625 | **False** |

With both endpoints carrying non-zero phase, the flip produces a genuine change in gating
(-0.1625 vs 0.7425). This confirms the general condition and demonstrates that the inertness
of L->M and S->L in the actual setup is due to the zero-phase target/source, **not** a
degenerate property of the M2 class.

## Connection to cell 9 (notebook M2 sweep)

Cell 9 (`adv_common.cell_lines(9)`) sweeps phi[S] over [-pi, pi] but keeps phi[L] = phi[M] = 0
throughout - exactly the configuration proven inert here. The `variance > 0.01` PASS verdict
(cell 9, L51) is therefore satisfied by **non-flatness of the M1 cos-profile inherited via
S->L and L->S**, not by any orientation-flip effect from L->M. The flipped edge is structurally
incapable of engaging because its source node L is pinned to phi = 0 at every sweep step.

## Verdict

**M2's flipped edge L->M is INERT.** Proven three ways:

1. **Algebraic**: d_phi = 0 in both flip and non-flip branches (phi[L] = phi[M] = 0).
2. **Gating**: cos(0) = 1 identically; the comparison table shows `identical = True` for
   all four edges.
3. **Numerical**: 30-tick simulation yields V[M] flip-on == V[M] flip-off
   (max |diff| = 0.0, pointwise identical).

The general inertness condition is `phi[source] = 0 OR phi[target] = 0`. L->M fails both
(both are zero) and the sole phase-carrying node S has all its wired outgoing edges
landing on zero-phase targets, making the entire graph's orientation-flip operator a
structural no-op.
