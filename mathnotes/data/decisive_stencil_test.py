"""
Decisive Test: Composite L² vs Direct Fourth-Order Stencil
===========================================================

Tests whether the +10% bias comes from:
- Composite stencil (L²) artifact
- Lattice dispersion of direct ∂⁴ stencil
- Estimator bias
"""

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as sla

# ============================================================================
# TWO DISCRETE BI-LAPLACIAN STENCILS
# ============================================================================

def laplacian_1d_sparse(N, h):
    """1D Dirichlet Laplacian: [-1, 2, -1]/h²"""
    main = 2.0 / h**2 * np.ones(N)
    off = -1.0 / h**2 * np.ones(N-1)
    return sps.diags([main, off, off], [0, -1, 1], format='csr')

def bilaplacian_composite(N, h):
    """Composite: L @ L where L is discrete Laplacian"""
    L = laplacian_1d_sparse(N, h)
    return L @ L

def bilaplacian_direct(N, h):
    """
    Direct fourth-order stencil: [1, -4, 6, -4, 1]/h⁴
    This is the natural discretization of ∂⁴/∂x⁴
    """
    main = 6.0 / h**4 * np.ones(N)
    off1 = -4.0 / h**4 * np.ones(N-1)
    off2 = 1.0 / h**4 * np.ones(N-2)
    return sps.diags([main, off1, off1, off2, off2], [0, -1, 1, -2, 2], format='csr')

def analytic_dispersion_composite(k, h):
    """Dispersion of composite L²: lambda(k) = (4/h² sin²(kh/2))²"""
    return (4.0 / h**2 * np.sin(k * h / 2)**2)**2

def analytic_dispersion_direct(k, h):
    """Dispersion of direct stencil: lambda(k) = (4/h⁴) (1 - cos(kh))²"""
    # Direct fourth-order: (2/h⁴) * (1 - cos(kh)) * (something)
    # Actually: [1, -4, 6, -4, 1] corresponds to 2*(1 - cos(kh))²/h⁴
    return (4.0 / h**4) * (1 - np.cos(k * h))**2

# ============================================================================
# DISPERSION COMPARISON
# ============================================================================

