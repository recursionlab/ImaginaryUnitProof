from __future__ import annotations
import numpy as np


class ComplexWallField:
    """Faithful lifting of ImaginaryUnit.ipynb to a complex phasor so the
    orientation T-flip (d_phi = -phi[j]-phi[i]) is OBSERVABLE.

    Notebook real model: d_phi sign is invisible because gating=cos(d_phi) (even).
    Complex model: complex-weighted diffusion psi_j -> exp(i*d_phi)*psi_j.
    The flip conjugates the hopping phase (exp(i*d_phi) -> exp(-i*d_phi)),
    which is distinguishable in interference iff the flipped edge has phase contrast.

    This is the minimal change that makes the theory's claims testable. The frozen
    gate contract decode (bit=1 iff cos(phi)<0) is applied to the OBSERVABLE real
    amplitude at the target node, exactly as the notebook gates.
    """

    def __init__(self, num_nodes: int):
        self.num_nodes = num_nodes
        self.psi = np.zeros(num_nodes, dtype=complex)
        self.phi = np.zeros(num_nodes, dtype=float)
        self.weights = np.zeros((num_nodes, num_nodes))
        self.flipped = np.zeros((num_nodes, num_nodes), dtype=bool)

    def set_node_state(self, idx, V_val, phi_val):
        self.psi[idx] = V_val * np.exp(1j * phi_val)
        self.phi[idx] = phi_val

    def set_listen_weight(self, source, target, weight):
        self.weights[source, target] = weight

    def set_flipped_edge(self, source, target, is_flipped=True):
        self.flipped[source, target] = is_flipped

    def tick(self, alpha=0.15, use_abs_clip=False):
        new_psi = np.copy(self.psi)
        for i in range(self.num_nodes):
            acc = 0.0 + 0.0j
            for j in range(self.num_nodes):
                if self.weights[j, i] > 0:
                    if self.flipped[j, i]:
                        d_phi = -self.phi[j] - self.phi[i]
                    else:
                        d_phi = self.phi[j] - self.phi[i]
                    hopping = self.weights[j, i] * np.exp(1j * d_phi)
                    acc += hopping * self.psi[j]
            leak = np.sum(self.weights[i, :]) * self.psi[i]
            new_psi[i] = self.psi[i] + alpha * (acc - leak)
        self.psi = new_psi
        if use_abs_clip:
            # Real-model-style clip on MAGNITUDE only (keeps phase/sign for interference)
            mags = np.abs(self.psi)
            mags = np.clip(mags, 0.0, 10.0)
            phase = np.angle(self.psi)
            self.psi = mags * np.exp(1j * phase)

    # --- observables the frozen contract can score ---
    @property
    def V(self):
        return np.abs(self.psi)

    def target_observable(self, target):
        """Complex target amplitude: exposes sign-flip under T-flip+contrast."""
        return self.psi[target]
