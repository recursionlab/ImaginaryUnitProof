"""
TRIGINTADUONION ENGINE — Cayley-Dickson construction up to 32 dimensions,
verified against Wikipedia's 155 distinguished triples, with a language-first
measurement layer. Pure Python, no dependencies.  python3 cd_trigintaduonion.py

THESIS (language-first, as designed by the project):
  The 155 distinguished triples {a, b, a XOR b} of the trigintaduonions are
  proposed as irreducible 3-way composition atoms of language (questions,
  prepositions, affixes -> triple types). Non-associativity is the claim that
  reading/parse order genuinely changes meaning rather than being surface
  variation.

VERIFIED ALGEBRAIC FACTS (this script re-derives them from scratch):
  * e_i * e_j = +/- e_{i XOR j}   (XOR index rule) for all imaginary i != j
  * The 155 extracted triples match Wikipedia's published list EXACTLY
    (0 missing, 0 extra; counts 45/20/15/60/15 by type)
  * ALL 155 distinguished triples are ASSOCIATIVE (each is a quaternion
    subloop -- the associator vanishes for every ordering)
  * The algebra is nonetheless non-associative: 15,960 ordered / 4,340
    unordered non-associative triples exist -- but ONLY among NON-distinguished
    triples, where the associator touches 4+ distinct basis units.

LINGUISTIC READING OF THAT FACT:
  The 155 atoms are the STABLE core: 3-way compositions that are bracketing-
  invariant (closed-class frames, safe grammar -- parse order doesn't change
  meaning). Reading/parse order becomes load-bearing only at 4+ distinct
  primitives: garden paths, scope, "man bites dog". So the model is: a finite
  stable core of 155 safe frames + a non-associative periphery where
  composition order is what carries meaning.

NOTE ON TYPE LABELS {a,a,b} / {b,b,b} / {a,b,g} / {b,g,g}:
  Wikipedia/Cawagas classifies the 155 into five groups (45/20/15/60/15).
  Empirically these are NOT separated by sign-orientation profile (+++/---)
  nor by generation multiset (highest-set-bit), so the exact definition is
  structural rather than those simple invariants -- classification remains
  open; the triple-set itself is verified exactly.
"""

import itertools

# ----------------------------------------------------------------------------
# 1. Cayley-Dickson construction
#    (a,b)(c,d) = (ac - conj(d)b, da + b conj(c)); conj(e_0)=+e_0, conj(e_i)=-e_i
#    A basis element is stored as (sign, index): e_i * e_j = sign * e_index.
# ----------------------------------------------------------------------------