def compare_dispersions(N=100):
    """Compare dispersion relations of both stencils"""
    h = 1.0 / (N + 1)
    
    # Build both operators
    H_comp = bilaplacian_composite(N, h)
    H_dir = bilaplacian_direct(N, h)
    
    # Get eigenvalues numerically
    eig_comp = sla.eigsh(H_comp, k=N-2, which='SM', return_eigenvectors=False, tol=1e-12)
    eig_dir = sla.eigsh(H_dir, k=N-2, which='SM', return_eigenvectors=False, tol=1e-12)
    eig_comp = np.sort(eig_comp)
    eig_dir = np.sort(eig_dir)
    
    # Analytic dispersion
    k_vals = np.arange(1, N+1) * np.pi / (N + 1)
    disp_comp = analytic_dispersion_composite(k_vals, h)
    disp_dir = analytic_dispersion_direct(k_vals, h)
    
    print("="*70)
    print("DISPERSION RELATION COMPARISON")
    print("="*70)
    print(f"{'k':>6} {'lambda_composite':>14} {'lambda_direct':>14} {'lambda_an_comp':>14} {'lambda_an_dir':>14} {'ratio C/A':>10} {'ratio D/A':>10}")
    for i in [0, N//8, N//4, 3*N//8, N//2]:
        print(f"{k_vals[i]:6.4f} {eig_comp[i]:14.4f} {eig_dir[i]:14.4f} {disp_comp[i]:14.4f} {disp_dir[i]:14.4f} {eig_comp[i]/disp_comp[i]:10.4f} {eig_dir[i]/disp_dir[i]:10.4f}")
    
    # Low-k scaling test
    print("\nLow-k scaling (k=1..5):")
    for i in range(min(5, N)):
        k = k_vals[i]
        lam_comp = eig_comp[i]
        lam_dir = eig_dir[i]
        # Fit power law lambda ~ k^z
        if i >= 2:
            # Use k=1,2,3,4,5
            pass
    
    # Local exponent z = d log lambda / d log k
    print("\nLocal exponent z(k) = d log lambda / d log k:")
    for stencil_name, eigvals in [("Composite", eig_comp), ("Direct", eig_dir)]:
        print(f"\n  {stencil_name}:")
        for i in [0, 1, 2, 4, 9, 19, 49]:
            if i + 1 < len(eigvals):
                z = np.log(eigvals[i+1] / eigvals[i]) / np.log(k_vals[i+1] / k_vals[i])
                print(f"    k={k_vals[i]:.4f}: z = {z:.4f} (lambda={eigvals[i]:.2f})")
    
    return eig_comp, eig_dir, k_vals

# ============================================================================
# HEAT TRACE EXPONENT EXTRACTION
# ============================================================================

def heat_trace(eigenvals, t_vals):
    eigenvals = eigenvals[eigenvals > 1e-14]
    return np.sum(np.exp(-t_vals[:, None] * eigenvals[None, :]), axis=1)

def fit_exponent(t_vals, Theta_vals, t_min=None, t_max=None):
    mask = (Theta_vals > 0) & (t_vals > 0)
    if t_min is not None: mask &= (t_vals >= t_min)
    if t_max is not None: mask &= (t_vals <= t_max)
    if np.sum(mask) < 4: return None, None, 0.0
    log_t = np.log(t_vals[mask])
    log_Theta = np.log(Theta_vals[mask])
    coeffs = np.polyfit(log_t, log_Theta, 1)
    alpha = -coeffs[0]
    d_s = 2 * alpha
    pred = coeffs[0] * log_t + coeffs[1]
    ss_res = np.sum((log_Theta - pred)**2)
    ss_tot = np.sum((log_Theta - np.mean(log_Theta))**2)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    return alpha, d_s, r2

def select_continuum_window(eigenvals, t_vals, Theta_vals, frac=0.1):
    eigenvals = eigenvals[eigenvals > 1e-14]
    N = len(eigenvals)
    k_cutoff = max(10, int(N * frac))
    eig_cont = eigenvals[:k_cutoff]
    lambda_max_cont = eig_cont[-1]
    lambda_min_all = eigenvals[0]
    t_min = 10.0 / lambda_max_cont
    t_max = 0.1 / lambda_min_all
    t_min = max(t_min, t_vals[0])
    t_max = min(t_max, t_vals[-1])
    if t_max <= t_min * 2:
        t_min = t_vals[len(t_vals)//4]
        t_max = t_vals[3*len(t_vals)//4]
    return t_min, t_max

def extract_exponent(eigenvals, name):
    """Extract exponent for given eigenvalues"""
    t_vals = np.logspace(-8, -1, 200)
    Theta = heat_trace(eigenvals, t_vals)
    t_min, t_max = select_continuum_window(eigenvals, t_vals, Theta, frac=0.15)
    alpha, d_s, r2 = fit_exponent(t_vals, Theta, t_min, t_max)
    print(f"  {name}: alpha={alpha:.6f}, d_s={d_s:.6f}, R²={r2:.6f}, window=[{t_min:.2e},{t_max:.2e}]")
    return alpha, d_s

# ============================================================================
# MAIN TEST
# ============================================================================

def run_decisive_test():
    print("#"*70)
    print("# DECISIVE TEST: COMPOSITE L² vs DIRECT FOURTH-ORDER STENCIL")
    print("#"*70)
    
    for N in [100, 200, 500, 1000]:
        h = 1.0 / (N + 1)
        print(f"\n--- N = {N} ---")
        
        H_comp = bilaplacian_composite(N, h)
        H_dir = bilaplacian_direct(N, h)
        
        # Compute eigenvalues (full spectrum for small N, partial for large)
        k_max = min(N-2, 300) if N <= 200 else min(N-2, 500)
        
        eig_comp = sla.eigsh(H_comp, k=k_max, which='SM', return_eigenvectors=False, tol=1e-12)
        eig_dir = sla.eigsh(H_dir, k=k_max, which='SM', return_eigenvectors=False, tol=1e-12)
        eig_comp = np.sort(eig_comp)
        eig_dir = np.sort(eig_dir)
        
        # Also compute analytic dispersion for reference
        k_vals = np.arange(1, k_max+1) * np.pi / (N + 1)
        disp_comp = analytic_dispersion_composite(k_vals, h)
        disp_dir = analytic_dispersion_direct(k_vals, h)
        
        # Compare at low k
        print(f"  Low-k (k=1): lambda_comp={eig_comp[0]:.4f}, lambda_ana_comp={disp_comp[0]:.4f}, ratio={eig_comp[0]/disp_comp[0]:.6f}")
        print(f"  Low-k (k=1): lambda_dir={eig_dir[0]:.4f}, lambda_ana_dir={disp_dir[0]:.4f}, ratio={eig_dir[0]/disp_dir[0]:.6f}")
        
        # Extract exponents
        print("  Exponent extraction (continuum window frac=0.15):")
        extract_exponent(eig_comp, "Composite L²")
        extract_exponent(eig_dir, "Direct [1,-4,6,-4,1]")
        
        # Also test with analytic eigenvalues for reference
        eig_comp_full = analytic_dispersion_composite(np.arange(1, N+1) * np.pi * h, h)
        eig_dir_full = analytic_dispersion_direct(np.arange(1, N+1) * np.pi * h, h)
        print("  Analytic eigenvalues (full N):")
        extract_exponent(eig_comp_full, "Composite (analytic)")
        extract_exponent(eig_dir_full, "Direct (analytic)")

def dispersion_analysis():
    """Detailed dispersion analysis"""
    print("\n" + "="*70)
    print("DETAILED DISPERSION ANALYSIS")
    print("="*70)
    
    N = 200
    h = 1.0 / (N + 1)
    k_vals = np.arange(1, N+1) * np.pi / (N + 1)
    
    # Analytic dispersions
    disp_comp = analytic_dispersion_composite(k_vals, h)
    disp_dir = analytic_dispersion_direct(k_vals, h)
    
    # Local exponent
    print("\nLocal exponent z(k) = d log lambda / d log k (analytic):")
    for i in range(min(10, N-1)):
        z_comp = np.log(disp_comp[i+1] / disp_comp[i]) / np.log(k_vals[i+1] / k_vals[i])
        z_dir = np.log(disp_dir[i+1] / disp_dir[i]) / np.log(k_vals[i+1] / k_vals[i])
        print(f"  k={k_vals[i]:.5f}: z_comp={z_comp:.4f}, z_dir={z_dir:.4f}, lambda_comp={disp_comp[i]:.2f}, lambda_dir={disp_dir[i]:.2f}")
    
    # Asymptotic at very low k
    k_small = np.logspace(-4, -1, 20)
    lam_comp = analytic_dispersion_composite(k_small, h)
    lam_dir = analytic_dispersion_direct(k_small, h)
    
    # Fit power law at low k
    for name, lam in [("Composite", lam_comp), ("Direct", lam_dir)]:
        coeffs = np.polyfit(np.log(k_small), np.log(lam), 1)
        z_asymptotic = coeffs[0]
        print(f"\n  {name} low-k asymptotic z = {z_asymptotic:.6f} (expected 4.0)")

if __name__ == "__main__":
    run_decisive_test()
    dispersion_analysis()
    
    print("\n" + "#"*70)
    print("# INTERPRETATION")
    print("#"*70)
    print("""
Three possible outcomes:

1. Direct stencil → alpha=0.250 (d_s=0.500): 
   The composite L² stencil was the problem. The framework's theory is 
   correct for the continuum operator; the discrete implementation needs 
   the correct fourth-order stencil.

2. Direct stencil → alpha=0.276 (d_s=0.552): 
   The lattice itself has a different exponent. The framework's "0.250" 
   is a continuum idealization; the discrete bi-Laplacian genuinely has 
   a different scaling. This is a real structural fact.

3. Both stencils give same bias, but analytic dispersion z=4.0:
   The estimator is biased by finite-t effects or window selection.
   
If outcome 2: The framework needs an explicit lattice correction term.
If outcome 1: Use direct stencil for discrete implementations.
If outcome 3: Fix the estimator/window selection.
""")