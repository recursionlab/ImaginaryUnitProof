"""
k4_pentagon_laplacian.py — Honest computational probe for K_4 (the pentagonal
associahedron tile), per the research prompt's "Python/SymPy stub" requirement.

WHAT THIS COMPUTES (all genuinely derivable; no fabricated anomalies):
  1. The 5 triangulations of a convex pentagon (= Catalan C_3) and their flip
     graph, which is the 1-skeleton of K_4 = the cycle C_5.
  2. The exact (SymPy, symbolic) spectrum of the unweighted C_5 graph Laplacian
     — the natural discrete Laplacian on the combinatorial associahedron.
  3. The induced metric G_ij (Gram matrix of edge vectors of a regular pentagon).
  4. A properly-posed Dirichlet finite-difference Laplacian on the pentagonal
     domain (diagonal 4/h^2, off-diagonal -1/h^2, outside fixed to 0), lowest
     eigenvalues, and the mesh-dependent (~1/h^2) spectral radius.

WHAT THIS DOES NOT DO (honesty):
  * Does NOT derive e^{-pi/2} as a K_4 conformal anomaly. i^i = e^{-pi/2} is a
    standard principal value; its identification with a K_4 anomaly is speculative.
    e^{-pi/2} is printed only as a diagnostic target for comparison.
  * Does NOT assert d_s = 1/2. The heat-trace asymptotics of ORDINARY K_4
    geometry are: 2D domain -> t^{-1} (d_s=2); metric graph -> t^{-1/2} (d_s=1);
    finite graph -> Tr(e^{-tL}) -> N as t->0 (slope -> 0, no spectral dimension).
    Therefore d_s = 1/2 CANNOT come from ordinary K_4 geometry; it would require a
    singular/fractal K_infty limit or subordinated/fractional diffusion. This is
    the central falsification point (see brief).
"""
from __future__ import annotations
import numpy as np
from itertools import combinations
import sympy as sp

# ---------------------------------------------------------------------------
# 1. Triangulations of a convex pentagon and their flip graph (= 1-skeleton C_5)
# ---------------------------------------------------------------------------
def triangulations(poly):
    n = len(poly)
    if n <= 3:
        return [frozenset()]
    out = []
    for k in range(1, n - 1):
        left, right = poly[:k + 1], poly[k:]
        for L in triangulations(left):
            for R in triangulations(right):
                diag = set()
                if k > 1: diag.add((poly[0], poly[k]))
                if k < n - 2: diag.add((poly[k], poly[-1]))
                out.append(frozenset(diag | L | R))
    seen, res = set(), []
    for t in out:
        key = frozenset((min(a, b), max(a, b)) for a, b in t)
        if key not in seen:
            seen.add(key); res.append(t)
    return res

PENT = tuple(range(5))
TRIS = triangulations(PENT)
print(f"# triangulations of pentagon = {len(TRIS)}  (Catalan C_3 = 5)")

def are_adjacent(t1, t2):
    s1 = {(min(a, b), max(a, b)) for a, b in t1}
    s2 = {(min(a, b), max(a, b)) for a, b in t2}
    return len(s1 ^ s2) == 2  # one flip

N = len(TRIS)
A = np.zeros((N, N), dtype=int)
for i, j in combinations(range(N), 2):
    if are_adjacent(TRIS[i], TRIS[j]):
        A[i, j] = A[j, i] = 1
deg = A.sum(axis=1)
edges = int(A.sum() / 2)
print(f"1-skeleton: {N} vertices, {edges} edges  (flip graph = C_5)")

# ---------------------------------------------------------------------------
# 2. EXACT (SymPy) spectrum of the unweighted C_5 graph Laplacian
# ---------------------------------------------------------------------------
L_sym = sp.Matrix(N, N, lambda i, j: (deg[i] if i == j else -A[i, j]))
eig_sym = L_sym.eigenvals()
print("\nExact unweighted C_5 graph Laplacian (SymPy):")
for ev, mult in sorted(eig_sym.items(), key=lambda kv: float(kv[0])):
    print(f"  eigenvalue {sp.simplify(ev)}  (multiplicity {mult})")
