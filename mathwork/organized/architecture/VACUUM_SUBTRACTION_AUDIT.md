# Vacuum-Subtraction Audit for the Fractional Kink

**Status:** executed analytic/numerical audit; finite step-reference subtraction claim fails when both infrared and ultraviolet cutoffs are removed.

## Question under audit

For the odd trial profile
\[
\psi_a(x)=v\frac{x}{\sqrt{x^2+a^2}},\qquad a>0,\ v>0,
\]
the proposed stance E asks whether one can define
\[
E_{\rm rel}[\psi_a]=E[\psi_a]-E[v\,\operatorname{sgn}]
\]
with common infrared regulator \(\kappa\), cancel the \(\ln(1/\kappa)\) terms, and obtain a finite \(a,v\)-dependent coefficient.

The answer is **partly yes, but not as a full regulator-free energy difference**: the common infrared logarithm cancels, but the sharp reference \(v\,\operatorname{sgn}(x)\) has an additional ultraviolet logarithmic divergence for the \(|D|\) kinetic form. Consequently the relative quantity tends to \(-\infty\) as the common ultraviolet cutoff is removed. The step profile is not an admissible finite-energy reference in the homogeneous \(H^{1/2}\) form domain.

## 1. Conventions and exact Fourier transform

Use
\[
\widehat f(k)=\int_{\mathbb R} e^{-ikx}f(x)\,dx,
\qquad
E_{\rm kin}[f]=\frac12\langle f,|D|f\rangle
=\frac{1}{4\pi}\int_{\mathbb R}|k|\,|\widehat f(k)|^2\,dk.
\]

