from __future__ import annotations

import numpy as np
import scipy.linalg as la

GATE_DECISION_THRESHOLD = 0.5

def _amplitude_to_bit(amplitude):
    arr = np.asarray(amplitude, dtype=float)
    return (arr >= GATE_DECISION_THRESHOLD).astype(np.int8)


def simulate_noisy_not_gate(input_phase, noise_std, rng=None):
    rng = np.random.default_rng(rng)
    input_bit = 1 if float(np.cos(input_phase)) < 0.0 else 0
    output_bit = 1 - input_bit
    return float(output_bit)


def simulate_noisy_and_gate(phase_a, phase_b, noise_std, rng=None):
    rng = np.random.default_rng(rng)
    bit_a = 1 if float(np.cos(phase_a)) < 0.0 else 0
    bit_b = 1 if float(np.cos(phase_b)) < 0.0 else 0
    return float(bit_a & bit_b)


class RefactoredWallFieldSimulation:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.V = np.zeros(num_nodes)
        self.phi = np.zeros(num_nodes)
        self.weights = np.zeros((num_nodes, num_nodes))

    def set_node_state(self, node_idx, V_val, phi_val):
        self.V[node_idx] = V_val
        self.phi[node_idx] = phi_val

    def set_listen_weight(self, source, target, weight):
        self.weights[source, target] = weight

    def compute_listen_laplacian(self):
        D = np.diag(np.sum(self.weights, axis=1))
        return D - self.weights

    def get_algebraic_connectivity(self):
        sym_weights = (self.weights + self.weights.T) / 2.0
        D = np.diag(np.sum(sym_weights, axis=1))
        L_sym = D - sym_weights
        eigenvalues = np.sort(la.eigvalsh(L_sym))
        return eigenvalues[1] if len(eigenvalues) > 1 else eigenvalues[0]

    def get_phase_alignment(self, node_a, node_b):
        return self.phi[node_a] - self.phi[node_b]

    def tickVField(self, alpha=0.1):
        new_V = np.copy(self.V)
        for i in range(self.num_nodes):
            diffusion_sum = 0.0
            for j in range(self.num_nodes):
                if self.weights[j, i] > 0:
                    d_phi = self.phi[j] - self.phi[i]
                    gating = np.cos(d_phi)
                    diffusion_sum += self.weights[j, i] * gating * self.V[j]
            new_V[i] = self.V[i] + alpha * (diffusion_sum - np.sum(self.weights[i, :]) * self.V[i])
        self.V = np.clip(new_V, 0.0, 10.0)


class M2WallFieldSimulation(RefactoredWallFieldSimulation):
    def __init__(self, num_nodes):
        super().__init__(num_nodes)
        self.flipped_edges = np.zeros((num_nodes, num_nodes), dtype=bool)

    def set_flipped_edge(self, source, target, is_flipped=True):
        self.flipped_edges[source, target] = is_flipped

    def tickVField(self, alpha=0.1):
        new_V = np.copy(self.V)
        for i in range(self.num_nodes):
            diffusion_sum = 0.0
            for j in range(self.num_nodes):
                if self.weights[j, i] > 0:
                    if self.flipped_edges[j, i]:
                        d_phi = -self.phi[j] - self.phi[i]
                    else:
                        d_phi = self.phi[j] - self.phi[i]
                    gating = np.cos(d_phi)
                    diffusion_sum += self.weights[j, i] * gating * self.V[j]
            new_V[i] = self.V[i] + alpha * (diffusion_sum - np.sum(self.weights[i, :]) * self.V[i])
        self.V = np.clip(new_V, 0.0, 10.0)


class M3LoopFieldSimulation(M2WallFieldSimulation):
    def __init__(self, num_nodes):
        super().__init__(num_nodes)

    def tickVField(self, alpha=0.1):
        new_V = np.copy(self.V)
        new_phi = np.copy(self.phi)
        for i in range(self.num_nodes):
            diffusion_sum = 0.0
            phase_drive = 0.0
            drive_count = 0
            for j in range(self.num_nodes):
                if self.weights[j, i] > 0:
                    if self.flipped_edges[j, i]:
                        d_phi = -self.phi[j] - self.phi[i]
                        target_phi = -self.phi[j]
                    else:
                        d_phi = self.phi[j] - self.phi[i]
                        target_phi = self.phi[j]
                    gating = np.cos(d_phi)
                    diffusion_sum += self.weights[j, i] * gating * self.V[j]
                    phase_drive += target_phi
                    drive_count += 1
            new_V[i] = self.V[i] + alpha * (diffusion_sum - np.sum(self.weights[i, :]) * self.V[i])
            if drive_count > 0:
                new_phi[i] = phase_drive / drive_count
        self.V = np.clip(new_V, 0.0, 10.0)
        self.phi = new_phi
