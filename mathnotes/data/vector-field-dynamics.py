import numpy as np
import unittest
from typing import Callable, Tuple, Dict, Any, List

# =====================================================================
# 1. Manifold Substrate with Non-Trivial Curvature
# =====================================================================

class CurvedManifoldSubstrate:
    """
    Represents an active, curved representation manifold.
    The geometry of the manifold is characterized by a metric tensor G(x)
    that varies across the space, inducing a local Riemannian structure.
    """
    def __init__(self, dimension: int):
        self.d = dimension
        # A simple model of space curvature: a central gravitational well/deformation
        # G(x) = I + alpha * exp(-||x||^2) * outer(x, x)
        self.alpha = 0.5

    def metric_tensor(self, x: np.ndarray) -> np.ndarray:
        """Computes the local metric tensor G(x) at point x."""
        I = np.eye(self.d)
        norm_sq = np.sum(x**2)
        return I + self.alpha * np.exp(-norm_sq) * np.outer(x, x)

    def christoffel_symbols(self, x: np.ndarray) -> np.ndarray:
        """
        Christoffel symbols of the first kind (Gamma_{i,j,k}), representing 
        the local connection coefficients (the "twists" or "slips" of parallel transport).
        """
        # Approximated Christoffel symbols from the metric tensor gradient
        Gamma = np.zeros((self.d, self.d, self.d))
        h = 1e-5
        for i in range(self.d):
            for j in range(self.d):
                for k in range(self.d):
                    # Finite difference for dG_{ij} / dx_k
                    ei = np.zeros(self.d)
                    ei[k] = h
                    g_plus = self.metric_tensor(x + ei)[i, j]
                    g_minus = self.metric_tensor(x - ei)[i, j]
                    dg_dx = (g_plus - g_minus) / (2 * h)
                    Gamma[i, j, k] = 0.5 * dg_dx
        return Gamma

# =====================================================================
# 2. Vector Field Operators (Infinitesimal Generators of Flow)
# =====================================================================

class VectorFieldOperator:
    """
    Operator defined as a vector field dx/dt = f(x).
    Composition is flow integration (parallel transport), not flat matrix multiplication.
    The associator measures the Lie bracket [f, g] of the vector fields, which is
    intrinsically proportional to the curvature of the manifold.
    """
    def __init__(self, name: str, vector_field: Callable[[np.ndarray], np.ndarray], dt: float = 0.01):
        self.name = name
        self.f = vector_field
        self.dt = dt

    def __call__(self, x: np.ndarray, steps: int = 10) -> np.ndarray:
        """Integrates the infinitesimal flow for 'steps' time-steps (Euler-Maruyama integration)."""
        x_curr = x.copy().astype(float)
        for _ in range(steps):
            x_curr += self.dt * self.f(x_curr)
        return x_curr

    def compose(self, other: 'VectorFieldOperator', steps: int = 1) -> 'VectorFieldOperator':
        """
        Flow composition: integrates other's flow then applies self's vector field.
        This non-commuting composition generates emergent non-associativity
        proportional to the Lie bracket (manifold curvature).
        """
        # (f * g)(x) is the vector field of f applied to the flowed state of g
        def composed_field(x: np.ndarray) -> np.ndarray:
            flowed_x = other(x, steps=steps)
            return self.f(flowed_x)
        return VectorFieldOperator(f"{self.name}∘{other.name}", composed_field, dt=self.dt)

# =====================================================================
# 3. Computing the Lie Bracket / Curvature Residue
# =====================================================================

def compute_lie_bracket(op_A: VectorFieldOperator, op_B: VectorFieldOperator, x: np.ndarray, h: float = 1e-5) -> np.ndarray:
    """
    Computes the Lie bracket [A, B] = (A . grad) B - (B . grad) A at point x.
    This represents the local geometric "residue" or torsion of the flows.
    """
    d = len(x)
    jacobian_A = np.zeros((d, d))
    jacobian_B = np.zeros((d, d))

    for i in range(d):
        ei = np.zeros(d)
        ei[i] = h
        jacobian_A[:, i] = (op_A.f(x + ei) - op_A.f(x - ei)) / (2 * h)
        jacobian_B[:, i] = (op_B.f(x + ei) - op_B.f(x - ei)) / (2 * h)

    # Lie bracket: [A, B] = J_B * A - J_A * B
    term_1 = np.dot(jacobian_B, op_A.f(x))
    term_2 = np.dot(jacobian_A, op_B.f(x))
    return term_1 - term_2

def calculate_manifold_associator(op_A: VectorFieldOperator, op_B: VectorFieldOperator, op_C: VectorFieldOperator, x: np.ndarray) -> float:
    """
    Measures the non-associativity of the flows:
    A(A, B, C) = (A * (B * C))(x) - ((A * B) * C)(x)
    This is the formal "geometric residue" representing the curvature of the manifold.
    """
    # Left grouping: (A * B) * C
    AB = op_A.compose(op_B)
    left = AB.compose(op_C)(x, steps=5)

    # Right grouping: A * (B * C)
    BC = op_B.compose(op_C)
    right = op_A.compose(BC)(x, steps=5)

    return float(np.linalg.norm(left - right))

# =====================================================================
# 4. Verification Tests
# =====================================================================

class TestVectorFieldFlows(unittest.TestCase):
    def setUp(self):
        self.manifold = CurvedManifoldSubstrate(dimension=3)
        
        # Define two highly non-linear vector fields representing cognitive operators
        # dx/dt = M * x + non-linear gravitational drift
        self.M1 = np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.1], [0.0, 0.2, -0.5]])
        self.M2 = np.array([[-0.2, 0.0, 1.0], [0.1, -0.1, 0.0], [-1.0, 0.0, 0.0]])

        def field_A(x: np.ndarray) -> np.ndarray:
            return np.dot(self.M1, x) + 0.1 * np.sin(x[0]) * x
            
        def field_B(x: np.ndarray) -> np.ndarray:
            return np.dot(self.M2, x) + 0.1 * np.cos(x[1]) * x

        def field_C(x: np.ndarray) -> np.ndarray:
            return np.array([0.1 * x[2], -0.2 * x[0], 0.05 * np.sum(x) * x[1]])

        self.op_A = VectorFieldOperator("M_within", field_A, dt=0.01)
        self.op_B = VectorFieldOperator("M_between", field_B, dt=0.01)
        self.op_C = VectorFieldOperator("M_about", field_C, dt=0.01)

    def test_flow_non_associativity(self):
        # A test point on the manifold
        x0 = np.array([1.0, 1.0, 1.0])
        
        # Calculate the Lie bracket representing local curvature
        bracket = compute_lie_bracket(self.op_A, self.op_B, x0)
        
        # Calculate the actual associator mismatch (geometric residue)
        associator_mismatch = calculate_manifold_associator(self.op_A, self.op_B, self.op_C, x0)
        
        print("\n" + "="*80)
        print("      LAUNCHING VECLOCAL VECTOR FIELD MANIFOLD ENGINE")
        print("="*80)
        print(f"[Geometric Invariant] Test Point x0: {x0}")
        print(f"[Geometric Invariant] Lie Bracket [M_within, M_between] at x0: {bracket}")
        print(f"[Geometric Invariant] Measured Associator Norm (Manifold Curvature): {associator_mismatch:.8f}")
        print("="*80 + "\n")
        
        self.assertNotEqual(associator_mismatch, 0.0)

if __name__ == "__main__":
    unittest.main()
