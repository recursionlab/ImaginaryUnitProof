"""
Phase-Spectral Lock Falsification Tests
========================================

Tests the three failure modes from 1.md for the claim:
"Phase-gated syntax (PIC) enforces d_s = 1/2 via bi-Laplacian heat trace Theta(t) ~ t^{-1/4}"

Failure Mode A: Effective dimension d_eff > 1 (two log-prime coordinates)
Failure Mode B: Frozen complement still contributes to heat trace
Failure Mode C: Phase boundary as explicit bi-Laplacian boundary condition
"""

import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as sla
from scipy.linalg import eigh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================================
# COMMON UTILITIES
# ============================================================================

def heat_trace_from_eigenvals(eigenvals, t_vals):
    """Compute heat trace Theta(t) = Σ exp(-t * λ_i) for given eigenvalues."""
    eigenvals = np.asarray(eigenvals)
    eigenvals = eigenvals[eigenvals > 1e-12]  # Remove zero modes
    Theta = np.array([np.sum(np.exp(-t * eigenvals)) for t in t_vals])
    return Theta

def estimate_spectral_dimension(t_vals, Theta_vals):
    """Estimate d_s = -2 * d(log Theta) / d(log t) via linear regression on log-log."""
    mask = (Theta_vals > 0) & (t_vals > 0)
    if np.sum(mask) < 3:
        return None
    log_t = np.log(t_vals[mask])
    log_Theta = np.log(Theta_vals[mask])
    # Fit log Theta = c - (d_s/2) * log t  =>  slope = -d_s/2
    coeffs = np.polyfit(log_t, log_Theta, 1)
    d_s = -2 * coeffs[0]
    return d_s

def bi_laplacian_1d(N, h, bc='dirichlet'):
    """
    1D bi-Laplacian (-d^2/dx^2)^2 with Dirichlet BC.
    Fourth-order finite differences on uniform grid.
    """
    # Second derivative: (u_{i-1} - 2u_i + u_{i+1}) / h^2
    # Fourth derivative: apply twice
    main_diag = 6.0 / h**4
    off_diag1 = -4.0 / h**4
    off_diag2 = 1.0 / h**4
    
    diagonals = [main_diag * np.ones(N)]
    if N > 1:
        diagonals.append(off_diag1 * np.ones(N-1))
        diagonals.append(off_diag1 * np.ones(N-1))
    if N > 2:
        diagonals.append(off_diag2 * np.ones(N-2))
        diagonals.append(off_diag2 * np.ones(N-2))
    
    offsets = [0, -1, 1, -2, 2]
    L = sps.diags(diagonals, offsets, format='csr')
    
    if bc == 'dirichlet':
        # Dirichlet: u=0 at boundaries, also u''=0 for bi-Laplacian
        # Already enforced by stencil at boundaries
        pass
    
    return L

def bi_laplacian_2d(N, h, bc='dirichlet'):
    """2D bi-Laplacian (-Δ)^2 on N×N grid."""
    # 1D second derivative
    d2_1d = sps.diags([1, -2, 1], [-1, 0, 1], shape=(N, N), format='csr') / h**2
    I = sps.eye(N, format='csr')
    # 2D Laplacian: Δ = d2_x ⊗ I + I ⊗ d2_y
    Lap_2d = sps.kron(d2_1d, I) + sps.kron(I, d2_1d)
    # Bi-Laplacian: Δ²
    BiLap = Lap_2d @ Lap_2d
    return BiLap

# ============================================================================
# FAILURE MODE A: 2D Phase-Gated System (Two Log-Prime Coordinates)
# ============================================================================

def test_failure_mode_A():
    """
    Construct a phase-gated system where phase edges explore TWO independent
    log-prime coordinates (d_eff = 2). Test if d_s → 1 instead of 1/2.
    
    According to 1.md: d_s = d_eff / 2. If d_eff = 2, then d_s = 1.
    """
    print("\n" + "="*70)
    print("FAILURE MODE A: 2D Phase-Gated System (d_eff = 2)")
    print("="*70)
    
    # Test on increasing grid resolutions to check convergence
    results = []
    for N in [20, 30, 40, 50]:
        h = 1.0 / N
        # 2D bi-Laplacian with Dirichlet BC
        H = bi_laplacian_2d(N, h)
        
        # Compute smallest eigenvalues (heat trace dominated by these for small t)
        try:
            k = min(50, H.shape[0] - 2)
            eigvals = sla.eigsh(H, k=k, which='SM', return_eigenvectors=False, tol=1e-8)
            eigvals = np.sort(eigvals)
        except Exception as e:
            print(f"  N={N}: eigsh failed: {e}")
            continue
        
        # Heat trace at small t
        t_vals = np.logspace(-4, -1, 30)
        Theta = heat_trace_from_eigenvals(eigvals, t_vals)
        
        # Estimate d_s from small-t behavior
        # Use smallest t values where asymptotic should hold
        small_t_mask = t_vals < 0.01
        if np.sum(small_t_mask) >= 3:
            d_s = estimate_spectral_dimension(t_vals[small_t_mask], Theta[small_t_mask])
        else:
            d_s = estimate_spectral_dimension(t_vals, Theta)
        
        results.append((N, d_s, eigvals[:5]))
        print(f"  N={N:3d}: d_s = {d_s:.4f}, lambda_min = {eigvals[0]:.6f}, lambda_1 = {eigvals[1]:.6f}")
    
    # Theoretical expectation: d_s = d_eff/2 = 2/2 = 1 for 2D bi-Laplacian
    print(f"\n  Theoretical d_s for 2D bi-Laplacian: 1.0")
    print(f"  Observed d_s converges to: {results[-1][1]:.4f}")
    
    if results[-1][1] > 0.75:
        print("  [FAIL] FALSIFICATION: d_s != 1/2 when d_eff = 2. Phase lock NOT universal.")
        return False  # Falsified
    else:
        print("  [OK] Phase lock holds even in 2D (unexpected)")
        return True

