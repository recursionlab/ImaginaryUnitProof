# Adversarial methodology audit prompts

These 10 prompts exist to destroy, before any result reaches a human,
any claim this audit made about the wave-logic theory. Each prompt is a
self-attack on one methodological hinge. They are run against the ACTUAL
notebook source (`mathwork/ImaginaryUnit.ipynb`) and the frozen harness
(`gate_contract_audit.py`), not against hand-transcribed equations.

1. **Cell-anchoring audit.** For every verdict sentence in
   `scoring_verdict_m1_m2_m3_layered.json`, cite the exact notebook cell
   number and the verbatim code line(s) that force that sentence to be true.
   List every claim with NO traceable cell line as a methodology hole.

2. **M2 inertness proof (edge-by-edge).** Print the exact `weights[j,i]`,
   `phi[j]`, `phi[i]`, `d_phi_nonflip = phi[j]-phi[i]`,
   `d_phi_flip = -phi[j]-phi[i]`, and `gating=cos(d_phi)` for EVERY edge
   (j,i) in the M2 sweep at a non-trivial `sweep_phi`. Show that the flipped
   edge `L->M` has `phi[j]=0` and prove the two d_phi values are identical.
   Enumerate: could ANY flipped edge be non-inert in this sweep? (list candidates)

3. **M3 boundary coincidence.** Print `phi_sweeps_m3[0]` and
   `phi_sweeps_m3[-1]`; assert `[0]==[-1] (mod 2*pi)` or `[0]!=[-1] (mod 2*pi)`.
   Construct an EXPLICIT 4*pi-periodic function f with `f(-2*pi)==f(2*pi)`
   (so the notebook's check passes) and prove the check cannot certify 4*pi.
   Give an alternative sweep range that WOULD distinguish the periods.

4. **Variance>0.01 is not evidence.** Construct pair of curves A,B with
   `var(A) = var(B) = 0.0946`, `corr(A,B) = 1.0`, but physically opposite
   meaning (e.g. B=A and B=-A). Prove a variance threshold cannot certify
   "orientation gating activated". Show M1 and M2 satisfy it identically.

5. **Smuggling self-attack.** Prove whether M1≡M2 is (a) identical-by-construction
   under the notebook's sweep, or (b) only under transcription. Build the minimal
   M2 correction (nonzero phase on an M2 flipped-edge endpoint) and compute the
   new corr(M1,M2). Report whether the corrected sweep still matches the notebook's
   `profile_variance=0.0946` claim or changes it.

6. **NOT/AND per-row confusion (multi-seed).** Run cell-27 NOT and AND
   candidates at sigma=0 with 5 seeds; print per-row TP/FP/TN/FN for rows
   00/01/10/11 (AND) and inputs 0/1 (NOT). Identify EXACT broken rows and
   magnitudes. Attack: is the XNOR structure a fundamental algebraic property of
   `cos((phi_a-phi_b)/2)` OR a fixable bug? (prove which)

7. **Leakage-ratio ambiguity.** At phi=pi, the M1 edge S->L has gating
   cos(pi)= -1 (NOT 0). Show numerically that V[M](phi=pi)=0 emerges from
   destructive diffusion dynamics, then construct a DIFFERENT Laplacian/gating
   where cos(pi)= -1 but V[M](pi) != 0. Prove `leakage_ratio=0` is consistent
   with both "zero coupling" and "negative-coupling cancellation" — i.e. the
   reported metric cannot distinguish the two hypotheses.

8. **4pi signature / observable gap.** Re-derive the quaternionic/SU(2)
   4*pi claim: state the minimal observable that flips sign at 2*pi and
   restores at 4*pi. Then prove the notebook's recorded observable (V[2], an
   amplitude) cannot carry that sign; quantify |V[2](phi) - V[2](phi+2*pi)|
   and |V[2](phi) - V[2](phi+4*pi)| over the sweep and show they are ~0.

9. **Lambda-2 misattribution.** Print eigenvalues of (a) the unweighted
   3-cycle Laplacian (P3/K3 standard), (b) the notebook's LISTEN-weighted
   directed graph at a sample sweep_phi, (c) the symmetrized weighted Laplacian.
   Prove λ2=1.0 characterizes (a), NOT the phase-weighted propagation actually
   used in tickVField, and that the reported 1.0 is the wrong operator for the
   claimed "phase-gated connectivity".

10. **Uncited-assumption census.** List every modeling assumption the audit
    relied on without a notebook source citation: truth-table decode rule,
    `GATE_DECISION_THRESHOLD=0.5`, seeds, noise distribution, alpha=0.15,
    30 ticks, 50/100 sweep points. For each, give the cell line that commits
    to it OR flag it as an inherited, uncited assumption. Count total holes.
