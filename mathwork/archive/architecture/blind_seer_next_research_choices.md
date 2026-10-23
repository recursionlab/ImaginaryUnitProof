# Blind Seer / STER — Next Research Choices

**Purpose:** choose the next work packages by evidential value, dependency order, and risk of generating another impressive but unsupported synthesis. This roadmap is based on the results and claims in the supplied conversation; it does not claim that the repository was independently inspected or that the reported runs were rerun in this session.

## Executive decision

**Choose B first, but narrow it:** derive and characterize the defect between the *independently defined* raw extraction-with-pair map `tau2` and the standard antipode `S`; then define and test the nontrivial phase-transport map `Phi_c`. Do not claim `tau2 = S`. The degree-3 and degree-4 audit already indicates that the raw map differs from the antipode.

**Treat A (degree-4 enumeration) as completed for the standard identity-transport toy algebra.** Extend to degree 5–6 only after the residue recurrence and tree/cut conventions are locked. More brute-force enumeration is not the main intellectual bottleneck.

**Keep the spectral scaling as a generic operator theorem, not a prime-specific result.** The supplied chain controls report that random integers reproduce the prime-weighted behavior. A prime-specific research track is justified only if the operator construction is defined independently and a preregistered statistic differentiates primes from matched null models.

**Keep the kink as an open variational problem.** Do not promote the old profile to a physical soliton. A smooth-reference relative functional is a mathematical comparison, not evidence that either profile is stationary. First solve or disprove the actual nonlocal Euler–Lagrange boundary-value problem.

## Ranked choices

### Priority 1 — B: characterize the `tau2` defect (highest value, low-to-medium risk)

Define

`tau2(T) = -T + sum_c P^c(T) R^c(T)`

and

`r(T) = tau2(T) - S(T)`.

From the standard antipode recursion,

`r(T) = sum_c (P^c(T) + S(P^c(T))) R^c(T)`.

Since `S(P) = tau2(P) - r(P)`, derive the recursive defect equation

`r(T) = sum_c (P^c(T) + tau2(P^c(T)) - r(P^c(T))) R^c(T)`.

This is useful only if `tau2` remains independently defined and the recurrence gives structural insight beyond restating the antipode recursion. Compare coefficients by tree shape, not just degree; distinguish plane from non-plane trees and edge cuts from admissible multi-edge cuts.

### Priority 2 — define `Phi_c` and test the custom phase-tree Hopf structure (highest dependency value)

The existing exact audit used identity phase transport. Before interpreting results as STER/PIC, define `Phi_c` on a basis and composition of nested cuts. Test unit/counit, coassociativity, multiplicativity where required, and both antipode convolution identities. A useful outcome can be a counterexample: if coassociativity fails, locate the smallest tree and the exact `Phi` composition defect.

Do not assume the condition `Phi_(c2 after c1) = Phi_c2 o Phi_c1` is sufficient until the coproduct's domains/codomains and cut composition are made precise.

### Priority 3 — scale the combinatorics only after the recurrence is clear

Enumerate all rooted-tree shapes through degree 5 or 6, all admissible cuts including multi-edge cuts, `tau2`, `S`, the defect `r`, and shape-deformation differences. Use exact integer/rational coefficients. Validate independent implementations against one another and preserve a compact counterexample ledger. Degree extension without a clear invariant or conjecture is lower value.

### Priority 4 — prime-specific spectral claim (high potential, high risk)

Treat `d_s = 2/q` for the continuum generator with symbol `|k|^q` as generic scaling. Do not claim primes generate `d_s = 1/2`; the provided controls do not support that. Only proceed with the block-chiral/GUE direction if the matrix/operator is explicitly defined from the source material. Preregister the statistic, eigenvalue window, unfolding method, sample size, and matched controls before examining outcomes. Controls should include random integers in the same range, shuffled log gaps, degree/weight-preserving graph surrogates, and a unit-chain baseline. Report null results as first-class outcomes.

### Priority 5 — kink sector (medium value, high model risk)

Keep the old odd profile as a trial ansatz, not a solution. Solve the actual nonlocal Euler–Lagrange equation with explicit boundary conditions and consistent operator normalization. Test domain-size and mesh convergence, residual norms, fluctuation stability, and energy differences against smooth references in the same asymptotic sector. Separate infrared subtraction from ultraviolet regularity. Do not call a finite reference-dependent number a physical rest mass without a stationary solution and a justified energy functional.

