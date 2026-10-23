# The Unified Framework of Self-Reference
*A recursive verification discipline for claims about mathematical/physical theories.*

Every claim must survive four layers applied IN ORDER. Stop at the first FAIL — do not gate-advance,
do not "refine," do not publish a PASS. The framework audits its own auditors (hence "self-reference").

## 0. Precommit (claim is bound to a source)
- Each claim is pinned to a **source artifact + line** before testing begins (notebook cells,
  harness file, or published derivation). Floating claims are disallowed at entry.
- The claim must declare a **falsifiable predicate** and its failure mode, not a narrative.

## 1. Source anchoring (claim cannot float free of proof)
For every sentence of a verdict, cite the minimal cell/file:line range that forces it TRUE.
Any claim with no traceable line is a METHODOLOGY_HOLE and the claim FAILS.
- Evidence template: `[sentence] -> cell[idx]:line | verbatim | PASS|HOLE`
- In our wave-logic run: M2 `corr=1.0` was never persisted in the notebook (only a plot-title
  string) — flagged as partially uncited; `lambda_2=1.0` traced to `get_algebraic_connectivity`
  which ignores phi — hole surfaced.

## 2. Inertness / degeneracy self-attack (the operator must actually engage)
A parametric operator claim ("orientation flip alters transmission") is FAILED if the parameter
is never varied in a way that can move the observable. Test the mechanism, not the metric.
Predicate (per edge `j->i` on the flipped set):
`d_phi(flip) = -phi[j]-phi[i] ; d_phi(nonflip) = phi[j]-phi[i]`.
Claim engages ONLY IF `exists flipped edge with phi[source] != 0 AND phi[target] != 0`
(such that `exp(i*d_phi)` differs and a sign-even observable can distinguish).
- Wave-logic result: flipped edges `L->M` (phi[L]=0) and `2->0` (phi[2]=0) -> inert -> claim FAIL.
- Engagement probe: corrected port with `phi[source]=0.9` + complex hopping drops `corr(M1,M2)`
  1.0 -> 0.0. Engagement in principle is possible, but a clean gated PROFILE was not produced
  (degenerate) — so "distinct profile" remains UNDEMONSTRATED, not PASS.

## 3. Distinguishability (the metric must separate the hypotheses)
For a metric M used to certify hypothesis H over ¬H, require M to be sensitive to the thing H predicts.
- Variance `> 0.01`: construct `B = -A` (same var 0.0946, corr -1.0, opposite physics) -> cannot certify
  orientation gating; it certifies non-flatness only. FAIL as evidence.
- 4π boundary `|V(-2pi)-V(2pi)| < 0.05`: endpoints are identical mod 2π; prove an explicit 4π function
  `cos(phi/2)` AND a 2π function `cos(phi)` both pass -> cannot distinguish periods. FAIL.
- leakage_ratio = 0: prove consistent with both "zero coupling (cos(pi)=0)" (FALSE: cos(pi)=-1)
  and "destructive cancellation (clip maps V[M]=-1 to 0)" -> cannot distinguish; counterexample
  with same `cos(pi)=-1` but leakage=0.40. FAIL.
- lambda_2 = 1.0: prove this is the unweighted P3 path Laplacian (phi-blind `get_algebraic_connectivity`)
  vs the phase-weighted operator (0.8592) vs the `tickVField` generator (not a Laplacian at all)
  -> metric is the wrong operator for the claim. FAIL as evidence.

Predicate pattern: **construct the adversarial pair/triple (same metric, opposite meaning, or
same physics, opposite metric) and show the claim's metric cannot separate them.**

## 4. Corrected port (exhibit the claim under a faithful realization)
Re-implement ONLY the physics the claim invokes, with the minimal change that makes the inert
parameter engage, using a representation the claim actually requires:
- orientation/T-flip -> complex phasor ψ with anti-unitary T (ψ -> ψ*) on the flipped arm, NOT
  a real amplitude (whose `cos(d_phi)` is even and hides the sign).
- 4π double cover -> spinor sign-flip test on the complex ψ, NOT an amplitude boundary sample.
Falsifiable spinor predicate:
```
4pi_cert :  max_phi |psi(phi+2pi) + psi(phi)| < eps   AND   max_phi ||psi(phi+2pi)| - |psi(phi)|| < eps
2pi_only :  max_phi |psi(phi+2pi) + psi(phi)|  is large (>= |psi|)
```
- Must also pass a CONTROL (no-T-flip loop is 2π) to show the T-flip is what drives the sign flip
  (not the flux).
- Result: with anti-unitary T the spinor predicate gave `max|psi(phi+2pi)+psi(phi)| = 1.6` (expect
  ~0) -> **NO sign flip -> 4π NOT demonstrated.** Claim withdrawn, not PASSed.

## 5. Gate discipline (the self-referential check on the framework itself)
The claimant (or wall, or downstream user) advances ONLY when ALL layers pass. Passing one layer
does not license the next. A FAIL at any layer -> the claim is recorded as FAIL/{OPEN} with the
precise failing predicate, and the wall stays gated.
- This framework audits itself at every layer: Layer 1 audits verdicts; Layer 2 audits whether
  the operator engages; Layer 3 audits whether metrics distinguish; Layer 4 audits whether a
  faithful realization exhibits the claim; Layer 5 audits that the prior layers did not skip
  themselves.

## Artifact map (this run)
- `organized/audit_outputs/adversarial/Round_1..10.md` — Layers 1,2,3 applied claim-by-claim.
- `organized/audit_outputs/adversarial/PROOF_PACKET.md` — consolidated verdicts + corrected-port lift.
- `wallfield_corrected.py` + `run_corrected_port.py` + `corrected_port_results.json` — Layer 4 (complex phasor; engagement shown, profile degenerate, 4π not reproduced).
- `run_spinor_4pi.py` + `spinor_4pi_results.json` — Layer 4 spinor predicate (4π NOT demonstrated).
- `organized/scoring_verdicts/scoring_verdict_m1_m2_m3_layered.json` — layered verdicts (logic / phase-model / physical kept separate).

## Verdict record for the wave-logic claims (final, falsifiable)
| Claim | Layer | Predicate outcome | Status |
|---|---|---|---|
| NOT/AND gates (cell 27) | 1,2,3 | NOT always-HIGH; AND = XNOR (`cos` even, 00 and 11 indistinguishable) | FAIL |
| M1 phase-gating | 1,2,3 | max_V_M=0.7989, leakage=0 reproduced; cos(pi)=-1 not 0; leakage=0 is a clip/cancellation artifact | logic PASS, phase PARTIAL, physical OPEN |
| M2 orientation flip is distinct | 1,2,3,4 | inert (source phi=0); engagement only in corrected port, no gated profile | logic FAIL, physical NOT ESTABLISHED |
| M3 4π double cover | 1,2,3,4 | boundary vacuous; spinor predicate max|sum|=1.6 (no sign flip) | logic FAIL, physical OPEN |
| lambda_2=1.0 evidences phase-gating | 1,3 | 1.0 = unweighted P3; phase-weighted=0.8592; tickVField not a Laplacian | FAIL (wrong operator) |

Wall remains GATED. The framework is reusable: instantiate Layers 0-4 against any new claim before any downstream commitment.