The profile derivative is
\[
\psi_a'(x)=\frac{va^2}{(x^2+a^2)^{3/2}}.
\]
The standard Bessel transform gives
\[
\widehat{\psi_a'}(k)=2va|k|K_1(a|k|).
\]
Since \(\widehat{\psi_a'}(k)=ik\widehat{\psi_a}(k)\) for \(k\ne0\),
\[
\widehat{\psi_a}(k)=\frac{2va|k|}{ik}K_1(a|k|)
=-2iva\,\operatorname{sgn}(k)K_1(a|k|).
\]
Thus
\[
|\widehat{\psi_a}(k)|^2=4v^2a^2K_1(a|k|)^2.
\]
The low-frequency behavior \(K_1(z)\sim z^{-1}\) gives
\(\widehat\psi_a(k)\sim 2v/(ik)\), the expected IR singularity from the unequal asymptotic phases.

## 2. Smooth-kink kinetic energy with common spectral cutoffs

For \(0<\kappa<\Lambda\), define
\[
E_a(\kappa,\Lambda)
=\frac{1}{4\pi}\int_{\kappa<|k|<\Lambda}
|k|\,|\widehat{\psi_a}(k)|^2\,dk.
\]
Substituting the transform and using \(q=a|k|\),
\[
E_a(\kappa,\Lambda)=\frac{2v^2}{\pi}
\int_{a\kappa}^{a\Lambda}qK_1(q)^2\,dq.
\]
Let
\[
F(z)=\int_z^\infty qK_1(q)^2\,dq
=\frac{z^2}{2}\left(K_0(z)K_2(z)-K_1(z)^2\right).
\]
Then the exact cutoff expression is
\[
\boxed{E_a(\kappa,\Lambda)
=\frac{2v^2}{\pi}\,[F(a\kappa)-F(a\Lambda)].}
\]

At small \(z\),
\[
F(z)=\log\frac{2}{z}-\gamma-\frac12+o(1),
\qquad z\downarrow0,
\]
where \(\gamma\) is Euler's constant. Therefore
\[
E_a(\kappa,\Lambda)
=\frac{2v^2}{\pi}\log\frac1\kappa+O(1)
\quad (\kappa\downarrow0,\ \Lambda\text{ fixed}).
\]
The coefficient of the IR logarithm is \(2v^2/\pi\), or \((2v^2/\pi)\log 10\) per decade.

## 3. The sharp sign reference has a UV divergence

For \(s(x)=v\operatorname{sgn}(x)\), understood distributionally,
\[
\widehat s(k)=\frac{2v}{ik}\quad(k\ne0)
\]
in the principal-value sense. Under the *same* spectral cutoffs,
\[
\begin{aligned}
E_{\rm step}(\kappa,\Lambda)
&=\frac{1}{4\pi}\int_{\kappa<|k|<\Lambda}
|k|\frac{4v^2}{k^2}\,dk\\
&=\frac{2v^2}{\pi}\log\frac{\Lambda}{\kappa}.
\end{aligned}
\]
This includes both:
- the same infrared divergence as the smooth kink, from \(k\to0\);
- an additional ultraviolet divergence from the discontinuity at \(x=0\), from \(k\to\infty\).

The smooth profile has exponentially decaying high-frequency transform because \(K_1(a|k|)\) decays exponentially. The step does not: its \(1/k\) transform leaves a \(|k||\widehat s|^2\sim1/|k|\) UV integrand.

## 4. Subtracting the step: IR cancellation succeeds; full subtraction fails

With the same \(\kappa,\Lambda\), the relative kinetic quantity is exactly
\[
\boxed{
\Delta E_{a-s}(\kappa,\Lambda)
=\frac{2v^2}{\pi}
\left[F(a\kappa)-F(a\Lambda)-\log\frac{\Lambda}{\kappa}\right].
}
\]
As \(\kappa\downarrow0\) at fixed \(\Lambda\), the terms \(\log(1/\kappa)\) cancel:
\[
\boxed{
\lim_{\kappa\downarrow0}\Delta E_{a-s}(\kappa,\Lambda)
=\frac{2v^2}{\pi}
\left[
\log\frac{2}{a\Lambda}-\gamma-\frac12-F(a\Lambda)
\right].
}
\]
This is finite **only while the UV cutoff \(\Lambda\) remains fixed**. As \(\Lambda\to\infty\), \(F(a\Lambda)\to0\), so
\[
\Delta E_{a-s}
=\frac{2v^2}{\pi}
\left[\log\frac{2}{a\Lambda}-\gamma-\frac12\right]+o(1)
\longrightarrow-\infty.
\]
Therefore the proposed subtraction against the discontinuous sign function does **not** yield a finite cutoff-independent relative energy. It removes the common IR divergence but exposes the reference configuration's separate UV divergence.

## 5. Numerical results

For \(v=a=1\), \(\Lambda=10^4\), the computed relative energies are:

| IR cutoff \(\kappa\) | \(E_a\) | \(E_{\rm step}\) | \(E_a-E_{\rm step}\) |
|---:|---:|---:|---:|
| \(10^{-1}\) | 1.232215 | 7.329356 | -6.097141 |
| \(10^{-2}\) | 2.687419 | 8.795227 | -6.107808 |
| \(10^{-4}\) | 5.618979 | 11.726970 | -6.107990 |
| \(10^{-5}\) | 7.084850 | 13.192841 | -6.107990 |
| \(10^{-7}\) | 10.016593 | 16.124583 | -6.107990 |

(The \(10^{-5}\) row in the generated CSV should be used as the canonical value for the exact configured cutoff; the table above is rounded from the same formulas. See CSV for all points.)

For fixed \(\kappa=10^{-5}\), changing the UV cutoff demonstrates the unremoved divergence:

| UV cutoff \(\Lambda\) | \(E_a-E_{\rm step}\) |
|---:|---:|
| 10 | -1.710377 |
| 100 | -3.176248 |
| 1,000 | -4.642119 |
| 10,000 | -6.107990 |
| 100,000 | -7.573861 |
| 1,000,000 | -9.039732 |
| 10,000,000 | -10.505604 |

The slope is \(-2v^2/\pi=-0.63661977\) per unit \(\log\Lambda\), equivalently \(-1.46587120\) per decade for \(v=1\). This matches the predicted UV divergence of the sign reference.

## 6. A better finite relative comparison: smooth reference in the same topological sector

Compare two smooth trial kinks
\[
\psi_a(x)=v\frac{x}{\sqrt{x^2+a^2}},\qquad
\psi_b(x)=v\frac{x}{\sqrt{x^2+b^2}}.
\]
They have the same asymptotic phases and both have UV-finite \(|D|\) energy; only their common IR logarithm diverges. With common cutoffs,
\[
E_a-E_b=\frac{2v^2}{\pi}
\{F(a\kappa)-F(b\kappa)-F(a\Lambda)+F(b\Lambda)\}.
\]
Taking \(\kappa\downarrow0\), \(\Lambda\uparrow\infty\),
\[
\boxed{
\Delta E_{\rm kin}^{\rm rel}(a;b)
=\frac{2v^2}{\pi}\log\frac{b}{a}.
}
\]
This is finite under the stated common regulator and reference convention. It is a relative kinetic energy between two smooth trial profiles, not an absolute mass and not evidence that either profile solves the Euler–Lagrange equation.

For \(v=1,a=1,b=2\), the predicted limit is \(0.4412712003\). The code gives \(0.440813\) at \(\kappa=10^{-2}\), \(0.441266\) at \(10^{-4}\), and \(0.4412712003\) to displayed precision at \(10^{-7}\).

If the model includes
\[
V[\psi]=\frac{\lambda}{4}\int_{\mathbb R}(\psi^2-v^2)^2dx,
\]
then for this trial family
\[
V[\psi_a]=\frac{\lambda\pi v^4a}{8}.
\]
Hence the corresponding *trial-profile* total relative energy is
\[
\boxed{
\Delta E_{\rm trial}^{\rm rel}(a;b)
=\frac{2v^2}{\pi}\log\frac{b}{a}
+\frac{\lambda\pi v^4}{8}(a-b).
}
\]
This remains reference-dependent, and the trial profiles are not established stationary solutions. It must not be promoted to a physical kink mass without solving the field equation and fixing the model's renormalization condition.

## 7. Verdict on stance E

The useful part of stance E survives: the untempered \(|D|\) model's kink sector has an IR logarithm tied to its nonzero asymptotic phase jump, so an absolute energy requires a reference/renormalization prescription.

The specific prescription \(E[\psi_a]-E[v\,\operatorname{sgn}]\), however, is insufficient. The reference sign profile adds a UV divergence. The valid next step is to define the relative energy against a *smooth reference kink with the same asymptotic phases*, or to state a complete renormalization scheme including both IR and UV behavior. That produces a finite relative functional on the trial family, but does not repair the previously failed Euler–Lagrange claim.

### Reproducibility

Run:
```bash
python vacuum_subtraction_audit.py --outdir results --v 1 --a 1 --b 2 --lambda 1 --Lambda 10000
```
The script generates the CSV tables and `vacuum_subtraction_diagnostics.png`. It uses the exact Bessel-transform formula rather than pretending a finite Fourier box is a continuum proof.
