import numpy as np
import uuid
import copy
import unittest
from typing import Callable, Any, Dict, List, Set, Tuple

# =====================================================================
# 1. Core Data Models for the Morphogenetic Cognitive Manifold
# =====================================================================

class NodeType:
    CONCEPT = "concept"
    RELATION = "relation"
    OPERATOR = "operator"
    INDEX = "index"

class EdgeType:
    COVALENT = "covalent"          # Deep Reasoning (strong causal/logical bond)
    HYDROGEN = "hydrogen"          # Self-Reflection (folding/validation link)
    VAN_DER_WAALS = "van_der_waals" # Self-Exploration (loose associative search)
    META = "meta"                  # Higher-order indexing/representational link
    TORSION = "torsion"            # Paradox/contradiction boundary marker

class Node:
    """
    Represents an individual cognitive node (concept, operator, index, etc.).
    Preserves direct ancestral provenance of its creation.
    """
    def __init__(self, node_id: str, label: str, node_type: str, provenance: List[str] = None, metadata: dict = None):
        self.id = node_id if node_id else f"node-{uuid.uuid4()}"
        self.label = label
        self.type = node_type
        self.provenance = provenance if provenance else []  # Ancestor node IDs
        self.metadata = metadata if metadata else {}

    def __repr__(self) -> str:
        return f"Node({self.id}, label='{self.label}', type='{self.type}')"

class Edge:
    """
    An Edge-First representation where each edge is a first-class citizen 
    carrying type, binding/indexing conditions, and a transformation function rho(e).
    """
    def __init__(self, edge_id: str, source: str, target: str, edge_type: str, 
                 binding_condition: Callable[[Any, Any], bool] = None,
                 transformation_func: Callable[[Any], Any] = None,
                 provenance: List[str] = None, metadata: dict = None):
        self.id = edge_id if edge_id else f"edge-{uuid.uuid4()}"
        self.source = source
        self.target = target
        self.type = edge_type
        self.binding_condition = binding_condition if binding_condition else (lambda s, t: True)
        self.transformation_func = transformation_func if transformation_func else (lambda g: g)
        self.provenance = provenance if provenance else []  # Ancestor edge IDs
        self.metadata = metadata if metadata else {}

    def __repr__(self) -> str:
        return f"Edge({self.id}, src='{self.source}', tgt='{self.target}', type='{self.type}')"

class TypedEdgeGraph:
    """
    G = (V, E, tau, beta, rho) represents the morphogenetic cognitive manifold.
    Enforces the Triple-Recursion Stack: Object (X), Context (C), and Operator (R),
    with an active and immutable history trace (H).
    """
    def __init__(self, context: str = "C_0"):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.context = context  # Context Index (C_n)
        self.history: List[dict] = []  # History trace (H_n)
        self.step_counter = 0

    def add_node(self, label: str, node_type: str, node_id: str = None, provenance: List[str] = None, metadata: dict = None) -> Node:
        node = Node(node_id, label, node_type, provenance, metadata)
        self.nodes[node.id] = node
        return node

    def add_edge(self, source: str, target: str, edge_type: str, edge_id: str = None,
                 binding_condition: Callable[[Any, Any], bool] = None,
                 transformation_func: Callable[[Any], Any] = None,
                 provenance: List[str] = None, metadata: dict = None) -> Edge:
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Cannot add edge between non-existent nodes: {source} -> {target}")
        edge = Edge(edge_id, source, target, edge_type, binding_condition, transformation_func, provenance, metadata)
        self.edges[edge.id] = edge
        return edge

    def remove_node(self, node_id: str):
        if node_id in self.nodes:
            del self.nodes[node_id]
            edges_to_remove = [eid for eid, e in self.edges.items() if e.source == node_id or e.target == node_id]
            for eid in edges_to_remove:
                del self.edges[eid]

    def get_adjacency_matrix(self) -> Tuple[np.ndarray, List[str]]:
        node_ids = sorted(list(self.nodes.keys()))
        n = len(node_ids)
        id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
        A = np.zeros((n, n))
        for e in self.edges.values():
            if e.source in id_to_idx and e.target in id_to_idx:
                u, v = id_to_idx[e.source], id_to_idx[e.target]
                A[u, v] = 1.0
                A[v, u] = 1.0  # Treat as undirected for standard Laplacian analysis
        return A, node_ids

    def get_normalized_laplacian(self) -> np.ndarray:
        A, _ = self.get_adjacency_matrix()
        n = A.shape[0]
        if n == 0:
            return np.zeros((0, 0))
        d = np.sum(A, axis=1)
        D_inv_sqrt = np.zeros((n, n))
        for i in range(n):
            if d[i] > 0:
                D_inv_sqrt[i, i] = 1.0 / np.sqrt(d[i])
        I = np.eye(n)
        L = I - D_inv_sqrt @ A @ D_inv_sqrt
        return L

    def clone(self) -> 'TypedEdgeGraph':
        new_g = TypedEdgeGraph(context=self.context)
        new_g.nodes = {nid: Node(n.id, n.label, n.type, list(n.provenance), dict(n.metadata)) for nid, n in self.nodes.items()}
        new_g.edges = {eid: Edge(e.id, e.source, e.target, e.type, e.binding_condition, e.transformation_func, list(e.provenance), dict(e.metadata)) for eid, e in self.edges.items()}
        new_g.history = copy.deepcopy(self.history)
        new_g.step_counter = self.step_counter
        return new_g

