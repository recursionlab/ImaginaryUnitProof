import numpy as np
import unittest

class MemristorNonAssociativeSpace:
    """
    Simulates a physical memristor array as a non-associative algebraic space.
    Conductance state (C) is a vector in R^d that carries the history of applied pulses.
    Applying a pulse is represented by a non-associative multiplication operator (*).
    """
    def __init__(self, dimension: int, alpha: float = 0.01):
        self.d = dimension
        self.alpha = alpha  # Crystallization rate parameter (conductance drift factor)
        
        # Initialize bilinear structure constants T for the non-associative product
        # T is a d x d x d tensor representing the multiplication table:
        # (x * y)_k = sum_{i,j} T_{i,j,k} * x_i * y_j
        np.random.seed(42)  # For deterministic physical properties
        self.T = np.random.randn(self.d, self.d, self.d) * 0.1
        # Add an identity-like component to stabilize transport
        for i in range(self.d):
            self.T[i, i, i] += 1.0

    def star_product(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Computes the non-associative product x * y using the structure tensor T.
        Also incorporates a history-dependent state drift mimicking phase-change material crystallization.
        """
        # Linear product from structure tensor
        prod = np.einsum('ijk,i,j->k', self.T, x, y)
        
        # Non-linear history-dependent drift correction (conductance saturation)
        state_drift = self.alpha * np.sin(np.dot(x, y)) * (x + y)
        return prod + state_drift

    def compute_associator(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        """
        Computes the associator: [x, y, z] = (x * y) * z - x * (y * z)
        This is the mathematical representation of the physical drift error.
        """
        xy = self.star_product(x, y)
        left = self.star_product(xy, z)
        
        yz = self.star_product(y, z)
        right = self.star_product(x, yz)
        
        return left - right

    def associator_norm(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
        """Returns the L2 norm of the associator, quantifying the non-associativity of the sequence."""
        return float(np.linalg.norm(self.compute_associator(x, y, z)))

# Unit tests to verify the non-associative physical simulation
class TestMemristorAlgebra(unittest.TestCase):
    def setUp(self):
        self.space = MemristorNonAssociativeSpace(dimension=4, alpha=0.05)
        
    def test_non_associativity(self):
        # Apply three distinct physical pulses
        A = np.array([1.0, 0.0, 0.5, -0.2])
        B = np.array([0.1, 0.9, -0.3, 0.4])
        C = np.array([-0.5, 0.2, 0.8, 0.1])
        
        # Verify (A * B) * C != A * (B * C)
        left = self.space.star_product(self.space.star_product(A, B), C)
        right = self.space.star_product(A, self.space.star_product(B, C))
        
        # Calculate the associator drift error
        drift_error = self.space.associator_norm(A, B, C)
        
        print(f"\n[Verification] Applied Pulses: A, B, C")
        print(f"  (A * B) * C: {left}")
        print(f"  A * (B * C): {right}")
        print(f"  Associator Norm (Drift Error τ_A): {drift_error:.6f}")
        
        self.assertNotAlmostEqual(drift_error, 0.0, places=5)

if __name__ == "__main__":
    unittest.main()
