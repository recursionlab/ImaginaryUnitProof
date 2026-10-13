import numpy as np
import os
import matplotlib.pyplot as plt

# Set matplotlib to run in headless mode
import matplotlib
matplotlib.use('Agg')

# =====================================================================
# 1. Complex-Valued Sedenion Algebra (dim=16)
# =====================================================================

def cd_conjugate_complex(x):
    if len(x) == 1:
        return np.conj(x)
    mid = len(x) // 2
    a = x[:mid]
    b = x[mid:]
    return np.concatenate([cd_conjugate_complex(a), -b])

def cd_multiply_complex(x, y):
    assert len(x) == len(y), "Dimension mismatch"
    if len(x) == 1:
        return x * y
    mid = len(x) // 2
    a = x[:mid]
    b = x[mid:]
    c = y[:mid]
    d = y[mid:]
    
    ac = cd_multiply_complex(a, c)
    d_conj_b = cd_multiply_complex(cd_conjugate_complex(d), b)
    da = cd_multiply_complex(d, a)
    b_c_conj = cd_multiply_complex(b, cd_conjugate_complex(c))
    
    left = ac - d_conj_b
    right = da + b_c_conj
    return np.concatenate([left, right])

def cd_associator_complex(x, y, z):
    xy = cd_multiply_complex(x, y)
    xy_z = cd_multiply_complex(xy, z)
    
    yz = cd_multiply_complex(y, z)
    x_yz = cd_multiply_complex(x, yz)
    
    return xy_z - x_yz

# =====================================================================
# 2. Time Crystal Non-Associative Simulator Suite
# =====================================================================

def run_complex_time_crystal_ref(M_defects: int, n_steps: int = 120, eps: float = 0.05, J: float = 0.35, J_xy: float = 0.25, alpha: float = 0.05):
    """
    Simulates a 16-dimensional complex non-associative Floquet system
    with Many-Body Localization (MBL) disorder modeled by M defects.
    """
    np.random.seed(42) # Keep deterministic across sweeps
    d = 16
    
    # 1. State vector (initially localized on qubit 0)
    psi = np.zeros(d, dtype=complex)
    psi[0] = 1.0 + 0j
    
    # 2. Localized random fields (Disorder potential)
    h_k = np.random.uniform(-1.0, 1.0, d)
    W = 4.5 * (M_defects / 15.0) # Disorder strength scaling
    U_dis = np.exp(-1j * W * h_k)
    
    # 3. Many-body interaction Hamiltonian (H_total = J * H_diag + J_xy * V_non_diag)
    v_k = np.random.uniform(-1.0, 1.0, d)
    H_diag = np.diag(v_k)
    
    V_non_diag = np.random.randn(d, d) + 1j * np.random.randn(d, d)
    V_non_diag = (V_non_diag + V_non_diag.conj().T) / 2.0
    np.fill_diagonal(V_non_diag, 0.0) # Exclude diagonal
    
    H_total = J * H_diag + J_xy * V_non_diag
    evals, evecs = np.linalg.eigh(H_total)
    U_int = evecs @ np.diag(np.exp(-1j * evals)) @ evecs.conj().T
    
    # 4. Non-associative Pulse Drive represented as a Sedenion
    U_pulse = np.zeros(d, dtype=complex)
    U_pulse[0] = eps
    U_pulse[1] = np.sqrt(1.0 - eps**2)
    U_pulse = U_pulse / np.linalg.norm(U_pulse)
    
    sz_history = []
    torsion_history = []
    entropy_history = []
    
    gamma = 0.15 # Baseline damping coefficient
    
    for step in range(n_steps):
        # Measure local torsion (associator defect) [U_pulse, U_dis, psi]
        assoc = cd_associator_complex(U_pulse, U_dis, psi)
        tau_A = float(np.linalg.norm(assoc))
        torsion_history.append(tau_A)
        
        # Calculate recursive entropy (REF)
        p = np.abs(psi)**2 / np.sum(np.abs(psi)**2)
        p = np.clip(p, 1e-12, 1.0)
        S_n = -np.sum(p * np.log(p))
        entropy_history.append(S_n)
        
        # Apply localizing disorder
        psi_dis = U_dis * psi
        
        # Apply many-body interaction and hopping
        psi_int = U_int @ psi_dis
        psi_int = psi_int / np.linalg.norm(psi_int)
        
        # Apply non-associative pulse drive
        psi_next = cd_multiply_complex(U_pulse, psi_int)
        
        # Apply RUEE+ self-correcting feedback clamp to suppress thermalization
        gamma_n = gamma * np.exp(-0.06 * np.abs(S_n))
        drift = alpha * np.sin(np.real(np.sum(psi))) * psi
        psi = psi_next + gamma_n * drift
        psi = psi / np.linalg.norm(psi)
        
        # Compute physical spin expectation: <sigma_z> = |psi_0|^2 - |psi_1|^2
        sz = np.abs(psi[0])**2 - np.abs(psi[1])**2
        sz_history.append(sz)
        
    return np.array(sz_history), np.array(torsion_history), np.array(entropy_history)

def run_f2_defect_sweep_complete():
    defect_range = range(0, 16)
    coherence_ratios = []
    mean_torsions = []
    
    print("\n" + "="*80)
    print("      LAUNCHING COMPLETED NON-ASSOCIATIVE DTC STABILIZER (SEDENION)")
    print("="*80)
    
    for M in defect_range:
        sz_hist, torsions, _ = run_complex_time_crystal_ref(M_defects=M)
        
        # Compute coherence ratio at f = 1/2
        fft_vals = np.fft.rfft(sz_hist - np.mean(sz_hist))
        freqs = np.fft.rfftfreq(len(sz_hist), d=1.0)
        sub_idx = np.argmin(np.abs(freqs - 0.5))
        coherence = np.abs(fft_vals[sub_idx])**2 / np.sum(np.abs(fft_vals)**2)
        
        coherence_ratios.append(coherence)
        mean_torsions.append(np.mean(torsions))
        
        if coherence < 0.2:
            state_str = "THERMAL (Unlocked)"
        elif coherence < 0.4:
            state_str = "TRANSITION MODE"
        elif coherence < 0.7:
            state_str = "DTC PHASE (LOCKED)"
        else:
            state_str = "FROZEN (Zeno)"
            
        print(f"  M = {M:2d} Defects | Subharmonic Coherence: {coherence:6.2%} | Mean Torsion (τ_A): {np.mean(torsions):.6f} | {state_str}")
        
    # Generate the validation plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    color = 'tab:blue'
    ax1.set_xlabel('Disorder Strength (M Defects)')
    ax1.set_ylabel('Subharmonic f=1/2 Coherence Ratio', color=color)
    ax1.plot(defect_range, coherence_ratios, 'o-', color=color, linewidth=2.5, label='Subharmonic Coherence')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Mean Non-Associative Torsion (τ_A)', color=color)
    ax2.plot(defect_range, mean_torsions, 's--', color=color, linewidth=1.5, alpha=0.7, label='Associator Torsion')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Complex Sedenionic DTC Phase Transition vs. MBL Defect Count (M)', fontsize=12, fontweight='bold')
    fig.tight_layout()  
    
    os.makedirs("/workspace/artifacts/", exist_ok=True)
    plot_path = "/workspace/artifacts/time_crystal_stabilizer.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print("\n  ✅ SUCCESS: Time Crystal phase transition plot saved to artifacts.")
    return coherence_ratios, plot_path

if __name__ == "__main__":
    run_f2_defect_sweep_complete()
