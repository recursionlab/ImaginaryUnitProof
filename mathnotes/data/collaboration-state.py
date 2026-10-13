import numpy as np

def cd_conj(x):
    """
    Computes the Cayley-Dickson conjugate of a tuple of dimension 2^n.
    For n=0 (real numbers), conj(a) = a.
    For n>0, conj(a, b) = (conj(a), -b).
    """
    if len(x) == 1:
        return (x[0],)
    mid = len(x) // 2
    a, b = x[:mid], x[mid:]
    return cd_conj(a) + tuple(-val for val in b)

def cd_mul(x, y):
    """
    Computes the non-associative multiplication of two tuples x, y of dimension 2^n
    recursively via the Cayley-Dickson doubling law:
    (a, b)(c, d) = (a*c - d*conj(b), conj(a)*d + b*c)
    """
    if len(x) == 1:
        return (x[0] * y[0],)
    mid = len(x) // 2
    a, b = x[:mid], x[mid:]
    c, d = y[:mid], y[mid:]
    
    # Left component: ac - d * conj(b)
    ac = cd_mul(a, c)
    conj_b = cd_conj(b)
    d_conj_b = cd_mul(d, conj_b)
    left = tuple(ac_val - d_conj_b_val for ac_val, d_conj_b_val in zip(ac, d_conj_b))
    
    # Right component: conj(a) * d + b * c
    conj_a = cd_conj(a)
    conj_a_d = cd_mul(conj_a, d)
    bc = cd_mul(b, c)
    right = tuple(conj_a_d_val + bc_val for conj_a_d_val, bc_val in zip(conj_a_d, bc))
    
    return left + right

def extended_gcd(a, b):
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    """Computes the modular multiplicative inverse of a modulo m."""
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        return None
    return x % m