def build_cd_table(prev, n):
    size = 2 * n
    T = [[(0, 0)] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i < n and j < n:                 # old * old -> base algebra
                T[i][j] = prev[i][j]
            elif i < n and j >= n:              # old * new -> (0, e_jp * e_i)
                jp = j - n
                s, k = prev[jp][i]
                T[i][j] = (s, n + k)
            elif i >= n and j < n:              # new * old -> (0, e_ip * conj(e_j))
                ip = i - n
                if j == 0:
                    T[i][j] = (1, i)
                else:
                    s, k = prev[ip][j]
                    T[i][j] = (-s, n + k)
            else:                               # new * new -> (conj(...)*..., 0)
                ip, jp = i - n, j - n
                if jp == 0:
                    T[i][j] = (-1, ip)
                else:
                    T[i][j] = prev[jp][ip]
    return T


def build_all():
    """R -> C -> H -> O -> S -> T (trigintaduonions, 32-dim)."""
    R = [[(1, 0)]]
    C = build_cd_table(R, 1)
    H = build_cd_table(C, 2)
    O = build_cd_table(H, 4)
    S = build_cd_table(O, 8)
    T = build_cd_table(S, 16)
    return {"R": R, "C": C, "H": H, "O": O, "S": S, "T": T}


# ----------------------------------------------------------------------------
# 2. Verification
# ----------------------------------------------------------------------------

def verify(table, name):
    errs = []
    n = len(table)
    for i in range(n):
        if table[0][i] != (1, i): errs.append(f"{name}: e0*e{i} != e{i}")
        if table[i][0] != (1, i): errs.append(f"{name}: e{i}*e0 != e{i}")
    for i in range(1, n):
        if table[i][i] != (-1, 0): errs.append(f"{name}: e{i}^2 != -1")
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                si, ki = table[i][j]
                sj, kj = table[j][i]
                if (sj, kj) != (-si, ki):
                    errs.append(f"{name}: e{i}e{j} fails anti-commutativity")
    xor_bad = 0
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                s, k = table[i][j]
                if k != (i ^ j):
                    xor_bad += 1
    if xor_bad:
        errs.append(f"{name}: {xor_bad} XOR-index-rule failures")
    return errs


# ----------------------------------------------------------------------------
# 3. The 155 distinguished triples  {a, b, a XOR b}
# ----------------------------------------------------------------------------

def extract_triples(table):
    n = len(table)
    t = set()
    for a in range(1, n):
        for b in range(a + 1, n):
            c = a ^ b
            if 1 <= c:
                t.add(frozenset((a, b, c)))
    return t


# Wikipedia's five type groups, embedded for exact comparison
WIKI = {
    "aab": [[3,13,14],[3,21,22],[3,25,26],[5,11,14],[5,19,22],[5,25,28],[6,11,13],
            [6,19,21],[6,26,28],[7,9,14],[7,10,13],[7,11,12],[7,17,22],[7,18,21],
            [7,19,20],[7,25,30],[7,26,29],[7,27,28],[9,19,26],[9,21,28],[10,19,25],
            [10,22,28],[11,17,26],[11,18,25],[11,19,24],[11,21,30],[11,22,29],
            [11,23,28],[12,21,25],[12,22,26],[13,17,28],[13,19,30],[13,20,25],
            [13,21,24],[13,22,27],[13,23,26],[14,18,28],[14,19,29],[14,20,26],
            [14,21,27],[14,22,24],[14,23,25],[15,19,28],[15,21,26],[15,22,25]],
    "bbb1": [[3,5,6],[3,9,10],[3,17,18],[3,29,30],[5,9,12],[5,17,20],[5,27,30],
             [6,10,12],[6,18,20],[6,27,29],[9,17,24],[9,23,30],[10,18,24],[10,23,29],
             [12,20,24],[12,23,27],[15,17,30],[15,18,29],[15,20,27],[15,23,24]],
    "bbb2": [[3,12,15],[3,20,23],[3,24,27],[5,10,15],[5,18,23],[5,24,29],[6,9,15],
             [6,17,23],[6,24,30],[9,18,27],[9,20,29],[10,17,27],[10,20,30],
             [12,17,29],[12,18,30]],
    "abg": [[1,6,7],[1,10,11],[1,12,13],[1,14,15],[1,18,19],[1,20,21],[1,22,23],
            [1,24,25],[1,26,27],[1,28,29],[2,5,7],[2,9,11],[2,12,14],[2,13,15],
            [2,17,19],[2,20,22],[2,21,23],[2,24,26],[2,25,27],[2,28,30],[3,4,7],
            [3,8,11],[3,16,19],[3,28,31],[4,9,13],[4,10,14],[4,11,15],[4,17,21],
            [4,18,22],[4,19,23],[4,24,28],[4,25,29],[4,26,30],[5,8,13],[5,16,21],
            [5,26,31],[6,8,14],[6,16,22],[6,25,31],[7,8,15],[7,16,23],[7,24,31],
            [8,17,25],[8,18,26],[8,19,27],[8,20,28],[8,21,29],[8,22,30],[9,16,25],
            [9,22,31],[10,16,26],[10,21,31],[11,16,27],[11,20,31],[12,16,28],
            [12,19,31],[13,16,29],[13,18,31],[14,16,30],[14,17,31]],
    "bgg": [[1,2,3],[1,4,5],[1,8,9],[1,16,17],[1,30,31],[2,4,6],[2,8,10],[2,16,18],
            [2,29,31],[4,8,12],[4,16,20],[4,27,31],[8,16,24],[8,23,31],[15,16,31]],
}


def wiki_set():
    s = set()
    for group in WIKI.values():
        for t in group:
            s.add(frozenset(t))
    return s


# ----------------------------------------------------------------------------
# 4. Associativity analysis
# ----------------------------------------------------------------------------

def assoc_ok(table, a, b, c):
    """(e_a e_b) e_c == e_a (e_b e_c)?  Indices are always equal by XOR,
    so only the accumulated signs can differ."""
    s1, k1 = table[a][b]
    s2, k2 = table[k1][c]
    t1, m1 = table[b][c]
    t2, m2 = table[a][m1]
    return (s1 * s2, k2) == (t1 * t2, m2)


def associativity_report(table):
    ordered_na = 0
    dist_na = set()
    nondist_na = set()
    for a, b, c in itertools.permutations(range(1, len(table)), 3):
        if not assoc_ok(table, a, b, c):
            ordered_na += 1
            key = frozenset((a, b, c))
            if (a ^ b) == c or (b ^ c) == a or (a ^ c) == b:
                dist_na.add(key)
            else:
                nondist_na.add(key)
    return ordered_na, dist_na, nondist_na


# ----------------------------------------------------------------------------
# 5. Language-first measurement layer
#    token -> basis unit -> algebra product; measure order/bracket sensitivity
# ----------------------------------------------------------------------------

def fnv1a64(s):
    h = 14695981039346656037
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h


def token_basis(token, dim=31):
    """Placeholder deterministic token->imaginary-unit map (1..31).
    In a real system this is a LEARNED embedding; this hash stands in for it."""
    return (fnv1a64(token) % dim) + 1


def product_left(table, idxs):
    """e_t0 * e_t1 * ... * e_tn  (left-associative)."""
    s, k = 1, 0
    for i in idxs:
        s2, k2 = table[k][i]
        s *= s2
        k = k2
    return (s, k)


def product_right(table, idxs):
    """t0*(t1*(...*tn))  (right-associative)."""
    s, k = 1, idxs[-1]
    for i in reversed(idxs[:-1]):
        s2, k2 = table[i][k]
        s *= s2
        k = k2
    return (s, k)


def measure_sentence(table, words):
    idxs = [token_basis(w) for w in words]
    left = product_left(table, idxs)
    right = product_right(table, idxs)
    rev = product_left(table, list(reversed(idxs)))
    return {
        "tokens": words,
        "basis": idxs,
        "left_assoc": left,
        "right_assoc": right,
        "reversed": rev,
        "non_associative": left != right,
        "non_commutative": left != rev,
    }


# ----------------------------------------------------------------------------
# 6. Main report
# ----------------------------------------------------------------------------

def main():
    algebras = build_all()
    T = algebras["T"]
    print("=== TRIGINTADUONION ENGINE (32-dim, verified) ===\n")

    for name in ["R", "C", "H", "O", "S", "T"]:
        errs = verify(algebras[name], name)
        status = "OK" if not errs else f"{len(errs)} ERRORS"
        print(f"  {name:>2}  {len(algebras[name])}x{len(algebras[name])}  {status}")
        for e in errs[:3]:
            print(f"       {e}")

    triples = extract_triples(T)
    wiki = wiki_set()
    print(f"\nExtracted triples: {len(triples)}   Wikipedia triples: {len(wiki)}")
    print(f"Missing from computed: {len(wiki - triples)}   Extra in computed: {len(triples - wiki)}")
    print(f"Wiki type counts: " + ", ".join(f"{k}={len(v)}" for k, v in WIKI.items()))

    ordered_na, dist_na, nondist_na = associativity_report(T)
    print(f"\nNon-associative ordered triples: {ordered_na}")
    print(f"  ...distinguished (among the 155): {len(dist_na)}  "
          f"(expected 0 -- all 155 are associative quaternion subloops)")
    print(f"  ...non-distinguished (4+ units in associator): {len(nondist_na)}")

    # sanity: the octonion layer must be non-associative OUTSIDE its 7 triples
    oct_na = 0
    for a, b, c in itertools.permutations(range(1, 8), 3):
        if not assoc_ok(algebras["O"], a, b, c):
            oct_na += 1
    print(f"\nOctonion sanity: {oct_na} non-associative orderings in O "
          f"(>0 proves the associator detector works)")

    print("\n=== LANGUAGE MEASUREMENT (placeholder token->basis map) ===")
    # Note: some token sets collide under the placeholder hash (e.g. "how" and
    # "to" both -> 31); a real system replaces token_basis with a learned
    # embedding. The examples below were chosen to have distinct basis units.
    for words in [["dog", "bites", "man"], ["man", "bites", "dog"],
                  ["the", "small", "step"], ["the", "runner", "collapsed"],
                  ["quick", "brown", "fox", "slept"]]:
        m = measure_sentence(T, words)
        print(f"  {' '.join(words):<22} basis={m['basis']}  "
              f"non-assoc={int(m['non_associative'])}  non-comm={int(m['non_commutative'])}  "
              f"left={m['left_assoc']} right={m['right_assoc']} rev={m['reversed']}")


if __name__ == "__main__":
    main()