# =====================================================================
# 2. Λ_w World-State Target Representation Structure
# =====================================================================

class LambdaW:
    """
    LambdaW (Λ_w) represents the target world-state model (the "ore deposit")
    against which representational gaps are identified and measured.
    """
    def __init__(self, target_structures: Dict[str, Dict[str, Any]] = None):
        self.w = target_structures if target_structures else {}

    def add_target_concept(self, label: str, node_type: str, signature: str, targets: List[str] = None):
        self.w[label] = {
            "type": node_type,
            "signature": signature,
            "targets": targets if targets else []
        }

    def compute_gap(self, G: TypedEdgeGraph) -> List[Tuple[str, str, str]]:
        """
        Gap(G, w) = M(G) - what G can currently represent.
        Identifies missing node types and target edges in G relative to Λ_w.
        """
        gaps = []
        existing_labels = {node.label for node in G.nodes.values()}
        label_to_id = {node.label: nid for nid, node in G.nodes.items()}

        for expected_label, specs in self.w.items():
            if expected_label not in existing_labels:
                gaps.append((expected_label, "None", f"missing-node-of-type-{specs['type']}"))
            else:
                src_id = label_to_id[expected_label]
                for tgt_label in specs.get("targets", []):
                    if tgt_label in existing_labels:
                        tgt_id = label_to_id[tgt_label]
                        has_edge = any(
                            (e.source == src_id and e.target == tgt_id) or 
                            (e.source == tgt_id and e.target == src_id) 
                            for e in G.edges.values()
                        )
                        if not has_edge:
                            gaps.append((expected_label, tgt_label, "missing-expected-relation"))
                    else:
                        gaps.append((expected_label, tgt_label, "unresolved-target-node"))
        return gaps

# =====================================================================
# 3. E_R Epistemic Representation Metric Class
# =====================================================================

class ERMetric:
    """
    E_R computes the spectral distance (L_2 norm) between two graphs' laplacian spectra.
    Can be used to compare an original representation G against its permuted/rewired variant.
    """
    @staticmethod
    def calculate(G1: TypedEdgeGraph, G2: TypedEdgeGraph) -> float:
        """
        Linear / Isomorphic Regime spectral comparison.
        """
        L1 = G1.get_normalized_laplacian()
        L2 = G2.get_normalized_laplacian()
        
        if L1.size == 0 or L2.shape != L1.shape:
            n = max(L1.shape[0], L2.shape[0])
            evals1 = np.linalg.eigvalsh(L1) if L1.size > 0 else np.zeros(0)
            evals2 = np.linalg.eigvalsh(L2) if L2.size > 0 else np.zeros(0)
            padded_evals1 = np.pad(evals1, (0, n - len(evals1)), 'constant')
            padded_evals2 = np.pad(evals2, (0, n - len(evals2)), 'constant')
            return float(np.linalg.norm(np.sort(padded_evals1) - np.sort(padded_evals2)))
            
        evals1 = np.linalg.eigvalsh(L1)
        evals2 = np.linalg.eigvalsh(L2)
        return float(np.linalg.norm(np.sort(evals1) - np.sort(evals2)))

    @staticmethod
    def calculate_nonlinear_activation(G1: TypedEdgeGraph, G2: TypedEdgeGraph, threshold: float = 0.5) -> float:
        """
        Non-linear Regime comparison. Applies a threshold (mimicking ReLU / activation gates)
        to the Laplacian eigenvalues before calculating the L_2 distance.
        """
        L1 = G1.get_normalized_laplacian()
        L2 = G2.get_normalized_laplacian()
        
        evals1 = np.linalg.eigvalsh(L1) if L1.size > 0 else np.zeros(1)
        evals2 = np.linalg.eigvalsh(L2) if L2.size > 0 else np.zeros(1)
        
        act_evals1 = np.maximum(0.0, evals1 - threshold)
        act_evals2 = np.maximum(0.0, evals2 - threshold)
        
        n = max(len(act_evals1), len(act_evals2))
        padded1 = np.pad(np.sort(act_evals1), (0, n - len(act_evals1)), 'constant')
        padded2 = np.pad(np.sort(act_evals2), (0, n - len(act_evals2)), 'constant')
        
        return float(np.linalg.norm(padded1 - padded2))

