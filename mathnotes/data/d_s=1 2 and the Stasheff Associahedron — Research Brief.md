# \(d_s = 1/2\) and the Stasheff Associahedron — A Falsification-Oriented Research Brief

**Method.** Per the standing instructions, this brief treats the prompt as a
*structural fossil record*: it extracts the skeletal architecture, separates every
claim into established / evidence-supported / proposed / speculative, and tries to
kill the speculative bridges rather than forcing the interpretation or importing
concepts merely because they sound compatible. The accompanying executable
`k4_pentagon_laplacian.py` computes what is genuinely computable on \(K_4\) and
marks the speculative identifications as unconfirmed.

---

## 1. The computational graph (skeleton)

The prompt chains six objects:

\[
d_s=\tfrac12\;(t^{-1/4}\text{ heat trace})
\;\xrightarrow{\text{prime coherence}}\;
\text{adelic Mellin / local }L\text{-factor}
\;\xrightarrow{e^{-W}}\;
\text{metric associahedron }K_n
\;\xrightarrow{\Pi_n}\;
\overline{\mathcal M}_{0,n+1}(\mathbb R)\to \mathrm{BHV}_n
\;\xrightarrow{H^2\text{ obstruction}}\;
\text{unitary RG fixed point}
\;\xrightarrow{\text{MacMahon}}\;
Z(t,q,z).
\]

The honest question is: **which arrows are theorems, which are bridges, and which
are forced identifications?** The audit below classifies each.

## 2. Claim classification

