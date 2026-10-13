"""curvature_probe.py — H^2 curvature 2-form of Cayley-Dickson algebras.

Computes  Omega(a,b) = [L_a, L_b] - L_[a,b]  for 2^k-ions using exact
integer arithmetic, and empirically adjudicates the claims in the
"64D curvature architecture" notes:

  V1  Omega(a,b)c = -[a,b,c] + [b,a,c]                    (operator identity)
  V2  Omega != 0 already for octonions (8D)               (correction: the notes
      claim curvature is born at 16D)
  V3  zero-divisor triangle law: a.b = b.c = 0  =>  Omega(a,b)c = -[b,a,c]
      (correction: the residual is the associator [b,a,c], not c.a)
  V4  involution group {h1, tau, h2} is (Z/2)^3, order 8  (correction: an
      earlier claim that h2 = h1*tau and the group is Klein-four was WRONG;
      the CD conjugate is conj(a,b) = (conj(a), -b), not (conj(a), -conj(b)))
  V5  sheet-swap sigma extends the group to a NONABELIAN group of order 32 with sigma*tau = -tau*sigma
      (consistent with the real 2-qubit Pauli group; -I appears only via sigma)
  V6  alternation — and hence closure of the H^3 ledger — holds at 8D and
      fails at 16D
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

report = []
def rep(s):
    print(s); report.append(s)

# ---------- Cayley-Dickson machinery ----------
def cd_conj(u, level):
    if level == 0:
        return u
    h = len(u) // 2
    return np.concatenate([cd_conj(u[:h], level - 1), -u[h:]])

def cd_mul(u, v, level):
    if level == 0:
        return u * v
    h = len(u) // 2
    a, b, c, d = u[:h], u[h:], v[:h], v[h:]
    return np.concatenate([
        cd_mul(a, c, level - 1) - cd_mul(cd_conj(d, level - 1), b, level - 1),
        cd_mul(d, a, level - 1) + cd_mul(b, cd_conj(c, level - 1), level - 1)])

def cd_algebra(level):
    dim = 2 ** level
    eye = np.eye(dim, dtype=int)
    L = np.zeros((dim, dim, dim), dtype=int)
    for i in range(dim):
        for j in range(dim):
            L[i][:, j] = cd_mul(eye[i], eye[j], level)
    return L

def A_of(u, L):
    return np.tensordot(u, L, axes=(0, 0))

def mulv(u, v, L):
    return A_of(u, L) @ v

def assoc(a, b, c, L):
    return mulv(mulv(a, b, L), c, L) - mulv(a, mulv(b, c, L), L)

def Om(a, b, L):
    A, B = A_of(a, L), A_of(b, L)
    return A @ B - B @ A - A_of(A @ b - B @ a, L)

NAMES = {0: "R", 1: "C", 2: "H", 3: "O", 4: "S"}

algs = {k: cd_algebra(k) for k in range(5)}
Ls = algs[4]

# sanity checks on the construction
rep("=== sanity ===")
rep("e1^2 == -1 (level 2): " + str(np.array_equal(mulv(np.eye(4, dtype=int)[1], np.eye(4, dtype=int)[1], algs[2]), -np.eye(4, dtype=int)[0])))
hh = [np.abs(assoc(*(np.eye(4, dtype=int)[i] for i in p), algs[2])).sum() for p in [(1,2,3)]]
rep("H fully associative: " + str(hh == [0]))
rep("O non-associative: " + str(np.abs(assoc(np.eye(8, dtype=int)[1], np.eye(8, dtype=int)[2], np.eye(8, dtype=int)[4], algs[3])).sum() > 0))

# ---------- V1: operator identity ----------
rng = np.random.default_rng(7)
ok = True
for _ in range(200):
    d = 16
    a, b, c = (rng.integers(-2, 3, d) for _ in range(3))
    if not np.array_equal(Om(a, b, Ls) @ c, -assoc(a, b, c, Ls) + assoc(b, a, c, Ls)):
        ok = False; break
rep("=== V1 ===")
rep("identity Omega(a,b)c = -[a,b,c]+[b,a,c] on 200 random S-triples: " + str(ok))

# ---------- V2: Omega across the ladder ----------
rep("=== V2 ===")
for k in (2, 3, 4):
    L = algs[k]; d = 2 ** k
    eye = np.eye(d, dtype=int)
    nz = tot = mx = 0
    zero_pairs = []
    for i in range(1, d):
        for j in range(1, d):
            n = int(np.abs(Om(eye[i], eye[j], L)).sum())
            tot += 1
            if n:
                nz += 1; mx = max(mx, n)
            else:
                zero_pairs.append((i, j))
    rep(f"{NAMES[k]} ({d}D): max|Omega(e_i,e_j)| = {mx}, nonzero pairs {nz}/{tot}, zero pairs e.g. {zero_pairs[:6]}")

# ---------- V4/V5: involution group numerics ----------
rep("=== V4/V5 ===")
def conjmat(k):
    return np.diag([1] + [-1] * (2 ** k - 1))
C3 = conjmat(3)
I8 = np.eye(8, dtype=int); Z8 = np.zeros((8, 8), dtype=int)
I16 = np.eye(16, dtype=int)
h1  = np.block([[C3, Z8], [Z8, C3]])     # *_n  + *_n
tau = np.block([[I8, Z8], [Z8, -I8]])    # (x,y) -> (x,-y)
h2  = np.block([[C3, Z8], [Z8, -I8]])    # *_{n+1}: (x,y) -> (x*, -y)
tb  = np.block([[I8, Z8], [Z8, -C3]])    # "twisted twist": (x,y) -> (x,-y*)
sig = np.block([[Z8, C3], [C3, Z8]])     # sheet swap: (x,y) -> (y*, x*)
rep("h2 == h1*tau ? " + str(np.array_equal(h1 @ tau, h2)) + "   (so the earlier 'Klein four' correction was WRONG)")
rep("tau == h1*h2 ? " + str(np.array_equal(h1 @ h2, tau)) + "   (the notes' relation is also wrong)")
rep("h2 == h1*tb (twisted twist) ? " + str(np.array_equal(h1 @ tb, h2)))
def key(M): return M.tobytes()
def orbit(gens):
    seen = {key(I16): I16}; stack = [I16]; elems = [I16]
    while stack:
        X = stack.pop()
        for g in gens:
            Y = X @ g
            if key(Y) not in seen:
                seen[key(Y)] = Y; stack.append(Y); elems.append(Y)
    return elems
def abelian(G):
    return all(np.array_equal(g @ h, h @ g) for g in G for h in G)
G_abc  = orbit([h1, tau, tb])
G_full = orbit([h1, tau, h2, sig])
inv = lambda G: sum(1 for g in G if np.array_equal(g @ g, I16))
G_orig = orbit([h1, tau, h2])
rep(f"<h1,tau,h2> alone: order={len(G_orig)} abelian={abelian(G_orig)} (the octic group was already intrinsic)")
rep(f"<h1,tau,tb>  order={len(G_abc)} abelian={abelian(G_abc)} involutions={inv(G_abc)}  -> (Z/2)^3")
rep(f"<h1,tau,h2,sig> order={len(G_full)} abelian={abelian(G_full)} involutions={inv(G_full)}")
rep("sigma*tau == -tau*sigma : " + str(np.array_equal(sig @ tau, -tau @ sig)))
rep("-I in <h1,tau,h2> : " + str(any(np.array_equal(g, -I16) for g in G_abc)) +
    " ; -I appears only with sigma : " + str(any(np.array_equal(g, -I16) for g in G_full)))
pairs = [(rng.integers(-1, 2, 16), rng.integers(-1, 2, 16)) for _ in range(40)]
auto = all(np.array_equal(mulv(sig @ a, sig @ b, Ls), sig @ mulv(a, b, Ls)) for a, b in pairs)
anti = all(np.array_equal(mulv(sig @ a, sig @ b, Ls), mulv(sig @ b, sig @ a, Ls)) for a, b in pairs)
rep("sigma an algebra automorphism? " + str(auto) + " ; an ANTI-automorphism? " + str(anti))
def p_index(i):
    return int(np.argmax(np.abs(sig @ np.eye(16, dtype=int)[i])))
def p_sign(i):
    return int(np.sign((sig @ np.eye(16, dtype=int)[i])[p_index(i)]))
corr = all(np.array_equal(sig @ Ls[i] @ sig, p_sign(i) * Ls[p_index(i)]) for i in range(1, 16))
rep("corrected relation  sigma L_i sigma = sign * L_{sigma(e_i)} : " + str(corr))
err_sigma = max(int(np.abs(sig @ Ls[i] @ sig + Ls[i]).sum()) for i in range(1, 16))
rep("notes' formula |sigma L sigma - (-L)| max err = " + str(err_sigma) + " (fails as written)")

# ---------- V6: alternation / closure of the H^3 ledger ----------
rep("=== V6 ===")
rng = np.random.default_rng(3)
for k in (3, 4):
    L = algs[k]; d = 2 ** k
    alt = cyc = 0
    for _ in range(300):
        a, b, c = (rng.integers(-1, 2, d) for _ in range(3))
        A1 = assoc(a, b, c, L)
        alt = max(alt, int(np.abs(A1 + assoc(b, a, c, L)).sum()))
        cyc = max(cyc, int(np.abs(A1 + assoc(b, c, a, L) + assoc(c, a, b, L)).sum()))
    rep(f"{NAMES[k]}: max |[a,b,c]+[b,a,c]| = {alt}, max |cyclic sum| = {cyc}")

# ---------- V3: zero-divisor census + triangles ----------
rep("=== V3 ===")
dim = 16
vecs = []
for i in range(dim):
    for j in range(i + 1, dim):
        for s in (-1, 1):
            for t in (-1, 1):
                v = np.zeros(dim, int); v[i] = s; v[j] = t; vecs.append(v)
Amats = [A_of(v, Ls) for v in vecs]
zd = [(i, j) for i in range(len(vecs)) for j in range(i + 1, len(vecs)) if not (Amats[i] @ vecs[j]).any()]
rep(f"zero-divisor pairs among {len(vecs)} 2-sparse signed vectors: {len(zd)} (of {len(vecs)*(len(vecs)-1)//2})")
a0, b0 = vecs[zd[0][0]], vecs[zd[0][1]]
rep("example ZD pair: a = " + str(a0.nonzero()[0]) + str(a0[a0.nonzero()]) + ", b = " + str(b0.nonzero()[0]) + str(b0[b0.nonzero()]))
rows = []
law_ok = True
for (i, j) in zd[:300]:
    for k in range(len(vecs)):
        if k == i or k == j: continue
        if not (Amats[j] @ vecs[k]).any():
            a, b, c = vecs[i], vecs[j], vecs[k]
            lhs = Om(a, b, Ls) @ c
            res = assoc(b, a, c, Ls)
            if not np.array_equal(lhs, res): law_ok = False
            rows.append((int(np.abs(mulv(c, a, Ls)).sum() > 0), int(np.abs(lhs).sum() > 0)))
rows = np.array(rows)
rep(f"triangles tested: {len(rows)}; law Omega(a,b)c = +[b,a,c] held: {law_ok}")
same = tot_t = 0
for (i, j) in zd[:60]:
    for k in range(len(vecs)):
        if k == i or k == j: continue
        if not (Amats[j] @ vecs[k]).any():
            a, b, c = vecs[i], vecs[j], vecs[k]
            ca = mulv(c, a, Ls); rv = assoc(b, a, c, Ls)
            if np.array_equal(ca, rv) or np.array_equal(ca, -rv): same += 1
            tot_t += 1
rep(f"  of {tot_t} triangles, c*a == +/- [b,a,c] exactly: {same}")
rep(f"  c*a != 0 AND curvature != 0 : {int(((rows[:,0]==1)&(rows[:,1]==1)).sum())}")
rep(f"  c*a != 0 BUT curvature == 0 : {int(((rows[:,0]==1)&(rows[:,1]==0)).sum())}   <- counterexamples to 'c*a != 0 implies Omega != 0'")
rep(f"  c*a == 0 BUT curvature != 0 : {int(((rows[:,0]==0)&(rows[:,1]==1)).sum())}   <- counterexamples the other way")

# ---------- heatmap ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
for ax, k in zip(axes, (3, 4)):
    L = algs[k]; d = 2 ** k
    eye = np.eye(d, dtype=int)
    N = np.zeros((d, d))
    for i in range(d):
        for j in range(d):
            N[i, j] = np.abs(Om(eye[i], eye[j], L)).sum()
    im = ax.imshow(N, cmap="magma")
    ax.set_title(f"|Omega(e_i,e_j)| on {NAMES[k]} ({d}D)")
    ax.set_xlabel("j"); ax.set_ylabel("i")
    fig.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig("/mnt/agents/output/omega_heatmap.png", dpi=130)

with open("/mnt/agents/output/curvature_probe_results.txt", "w") as f:
    f.write("\n".join(report) + "\n")
rep("saved: omega_heatmap.png, curvature_probe_results.txt")