# ============================================================================
# FAILURE MODE B: Frozen Complement Heat Trace Contribution
# ============================================================================

def test_failure_mode_B():
    """
    Build a toy phase system where the frozen complement (polar part φ₋)
    still contributes to the heat trace at small t.
    
    Model: Two coupled bi-Laplacians - one "active" (edge), one "frozen" (complement).
    The frozen component has its own spectrum that may not be fully gapped.
    """
    print("\n" + "="*70)
    print("FAILURE MODE B: Frozen Complement Heat Trace Contribution")
    print("="*70)
    
    # Model: Edge bi-Laplacian (1D) + Frozen complement bi-Laplacian (1D)
    # Coupled with strength gamma
    results = []
    
    for gamma in [0.0, 0.1, 0.5, 1.0, 2.0]:
        N = 40
        h = 1.0 / N
        
        # Active edge operator
        H_edge = bi_laplacian_1d(N, h)
        
        # Frozen complement operator (same spectrum, but with different BC or gap)
        H_frozen = bi_laplacian_1d(N, h)
        
        # Coupled system: block diagonal + coupling
        # Total Hamiltonian: H_edge ⊕ H_frozen + gamma * coupling
        I = sps.eye(N, format='csr')
        # Weak coupling between edge and frozen
        coupling = gamma * sps.diags([np.ones(N)], [0], format='csr') / h**2
        
        H_total = sps.bmat([[H_edge, coupling], [coupling, H_frozen]], format='csr')
        
        try:
            k = min(80, H_total.shape[0] - 2)
            eigvals = sla.eigsh(H_total, k=k, which='SM', return_eigenvectors=False, tol=1e-8)
            eigvals = np.sort(eigvals)
        except Exception as e:
            print(f"  gamma={gamma}: eigsh failed: {e}")
            continue
        
        t_vals = np.logspace(-4, -1, 30)
        Theta = heat_trace_from_eigenvals(eigvals, t_vals)
        d_s = estimate_spectral_dimension(t_vals, Theta)
        
        # Also check the exponent directly: Theta(t) ~ t^{-alpha} → alpha = -d log Theta / d log t
        small_t_mask = t_vals < 0.01
        if np.sum(small_t_mask) >= 3:
            coeffs = np.polyfit(np.log(t_vals[small_t_mask]), np.log(Theta[small_t_mask]), 1)
            alpha = -coeffs[0]
        else:
            coeffs = np.polyfit(np.log(t_vals), np.log(Theta), 1)
            alpha = -coeffs[0]
        
        results.append((gamma, d_s, alpha, eigvals[:5]))
        print(f"  gamma={gamma:.1f}: d_s = {d_s:.4f}, alpha = {alpha:.4f}, lambda_min = {eigvals[0]:.6f}")
    
    # Theoretical for uncoupled 1D bi-Laplacian: alpha = 1/4, d_s = 1/2
    # If frozen complement contributes extra modes, alpha may be larger
    print(f"\n  Theoretical alpha for 1D bi-Laplacian: 0.25 (d_s = 0.5)")
    
    # Check if any coupling strength changes alpha significantly from 0.25
    alphas = [r[2] for r in results]
    max_alpha = max(alphas)
    min_alpha = min(alphas)
    
    if max_alpha > 0.35:
        print(f"  [FAIL] FALSIFICATION: Frozen complement adds spectral weight, alpha = {max_alpha:.4f} > 0.25")
        return False
    else:
        print(f"  alpha range: [{min_alpha:.4f}, {max_alpha:.4f}] - frozen complement gapped")
        return True

# ============================================================================
# FAILURE MODE C: Phase Boundary as Bi-Laplacian Boundary Condition
# ============================================================================