### Priority 6 — independent literature and novelty review

Only after the claims are typed and the constructions are stable, search prior work on rooted-tree antipodes/cut recursions, defect/cumulant recurrences, fractional Allen–Cahn-type equations, fractional kink energy, spectral dimension of powers of Laplacians, prime-related random-matrix statistics, and spectral trace formulas. The purpose is to identify exact overlap and a defensible novelty delta, not to find analogies that sound similar.

## Do not choose next

- **D: claim raw `tau2` satisfies the antipode identity.** The supplied exact audit contradicts it from degree 3 onward.
- **E: declare the old kink ansatz a physical soliton.** Its Euler–Lagrange residual is nonzero; the mass integral evaluated a stipulated density, not an established on-shell energy.
- **F: merge all tracks into one master theory now.** Hopf combinatorics, nonlocal variational analysis, and prime spectral statistics have different objects, assumptions, and validation criteria. Premature synthesis conceals failure modes.
- **Unfocused extra degree enumeration.** Do not scale up until the defect recurrence or `Phi_c` supplies a specific conjecture to test.

## Copy-ready Deep Research prompts

### Prompt 1 — Defect recurrence (run first)

> Investigate the independently defined extraction-with-pair map `tau2(T) = -T + Σ_c P^c(T)R^c(T)` in the standard Connes–Kreimer rooted-tree Hopf algebra, where the sum includes every nontrivial admissible cut, including multi-edge cuts. Define `r(T)=tau2(T)-S(T)` and derive its exact recursion from the standard antipode recursion without defining `tau2` in terms of `S`. Prove the recurrence `r(T)=Σ_c(P^c(T)+tau2(P^c(T))-r(P^c(T)))R^c(T)` under explicit conventions. Calculate exact results for every rooted-tree shape through degree 4, and independently verify the degree-3 chain/star and all degree-4 defects. Determine whether the recurrence yields a new structural characterization or merely rewrites the known antipode recursion. Do not claim `tau2=S`; preserve counterexamples and give a proof/counterexample ledger.

### Prompt 2 — Phase transport and Hopf validity (run second)

> Define the missing phase-transport map `Phi_c` for a phase-tree coproduct. First specify its domain/codomain, action on basis trees/forests, compatibility with multiplication, and how it composes for nested or disjoint admissible cuts. Then test the coproduct's unit, counit, coassociativity, and the two antipode convolution identities exactly on all trees through degree 4. Do not assume a cocycle condition is sufficient without proving it for the chosen cut convention. If a condition fails, return the smallest counterexample and explicit tensor expressions. Separate established Connes–Kreimer results from new STER/PIC definitions.

### Prompt 3 — Exact enumeration to degree 6

> Extend the verified rooted-tree cut enumeration to all non-plane rooted-tree shapes through degree 6 (and keep a separate mode for plane trees if the theory requires them). Use exact integer coefficients; enumerate admissible antichains of edges correctly; compute `tau2`, the standard antipode, `r=tau2-S`, and deformation differences between specified tree shapes. Test any proposed coefficient or branching invariant against all shapes, not selected examples. Cross-check with an independent implementation or hand-derived low-degree cases. Output CSVs, a tree-shape convention, source code, verification tests, and explicit failures. Do not infer topological invariance from a finite coefficient pattern.

### Prompt 4 — Decide if the defect has independent content

> Conduct a hostile mathematical review of the raw extraction-with-pair defect `r(T)=tau2(T)-S(T)`. Search prior work on antipode recursions, Möbius inversion, admissible cuts, forest products, cumulant/inclusion–exclusion corrections, and rooted-tree combinatorics. Determine whether the defect recurrence yields a genuinely new theorem, a known identity in different notation, or only a diagnostic residual. State the exact novelty delta, weakest assumptions, a theorem that could be proved, and a counterexample that would invalidate the strongest claim. Do not market notation changes as novelty.

### Prompt 5 — Fractional kink existence, not ansatz rescue

> For `D=|D|` and the specified double-well nonlinearity, investigate existence of a stationary odd heteroclinic connecting `-v` to `+v` under explicit function spaces and boundary conditions. Do not assume `psi_a(x)=v x/sqrt(x^2+a^2)` is a solution. Derive the Euler–Lagrange equation from a declared functional, assess whether the heteroclinic can have finite unrenormalized `H^{1/2}` kinetic energy, and separate existence, asymptotic tail, stationarity, stability, and energy finiteness. Compare smooth same-sector reference energies with consistent IR/UV regulators. Return a theorem if available or a precise numerical research problem with convergence and falsification criteria.

