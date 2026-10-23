import math
import adv_common as ac

print("=" * 70)
print("STEP 1: Cell-anchored evidence from ImaginaryUnit.ipynb cell 12 (0-based idx=12)")
print("=" * 70)

lines = ac.cell_lines(12)
print("\nphi_sweeps_m3[0] / [-1] definition and the check, verbatim from cell 12:")
for lineno, text in lines:
    if lineno in (24, 52, 55):
        label = {24: "  (sweep def)", 52: "  (check line)", 55: "  (verdict line)"}[lineno]
        print(f"  cell12.py L{lineno}{label}: {text.rstrip()}")

phi0 = -2 * math.pi
phiN = 2 * math.pi
print(f"\n  phi_sweeps_m3[0]  = -2*pi = {phi0!r}")
print(f"  phi_sweeps_m3[-1] = +2*pi = {phiN!r}")

print("\n" + "=" * 70)
print("STEP 2: Assert [0] == [-1] (mod 2*pi)")
print("=" * 70)
diff = phiN - phi0
print(f"  phi[-1] - phi[0] = 4*pi = {diff!r}")
print(f"  (phi[-1] - phi[0]) mod (2*pi) = {diff % (2*math.pi)!r}")
mod0 = phi0 % (2 * math.pi)
modN = phiN % (2 * math.pi)
print(f"  phi[0] mod 2*pi = {mod0!r}")
print(f"  phi[-1] mod 2*pi = {modN!r}")
assert math.isclose(mod0, modN, abs_tol=1e-15) or (mod0, modN) == (0, 0)
print("  ASSERTION OK: phi[0] == phi[-1] (mod 2*pi); both == 0 (mod 2*pi).")

print("\n  => The endpoints are the SAME physical phase (mod 2*pi).")
print("     Any 2*pi-periodic observable satisfies V(phi[0]) == V(phi[-1]).")

print("\n" + "=" * 70)
print("STEP 3: Explicit 4*pi-periodic function f with f(-2pi)==f(2pi); check passes")
print("=" * 70)

def f(phi):
    return math.cos(phi / 2.0)

f0 = f(phi0)
fN = f(phiN)
print(f"  f(phi) = cos(phi/2)")
print(f"  f(-2*pi) = cos(-pi)  = {f0!r}")
print(f"  f(+2*pi) = cos(+pi)  = {fN!r}")
print(f"  |f(-2pi) - f(+2pi)|  = {abs(f0 - fN)!r}  < 0.05  =>  check PASSES")
print(f"\n  4*pi periodicity: f(phi+4*pi) = cos((phi+4pi)/2) = cos(phi/2 + 2pi) = cos(phi/2) = f(phi).  CONFIRMED 4*pi-periodic.")
print(f"  NOT 2*pi-periodic: f(0)=cos(0)={f(0)!r}; f(0+2pi)=cos(pi)={f(2*math.pi)!r}; {f(0)} != {f(2*math.pi)}  =>  NOT 2*pi-periodic.")

print("\n  VACUITY PROOF:")
print("  The SAME boundary check |V[a]-V[b]|<0.05 with a==b (mod 2pi) ALSO passes")
print("  for a generic 2*pi-periodic function g(phi)=cos(phi):")
g0 = math.cos(phi0)
gN = math.cos(phiN)
print(f"    g(-2pi)=cos(-2pi)={g0!r}; g(+2pi)=cos(2pi)={gN!r}; |diff|={abs(g0-gN)!r} < 0.05. PASSES too.")
print("  => Passing the check is necessary but NOT sufficient for 4*pi. It certifies NOTHING about the period.")

print("\n  Real M3 simulation: boundary_deviation reported = 0.0 (V[0] == V[-1] exactly),")
print("  periodicity_conforms_to_4pi = True. But the actual system is 2*pi-periodic (flip inert),")
print("  so 0.0 deviation is the EXPECTED outcome of a 2*pi-periodic system, NOT evidence of 4*pi.")

print("\n" + "=" * 70)
print("STEP 4: Minimal alternative phase set that WOULD distinguish 2*pi from 4*pi")
print("=" * 70)
print("""
  The flaw: endpoints -2pi, +2pi are 4pi APART (so any 4pi-periodic f agrees)
  AND 0 mod 2pi (so any 2pi-periodic f agrees). They cannot separate the periods.

  Fix: sample at points phi and phi+2pi that BOTH lie inside [-2pi, +2pi],
  i.e. phi in [-2pi, 0]. A 2pi-periodic system gives V(phi)=V(phi+2pi) for ALL phi;
  a (non-2pi) 4pi-periodic system must differ at SOME such pair.

  Minimal phase set (5 points): { -2pi, -pi, 0, pi, 2pi }
  => check the three 2pi-separated pairs simultaneously:
       P1 = |V(-2pi) - V(0)|
       P2 = |V(-pi)  - V(pi)|
       P3 = |V(0)     - V(2pi)|
  Distinguishing predicate (existence test):
       4pi-cert : max(P1, P2, P3) > 0.05   AND   boundary |V(-2pi)-V(2pi)| < 0.05
       2pi       : all(P1, P2, P3) < 0.05   (no 2pi-shift breaks invariance)
  For f(phi)=cos(phi/2): P1=|cos(-pi)-cos(0)|=|-1-1|=2 >0.05  => distinguishes.
""")
print("  Verification on the explicit f(phi)=cos(phi/2):")
for a, b, label in [(-2*math.pi, 0, "P1"), (-math.pi, math.pi, "P2"), (0, 2*math.pi, "P3")]:
    d = abs(f(a) - f(b))
    print(f"    {label} = |f({label[0]}) - f({label[1]})| ... phi={a:.4f},{b:.4f} -> |{f(a):.4f}-{f(b):.4f}|={d:.4f}  {'>' if d>0.05 else '<='} 0.05")

print("\n  Spinor sign-flip (stronger, SU(2) signature) variant:")
print("    Sample psi(phi) as a COMPLEX amplitude. The true 4pi signature is:")
print("      psi(phi+2pi) == -psi(phi)   (sign flip)")
print("      psi(phi+4pi) == +psi(phi)   (restoration)")
print("    Predicate: for some interior phi, |psi(phi)+psi(phi+2pi)| < eps  AND")
print("    |psi(phi)-psi(phi+2pi)| > eps. V[2] in the notebook is |psi|^2 (intensity),")
print("    which is blind to the sign flip, so it can NEVER certify the SU(2) double cover.")