| # | Claim | Status | Nearest established literature |
|---|-------|--------|-------------------------------|
| C1 | Spectral dimension \(d_s\) defined by heat trace \(K(t)\sim t^{-d_s/2}\); so \(d_s=1/2\Leftrightarrow t^{-1/4}\) | **Established** (definition) | Spectral dimension in fractal / QG literature ([arXiv:2604.00033](https://arxiv.org/html/2604.00033v1)) |
| C2 | A *prime-coherence Hamiltonian* produces \(d_s=1/2\) with \(S(t)\sim\log(1/t)^{0.25}\) | **Premise / unverified** — no primary source found. Note \(S(t)\sim\log(1/t)^{0.25}\) does **not** follow from \(d_s=1/2\); it is part of the same unverified premise | p-adic heat kernels exist ([Taibleson/Vladimirov](https://msp.org/pjm/2008/237-2/pjm-v237-n2-p06-s.pdf); [Albeverio–Karwowski](https://arxiv.org/pdf/1701.08732)) but **no \(d_s=1/2\) result is established there** |
| C3 | Associahedron \(K_n\) has a cubical decomposition (one cube per planar binary tree) | **Established** | [arXiv:0710.0572](https://arxiv.org/pdf/0710.0572v2); [Loday, Clay notes](https://www.claymath.org/library/academy/LectureNotes05/Loday.pdf) |
| C4 | The cube count is \(C_{n-1}\) cubes of dimension \(n-2\) | **Evidence-supported, convention-sensitive** | Catalan \(C_k\) counts triangulations of a \((k+2)\)-gon; indexing shifts by convention (off-by-one risk) |
| C5 | Orientable cover of \(\mathcal M_{0,n+1}(\mathbb R)\) is tiled by associahedra and resolves BHV singularities | **Established** | Devadoss–Morava, [arXiv:1009.3224](https://arxiv.org/abs/1009.3224); Devadoss–Forcey, [arXiv:2408.03431](https://arxiv.org/html/2408.03431v1) |
| C6 | The projection \(\Pi_n\) is generically \(2^{n-1}\)-to-1 | **Unverified** — the checked primary sources state only "collapsing and folding" and give **no degree**; the multiplicity is map / labeling / orientation-cover dependent and must not be asserted as \(2^{n-1}\) (nor replaced by another unverified number such as \((n-1)!/2\)) | Same Devadoss–Morava / Devadoss–Forcey sources |
| C7 | A path-weight coordinate \(x_i=e^{-W_i}\) maps metric planar trees to ordered real configurations | **Plausible, needs exact citation** — directionality matters: \(e^{-W}\) maps additive path weights to multiplicative coordinates; \(-\log x\) maps multiplicative scales to additive lengths | [arXiv:1009.3224](https://arxiv.org/abs/1009.3224); the exact formula needs a primary-source check |
| C8 | The map \(e^{-W}\) is a *conformal regularizer* sending prime multiplicative independence onto the additive cubical boundary of \(K_n\) | **Proposed bridge** (not a theorem) | No primary source combines primes with associahedral boundary geometry |
| C9 | \(H^2(B,\mathfrak g)\neq0\) obstruction ("SI-defect") to flat gluing; RG flow contracts rep space to a unitary phase matching \(d_s=1/2\) | **Speculative** | Gerbe/2-cocycle obstructions are real (\(H^2\) classifies central extensions), but the "RG fixed point = \(d_s=1/2\) vacuum" link is ungrounded |
| C10 | Local \(L\)-factor at prime \(p\) maps to the transition matrix of a random walk on the 1-skeleton of \(K_n\) | **Speculative analogy** | Adelic Mellin transforms are real ([Tate](https://empslocal.ex.ac.uk/people/staff/mrwatkin/zeta/padicreview.pdf)); the specific map to associahedron random walks is not established |
| C11 | MacMahon generating function + \(\mathrm{Vol}(K_n)\) combine into a heat-trace partition function with \(t^{-1/4}\) asymptotics | **Proposed ansatz** (not derived) | MacMahon / crystal melting is established ([Okounkov–Reshetikhin](https://link.springer.com/content/pdf/10.1007/JHEP07(2015)097.pdf)); Loday volume formulas exist; their *combination forcing \(t^{-1/4}\)* is not |
| C12 | \(i^i=e^{-\pi/2}\) is the conformal anomaly of \(K_4\) collapsing to the real sector | **Speculative / forced identification** | \(i^i=e^{-\pi/2}\) is a standard principal value; its identification with a \(K_4\) conformal anomaly is not grounded |

## 3. Kill tests (what would falsify each bridge)

- **Kill C8 (prime → associahedron conformal map).** If the spectrum of the
  Laplacian on the \(K_n\) cubical complex (or its \(n\to\infty\) limit) does **not**
  have an asymptotic heat trace \(t^{-1/4}\) independent of the prime lattice, the
  "conformal regularizer" claim is dead.
- **Kill C9 (RG → \(d_s=1/2\) unitary phase).** Require an explicit RG beta-function
  on the representation space whose unique attractive fixed point has heat-trace
  exponent \(1/4\). Absent the beta-function, this is a slogan.
- **Kill C10 (local \(L\)-factor → random-walk transition matrix).** Require that the
  Euler product of the walk's spectral zeta on the 1-skeleton reproduces the
  Artin/local \(L\)-factor of a specified prime. No such derivation exists.
- **Kill C12 (\(i^i\leftrightarrow K_4\) anomaly).** Require an anomaly whose value
  is *derived* from \(K_4\)'s geometry and *equals* \(e^{-\pi/2}\). The stub computes
  the \(K_4\) Laplacian spectrum and finds **no** such derived anomaly; \(e^{-\pi/2}\)
  appears only as a pasted-in diagnostic target. This is the clearest forced
  identification in the prompt.

## 4. Corrected 5-point hypothesis (every bridge conditional)

1. **(Definition, established.)** If a space carries a heat trace
   \(K(t)\sim t^{-d_s/2}\), then \(d_s=1/2\) is *equivalent* to \(K(t)\sim t^{-1/4}\).
   The \(d_s=1/2\) claim is well-posed *only if* a Laplacian with this asymptotic
   is specified.

2. **(Premise, unverified.)** *If* a prime-coherence Hamiltonian is defined whose
   return probability scales as \(t^{-1/4}\), *then* \(d_s=1/2\) follows — but the
   existence of such a Hamiltonian is a premise, not an established result; no
   p-adic/adelic heat-kernel source supplies it, and \(S(t)\sim\log(1/t)^{0.25}\)
   does not follow from \(d_s=1/2\) (it is part of the same premise).

3. **(Bridge, proposed.)** *If* a path-weight coordinate \(x_i=e^{-W_i}\) is applied
   to a prime-indexed multiplicative lattice, *then* it maps additive path weights
   to multiplicative coordinates (and \(-\log x\) maps back) — but the further claim
   that this *conformally* realizes the \(d_s=1/2\) scaling on the associahedral
   boundary is not proven; it requires the cubical-complex Laplacian to have a
   convention-independent \(t^{-1/4}\) asymptotic in the \(n\to\infty\) limit.

4. **(Bridge, proposed.)** *If* the origami projection \(\Pi_n\) has a nontrivial
   \(H^2\) obstruction to flat gluing, *then* it is a candidate gerbe/2-cocycle
   class — but the generic fiber multiplicity \(2^{n-1}\) is unverified (the
   established Devadoss–Morava statement is "collapsing and folding," no degree
   given), and the RG contraction to a unitary \(d_s=1/2\) phase is ungrounded.

5. **(Synthesis, speculative.)** *If* a regulated partition function
   \(Z(t,q,z)=\sum_n z^{n}\,\mathrm{Vol}(K_n,g_n)\,M(q)^{\alpha_n}\,
   \mathrm{Tr}(e^{-t a_n\Delta_{K_n}})\) is defined, *then* \(d_s=1/2\) would require
   its small-\(t\) asymptotics to force \(Z\sim t^{-1/4}\) — a condition **not**
   guaranteed by MacMahon's function \(M(q)\) or by \(\mathrm{Vol}(K_n)\) alone.

## 5. Heat-trace partition function (ansatz, not derivation)

A well-posed *ansatz* combining the established ingredients (MacMahon crystal
melting, Loday volume) with the heat trace must include a regulator, a per-level
Laplacian scale, and a specified metric and order of limits — otherwise the sum
over \(n\) is not well-posed:

\[
\boxed{\;Z(t,q,z)=\sum_{n\ge 2} z^{n}\,\mathrm{Vol}(K_n,g_n)\,\bigl[M(q)\bigr]^{\alpha_n}\,\mathrm{Tr}\!\bigl(e^{-t\,a_n\,\Delta_{K_n}}\bigr)\;}
\]

where \(M(q)=\prod_{k\ge1}(1-q^k)^{-1}\) is the MacMahon function, \(g_n\) a chosen
metric on the \(K_n\) cubical complex, \(a_n\) a per-level energy scale, \(z\) a
fugacity/regulator controlling large-\(n\) convergence, and the order of the limits
\(n\to\infty\), \(t\to0\), \(q\to0\) must be fixed. The **\(d_s=1/2\) requirement**
is a *constraint* on this ansatz:

\[
Z(t,q\to0)\;\stackrel{?}{\sim}\;t^{-1/4}.
\]

This is **not** automatic: the \(q\)-asymptotics are controlled by MacMahon, while the
heat-trace exponent is controlled by the *spectral density* of \(\Delta_{K_n}\) in the
\(n\to\infty\) limit. The two are independent unless a theorem links them. No such
theorem is known, so the ansatz is a target for future derivation, not a result.

## 6. The \(K_4\) stub: what is and is not computed

`k4_pentagon_laplacian.py` computes, honestly and without fabricated anomalies:

- the 5 triangulations of the pentagon (= Catalan \(C_3\)) and their flip graph
  (the 1-skeleton of \(K_4\), the cycle \(C_5\));
- the **exact (SymPy, symbolic) spectrum** of the unweighted \(C_5\) graph Laplacian:
  \(0\) (once), \((5-\sqrt5)/2\) (twice), \((5+\sqrt5)/2\) (twice), spectral radius
  \((5+\sqrt5)/2\approx 3.618\);
- the induced metric \(G_{ij}\) (Gram matrix of edge vectors of a regular pentagon,
  side \(2\sin(\pi/5)\));
- a **properly-posed Dirichlet finite-difference Laplacian** on the pentagonal domain
  (diagonal \(4/h^{2}\), off-diagonal \(-1/h^{2}\), outside values fixed to 0), with
  lowest eigenvalues and the mesh-dependent (\(\sim 1/h^{2}\)) spectral radius;
- \(e^{-\pi/2}\) printed **only as a diagnostic target**, explicitly not derived.

**Central falsification point (the load-bearing result).** The heat-trace asymptotics
of *ordinary* \(K_4\) geometry are fixed by the dimension of the object the Laplacian
lives on:

| Object | \(\mathrm{Tr}(e^{-t\Delta})\) as \(t\to0\) | spectral dimension |
|---|---|---|
| 2D pentagonal domain | \(\sim t^{-1}\) | \(d_s=2\) |
| metric graph (1-skeleton) | \(\sim t^{-1/2}\) | \(d_s=1\) |
| finite graph \(C_5\) | \(\to N\) (slope \(\to0\)) | none |

Therefore \(d_s=1/2\) **cannot** come from ordinary \(K_4\) geometry — it is below
the metric-graph value \(d_s=1\). Realizing \(d_s=1/2\) would require a
singular/fractal \(K_\infty\) limit, subordinated or fractional diffusion, or a
nonstandard Laplacian. This is the strongest falsification of the prompt's core
identification: unless such a singular limit is constructed and shown to have
\(t^{-1/4}\) return probability, the link from \(K_n\) to \(d_s=1/2\) does not hold.
The stub thus *sets up* the question (exact spectrum, proper domain Laplacian,
metric) without faking the asymptotics.

## 7. Bottom line

The architecture is real where it is established (associahedral cubical complex,
Devadoss–Morava tiling of \(\mathcal M_{0,n}(\mathbb R)\), MacMahon, \(i^i\)). The
**load-bearing speculative links** are: (i) a prime-coherence Hamiltonian with
\(d_s=1/2\) (premise, no source); (ii) the \(e^{-W}\) map as a conformal prime→
associahedron regularizer (proposed bridge); (iii) the \(2^{n-1}\) fiber multiplicity
(unverified — sources give no degree); (iv) the local-\(L\)-factor→random-walk
identification (speculative analogy); (v) the \(i^i\leftrightarrow K_4\) anomaly
(forced identification, the clearest to kill); and (vi) the strongest of all —
ordinary \(K_4\) geometry gives \(d_s\ge1\), so \(d_s=1/2\) cannot arise from it
without a singular \(K_\infty\) limit or subordinated diffusion. Each is converted
above into a conditional with an explicit kill test. The partition function is
presented as a regulated ansatz with the \(d_s=1/2\) requirement stated as a
constraint the ansatz does not yet satisfy. This preserves the creative synthesis
while refusing to force mathematics the sources do not support.