# =====================================================================
# 4. DISTINGUISH Operator Implementation and Test Loop
# =====================================================================

def Distinguish(G: TypedEdgeGraph, node_id: str, criteria_label: str, split_func: Callable[[Node], Tuple[dict, dict]]) -> TypedEdgeGraph:
    """
    Distinguish (Lambda_distinguish): Splits a node into two separate nodes based on a criteria function,
    relating the split halves via a Torsion/boundary edge.
    """
    if node_id not in G.nodes:
        return G
    target_node = G.nodes[node_id]
    meta_a, meta_b = split_func(target_node)
    
    id_a = f"{node_id}-alpha"
    id_b = f"{node_id}-beta"
    
    G.add_node(f"{target_node.label}_[{criteria_label}_A]", target_node.type, id_a, provenance=[node_id], metadata=meta_a)
    G.add_node(f"{target_node.label}_[{criteria_label}_B]", target_node.type, id_b, provenance=[node_id], metadata=meta_b)
    
    G.add_edge(id_a, id_b, EdgeType.TORSION, provenance=[], metadata={"criteria": criteria_label})
    
    for eid, e in list(G.edges.items()):
        if e.source == node_id:
            G.add_edge(id_a, e.target, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            G.add_edge(id_b, e.target, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
        elif e.target == node_id:
            G.add_edge(e.source, id_a, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            G.add_edge(e.source, id_b, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            
    G.remove_node(node_id)
    return G

# =====================================================================
# 5. Unit Test Suite for the Morphogenesis Engine
# =====================================================================

class TestMorphogenesisEngine(unittest.TestCase):
    def setUp(self):
        # Set up a canonical base graph for testing
        self.G = TypedEdgeGraph(context="C_0")
        self.G.add_node("Egypt_Fraction", NodeType.CONCEPT, "node-egypt_fraction", metadata={"coherence": 1.0})
        self.G.add_node("Fano_Plane", NodeType.CONCEPT, "node-fano_plane", metadata={"coherence": 1.0})
        self.G.add_edge("node-egypt_fraction", "node-fano_plane", EdgeType.COVALENT)

        # Set up a target World-State Model Λ_w
        self.w = LambdaW()
        self.w.add_target_concept("Egypt_Fraction", NodeType.CONCEPT, "decomposition", ["Fano_Plane"])
        self.w.add_target_concept("Fano_Plane", NodeType.CONCEPT, "composition-closure")
        self.w.add_target_concept("Torsion_Tensor", NodeType.OPERATOR, "skew-geometry")

    def test_gap_detection_logic(self):
        # 1. Initially, 'Torsion_Tensor' is missing from the graph
        gaps = self.w.compute_gap(self.G)
        self.assertTrue(any("Torsion_Tensor" in g[0] for g in gaps))
        self.assertTrue(any("missing-node" in g[2] for g in gaps))

        # 2. Add the missing node and verify the gap is resolved
        self.G.add_node("Torsion_Tensor", NodeType.OPERATOR, "node-torsion_tensor", metadata={"coherence": 1.0})
        resolved_gaps = self.w.compute_gap(self.G)
        self.assertFalse(any("Torsion_Tensor" in g[0] for g in resolved_gaps))

    def test_er_metric_isometry(self):
        # Verify that isomorphic graphs yield exactly 0.0 distance
        G_clone = self.G.clone()
        distance = ERMetric.calculate(self.G, G_clone)
        self.assertEqual(distance, 0.0)

    def test_er_metric_non_linear_rewiring(self):
        # Introduce a re-wiring perturbation and compute non-linear metric
        G_perturbed = self.G.clone()
        G_perturbed.add_node("New_Concept", NodeType.CONCEPT, "node-new_concept")
        G_perturbed.add_edge("node-new_concept", "node-fano_plane", EdgeType.VAN_DER_WAALS)
        
        dist_linear = ERMetric.calculate(self.G, G_perturbed)
        dist_nonlinear = ERMetric.calculate_nonlinear_activation(self.G, G_perturbed, threshold=0.3)
        
        self.assertGreater(dist_linear, 0.0)
        self.assertGreater(dist_nonlinear, 0.0)

    def test_distinguish_operator_invariants(self):
        # Test the formal invariants of the DISTINGUISH split operator
        def mock_split(node: Node) -> Tuple[dict, dict]:
            return {"polarity": "+"}, {"polarity": "-"}
            
        test_id = "node-fano_plane"
        G_split = Distinguish(self.G, test_id, "symmetry_breaking", mock_split)
        
        # 1. Verify original node is purged
        self.assertNotIn(test_id, G_split.nodes)
        
        # 2. Verify split nodes are generated
        self.assertIn(f"{test_id}-alpha", G_split.nodes)
        self.assertIn(f"{test_id}-beta", G_split.nodes)
        
        # 3. Verify TORSION edge exists between split halves
        torsion_edges = [e for e in G_split.edges.values() if e.type == EdgeType.TORSION]
        self.assertEqual(len(torsion_edges), 1)
        self.assertEqual(torsion_edges[0].source, f"{test_id}-alpha")
        self.assertEqual(torsion_edges[0].target, f"{test_id}-beta")
        
        # 4. Verify incoming edge is correctly rewired to both split halves
        rewired = [e for e in G_split.edges.values() if e.source == "node-egypt_fraction"]
        self.assertEqual(len(rewired), 2)

# =====================================================================
# 6. Main Execution Pipeline
# =====================================================================

def run_morphogenesis_validation():
    print("\n" + "="*80)
    print("      LAUNCHING GRAPH MORPHOGENESIS SPECIFICATION ENGINE v2.0")
    print("="*80)
    
    # 1. Define Λ_w Target World-State
    w = LambdaW()
    w.add_target_concept("Egypt_Fraction", NodeType.CONCEPT, "decomposition", ["Fano_Plane"])
    w.add_target_concept("Fano_Plane", NodeType.CONCEPT, "composition-closure")
    w.add_target_concept("Torsion_Tensor", NodeType.OPERATOR, "skew-geometry")
    
    # 2. Instantiate Base Graph G
    G = TypedEdgeGraph(context="C_0")
    G.add_node("Egypt_Fraction", NodeType.CONCEPT, "node-egypt_fraction")
    G.add_node("Fano_Plane", NodeType.CONCEPT, "node-fano_plane")
    G.add_edge("node-egypt_fraction", "node-fano_plane", EdgeType.COVALENT)
    
    print("\n[Step 1] Target World-State Λ_w Defined.")
    print("[Step 2] Representational Gap Analysis via compute_gap(G, w):")
    gaps = w.compute_gap(G)
    for g in gaps:
        print(f"  - Detected Gap: Subject '{g[0]}', Target '{g[1]}', Type: '{g[2]}'")
        
    print("\n[Step 3] Spectral E_R Metric Calculation (Linear vs. Non-linear Activation):")
    G_perm = G.clone()
    # Randomly permute/rewire by adding a node
    G_perm.add_node("Bitemporal_Ledger", NodeType.INDEX, "node-ledger")
    G_perm.add_edge("node-ledger", "node-egypt_fraction", EdgeType.META)
    
    e_r_linear = ERMetric.calculate(G, G_perm)
    e_r_nonlinear = ERMetric.calculate_nonlinear_activation(G, G_perm, threshold=0.3)
    print(f"  - E_R Metric (Linear): {e_r_linear:.6f}")
    print(f"  - E_R Metric (Non-linear Thresholded): {e_r_nonlinear:.6f}")
    
    print("\n" + "="*80)
    print("                      MORPHOGENESIS SIMULATION SUCCESS")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Execute verification pipelines
    run_morphogenesis_validation()
    
    # Run unit test suite
    print("Running formal verification tests...")
    unittest.main()
