import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil

def run_cohomology_simulation():
    os.makedirs('/workspace/scratch', exist_ok=True)
    os.makedirs('/workspace/out', exist_ok=True)
    
    vertices = ['a', 'b', 'c', 'd', 'e', 'f']
    edges = [
        ('a', 'b'), ('a', 'c'), ('a', 'd'),
        ('b', 'c'), ('b', 'd'), ('c', 'd'),
        ('c', 'e'), ('d', 'e'), ('e', 'f')
    ]
    simplices2 = [('c', 'd', 'e')]
    
    d = 2
    dim_C0 = len(vertices) * d    # 6 * 2 = 12
    dim_C1 = len(edges) * d       # 9 * 2 = 18
    dim_C2 = len(simplices2) * d  # 1 * 2 = 2
    
    noise_levels = np.linspace(0.0, 1.0, 100)
    
    # Lists for Flat/Gauge-Invariant Sheaf Cohomology
    flat_h0 = []
    flat_h1 = []
    flat_h2 = []
    
    # Lists for Obstructed/Curved Sheaf Cohomology (1D Graph Cohomology to keep d1*d0=0 vacuously satisfied)
    obstructed_h0 = []
    obstructed_h1 = []
    
    np.random.seed(42)
    
    def get_map(scale):
        if scale == 0:
            return np.eye(d)
        # Perturb identity matrix
        matrix = np.eye(d) + scale * np.random.randn(d, d)
        u, s, vh = np.linalg.svd(matrix)
        return u @ vh # Orthonormal projection
        
    def get_rank_and_nullity(matrix):
        if matrix.size == 0:
            return 0, 0
        s = np.linalg.svd(matrix, compute_uv=False)
        tol = max(matrix.shape) * np.spacing(np.float64(1.0)) * s[0] if len(s) > 0 else 0
        rank = np.sum(s > tol)
        nullity = matrix.shape[1] - rank
        return rank, nullity

    v_to_col = {v: i * d for i, v in enumerate(vertices)}
    
    for sigma in noise_levels:
        # -------------------------------------------------------------
        # 1. FLAT CONNECTION SHEAF (Symmetry Preserved)
        # -------------------------------------------------------------
        R_vertices = {v: get_map(sigma) for v in vertices}
        R_edges = {e: get_map(sigma) for e in edges}
        R_s = get_map(sigma)
        
        d0_flat = np.zeros((dim_C1, dim_C0))
        for e_idx, (u, v) in enumerate(edges):
            map_u = R_edges[(u, v)] @ R_vertices[u]
            map_v = R_edges[(u, v)] @ R_vertices[v]
            
            row_start = e_idx * d
            col_u_start = v_to_col[u]
            col_v_start = v_to_col[v]
            
            d0_flat[row_start : row_start + d, col_u_start : col_u_start + d] = -map_u
            d0_flat[row_start : row_start + d, col_v_start : col_v_start + d] = map_v
            
        d1_flat = np.zeros((dim_C2, dim_C1))
        idx_cd = edges.index(('c', 'd'))
        idx_ce = edges.index(('c', 'e'))
        idx_de = edges.index(('d', 'e'))
        
        map_cd = R_s @ np.linalg.inv(R_edges[('c', 'd')])
        map_ce = R_s @ np.linalg.inv(R_edges[('c', 'e')])
        map_de = R_s @ np.linalg.inv(R_edges[('d', 'e')])
        
        d1_flat[0 : d, idx_cd * d : (idx_cd + 1) * d] = map_cd
        d1_flat[0 : d, idx_ce * d : (idx_ce + 1) * d] = -map_ce
        d1_flat[0 : d, idx_de * d : (idx_de + 1) * d] = map_de
        
        rank_d0_f, nullity_d0_f = get_rank_and_nullity(d0_flat)
        rank_d1_f, nullity_d1_f = get_rank_and_nullity(d1_flat)
        
        flat_h0.append(nullity_d0_f)
        flat_h1.append(nullity_d1_f - rank_d0_f)
        flat_h2.append(dim_C2 - rank_d1_f)
        
        # -------------------------------------------------------------
        # 2. OBSTRUCTED CONNECTION SHEAF (1D Graph Cohomology, Symmetries Broken)
        # -------------------------------------------------------------
        # Here, restriction maps are chosen independently with noise, breaking flatness.
        d0_obs = np.zeros((dim_C1, dim_C0))
        for e_idx, (u, v) in enumerate(edges):
            # Non-coherent independent noise
            map_u = get_map(sigma)
            map_v = get_map(sigma)
            
            row_start = e_idx * d
            col_u_start = v_to_col[u]
            col_v_start = v_to_col[v]
            
            d0_obs[row_start : row_start + d, col_u_start : col_u_start + d] = -map_u
            d0_obs[row_start : row_start + d, col_v_start : col_v_start + d] = map_v
            
        rank_d0_o, nullity_d0_o = get_rank_and_nullity(d0_obs)
        obstructed_h0.append(nullity_d0_o)
        # Since there are no 2-simplices in the pure 1D graph, H1 is just C1 / im(d0)
        obstructed_h1.append(dim_C1 - rank_d0_o)

    # Validate output console log
    print("=== SHEAF COHOMOLOGY RIGOROUS COMPLIANCE VERIFICATION ===")
    print("1. GAUGE-INVARIANT FLAT SHEAF:")
    print(f"   At sigma=0.0: dim(H0) = {flat_h0[0]}, dim(H1) = {flat_h1[0]}, dim(H2) = {flat_h2[0]}")
    print(f"   At sigma=1.0: dim(H0) = {flat_h0[-1]}, dim(H1) = {flat_h1[-1]}, dim(H2) = {flat_h2[-1]}")
    print("   -> Symmetries hold perfectly under local gauge rotations!")
    print("2. OBSTRUCTED CURVED SHEAF (1D Graph):")
    print(f"   At sigma=0.0: dim(H0) = {obstructed_h0[0]}, dim(H1) = {obstructed_h1[0]} (Euler Char = {obstructed_h0[0] - obstructed_h1[0]})")
    print(f"   At sigma=1.0: dim(H0) = {obstructed_h0[-1]}, dim(H1) = {obstructed_h1[-1]} (Euler Char = {obstructed_h0[-1] - obstructed_h1[-1]})")
    print("   -> Symmetries break completely, collapsing global sections while preserving topological Euler Characteristic!")
    print("=========================================================")

    # Plotting
    sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Sheaf Cohomology Under Semantic Drift: Gauge-Invariant Stability vs. Symmetry Breaking", fontsize=16, fontweight='bold')
    
    # Left Panel: Flat Connection (Symmetry Preserved)
    ax1.plot(noise_levels, flat_h0, label=r"$\dim(H^0(X; F))$: Global Sections", linewidth=3, color='#2563eb')
    ax1.plot(noise_levels, flat_h1, label=r"$\dim(H^1(X; F))$: Gluing Obstructions", linewidth=3, color='#dc2626')
    ax1.plot(noise_levels, flat_h2, label=r"$\dim(H^2(X; F))$: 2D Cohomology", linewidth=3, color='#16a34a', linestyle='--')
    ax1.set_title("Flat Gauge Connection: Topologically Protected Invariance", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Local Gauge Rotation Angle / Intensity (σ)")
    ax1.set_ylabel("Cohomology Group Dimension")
    ax1.set_ylim(-0.5, 8.5)
    ax1.legend(loc='upper right', fontsize=9)
    
    # Right Panel: Obstructed Connection (Symmetry Broken)
    ax2.plot(noise_levels, obstructed_h0, label=r"$\dim(H^0(X; F))$: Global Sections (Lucidity)", linewidth=3, color='#2563eb')
    ax2.plot(noise_levels, obstructed_h1, label=r"$\dim(H^1(X; F))$: Obstruction Class (Torsion)", linewidth=3, color='#dc2626')
    ax2.set_title("Curved / Non-Flat Connection: Semantic Drift & Symmetries Collapse", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Independent Noise / Obstruction Intensity (σ)")
    ax2.set_ylabel("Cohomology Group Dimension")
    ax2.set_ylim(-0.5, 9.5)
    ax2.legend(loc='upper right', fontsize=9)
    
    # Annotate Euler Characteristic Conservation on right panel
    text_info = (
        r"$\chi(X; F) = \dim(H^0) - \dim(H^1)$" + "\n"
        r"$\chi(0.0) = 2 - 8 = -6$" + "\n"
        r"$\chi(1.0) = 0 - 6 = -6$" + "\n\n"
        "Euler Characteristic is\n"
        "strictly conserved as a\n"
        "topological invariant!"
    )
    ax2.text(0.4, 1.5, text_info, bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.5'), fontsize=10, family='monospace')
    
    fig.text(0.02, 0.02, "Source: Sheaf Theory Through Examples Abridged.pdf, Section 4.2.2 & 4.2.3", fontsize=8, color='gray')
    
    sns.despine()
    plt.tight_layout(pad=2.0)
    
    plot_path = '/workspace/scratch/sheaf_cohomology_decay.png'
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Copy final artifact to out
    shutil.copy(plot_path, '/workspace/out/sheaf-cohomology-decay.png')
    print("Saved sheaf-cohomology-decay.png to out")

if __name__ == '__main__':
    run_cohomology_simulation()
