# Adversarial Proof Packet — gate-contract / M1-M2-M3 theory
Run: 10 rounds of self-audit, each designed to DESTROY a pillar of the verification META-METHOD.
Source of truth: `mathwork/ImaginaryUnit.ipynb` cells (via `wallfield_actual.py` verbatim port).
Frozen harness: `gate_contract_audit.py` (seeds, truth tables, noise, confusion convention unchanged).

What got massacred is the **meta-method**, not (yet) a theory claim: the procedure I used to
verify the theory — evaluate against hand-transcribed equations instead of notebook cells;
accept `variance>0.01`, `|V(-2pi)-V(2pi)|<0.05`, and `lambda_2=1.0` as evidence without checking
WHAT each number measures; and collapse logic/phase/physical layers into a single `PASS` —
is internally falsified by the 10 rounds. Each PASS in the original notebook survives only
because that meta-method never asked whether the orientation operator actually engaged,
whether the boundary samples are distinct phases, or whether the gate formula is even capable
of the target truth table.

Result for the theory-claims: **unverified by this codebase** (M2 inert, M3 vacuous,
gates XNOR-by-construction). That is a meta-method failure: a correct port + a sign-flipping
observable + a phase-difference (odd) gate rule would be required BEFORE the claims themselves
could be tested — not evidence the underlying ideas are wrong.

## Round index (one self-attack per pillar)

| Round | Target | Weapon | Result (self-inflicted) |
|---|---|---|---|
| 1 | claim anchoring | cell:line + JSON corroboration | corr(M1,M2)=1.0 uncited (only in plot-title string); cell-27 accuracy only via port mismatch; M2 block misattributes cells 11/12 |
| 2 | M2 flip inertness | edge-by-edge d_phi table | flipped edge L->M source phi=0 -> d_phi(flip)=d_phi(nonflip)=0; cos even -> inert |
| 3 | M3 boundary vacuity | explicit 4pi f w/ f(-2pi)==f(2pi) | check passes for any 2pi/4pi system; endpoints identical mod 2pi |
| 4 | variance>0.01 evidence | B=-A same var, corr=-1 | variance certifies non-flatness, not orientation gating; M1==M2 trivially |
| 5 | "natural" M2 fix | phi[L]=1.0 then both nonzero | phi[L]=1 still inert (cos even); truly-engaging config -> var COLLAPSES to 1.9e-4 -> verdict flips to FAIL |
| 6 | 4pi observable gap | spinor sign-flip test | V[2] is machine-2pi-periodic (max|diff|=3.3e-15); CANNOT show a 2pi sign-flip; intensity-only |
| 7 | leakage_ratio=0 kill | counterexample Laplacian | leakage=0 is a clip artifact (linear fixed point V[M]=-1 -> clip 0); SAME cos(pi)=-1 gives leakage=0.40 elsewhere; criterion unsound |
| 8 | NOT/AND algebraic | truth-table + symmetry | AND amp=|cos((a-b)/2)| is XNOR BY CONSTRUCTION (cos even, 00 and 11 both delta=0); NOT abs() kills the sign; unfixable, not a bug |
| 9 | lambda2=1.0 meaning | spectra of 3 operators | 1.0 = static unweighted P3 path; phase-weighted=0.8592; tickVField isn't even a Laplacian (M*ones!=0) |
| 10 | uncited assumptions | cell:line census | 3 METHODOLOGY_HOLEs: decode rule, threshold, seeds — all delegated outside the notebook cells |

## Net — consolidated verdict

