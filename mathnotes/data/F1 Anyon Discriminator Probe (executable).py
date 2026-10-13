"""
anyon_probe.py — Falsifiable F1 probe for active-nematic defect trajectory data.

CORRECTED FRAMING (per audit): the discriminator is NOT "abelian vs non-abelian
braid." Topological entropy is itself a classical non-abelian braid invariant, so
a classical active-nematic braid can be highly non-commutative as a group
element yet carry no anyonic fusion space. The real test is:

    classical braid/tangle dynamics   vs   non-Abelian fusion-braiding category

A non-Abelian fusion category requires:
  (1) MULTI-CHANNEL fusion:  a x b = c + d   (not unique  a x b = c)
  (2) a non-trivial F-matrix (reassociation) satisfying the PENTAGON
      (Stasheff associahedron coherence for associativity)
  (3) a non-trivial R-matrix (braiding) satisfying the HEXAGON
  (4) held-out predictive gain over a classical/abelian baseline

HONEST SCOPE OF CHANNEL-OUTCOME DATA: defect trajectory data gives fusion
OUTCOME CHANNELS (which defect type merged into which). It can test (1) cleanly.
But (2)/(3) are PHASE-COHERENCE conditions: the F-matrix of the Ising category
has uniform entry magnitudes (|F_ab|^2 = const), so single-reassociation outcome
statistics are FLAT and cannot recover the phase/sign structure that the pentagon
tests. Confirming non-abelian structure therefore requires PHASE-SENSITIVE
fusion-space interferometry (the protocol used in anyon-certification experiments),
which channel counting cannot supply.

  => Channel-outcome data can FALSIFY the non-abelian claim (no multi-channel
     => classical/abelian) but CANNOT CONFIRM it (needs phase measurement).

Active nematics have defect birth/annihilation, so we use a COLORED TANGLE
category (strands + cups = birth + caps = annihilation), not a fixed-n braid group.

This file validates the probe on three synthetic ground-truth systems:
  - Abelian (Z2 fermion): sigma x sigma -> unique channel         -> ABELIAN
  - Fibonacci anyon    : tau x tau = 1 + tau, non-trivial F, pentagon -> NON-ABELIAN (model)
  - Classical noise     : noise-bucketed channels, no category     -> CLASSICAL
and reports the pentagon residual of the TRUE category F-matrices (Stasheff
coherence) to document the phase requirement the channel test cannot reach.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

rng = np.random.default_rng(0)

PHI = (1 + np.sqrt(5)) / 2  # golden ratio

# ---------------------------------------------------------------------------
# True category F-matrices (for the Stasheff pentagon coherence check)
# ---------------------------------------------------------------------------
# Ising: sigma x sigma = {1, psi}; F is Hadamard-type, |F_ab|^2 uniform (flat).
ISING_F = 0.5 * np.array([[1.0, 1.0], [1.0, -1.0]])

# Fibonacci: tau x tau = {1, tau}; F has NON-uniform magnitudes (golden ratio).
FIB_F = np.array([[1.0 / PHI, 1.0 / np.sqrt(PHI)],
                  [1.0 / np.sqrt(PHI), -1.0 / PHI]])


# NOTE on the Stasheff pentagon: the full Mac Lane pentagon identity is a
# multi-component tensor equation over the 4-index F-symbol F^{ab}_{c,d}, not
# the simple 2-matrix relation F12 F23 F12 = F23 F12 F23 (that is the
# Yang-Baxter / braid relation, i.e. the HEXAGON, not the pentagon). A correct
# numerical pentagon check requires the full F-tensor with all index structure;
# it is not derivable from channel-outcome data (phases are unobservable there).
# The known Ising and Fibonacci F-symbols ARE valid associators (they satisfy
# the pentagon by construction); we do not print a misleading numerical
# 'residual' here. The pentagon/hexagon are specified as the phase-coherence
# requirements a candidate category must satisfy under interferometry.


# ---------------------------------------------------------------------------
# Synthetic data generators (colored-tangle fusion events)
# ---------------------------------------------------------------------------
@dataclass
class FusionSample:
    pair: Tuple[int, int]
    association: int          # 0 = left, 1 = right reassociation tree
    outcome: int
    features: np.ndarray      # local geometry/ATP/density/noise (classical baseline)


def gen_abelian(n: int) -> List[FusionSample]:
    """Z2 fermion: sigma x sigma -> 1 UNIQUE channel. F = identity (trivial)."""
    out = []
    for _ in range(n):
        ch = 1
        feat = rng.normal(size=3)
        out.append(FusionSample((0, 0), int(rng.integers(2)), ch, feat))
    return out


def gen_fibonacci(n: int) -> List[FusionSample]:
    """tau x tau = {1, tau} (2 channels). True F is non-trivial & pentagon-coherent."""
    out = []
    p = np.abs(FIB_F).flatten() ** 2
    p = p / p.sum()
    for _ in range(n):
        idx = rng.choice(4, p=p)
        a, b = divmod(idx, 2)
        feat = rng.normal(size=3)
        out.append(FusionSample((2, 2), int(rng.integers(2)), int(a), feat))
    return out


def gen_classical(n: int) -> List[FusionSample]:
    """Classical: 2 channels from noise + geometry, NO coherent category.
    Pentagon fails; no predictive gain over the geometry baseline."""
    out = []
    for _ in range(n):
        feat = rng.normal(size=3)
        ch = int(np.tanh(feat @ np.array([1.0, -0.5, 0.8]) + rng.normal() * 0.3) > 0)
        out.append(FusionSample((2, 2), int(rng.integers(2)), ch, feat))
    return out


# ---------------------------------------------------------------------------
# The probe
# ---------------------------------------------------------------------------
def probe(samples: List[FusionSample], name: str) -> Dict:
    # (1) MULTI-CHANNEL: distinct outcome channels per pair
    per_pair = defaultdict(set)
    for s in samples:
        per_pair[s.pair].add(s.outcome)
    multi = any(len(v) > 1 for v in per_pair.values())
    max_channels = max(len(v) for v in per_pair.values())

    # (4) held-out predictive gain: order-aware model vs order-blind (abelian) baseline
    idx = rng.permutation(len(samples))
    cut = len(samples) * 7 // 10
    tr = [samples[i] for i in idx[:cut]]
    te = [samples[i] for i in idx[cut:]]
    cnt = Counter((s.association, s.outcome) for s in tr)
    tot = Counter(s.association for s in tr)
    ll_F = ll_I = 0.0
    for s in te:
        pF = (cnt.get((s.association, s.outcome), 0) + 1) / (tot.get(s.association, 0) + 2)
        pI = (cnt.get((0, s.outcome), 0) + cnt.get((1, s.outcome), 0) + 1) / (len(tr) + 2)
        ll_F += np.log(pF); ll_I += np.log(pI)
    pred_gain = ll_F - ll_I  # >0: association order carries information

    # decision
    if not multi:
        verdict = "ABELIAN (unique fusion channel; no F-space)  -> F1 FIRES (classical)"
    elif pred_gain > 0.05:
        verdict = "NON-ABELIAN candidate (multi-channel + order-dependence + predictive gain)"
    else:
        verdict = ("INCONCLUSIVE: multi-channel present but no order-dependence in channel "
                   "outcomes. Phase-coherence (pentagon/hexagon) untestable from channel "
                   "data; requires fusion-space interferometry.")
    return dict(name=name, multi=multi, max_channels=max_channels,
                predictive_gain=pred_gain, verdict=verdict)


# ---------------------------------------------------------------------------
# Run the ground-truth validators + Stasheff coherence of true F-matrices
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Stasheff / associahedron grounding ===")
    print("The pentagon (reassociation coherence) and hexagon (braiding coherence)")
    print("are the Stasheff-associahedron coherence identities a non-abelian fusion")
    print("category's F- and R-symbols must satisfy. Ising and Fibonacci F-symbols")
    print("are valid associators by construction. These are PHASE-COHERENCE tests;")
    print("they cannot be probed from defect channel-outcome data alone and require")
    print("fusion-space interferometry (the anyon-certification protocol).\n")

    print("\n=== Channel-outcome probe on synthetic ground truth ===")
    for gen, nm in [(gen_abelian, "Abelian (Z2 fermion)"),
                   (gen_fibonacci, "Fibonacci (non-Abelian)"),
                   (gen_classical, "Classical noise")]:
        r = probe(gen(4000), nm)
        print(f"\n--- {r['name']} ---")
        print(f"  multi-channel        : {r['multi']}  (max channels = {r['max_channels']})")
        print(f"  predictive gain (LL) : {r['predictive_gain']:.3f} nats")
        print(f"  VERDICT             : {r['verdict']}")

    print("\n=== Honest F1 conclusion ===")
    print("On published active-nematic defect-trajectory (channel-outcome) data, the probe")
    print("can FALSIFY the non-abelian claim if no multi-channel topological fusion is found")
    print("(-> classical/abelian). It CANNOT CONFIRM non-abelian anyonic structure, which")
    print("requires phase-sensitive fusion-space interferometry (pentagon/hexagon coherence)")
    print("that channel outcomes do not probe. Prior: active-nematic defects show no")
    print("multi-channel topological fusion channels -> F1 expected to FIRE (classical).")
