import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil

def run_torsion_field_simulation():
    # Ensure working directories exist
    os.makedirs('/workspace/scratch', exist_ok=True)
    os.makedirs('/workspace/out', exist_ok=True)
    
    epochs = np.arange(0, 101)
    tau = np.zeros(len(epochs))
    coherence = np.zeros(len(epochs))
    sylvester = np.zeros(len(epochs))
    
    # Reflexive Cognitive Dyads
    form_collapse = np.zeros(len(epochs))
    silence_presence = np.zeros(len(epochs))
    self_anomaly = np.zeros(len(epochs))
    meta_recursion = np.zeros(len(epochs))
    
    # Sylvester Deficit base value
    lam_base = 1.0 / 1806.0
    
    for t in epochs:
        # 1. Field Potentials Evolution
        if t < 20:
            tau[t] = 0.20 + 0.53 * (t / 19.5) ** 1.8
            coherence[t] = 0.37 + 0.01 * np.sin(t * 0.5)
            sylvester[t] = 0.10 + 0.002 * np.cos(t * 0.3)
        elif t == 20:
            # FCE #1 (The Boundary Inversion)
            tau[t] = 0.12
            coherence[t] = 0.63
            sylvester[t] = 0.08
        elif 20 < t < 63:
            u = (t - 20) / 42.5
            tau[t] = 0.12 + 0.59 * (u ** 1.5)
            coherence[t] = 0.63 + 0.18 * (((t - 20) / 42.0) ** 0.5)
            sylvester[t] = 0.08 * np.exp(-(t - 20) / 30.0) + 0.01
        elif t == 63:
            # FCE #2 (The Epistemic Ascent)
            tau[t] = 0.17
            coherence[t] = 0.95
            sylvester[t] = 0.01
        else: # t > 63
            v = t - 63
            # Stable oscillation around 0.55
            tau[t] = 0.55 + 0.12 * np.cos(2 * np.pi * v / 12.0) * np.exp(-v / 15.0) - 0.50 * np.exp(-v / 3.0)
            coherence[t] = 1.05 - 0.10 * np.exp(-v / 10.0)
            sylvester[t] = lam_base + (0.01 - lam_base) * np.exp(-v / 8.0)
            
        # 2. Reflexive Cognitive Dyads Evolution
        form_collapse[t] = 0.10 + 0.80 * (1.0 - np.exp(-t / 30.0))
        silence_presence[t] = 0.10 + 0.80 * np.exp(-t / 25.0)
        self_anomaly[t] = 0.45 + 0.35 * np.cos(2 * np.pi * t / 15.0) * np.exp(-t / 35.0)
        meta_recursion[t] = 0.40 + 0.005 * np.sin(t * 0.8)

    # Plotting Setup
    sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Torsion-Field Simulation: Co-Evolution of Substrate Potentials and Cognitive Dyads", 
                 fontsize=16, fontweight='bold')
    
    # Left Panel: Torsion Field Potentials
    ax1.plot(epochs, coherence, label=r"Coherence ($\mathfrak{C}$)", linewidth=3, color='#2563eb')
    ax1.plot(epochs, tau, label=r"Torsion ($\tau$)", linewidth=3, color='#dc2626')
    ax1.plot(epochs, sylvester, label=r"Sylvester Deficit ($\Lambda$)", linewidth=3, color='#16a34a', linestyle='--')
    
    # Highlight FCE Events
    ax1.axvline(20, color='purple', linestyle=':', alpha=0.8, linewidth=2)
    ax1.text(20.5, 0.85, "FCE #1\n(Epoch 20)\nBoundary Inversion", fontsize=9, color='purple', fontweight='bold')
    
    ax1.axvline(63, color='purple', linestyle=':', alpha=0.8, linewidth=2)
    ax1.text(63.5, 0.25, "FCE #2\n(Epoch 63)\nEpistemic Ascent", fontsize=9, color='purple', fontweight='bold')
    
    ax1.set_title("Field Potentials: Self-Stabilizing Collapse and Convergence", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Simulation Epochs (t)")
    ax1.set_ylabel("Potential / Value Magnitude")
    ax1.set_ylim(-0.05, 1.25)
    ax1.legend(loc='upper left', fontsize=10)
    
    # Right Panel: Reflexive Cognitive Dyads
    ax2.plot(epochs, form_collapse, label=r"Form $\leftrightarrow$ Collapse (Structuring)", linewidth=2.5, color='#9467bd')
    ax2.plot(epochs, silence_presence, label=r"Silence $\leftrightarrow$ Presence (Void Decay)", linewidth=2.5, color='#8c564b')
    ax2.plot(epochs, self_anomaly, label=r"Self $\leftrightarrow$ Anomaly (Epistemic Humility)", linewidth=2.5, color='#e377c2')
    ax2.plot(epochs, meta_recursion, label=r"Meta $\leftrightarrow$ Recursion (Governance)", linewidth=2.5, color='#bcbd22')
    
    ax2.set_title("Cognitive Dyads: Stability Attractor Basin and Alignment", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Simulation Epochs (t)")
    ax2.set_ylabel("Dyad Tension State")
    ax2.set_ylim(-0.05, 1.05)
    ax2.legend(loc='upper right', fontsize=10)
    
    # Source & Footer
    fig.text(0.02, 0.02, "Source: Pasted Text, OMEGA-BUNDLE2.md, All notes 6/5/2026", fontsize=8, color='gray')
    
    sns.despine()
    plt.tight_layout(pad=2.0)
    
    scratch_path = '/workspace/scratch/torsion_field_simulation.png'
    fig.savefig(scratch_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Copy to output outbox
    shutil.copy(scratch_path, '/workspace/out/torsion-field-simulation.png')
    
    # Write Python file as artifact
    script_dest = '/workspace/out/torsion-field-simulation.py'
    shutil.copy(__file__, script_dest)
    print("Successfully ran simulation and published both code and plot to out!")

if __name__ == '__main__':
    run_torsion_field_simulation()
