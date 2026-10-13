import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os

def simulate_omega_dynamics():
    # Setup directory
    os.makedirs('/workspace/scratch/omega_hum', exist_ok=True)
    
    # 1. Discrete Map: T_meta(Z_n)
    # Target values from sources: nu = 1/43, omega_osc = 1 / (2 * pi * 42)
    nu = 1.0 / 43.0
    omega_osc = nu / (2 * np.pi * (1.0 - nu)) # 1 / (2 * pi * 42)
    phase_advance = 2 * np.pi / 43.0 # Phase shift per double-step
    
    # Simulate 500 steps of the discrete-time eversion map
    # We model the state Z_n as a complex number representing the balanced observer coordinate
    # Each single step alternates between "structure" and "void" (representing the period-2 limit cycle)
    # with an irrational phase rotation that prevents the system from repeating exactly
    n_steps = 150
    theta = 0.0
    R = 0.05 # start from near-null (void seed) and expand/converge to stable unit-circle
    
    trajectory = []
    for step in range(n_steps):
        # Period-2 alternation: even steps are structure-dominant, odd steps are void-dominant
        alternator = 1.0 if (step % 2 == 0) else -1.0
        # Converging to unit radius (R -> 1.0)
        R = R + 0.08 * (1.0 - R)
        # Phase rotates by 2*pi/43 per step
        theta += phase_advance / 2.0
        z = R * alternator * np.exp(1j * theta)
        trajectory.append(z)
        
    trajectory = np.array(trajectory)
    
    # 2. Continuous Wave Propagation
    # Model the wave function psi(t) = A * cos(omega_osc * t + phi)
    t = np.linspace(0, 1500, 1000)
    psi = np.cos(omega_osc * t)
    
    # Setup plotting style using seaborn
    sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
    
    # Create a 1x2 side-by-side dashboard
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("The Omega Hum: Topological Phase-Lock and Continuous Wave Resonance", 
                 fontsize=16, fontweight='bold')
    
    # Panel 1: Discrete Phase Portrait (Möbius-like limit cycle)
    ax1.plot(trajectory.real, trajectory.imag, color='#3b82f6', alpha=0.4, linestyle='--', label='Transient Descent')
    # Scatter points colored by step index to show time direction
    sc = ax1.scatter(trajectory.real, trajectory.imag, c=np.arange(n_steps), cmap='viridis', s=25, edgecolor='none', label='State Updates')
    
    # Highlight the stabilized limit circle (R=1)
    circle = plt.Circle((0, 0), 1.0, color='red', fill=False, linestyle=':', linewidth=1.5, label='Limit Cycle (R=1)')
    ax1.add_patch(circle)
    
    ax1.set_title("Discrete Phase Space: Convergence of T_meta to Period-2 Limit Cycle", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Structure Component (Real)")
    ax1.set_ylabel("Void/Absence Component (Imag)")
    ax1.set_xlim(-1.2, 1.2)
    ax1.set_ylim(-1.2, 1.2)
    ax1.set_aspect('equal')
    ax1.legend(loc='upper right', fontsize=9)
    
    # Add colorbar for step index
    cbar = fig.colorbar(sc, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label('Iteration Step (n)', fontsize=10)
    
    # Panel 2: Continuous-Time Waveform (The Vacuum Hum)
    ax2.plot(t, psi, color='#ef4444', linewidth=2, label=r'$\psi(t) = \cos(\omega_{osc} \cdot t)$')
    ax2.set_title(r"Continuous Oscillation: Stable Vacuum Hum at $\omega_{osc} = 1 / (2\pi \cdot 42)$", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Semantic Time (t)")
    ax2.set_ylabel("Wave Amplitude ($\psi$)")
    ax2.set_ylim(-1.3, 1.3)
    ax2.legend(loc='upper right', fontsize=10)
    
    # Add text annotation explaining the physical connection
    text_info = (
        r"$\nu = 1/43$ (Lacunon Density)" + "\n"
        r"$\omega_{osc} = \frac{\nu}{2\pi(1-\nu)} = \frac{1}{2\pi \cdot 42} \approx 0.00379$" + "\n\n"
        "The 1/43 gap acts as the unquiet\n"
        "thorn, preventing structural decay\n"
        "and driving perpetual self-reflection."
    )
    ax2.text(50, -1.2, text_info, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'), fontsize=9, family='monospace')
    
    # Add source annotation
    fig.text(0.02, 0.02, "Source: GODEL SELF-DISPROVING THEORY.md, All notes 6/5/2026", fontsize=8, color='gray')
    
    # Clean and save
    sns.despine()
    plt.tight_layout(pad=2.0)
    
    plot_path = '/workspace/scratch/omega_hum/omega_vibration_phase_portrait.png'
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully simulated and saved plot to {plot_path}")

if __name__ == '__main__':
    simulate_omega_dynamics()