### Prompt 6 — Relative-energy scheme audit

> Analyze relative kinetic energies between smooth profiles with the same asymptotic phases for the one-dimensional half-Laplacian. Verify the Bessel transform formula and the finite difference `E_a-E_b=(2v^2/pi) log(b/a)` under the stated Fourier convention. Then vary the reference profile and regulator scheme to identify which quantities are invariant and which are reference-dependent. Audit the potential contribution separately. Never call the resulting trial-profile difference a soliton mass unless the profiles satisfy the field equation and the variational stability requirements.

### Prompt 7 — Prime spectral claim under preregistered controls

> Evaluate the claim that prime-derived structure contributes spectral information beyond generic weighted chains. First recover the exact block-chiral operator matrix and its construction from the project materials; if unavailable, report this as a blocker rather than inventing a matrix. Preregister matrix size, eigenvalue window, unfolding method, spacing-ratio statistic, control distributions, and rejection criterion before calculating. Compare primes against matched random integers, shuffled log gaps, weight/degree-preserving surrogates, and a uniform chain. Use known random-matrix benchmarks cautiously and account for finite-size effects. Distinguish a generic `d_s=2/q` heat-kernel scaling law from any prime-specific spectral statistic.

### Prompt 8 — Generic spectral scaling versus graph measurements

> Derive the continuum heat-kernel scaling for a one-dimensional translation-invariant generator with symbol `|k|^q`, showing which assumptions yield `Theta(t) ~ C t^(-1/q)` and `d_s=2/q`. Then analyze why finite weighted-chain estimates can deviate. Separate the continuum theorem, finite-size estimator, graph topology, edge weighting, and empirical fit-window uncertainty. Reproduce the unit-chain, prime-weighted, and random-integer comparisons with fixed estimators and sensitivity analysis. Do not call the `d_s=1/2` value prime-generated unless matched controls reject the generic explanation.

### Prompt 9 — Claim dependency and source-grounding audit

> Build a claim-dependency graph for the current STER program. For every claim, list definitions, lemmas, numerical evidence, external prior art, upstream assumptions, and downstream claims that depend on it. Mark unsupported bridges (especially `tau2` to antipode, PIC to Rota–Baxter, prime trace to a spectral operator, and spectral dimension to physical/cosmological claims). Identify the minimal set of upstream results that must be validated before any synthesis paper is defensible. Do not silently repair gaps; enumerate them with exact required evidence.

### Prompt 10 — Independent red-team replication

> Reproduce the strongest surviving claims from a clean implementation that does not reuse the original enumeration or analysis functions. The targets are: (1) the standard antipode and `tau2` defect through degree 4; (2) the half-Laplacian relative-energy cutoff asymptotics; and (3) the generic heat-trace scaling for a chosen operator. Use exact arithmetic for tree algebra and independent numerical methods for continuum integrals. Compare outputs item-by-item, record discrepancies, and stop any claim whose independent reproduction fails. A successful reproduction verifies only the stated calculation, not broader physical interpretations.

## Recommended execution order

1. Prompt 1 — defect recurrence.
2. Prompt 2 — define/test `Phi_c`.
3. Prompt 4 — establish novelty before scaling.
4. Prompt 3 — extend exact enumeration only if a new invariant/conjecture remains.
5. Prompt 8 — lock generic spectral scaling and control interpretation.
6. Prompt 7 — prime-specific test only with the source matrix recovered.
7. Prompts 5–6 — kink existence and relative-energy research as a separate track.
8. Prompt 9 — maintain the dependency ledger throughout.
9. Prompt 10 — independent red-team replication at release gates.

## Work ledger fields

`Prompt ID | Source revision | Hypothesis | Definitions fixed? | Evidence gathered | Tests run | Result | Counterexample | Claims retracted/modified | Artifact paths | Next permitted action | Blocker evidence | Reviewer`

**Final rule:** do not reward output volume. A research run counts as progress only when it produces a verified result, a reduced uncertainty, a counterexample, a corrected artifact, or a precisely evidenced blocker.