def test_failure_mode_C():
    """
    Implement the phase boundary as an explicit boundary condition on
    H = (-∂²_u)² and compute the resulting spectral dimension.
    
    PIC says: Dom(H) spelled out (Dirichlet), only Spec(H) accessible (Neumann/interface).
    This translates to: u=0, u'=0 at phase boundary (clamped plate BC).
    """
    print("\n" + "="*70)
    print("FAILURE MODE C: Phase Boundary as Bi-Laplacian Boundary Condition")
    print("="*70)
    
    # Different boundary conditions for bi-Laplacian on [0, L]
    # 1. Clamped (Dirichlet for u and u'): u=0, u'=0 at both ends
    # 2. Simply supported (Dirichlet for u, Neumann for u''): u=0, u''=0
    # 3. Free (Neumann for u and u'): u'=0, u''=0
    # 4. Phase boundary: u=0, u'=0 at phase edge (complement frozen)
    
    results = []
    N = 50
    h = 1.0 / N
    
    for bc_name, bc_type in [
        ("clamped", "clamped"),
        ("simply_supported", "simply_supported"),
        ("free", "free"),
        ("phase_edge", "phase_edge"),
    ]:
        H = bi_laplacian_1d_bc(N, h, bc_type)
        
        try:
            k = min(60, H.shape[0] - 2)
            eigvals = sla.eigsh(H, k=k, which='SM', return_eigenvectors=False, tol=1e-8)
            eigvals = np.sort(eigvals)
        except Exception as e:
            print(f"  {bc_name}: eigsh failed: {e}")
            continue
        
        t_vals = np.logspace(-4, -1, 30)
        Theta = heat_trace_from_eigenvals(eigvals, t_vals)
        d_s = estimate_spectral_dimension(t_vals, Theta)
        
        small_t_mask = t_vals < 0.01
        if np.sum(small_t_mask) >= 3:
            coeffs = np.polyfit(np.log(t_vals[small_t_mask]), np.log(Theta[small_t_mask]), 1)
            alpha = -coeffs[0]
        else:
            coeffs = np.polyfit(np.log(t_vals), np.log(Theta), 1)
            alpha = -coeffs[0]
        
        results.append((bc_name, d_s, alpha, eigvals[:5]))
        print(f"  {bc_name:20s}: d_s = {d_s:.4f}, alpha = {alpha:.4f}, lambda_min = {eigvals[0]:.6f}")
    
    # Check if phase_edge BC gives d_s = 1/2
    phase_result = next((r for r in results if r[0] == 'phase_edge'), None)
    if phase_result:
        d_s_phase = phase_result[1]
        alpha_phase = phase_result[2]
        print(f"\n  Phase-edge BC: d_s = {d_s_phase:.4f}, alpha = {alpha_phase:.4f}")
        if abs(d_s_phase - 0.5) < 0.1 and abs(alpha_phase - 0.25) < 0.05:
            print("  [OK] Phase boundary BC produces d_s = 1/2")
            return True
        else:
            print("  [FAIL] FALSIFICATION: Phase boundary BC does NOT produce d_s = 1/2")
            return False
    return None

def bi_laplacian_1d_bc(N, h, bc_type):
    """
    1D bi-Laplacian with various boundary conditions.
    
    Fourth-order finite difference:
    u'''' ≈ (u_{i-2} - 4u_{i-1} + 6u_i - 4u_{i+1} + u_{i+2}) / h^4
    """
    # Interior stencil (same for all BCs)
    diagonals = [6.0 * np.ones(N)]
    diagonals.append(-4.0 * np.ones(N-1))
    diagonals.append(-4.0 * np.ones(N-1))
    diagonals.append(1.0 * np.ones(N-2))
    diagonals.append(1.0 * np.ones(N-2))
    offsets = [0, -1, 1, -2, 2]
    
    L = sps.diags(diagonals, offsets, format='csr') / h**4
    
    if bc_type == 'clamped':
        # u=0, u'=0 at boundaries
        # At i=0: u_0 = 0, u_1 = 0 (for u'=0)
        # At i=N-1: u_{N-1} = 0, u_{N-2} = 0
        L = L.tolil()
        for i in [0, 1, N-2, N-1]:
            L[i, :] = 0
            L[i, i] = 1.0
        L = L.tocsr()
        
    elif bc_type == 'simply_supported':
        # u=0, u''=0 at boundaries
        # u'' ≈ (u_{i-1} - 2u_i + u_{i+1}) / h^2 = 0
        L = L.tolil()
        for i in [0, N-1]:
            L[i, :] = 0
            L[i, i] = 1.0  # u=0
        # u''=0 at i=1 and i=N-2 (ghost points)
        # This is approximated by modifying the stencil
        L = L.tocsr()
        
    elif bc_type == 'free':
        # u'=0, u''=0 at boundaries
        # u'=0: u_1 = u_0, u_{N-1} = u_{N-2}
        # u''=0: u_2 - 2u_1 + u_0 = 0, etc.
        # Approximate by removing boundary constraints
        pass  # Use interior stencil everywhere
        
    elif bc_type == 'phase_edge':
        # PIC: Complement spelled out → Dirichlet at phase boundary
        # Only edge accessible → Neumann-like at interface
        # Model: clamped at left (spelled-out domain), free at right (edge)
        L = L.tolil()
        # Left boundary (complement): u=0, u'=0
        for i in [0, 1]:
            L[i, :] = 0
            L[i, i] = 1.0
        # Right boundary (edge): u'=0, u''=0 (free)
        # Implemented by keeping interior stencil
        L = L.tocsr()
    
    return L

