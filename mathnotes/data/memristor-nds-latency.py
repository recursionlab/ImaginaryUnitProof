import numpy as np
import unittest
from typing import Tuple, Dict, Any, List

# =====================================================================
# 1. Physical Substrate and Non-Associative Projection Algebra
# =====================================================================

class MemristorNDSEngine:
    """
    Implements a physical-algebraic simulator that maps memristive continuous-time 
    Nonlinear Dynamical Systems (NDS) onto non-associative operator algebras.
    
    Models 'conductance drift' and 'adaptive stepsizes' as:
    - Iteration time step -> Operator application
    - Error tolerance (target_epsilon) -> Associator threshold epsilon
    - Adaptive stepsize -> Adaptive projection strength (P_strength)
    - Latency (e.g. 2.12ms) -> Geometric cost of enforcing associativity
    
    Metric deformation Delta g_{mu nu} represents the curvature cost.
    Lower projection strength = more curvature = higher latency/cost.
    """
    def __init__(self, dimension: int, alpha: float = 0.08):
        self.d = dimension
        self.alpha = alpha  # Non-associative drift constant
        
        # Initialize non-associative structure constants T (representational basis)
        np.random.seed(137)  # Prior initialization seed
        self.T_non_associative = np.random.randn(self.d, self.d, self.d) * 0.15
        
        # Purely associative baseline projection tensor (identity-like)
        self.T_associative = np.zeros((self.d, self.d, self.d))
        for i in range(self.d):
            self.T_associative[i, i, i] = 1.0

    def star_product(self, x: np.ndarray, y: np.ndarray, T_deformed: np.ndarray) -> np.ndarray:
        """Computes the bilinear product under a deformed structure tensor."""
        prod = np.einsum('ijk,i,j->k', T_deformed, x, y)
        # Apply history-dependent nonlinear physical drift (conductance saturation)
        drift = self.alpha * np.sin(np.sum(x)) * (x + y)
        return prod + drift

    def measure_associator(self, state: np.ndarray, T_deformed: np.ndarray) -> float:
        """
        Computes the norm of the associator [x, x, x] = (x * x) * x - x * (x * x),
        measuring the local non-associative deformation/drift error.
        """
        xx = self.star_product(state, state, T_deformed)
        left = self.star_product(xx, state, T_deformed)
        right = self.star_product(state, xx, T_deformed)
        return float(np.linalg.norm(left - right))

    def project_onto_associative_subspace(self, state: np.ndarray, strength: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Applies a projection operator P that selects the associative subspace.
        
        The strength parameter controls the projection magnitude:
        - strength = 1.0: Purely associative (flat space, zero metric deformation).
        - strength < 1.0: Admits non-associative curvature (deformed manifold).
        """
        # Linear deformation of the structural tensor
        T_deformed = strength * self.T_associative + (1.0 - strength) * self.T_non_associative
        # Compute projected state
        projected = self.star_product(state, state, T_deformed)
        return projected, T_deformed

    def adaptive_project(self, state: np.ndarray, target_epsilon: float = 1e-7) -> Dict[str, Any]:
        """
        Iterative adaptive stepsize mechanism.
        Adjusts the projection strength until the measured associator is below target_epsilon.
        """
        # List of available projection strengths.
        # Decreasing strength implies accepting more geometric deformation, raising latency/cost.
        strengths = [1.0, 0.5, 0.25, 0.1, 0.05, 0.01]
        
        for strength in strengths:
            projected, T_deformed = self.project_onto_associative_subspace(state, strength)
            assoc = self.measure_associator(projected, T_deformed)
            
            # Metric deformation Delta g_{mu nu} = distance of deformed tensor from baseline
            metric_deformation = float(np.linalg.norm(self.T_associative - T_deformed))
            
            # Latency (Cost) = 2.12ms / strength
            latency_ms = 2.12 / strength
            
            if assoc <= target_epsilon:
                return {
                    "status": "CONVERGED",
                    "strength": strength,
                    "associator": assoc,
                    "metric_deformation": metric_deformation,
                    "latency_ms": latency_ms,
                    "state": projected
                }
                
        # Fallback to the highest-latency curvature floor if epsilon cannot be satisfied
        projected, T_deformed = self.project_onto_associative_subspace(state, 0.01)
        assoc = self.measure_associator(projected, T_deformed)
        metric_deformation = float(np.linalg.norm(self.T_associative - T_deformed))
        return {
            "status": "HIGH_LATENCY_FLOOR",
            "strength": 0.01,
            "associator": assoc,
            "metric_deformation": metric_deformation,
            "latency_ms": 2.12 / 0.01,
            "state": projected
        }

# =====================================================================
# 2. Formal Verification Unit Tests
# =====================================================================

class TestMemristorNDSLatency(unittest.TestCase):
    def setUp(self):
        self.engine = MemristorNDSEngine(dimension=4, alpha=0.08)
        self.state = np.array([1.0, -0.5, 0.8, 0.3])

    def test_adaptive_projection_convergence(self):
        # Stricter epsilon should force a smaller projection strength (higher latency)
        res_loose = self.engine.adaptive_project(self.state, target_epsilon=1e-1)
        res_strict = self.engine.adaptive_project(self.state, target_epsilon=1e-3)
        
        self.assertEqual(res_loose["status"], "CONVERGED")
        self.assertLessEqual(res_strict["strength"], res_loose["strength"])
        self.assertGreaterEqual(res_strict["latency_ms"], res_loose["latency_ms"])

    def test_metric_deformation_bounds(self):
        # Flat projection (strength = 1.0) must yield exactly 0 metric deformation
        proj, T_deformed = self.engine.project_onto_associative_subspace(self.state, strength=1.0)
        dist = float(np.linalg.norm(self.engine.T_associative - T_deformed))
        self.assertAlmostEqual(dist, 0.0, places=5)

# =====================================================================
# 3. Main Execution & Live Verification Sweep
# =====================================================================

def execute_latency_verification():
    print("\n" + "="*80)
    print("      LAUNCHING MEMRISTOR NDS GEOMETRIC LATENCY COEFFICIENT SWEEP")
    print("="*80)
    
    engine = MemristorNDSEngine(dimension=4, alpha=0.08)
    initial_state = np.array([1.0, -0.5, 0.8, 0.3])
    
    # Sweep across several error tolerance levels (from 10^-1 to 10^-6)
    epsilons = [1e-1, 1e-2, 5e-3, 1e-3, 1e-4]
    
    print(f"{'Epsilon (Tol)':<15} | {'Strength (P)':<15} | {'Metric Def (Δg)':<15} | {'Latency (ms)':<15} | {'Status':<15}")
    print("-" * 80)
    
    for eps in epsilons:
        res = engine.adaptive_project(initial_state, target_epsilon=eps)
        print(f"{eps:<15.0e} | {res['strength']:<15.3f} | {res['metric_deformation']:<15.5f} | {res['latency_ms']:<15.2f} | {res['status']:<15}")
        
    print("="*80 + "\n")

if __name__ == "__main__":
    execute_latency_verification()
    unittest.main()