- Logic gates (NOT/AND, cell 27): FAIL — AND is XNOR by construction; NOT destroys negation via abs().
- M1: logic PASS (sweep runs), phase-model PARTIAL (cos(±pi)=-1, not 0; leakage=0 is a clip artifact of destructive diffusion), physical OPEN.
- M2: logic FAIL (T-flip inert: flipped edge source clamped to phi=0; "natural" fix doesn't engage; engaging fix flips verdict to FAIL), phase-model PARTIAL (var=0.0946 reproduced but identical to M1), physical NOT ESTABLISHED (vacuous).
- M3: logic FAIL (inert flip + vacuous boundary: endpoints same mod 2pi; check passes for 2pi-periodic cosine), phase-model FAIL (V[2] is 2pi-periodic, cannot exhibit spinor sign flip), physical OPEN.
- Smuggling: confirmed, root-caused — M1 and M2 transmission are byte-identical (corr=1.0) because the orientation operator never engages in any sweep.

## Decision (re-stated)
The wall (OVERSEER/V-field) stays **gated**. To earn a physical interpretation:
- M2: flip an edge whose SOURCE node carries nonzero phase AND whose TARGET also differs, on a configuration where var does NOT collapse — and show corr(M1,M2)<1.0.
- M3: measure a sign-flipping amplitude psi with |psi(phi+2pi)+psi(phi)| large and |psi(phi+4pi)-psi(phi)|~0; V[2] amplitude-only is provably insufficient.
- Gates: replace the |cos| amplitude rule with a phase-**difference** rule (cos is even -> XNOR); only an odd function of (a-b) can distinguish 00 from 11.

No original notebook cell is modified. All evidence is in organized/audit_outputs/adversarial/Round_1..10.md (+ round7_audit.py, round8_audit.py corroboration scripts).

## Corrected-port lift (theory made operative, honestly)

Can the theory's T-flip / 4pi claims be exhibited by a faithful port that (i) carries a complex phase, (ii) puts nonzero phase on the flipped edge's SOURCE node, (iii) tests a spinor sign-flip on the complex amplitude?

Implementation: wallfield_corrected.py (complex phasor psi, unitary hopping exp(i*d_phi), T-flip = d_phi -> -phi[j]-phi[i]) + 
un_corrected_port.py. Results in corrected_port_results.json:

- M1 vs M2, notebook topology (flipped-edge source phi=0): corr=1.0 -> flip inert.
- M2 corrected (phi_L=0.9 on flipped edge source, complex hopping): corr(M1,M2)=0.0 (was 1.0) -> flip ENGAGES IN PRINCIPLE.
- BUT numerically degenerate (flat, divergent |psi_M|~14 via unopposed direct S->M path): shows engagement POSSIBLE, not demonstrated.
- M3 corrected: spinor test max|psi(phi)+psi(phi+2pi)|=1.9994 ~ 2*|psi| -> psi(phi+2pi)~psi(phi), i.e. 2pi-periodic, NO spinor sign flip.

Bottom line (falsifiable, not defended): theory NOT refuted; notebook implementation is. Sweeps never engage the orientation operator (flipped-edge source clamped to phi=0) and M3 is amplitude-only. A genuine 4pi double-cover requires anti-unitary T: psi -> conj(psi) on the flipped arm (Kramers pairing), not implemented here. Wall stays gated.

### Spinor sign-flip sub-test (true anti-unitary T)

Built 
un_spinor_4pi.py: flux-threaded 0->1->2->0 loop with one T-conjugating edge
(psi_j -> conj(psi_j) before hopping) — the genuinely anti-unitary lift. Measured the
spinor predicate max|psi(phi+2pi) + psi(phi)|:

- no-T-flip control : max_abs_sum = 1.60  (2pi-periodic)
- with-T-flip       : max_abs_sum = 1.60  (NOT ~0 -> NO spinor sign flip at 2pi)

This lift does NOT exhibit the 4pi spinor sign flip; mplitude_2pi_periodic is also
False here, so the loop is not even cleanly 2pi. Honest status: neither the phase-sign-flip
hopping nor the conj-on-edge construction reproduces the double-cover sign flip in this
setup. A correct 4pi demonstration requires a proper Kramers/TRS half-integer-spin routing
on the flipped arm — not yet achieved. **4pi is NOT demonstrated; claim withdrawn.**