spec_radius = max(float(sp.N(ev)) for ev in eig_sym)
print(f"  spectral radius = (5 + sqrt(5))/2 = {spec_radius:.6f}")

# ---------------------------------------------------------------------------
# 3. Induced metric: regular pentagon on the unit circle (side = 2 sin(pi/5))
# ---------------------------------------------------------------------------
theta = np.array([np.pi/2 + 2*np.pi*k/5 for k in range(5)])
coords = np.stack([np.cos(theta), np.sin(theta)], axis=1)
side = 2*np.sin(np.pi/5)
print(f"\nRegular pentagon on unit circle: side length = 2 sin(pi/5) = {side:.6f}")
nb = np.where(A[0] > 0)[0]
vecs = np.array([coords[k] - coords[0] for k in nb])
G = vecs @ vecs.T
print("Gram matrix G_ij of face-edge vectors at vertex 0:")
print(np.round(G, 4))

# ---------------------------------------------------------------------------
# 4. Proper Dirichlet finite-difference Laplacian on the pentagonal domain
#    diagonal 4/h^2, off-diagonal -1/h^2, outside values fixed to 0.
# ---------------------------------------------------------------------------
def inside(p, poly):
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        if (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0]) < -1e-9:
            return False
    return True

h = 0.05
xs = np.arange(-1.1, 1.1, h)
pts = [np.array([x, y]) for x in xs for y in xs if inside(np.array([x, y]), coords)]
idx = {}
for i, p in enumerate(pts):
    idx[(round(p[0]/h), round(p[1]/h))] = i
n = len(pts)
rows, cols, vals = [], [], []
for i, p in enumerate(pts):
    cx, cy = round(p[0]/h), round(p[1]/h)
    neigh = 0
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        j = idx.get((cx+dx, cy+dy))
        if j is not None:
            rows.append(i); cols.append(j); vals.append(-1.0); neigh += 1
    rows.append(i); cols.append(i); vals.append(4.0)  # Dirichlet: diag 4/h^2, outside = 0
# assemble with 1/h^2 scaling
import scipy.sparse as sps
Lap = sps.csr_matrix((np.array(vals)/h**2, (rows, cols)), shape=(n, n))
eigD = sps.linalg.eigsh(Lap, k=4, which='SM', return_eigenvectors=False)
print(f"\nDirichlet finite-difference Laplacian on pentagon domain (h={h:.3f}):")
print(f"  lowest eigenvalues: {np.round(np.sort(eigD), 4)}")
print(f"  spectral radius ~ 4/h^2 = {4/h**2:.1f} (mesh-dependent, NOT a fixed anomaly)")

# ---------------------------------------------------------------------------
# 5. Heat-trace asymptotics of ORDINARY K_4 geometry (the falsification point)
# ---------------------------------------------------------------------------
print("\n--- Heat-trace asymptotics of ordinary K_4 geometry ---")
print("2D pentagonal domain : Tr(e^{-t Delta}) ~ t^{-1}   -> d_s = 2")
print("metric graph (1-skel): Tr(e^{-t Delta}) ~ t^{-1/2} -> d_s = 1")
print("finite graph (C_5)   : Tr(e^{-t L}) -> N as t->0   -> slope -> 0 (no d_s)")
print("=> d_s = 1/2 CANNOT come from ordinary K_4 geometry;")
print("   it requires a singular/fractal K_infty limit or subordinated diffusion.")

# ---------------------------------------------------------------------------
# 6. Diagnostic target only (NOT derived)
# ---------------------------------------------------------------------------
print(f"\nDiagnostic target e^(-pi/2) = {np.exp(-np.pi/2):.6f}  (i^i principal value;")
print("  identification with a K_4 conformal anomaly is SPECULATIVE, not computed here.)")