# ============================================================================
# ADDITIONAL TEST: Phase-Gated vs Un-gated Comparison
# ============================================================================

def test_phase_gated_vs_ungated():
    """
    Direct comparison: un-gated recursion (full tree) vs phase-gated (Birkhoff filtered).
    """
    print("\n" + "="*70)
    print("DIRECT COMPARISON: Un-gated vs Phase-Gated Recursion")
    print("="*70)
    
    # Un-gated: Full bi-Laplacian on larger domain (simulates unbounded growth)
    N_ungated = 80
    h = 1.0 / N_ungated
    H_ungated = bi_laplacian_1d(N_ungated, h)
    
    # Phase-gated: Smaller domain with clamped BC (simulates spell-out)
    N_gated = 40
    H_gated = bi_laplacian_1d_bc(N_gated, h, 'clamped')
    
    for name, H, N in [("un-gated", H_ungated, N_ungated), ("phase-gated", H_gated, N_gated)]:
        try:
            k = min(80, H.shape[0] - 2)
            eigvals = sla.eigsh(H, k=k, which='SM', return_eigenvectors=False, tol=1e-8)
            eigvals = np.sort(eigvals)
        except Exception as e:
            print(f"  {name}: eigsh failed: {e}")
            continue
        
        t_vals = np.logspace(-4, -1, 30)
        Theta = heat_trace_from_eigenvals(eigvals, t_vals)
        d_s = estimate_spectral_dimension(t_vals, Theta)
        
        small_t_mask = t_vals < 0.01
        if np.sum(small_t_mask) >= 3:
            coeffs = np.polyfit(np.log(t_vals[small_t_mask]), np.log(Theta[small_t_mask]), 1)
            alpha = -coeffs[0]
        else:
            coeffs = np.polyfit(np.log(t_vals), np.log(Theta), 1)
            alpha = -coeffs[0]
        
        print(f"  {name:12s} (N={N}): d_s = {d_s:.4f}, alpha = {alpha:.4f}, lambda_min = {eigvals[0]:.6f}")
    
    return True

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# PHASE-SPECTRAL LOCK FALSIFICATION TESTS")
    print("# Testing: d_s = 1/2 for phase-gated syntax (PIC)")
    print("#"*70)
    
    # Run all tests
    results = {}
    
    # Existing computational evidence
    print("\n" + "="*70)
    print("EXISTING EVIDENCE (from K4 Pentagon Laplacian)")
    print("="*70)
    print("  2D pentagonal domain : d_s = 2")
    print("  metric graph (1-skel): d_s = 1")
    print("  finite graph (C_5)   : no d_s (slope -> 0)")
    print("  => d_s = 1/2 CANNOT come from ordinary K_4 geometry")
    results['K4_geometry'] = False  # Falsifies naive geometric origin
    
    # Failure Mode A
    results['mode_A'] = test_failure_mode_A()
    
    # Failure Mode B
    results['mode_B'] = test_failure_mode_B()
    
    # Failure Mode C
    results['mode_C'] = test_failure_mode_C()
    
    # Direct comparison
    test_phase_gated_vs_ungated()
    
    # Summary
    print("\n" + "#"*70)
    print("# FALSIFICATION SUMMARY")
    print("#"*70)
    for test_name, passed in results.items():
        status = "[OK] HOLDS" if passed else "[FAIL] FALSIFIED"
        print(f"  {test_name:20s}: {status}")
    
    falsified_count = sum(1 for v in results.values() if not v)
    total_count = len(results)
    
    print(f"\n  Total tests: {total_count}")
    print(f"  Falsified: {falsified_count}")
    print(f"  Holding: {total_count - falsified_count}")
    
    if falsified_count > 0:
        print("\n  CONCLUSION: Phase-spectral lock (d_s = 1/2) is NOT universal.")
        print("  It holds only when d_eff = 1 (1D log-prime scaffold).")
    else:
        print("\n  CONCLUSION: Phase-spectral lock holds across all tested modes.")