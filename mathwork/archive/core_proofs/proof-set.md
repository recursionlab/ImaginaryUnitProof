# The Imaginary Unit, Straightened — Proof Set v0.1

Working draft. Purpose: separate what is standard from what is novel, so the novel
part can be killed or kept on evidence. Built to be run on the wall (see §6).

## 0. Claim, precisely

NOT claimed:

- That complex numbers are inconsistent.
- That the real-matrix form of QM is new. It is standard (Stueckelberg and
  everyone since): `C^N ≅ R^{2N}` with a complex structure `J`, `J² = −1`.

CLAIMED:

- Scalar `i` conflates (at least) three distinct geometric operators that happen
  to coincide in flat single-particle QM and stop coinciding under doubling,
  time reversal, or self-reference:
  - (a) complex structure `J` (unitary, cyan),
  - (b) time-reversal orientation flip `T` (anti-unitary, amber),
  - (c) quaternionic synthesis on `S³ ≅ Sp(1) ≅ SU(2)` (purple).
- Making them explicit yields predictions that scalar-`i` handling gets wrong.
  §4 lists three. §5 lists what kills each.

Status of the whole: CONJECTURE with testable teeth. Nothing here is declared proven.

## 1. Definitions

- D1 (scalar-i): the symbol `i`, `i² = −1`, used as a number.
- D2 (complex structure): real-linear `J : R^{2N} → R^{2N}`, `J² = −1`.
  Standard form `Z^α = x^α + i y^α` ↔ `X^I = [x^α, y^α]^T`.
- D3 (doubled space): the `R^{2N}` image of `C^N` under D2.
- D4 (time reversal): anti-unitary `Θ`/`T`; in doubled space, orientation flip
  on the phase half (`φ → −φ`), not a mere conjugation of scalars.
- D5 (quaternionic synthesis): `q = a + bi + cj + dk` on `S³`; `Sp(1) ≅ SU(2)`,
  double cover of `SO(3)` — some loops need 4π, not 2π, to close.
- D6 (wall field): per-monitor real pair `(V, φ)` — amplitude + phase.
  LISTEN edge `S→L` carries weight `w`; `V` diffuses, `φ` gates.

## 2. Standard results (PROVEN — background, not the contribution)

- R1: `C^N ≅ R^{2N}` with `J² = −1`. Textbook.
- R2 (Wigner): time reversal is anti-unitary. Textbook.
- R3: `S³ ≅ Sp(1) ≅ SU(2)` double-covers `SO(3)`. Textbook.
- R4: Laplacian algebraic connectivity `λ₂` governs diffusion capacity on a
  graph. Textbook spectral graph theory.

## 3. Lemmas (the straightening)

- L1 (doubling): every scalar-`i` expression has a doubled real form via D2.
  Mechanical. Status: PROVEN (construction).
- L2 (operator split): in doubled form, unitary evolution uses `J` while
  time-reversed evolution uses `J` + orientation flip. They are separable
  operations. Status: PROVEN (construction) — the *interpretation* as
  distinct actors is the claim, tested in §4.
- L3 (phase gate): IF the doubled form is ontic (not just notation), THEN flow
  between two nodes depends on phase alignment `Δφ`, not only on amplitude
  difference `ΔV`. Status: CONSEQUENCE of the claim — testable (P1).

## 4. Points of divergence (where scalar-i and operator-i disagree)

- P1 — φ-gating: clamp source `V` high, twist relative phase `Δφ → π`.
  Scalar-i account: flow continues (phase-blind diffusion on amplitudes).
  Operator-i account: flow chokes despite high `ΔV`.
- P2 — time-reversal junction: insert a LISTEN flip (`φ → −φ`) mid-chain.
  Scalar-i: "conjugate and continue," reunion node sums constructively.
  Operator-i: orientation flip turns the reunion destructive at a computable
  node. Fringe position differs.
- P3 — 4π loop: close a 2-step LISTEN loop with an odd number of flips.
  Scalar-i: 2π closure. Operator-i: needs the double circuit (spinor-like)
  to return to start; single circuit lands antiphase.

## 5. Falsifiers (what kills the claim — non-negotiable)

- F1: high-`V`, high-`Δφ` propagates exactly as high-`V`, low-`Δφ`
  (controlled for `λ₂`, weights, thresholds) → P1 dead.
- F2: flipped-edge reunion matches scalar prediction at the predicted node,
  repeatedly, blinded → P2 dead.
- F3: odd-flip loop closes in one circuit with no antiphase residue → P3 dead.
- F0 (global): all three fail → the operator split is notation, not physics.
  Accept it and move on. That outcome is also a result.

Controls required for every run: hold graph `λ₂`, edge weights `w`, claim
threshold, and tick count fixed; randomize target; log prediction BEFORE
amputation; isolated-node negative control must FAIL to regenerate
(if it heals with no LISTEN in, the check is lying, not the theory).

## 6. Wall mapping (how each test runs on the array)

- M1 (P1): chain `S→L→M`, `w = 1.0`. Clamp `V[S] = 1.0`, sweep `Δφ`.
  Readouts: `V[L]`, `V[M]` after fixed ticks; task auto-claim events.
  Harness: `setV`, `setListenWeight`, `tickVField`, `getLinkGraph`.
- M2 (P2): same chain + one flipped edge. Predict reunion node first,
  then run. Harness: `runFalsifiableDrill` (predict → amputate → measure
  `patternDist`, pass iff `dist ≤ 2` with verified unmount).
- M3 (P3): 2-node loop, odd flips. Single vs double circuit readout.
- Health gate for all runs: compute LISTEN Laplacian `λ₂`; distribute/run
  iff `λ₂ > ε`. If payloads strand, check `λ₂` first — fragmentation, not
  theory, is the usual killer.

## 7. Status table

| Item | Status | Needs |
|------|--------|-------|
| L1, L2 (constructions) | done | — |
| P1 φ-gating | open, runnable now | phase field `φ` per monitor (V exists; φ pending `weld V-field` follow-up) |
| P2 junction | open, runnable after P1 | same + flip operator |
| P3 4π loop | open, last | same + loop readout |
| λ₂ health meter | proposed (~30 lines) | LISTEN Laplacian + overseer display |

## 8. Sources pinned to this draft

- Cover: "Beyond Imaginary — The Geometric Algebra of Time, Symmetry, and
  Self-Reference" (`q = a+bi+cj+dk`, `S³`, `Sp(1)`, `SU(2)`; cyan/amber/purple key).
- "De-complexifying Quantum Mechanics" page (`Z^α` vs `X^I`, `C^N → R^{2N}`).
- Table rows: #64 (cognitive Laplacian ground state / spectral flow),
  #110 (spectral gap `Δλ₂ ≥ ε`, algebraic connectivity),
  #111 (intrinsic dimensionality contraction),
  #112 (topological stabilization / persistence).

## 9. Next actions (urgent list offload)

1. Add `φ` per monitor + flip operator (wall already has `V`, `w`, ticks).
2. Add `λ₂` meter to overseer.
3. Run M1 → record; M1 decides whether M2/M3 are worth the weld.
4. If F1–F3 all fire: file under "notation, not physics" and close the file.

*End of proof set v0.1.*
