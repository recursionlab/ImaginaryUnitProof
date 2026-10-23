# Fractional kink energy audit

## Scope

Trial profile: `psi_a(x) = v*x/sqrt(x^2+a^2)`, with Fourier multiplier `|k|`. This script evaluates exact Bessel-transform formulas using spectral cutoffs; it does not claim the profile solves the nonlinear Euler–Lagrange equation.

## Exact kinetic formula

With `F(z) = integral_z^infinity q K1(q)^2 dq = z^2/2 * (K0(z)K2(z)-K1(z)^2)`,

`E_a(kappa,Lambda) = (2 v^2/pi) [F(a*kappa)-F(a*Lambda)]`.

For the discontinuous reference `v*sgn(x)`, the same spectral cutoff gives `E_step = (2v^2/pi) ln(Lambda/kappa)`. Subtracting it cancels the common IR logarithm but leaves a UV divergence with slope `-2v^2/pi` against `ln(Lambda)`. It is therefore not a finite regulator-free reference prescription.

## Smooth-reference relative functional

For two smooth profiles `psi_a` and `psi_b` with the same asymptotic phases,

`Delta E_kin(a;b) = (2v^2/pi) ln(b/a)`.

Adding `V[psi_a] = lambda*pi*v^4*a/8` gives the finite trial-profile difference

`Delta E_trial(a;b) = (2v^2/pi) ln(b/a) + lambda*pi*v^4*(a-b)/8`.

This quantity is reference-dependent and is not an on-shell kink mass until a solution of the field equation and a renormalization convention are established.

## Numerical checks

- UV slope measured: `-0.636619772368` per natural log of Lambda.
- UV slope predicted: `-0.636619772368`.
- Smooth relative kinetic limit: `0.441271200305`.
- Absolute error at smallest tested kappa: `1.561e-13`.
- Total smooth trial-relative functional: `0.048572118607`.

## Files

- `sharp_reference_ir_cutoff.csv` — IR cancellation at fixed UV cutoff.
- `sharp_reference_uv_cutoff.csv` — remaining UV divergence.
- `smooth_reference_relative_energy.csv` — convergence to smooth-reference limit.
- `kink_energy_audit.json` — formulas, parameters, validation, and limitations.
