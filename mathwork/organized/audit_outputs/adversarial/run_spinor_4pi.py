from __future__ import annotations
import json
import numpy as np


class TNetwork:
    """Minimal complex-phasor loop with TRUE anti-unitary time-reversal on a flipped
    edge: hopping on edge (j->i) is w*exp(i*d_phi)*psi_j, but on a T-flipped edge the
    wavefunction is conjugated before hopping: w*exp(i*d_phi)*conj(psi_j).

    4pi double-cover expectation: threading a flux phi around a loop with an ODD number
    of T-conjugating links yields psi_target(phi+2pi) = -psi_target(phi) (sign flip),
    restoring psi_target(phi+4pi) = +psi_target(phi). This is the real SU(2)/spinor
    signature, NOT an amplitude boundary sample.
    """

    def __init__(self, n):
        self.n = n
        self.psi = np.zeros(n, dtype=complex)
        self.phi = np.zeros(n, dtype=float)
        self.w = np.zeros((n, n))
        self.tflip = np.zeros((n, n), dtype=bool)
        self.flux = 0.0  # AB flux threaded through the loop

    def edge(self, s, t, weight=1.0, t_flip=False, flux_share=0.0):
        self.w[s, t] = weight
        self.tflip[s, t] = t_flip
        # store flux share on source->target edges (applied as +flux_share*phi)
        if flux_share != 0.0:
            self._fshare[s, t] = flux_share

    def _init_flux(self):
        self._fshare = np.zeros((self.n, self.n))

    def set_state(self, i, V, phi):
        self.psi[i] = V * np.exp(1j * phi)
        self.phi[i] = phi

    def tick(self, alpha=0.15):
        new = np.copy(self.psi)
        for i in range(self.n):
            acc = 0.0 + 0.0j
            for j in range(self.n):
                if self.w[j, i] > 0:
                    d_phi = self.phi[j] - self.phi[i] + self._fshare[j, i] * self.flux
                    hop = self.w[j, i] * np.exp(1j * d_phi)
                    contrib = hop * (np.conj(self.psi[j]) if self.tflip[j, i] else self.psi[j])
                    acc += contrib
            leak = np.sum(self.w[i, :]) * self.psi[i]
            new[i] = self.psi[i] + alpha * (acc - leak)
        self.psi = new


def run_loop(flip_edge: bool, flux_range=(-2*np.pi, 2*np.pi), npts=201):
    net = TNetwork(3)
    net._init_flux()
    # directed cycle 0->1->2->0, flux +flux on forward edges, -flux on 0->2 return (so loop flux = phi)
    net.edge(0, 1, 1.0, t_flip=False, flux_share=0.5)
    net.edge(1, 2, 1.0, t_flip=False, flux_share=0.5)
    net.edge(2, 0, 1.0, t_flip=flip_edge, flux_share=-1.0)   # odd T-flip on this edge
    net.edge(1, 0, 1.0); net.edge(2, 1, 1.0); net.edge(0, 2, 1.0)
    out = []
    for phi in np.linspace(*flux_range, npts):
        net.psi.fill(0.0); net.phi.fill(0.0)
        net.flux = phi
        net.set_state(0, V=1.0, phi=0.0)
        for _ in range(200):
            net.psi[0] = 1.0
            net.tick(alpha=0.15)
        out.append(complex(net.psi[2]))
    return np.linspace(*flux_range, npts), np.array(out)


def spinor_metric(psi, half):
    n = len(psi)
    pairs = min(half, n - half)
    a = np.abs(psi[half:half+pairs] + psi[:pairs])
    return {
        "max_abs_sum": float(np.max(a)),
        "mean_abs_sum": float(np.mean(a)),
        "min_abs_sum": float(np.min(a)),
        "interpretation": "sum ~ 0 => spinor sign flip at 2pi (4pi return); sum ~ 2*|psi| => 2pi-periodic",
    }


def main():
    p, psi_noflip = run_loop(flip_edge=False)
    _, psi_flip = run_loop(flip_edge=True)
    half = len(p) // 2  # +2pi shift
    res = {
        "no_T_flip": {
            "amplitude": "|psi| is 2pi periodic (control)",
            "spinor": spinor_metric(psi_noflip, half),
            "boundary_deviation_amp": float(abs(abs(psi_noflip[0]) - abs(psi_noflip[-1]))),
        },
        "with_T_flip": {
            "amplitude_boundary_deviation": float(abs(abs(psi_flip[0]) - abs(psi_flip[-1]))),
            "spinor": spinor_metric(psi_flip, half),
            "sign_flip_at_2pi": bool(spinor_metric(psi_flip, half)["max_abs_sum"] < 0.1),
            "amplitude_2pi_periodic": bool(np.max(np.abs(np.abs(psi_flip[half:half+half]) - np.abs(psi_flip[:half]))) < 0.1),
            "verdict_4pi": "DEMONSTRATED if sign_flip_at_2pi=True AND amplitude_2pi_periodic=True (spinor flips sign, intensity periodic)",
        },
        "honest_framing": {
            "what_this_tests": "anti-unitary T (conj on flipped edge) + flux-threaded loop; spinor sign flip on complex psi over 2pi.",
            "claim_policy": "4pi demonstrated ONLY if with_T_flip.sign_flip_at_2pi=True AND amplitude-only metric stays vacuous (so the sign test is what carries it).",
        },
    }
    json.dump(res, open("spinor_4pi_results.json", "w"), indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
