# A Falsifiable Polycomputer Time-Folding Experiment

## 0. One-paragraph design

Drive a quasi-2D microtubule-kinesin **active nematic** (the substrate with the strongest published topological-defect-braiding data, [Nature Physics 2019](https://www.nature.com/articles/s41567-019-0600-y)) under a **programmable periodic drive** (candidate Floquet / discrete-time-crystal condition = "time-folding"). From the **same** recorded defect worldlines, four "observers" — each a 5-tuple frame on the dual crystal — extract four different invariants simultaneously: classical braid entropy, non-abelian anyonic fusion/braiding statistics, subharmonic (period-doubled) time response, and non-Hermitian transport. The substrate is a **polycomputer** iff ≥2 of these readings are simultaneously valid and non-redundant; it is **time-folding** iff the drive yields persistent subharmonic defect motion; it realizes the **quantum categorical layer** iff the defect braiding is non-abelian (multi-channel fusion, non-commuting braid representation). Each clause is independently falsifiable.

---

## 1. Why this substrate and this drive

- **Active nematic** defects (+1/2, -1/2 disclinations) are already known to braid in space-time with measurable topological entropy and to realize the "golden braid" ([arXiv:2401.04363](https://arxiv.org/html/2401.04363v1); [Frontiers 2022](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2022.880198/full)). This is the *one* biological-matter system where the braiding observable is established, so it is the natural place to ask the next question.
- A **periodic drive** (oscillatory ATP concentration, oscillatory confinement, or AC field) imposes a discrete time-translation symmetry \(H(t)=H(t+T)\). Persistent response at \(2T\) (period-doubling) in the many-defect limit is the operational definition of a **discrete time crystal** ([Nature Materials](https://www.nature.com/articles/s41563-018-0127-0); [arXiv:1704.03735](https://arxiv.org/abs/1704.03735)). This is the literal "folding" of the time direction into a lattice period — the same compactification that curls a quasicrystal's perpendicular space into a circle.
- Floquet topological **defects** are a recognized object ([PRB 2017](https://link.aps.org/doi/10.1103/PhysRevB.96.195303)), so a driven active nematic is a legitimate setting in which both the Floquet and the defect-braiding pictures are simultaneously meaningful.

## 2. The four observers = four 5-tuple frames on the dual crystal

Per the frame ontology \(F=(\)DOMAIN, PERSPECTIVE, DIRECTION, POLARITY, LEVEL\()\):

| Observer | Frame | What it reads from the same defect data | Established? |
|---|---|---|---|
| **A. Classical-braid** | DOMAIN=\(\Lambda\) (geometric), LEVEL=1 | Topological entropy of defect worldlines via pseudo-Anosov braid growth | Yes ([Nature Physics 2019](https://www.nature.com/articles/s41567-019-0600-y)) |
| **B. Quantum-categorical** | DOMAIN=\(\Gamma\) (categorical), LEVEL\(\geq 2\) | Non-abelian certification: (i) multi-channel "fusion" on defect pair annihilation/merger, (ii) non-commuting braid representation (\(\sigma_1\sigma_2\neq\sigma_2\sigma_1\)) on measured observables | Protocol adapted from anyon certification ([Nature 2023](https://www.nature.com/articles/s41586-023-05954-4); [Nature Physics 2024](https://www.nature.com/articles/s41567-024-02529-6)) |
| **C. Time-crystal** | DIRECTION=\(\pm\) on the time axis | Subharmonic response: defect density/position spectrum peaked at \(2T\) (not \(T\)), persistent in the many-defect limit | Standard DTC test |
| **D. Non-Hermitian** | POLARITY (directed transport) | Non-reciprocal defect transport; exceptional points in the driven response (cf. [arXiv, C. elegans active matter](https://arxiv.org/search/cond-mat?searchtype=author&query=Ozdemir,+S+K)) | Established in active matter |

**Eversion** (the perspective-flip operator) is what maps one observer's reading onto another: each observer reads the *same* Wilson-loop/curvature object \(\tau\) from a different frame. Polycomputing is confirmed exactly when \(\tau\) is non-trivial *and* non-redundant across frames — i.e., the dual crystal's geometric and categorical faces are physically co-realized, not merely verbally distinct.

## 3. Measurements

1. **Track** all \(+1/2\) and \(-1/2\) defect worldlines over the driven steady state (particle-image-velocimetry + defect-detection, standard for active nematics).
2. **Observer A**: compute braid entropy \(h_{\mathrm{T}}\) from worldlines; confirm pseudo-Anosov growth.
3. **Observer B**: for every defect-pair merger/annihilation event, record the set of distinguishable outcome channels \(N_{ab}^{c}\); construct the effective braid-group representation on a measured observable basis and test whether \(\sigma_1\sigma_2-\sigma_2\sigma_1\neq 0\) (non-commuting, i.e. \(R^{2}\) is a matrix not a scalar).
4. **Observer C**: Fourier-analyze defect density/mean position as a function of drive phase; test for a persistent \(2T\) (period-doubled) component that survives increasing system size / defect number (the finite-size persistence is the key non-triviality, [Nature Materials](https://www.nature.com/articles/s41563-018-0127-0)).
5. **Observer D**: measure directionality of defect drift under symmetric drive; look for exceptional-point signatures (coalescence of modes under parameter sweep).

## 4. Controls

- **Undriven control**: run the same active nematic with no periodic drive. Observer A should still see braid entropy; Observers C and D should see *no* \(2T\) peak and *no* driven non-reciprocity. This isolates the Floquet contribution.
- **Classical-model null**: fit a deterministic hydrodynamic active-nematic simulation (no quantum degrees of freedom) to the data. If it reproduces Observers A, C, D within error, then any "polycomputing" reading must reduce to this classical model — i.e. the polycomputing is verbal, not physical (Occam falsifier).
- **Abelian-baseline control**: in a system known to host only abelian statistics, Observer B must return a unique fusion channel and a scalar \(R^{2}\). The protocol's discriminating power is validated by returning "abelian" here.

## 5. Falsifiers (any one of these kills a claim)

| Claim | Falsifier | Label |
|---|---|---|
| Quantum categorical layer | **F1**: braid representation is abelian — unique fusion channel (\(a\times b=c\), not \(c+d\)), \(R^{2}\) a scalar, fully reproduced by classical pseudo-Anosov entropy | Kills quantum categorical |
| Time-folding (DTC) | **F2**: no persistent \(2T\) subharmonic response in the many-defect limit; any period-doubling is transient or finite-size only | Kills time-folding |
| Polycomputing | **F3**: only one observer's reading is non-redundant; the others are re-expressions of the same classical computation (e.g. the non-Hermitian and braid readings collapse to the same \(h_{\mathrm{T}}\)) | Kills polycomputing (→ monocomputing with multiple descriptions) |

## 6. Decision tree and what each outcome means

| F1 | F2 | F3 | Verdict |
|---|---|---|---|
| survives | survives | survives | **Polycomputing time-folding substrate with a quantum categorical layer.** First biological instance of non-abelian/topologically-protected structure. |
| fires | survives | survives | **Classical polycomputer time crystal** in biological active matter. Quantum categorical layer absent, but time-folding and genuine multi-observer computation hold. Real, publishable, and still a categorical-layer signature in its classical (braid-group) shadow. |
| fires | fires | survives | Polycomputing holds, but no time-folding and no quantum layer. The substrate computes multiple non-redundant classical things simultaneously. |
| fires | fires | fires | **Null.** The substrate is a single classical computation with multiple verbal descriptions. The dual crystal's "multiple faces" are not physically co-realized; the framework's bridges remain valid as mathematics but have no biological instantiation. |

## 7. Honest priors and why run it anyway

The active nematic is a **classical** active-matter system. The prior is therefore that **F1 fires** (defect braiding is abelian / pseudo-Anosov, not anyonic) and likely **F2 fires** (no true DTC, since thermal/active fluctuations usually preclude the many-body coherence a DTC needs). If both fire, the experiment's value is that it *falsifies the quantum-categorical-biology and time-folding-biology claims at the smallest possible cost* — converting a sprawling speculative framework into a clean negative result with a defined boundary: biology realizes the **classical** (geometric, braid-group, non-Hermitian) face of the dual crystal, not the quantum categorical face.

The only way the framework survives as biology rather than as mathematics is the top row of the decision tree: F1, F2, F3 all survive. That would require defect braiding to be non-abelian *and* the drive to produce a persistent many-body subharmonic response. Neither has ever been observed in a classical active nematic, so the experiment is genuinely decisive — and a null result is the informative, expected, honest outcome.
