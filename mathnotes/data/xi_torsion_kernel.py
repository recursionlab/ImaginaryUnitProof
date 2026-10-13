import numpy as np

def cd_conj(x):
    """Computes the Cayley-Dickson conjugate for dimension 2^n."""
    if len(x) == 1:
        return (x[0],)
    mid = len(x) // 2
    a, b = x[:mid], x[mid:]
    return cd_conj(a) + tuple(-v for v in b)

def cd_mul(x, y):
    """Computes recursive Cayley-Dickson multiplication: (a,b)(c,d) = (ac - d*conj(b), conj(a)d + bc)."""
    if len(x) == 1:
        return (x[0] * y[0],)
    mid = len(x) // 2
    a, b = x[:mid], x[mid:]
    c, d = y[:mid], y[mid:]
    
    ac = cd_mul(a, c)
    conj_b = cd_conj(b)
    d_conj_b = cd_mul(d, conj_b)
    left = tuple(ac_val - d_conj_b_val for ac_val, d_conj_b_val in zip(ac, d_conj_b))
    
    conj_a = cd_conj(a)
    conj_a_d = cd_mul(conj_a, d)
    bc = cd_mul(b, c)
    right = tuple(conj_a_d_val + bc_val for conj_a_d_val, bc_val in zip(conj_a_d, bc))
    
    return left + right

def associator(a, b, c):
    """Computes the non-associative associator [a,b,c] = (a*b)*c - a*(b*c)."""
    ab_c = cd_mul(cd_mul(a, b), c)
    a_bc = cd_mul(a, cd_mul(b, c))
    return tuple(x - y for x, y in zip(ab_c, a_bc))

def run_simulation():
    dim = 16 # Sedenions
    # Basis vectors e_1, e_3, e_4, e_6
    e1 = np.zeros(dim); e1[1] = 1.0
    e3 = np.zeros(dim); e3[3] = 1.0
    e4 = np.zeros(dim); e4[4] = 1.0
    e6 = np.zeros(dim); e6[6] = 1.0
    
    # Sedenion zero divisor pair: x = e1 + e6, y = e3 - e4
    x = tuple(e1 + e6)
    y = tuple(e3 - e4)
    prod = cd_mul(x, y)
    prod_norm = np.linalg.norm(prod)
    
    # Jacobi Scar norm ||[e1, e2, e4]||
    e2 = np.zeros(dim); e2[2] = 1.0
    assoc_val = associator(tuple(e1), tuple(e2), tuple(e4))
    jacobi_scar_norm = np.linalg.norm(assoc_val)
    
    # Construct Left-Multiplication matrix L_x
    Lx = np.zeros((dim, dim))
    for j in range(dim):
        ej = np.zeros(dim); ej[j] = 1.0
        res = cd_mul(x, tuple(ej))
        Lx[:, j] = res
        
    # Unrotated overlap S = Lx^T * Lx
    S0 = Lx.T @ Lx
    eigenvals_S0 = np.sort(np.linalg.eigvalsh(S0))
    
    # Synthetic Noisy Hamiltonian H
    np.random.seed(42)
    H_noise = np.random.normal(0, 0.05, (dim, dim))
    H = H_noise + H_noise.T + np.diag(np.linspace(1.0, 5.0, dim))
    
    # SO(2) Rotation mixing H and S
    theta = 1.4756 # ~84.55 degrees
    S_theta = S0 * np.cos(theta) + H * np.sin(theta)
    eigenvals_S_theta = np.sort(np.linalg.eigvalsh(S_theta))
    
    print(f"Sedenion Zero-Divisor Product Norm ||x * y||: {prod_norm:.6f}")
    print(f"Jacobi Scar Norm ||[e1, e2, e4]||: {jacobi_scar_norm:.6f}")
    print(f"Unrotated Overlap Min Eigenvalue: {eigenvals_S0[0]:.6f}")
    print(f"SO(2) Rotated Overlap Min Eigenvalue (theta={theta:.4f} rad): {eigenvals_S_theta[0]:.6f}")

if __name__ == "__main__":
    run_simulation()