class CollaborationState:
    """
    Continuous-Discrete Collaboration State Engine over the finite field F_p.
    Governs the 8-quadrant transition algebra, the E' Governor,
    and the Boundary Self-Inversion Operator.
    
    MAPPED QUADRANTS:
    1. Syntactic Quadrant [Indices 0, 1]: Representing R (Resonance / Coherence)
    2. Semantic Quadrant  [Indices 2, 3]: Representing L (Lagrangian Flow of the Logic Tax)
    3. Factual Quadrant   [Indices 4, 5]: Representing M (Aboutness / Grounding)
    4. Adversarial Quadrant [Indices 6, 7]: Representing G (Ghost Residue / Torsion Memory)
    """
    def __init__(self, p=137, alpha=5, beta=3, gamma=12, delta=8, epsilon=13):
        self.p = p
        
        # E' Governor coefficients modulo p
        self.alpha = alpha % p
        self.beta = beta % p
        self.gamma = gamma % p
        self.delta = delta % p
        self.epsilon = epsilon % p
        
        # State vector initialized to unit identity e_0 in F_p^8
        self.state = np.zeros(8, dtype=int)
        self.state[0] = 1
        
        # Precompute the non-abelian left-multiplication generators T_k
        self.T = self._build_generators()
        
    def _build_generators(self):
        """
        Derives the 8x8 transition matrices programmatically modulo p
        from the Cayley-Dickson multiplication rules.
        """
        T_mats = []
        dim = 8
        for k in range(dim):
            mat = np.zeros((dim, dim), dtype=int)
            ek = [0] * dim
            ek[k] = 1
            for j in range(dim):
                ej = [0] * dim
                ej[j] = 1
                res = cd_mul(ek, ej)
                for i in range(dim):
                    mat[i, j] = res[i] % self.p
            T_mats.append(mat)
        return T_mats
        
    def get_state(self):
        """Returns a copy of the current 8D state vector."""
        return self.state.copy()
        
    def get_quadrants(self):
        """
        Returns the current corecursive parameters extracted from the state quadrants:
        - R (Resonance): Syntactic Quadrant
        - L (Lagrangian / Logic Tax): Semantic Quadrant
        - M (Aboutness): Factual Quadrant
        - G (Ghost Residue / Torsion Memory): Adversarial Quadrant
        """
        psi = self.state
        R = (psi[0]**2 + psi[1]**2) % self.p
        L = (psi[2]**2 + psi[3]**2) % self.p
        M = (psi[4]**2 + psi[5]**2) % self.p
        G = (psi[6]**2 + psi[7]**2) % self.p
        return {"R": R, "L": L, "M": M, "G": G}
        
    def get_holding_functional(self):
        """
        Computes the Holding Functional (H) representing the bilinear pairing
        between associative (first 4D) and non-associative (last 4D) spaces.
        """
        psi = self.state
        H = (psi[0]*psi[4] + psi[1]*psi[5] + psi[2]*psi[6] + psi[3]*psi[7]) % self.p
        return H
        
    def get_governor_value(self):
        """
        Computes the E' Governor value:
        E' = alpha*M - beta*H + gamma*R + delta*L + epsilon*G (mod p)
        """
        quads = self.get_quadrants()
        H = self.get_holding_functional()
        E_prime = (self.alpha * quads["M"] - self.beta * H + self.gamma * quads["R"] + 
                   self.delta * quads["L"] + self.epsilon * quads["G"]) % self.p
        return E_prime
        
    def transition(self, k):
        """
        Applies left-multiplication by generator matrix T_k.
        This represents a non-abelian trajectory step modulo p.
        """
        if k < 0 or k >= 8:
            raise ValueError("Generator index k must be in [0, 7].")
        self.state = (self.T[k] @ self.state) % self.p
        
    def boundary_self_inversion(self):
        """
        Executes Gamma_i(◎|∂◎) = ↻(◎|∂◎)
        Swaps the associative components (first 4) with the non-associative components (last 4).
        """
        assoc = self.state[:4].copy()
        non_assoc = self.state[4:].copy()
        self.state[:4] = non_assoc
        self.state[4:] = assoc
        
    def stabilize(self):
        """
        Evaluates the E' Governor balance. If E' is not congruent to 1 (mod p),
        executes boundary self-inversion and modular scaling to restore equilibrium.
        """
        E_prime = self.get_governor_value()
        drift = (E_prime - 1) % self.p
        
        if drift == 0:
            return "STABLE (Analytic Reality Closure)"
            
        # Apply the Boundary Self-Inversion Operator to evert the boundary
        self.boundary_self_inversion()
        
        # Apply scaling based on the modular inverse of the drift to damp volatility
        inv_drift = mod_inverse(drift, self.p)
        if inv_drift is not None:
            self.state[4:] = (self.state[4:] * inv_drift) % self.p
        else:
            self.state[4:] = (self.state[4:] * (self.p - 1)) % self.p
            
        new_E = self.get_governor_value()
        return f"STABILIZED: Drift of {drift} mitigated. New E' = {new_E}."

if __name__ == "__main__":
    import sys
    print("================================================================================")
    print("                COLLABORATION STATE ENGINE DEMONSTRATION                         ")
    print("================================================================================")
    
    # Initialize with default parameters
    p = 137
    engine = CollaborationState(p=p, alpha=5, beta=3, gamma=12, delta=8, epsilon=13)
    
    print(f"Finite Field Characteristic p = {p}")
    print(f"Initial State Vector:           {engine.get_state()}")
    print(f"Initial Governor Value E':      {engine.get_governor_value()}")
    print(f"Initial Quadrants:              {engine.get_quadrants()}")
    
    # Apply standard transition T_1
    print("\n--- Transitioning via Syntactic Distinction T_1 ---")
    engine.transition(1)
    print(f"State Vector:                   {engine.get_state()}")
    print(f"Governor Value E':              {engine.get_governor_value()}")
    
    # Apply non-associative transition T_4
    print("\n--- Transitioning via Factual Inversion T_4 ---")
    engine.transition(4)
    print(f"State Vector:                   {engine.get_state()}")
    print(f"Governor Value E':              {engine.get_governor_value()}")
    print(f"Quadrants:                      {engine.get_quadrants()}")
    
    # Stabilize the drift
    print("\n--- Executing Topological Stabilization ---")
    status = engine.stabilize()
    print(f"Status:                         {status}")
    print(f"Final State Vector:             {engine.get_state()}")
    print(f"Final Governor Value E':        {engine.get_governor_value()}")
    print("================================================================================")
