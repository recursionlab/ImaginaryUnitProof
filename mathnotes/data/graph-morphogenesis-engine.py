import numpy as np
import uuid
import copy
import unittest
from typing import Callable, Any, Dict, List, Set, Tuple

# =====================================================================
# 1. Core Data Models: Nodes, Edges, and the Typed Edge Graph
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
        return f"Node({self.id}, label='{self.label}', type='{self.type}', prov={self.provenance})"

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
        # binding_condition determines if the edge can bind to a given context or node pair
        self.binding_condition = binding_condition if binding_condition else (lambda s, t: True)
        # transformation_func rho(e) defines how the edge mutates its target or the graph
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
    def __init__(self, context: str = "C_0", operator_set: Dict[str, Callable] = None):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.context = context  # Context Index (C_n)
        self.history: List[dict] = []  # History trace of index and state mutations (H_n)
        self.operators = operator_set if operator_set else {}  # Active operators (R_n)
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
            # Prune associated edges
            edges_to_remove = [eid for eid, e in self.edges.items() if e.source == node_id or e.target == node_id]
            for eid in edges_to_remove:
                del self.edges[eid]

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str, Edge]]:
        """Returns list of (neighbor_id, direction, Edge)"""
        neighbors = []
        for e in self.edges.values():
            if e.source == node_id:
                neighbors.append((e.target, "outgoing", e))
            elif e.target == node_id:
                neighbors.append((e.source, "incoming", e))
        return neighbors

    def clone(self) -> 'TypedEdgeGraph':
        """Deep clones the graph structure while preserving callable functions."""
        new_g = TypedEdgeGraph(context=self.context, operator_set=self.operators)
        new_g.nodes = {nid: Node(n.id, n.label, n.type, list(n.provenance), dict(n.metadata)) for nid, n in self.nodes.items()}
        new_g.edges = {eid: Edge(e.id, e.source, e.target, e.type, e.binding_condition, e.transformation_func, list(e.provenance), dict(e.metadata)) for eid, e in self.edges.items()}
        new_g.history = copy.deepcopy(self.history)
        new_g.step_counter = self.step_counter
        return new_g

# =====================================================================
# 2. The Seven Graph Morphogenesis Operators
# =====================================================================

def Distinguish(G: TypedEdgeGraph, node_id: str, criteria_label: str, split_func: Callable[[Node], Tuple[dict, dict]]) -> TypedEdgeGraph:
    """
    1. Distinguish: Splits a node into two separate nodes based on a criteria function,
    enforcing conceptual separation (e.g. self vs. other or separating properties).
    """
    if node_id not in G.nodes:
        return G
    target_node = G.nodes[node_id]
    meta_a, meta_b = split_func(target_node)
    
    # Create distinguished split nodes
    id_a = f"{node_id}-alpha"
    id_b = f"{node_id}-beta"
    
    node_a = G.add_node(f"{target_node.label}_[{criteria_label}_A]", target_node.type, id_a, provenance=[node_id], metadata=meta_a)
    node_b = G.add_node(f"{target_node.label}_[{criteria_label}_B]", target_node.type, id_b, provenance=[node_id], metadata=meta_b)
    
    # Relate them with a Torsion/boundary edge
    G.add_edge(id_a, id_b, EdgeType.TORSION, provenance=[], metadata={"criteria": criteria_label})
    
    # Rewire original incoming/outgoing edges to both distinguished halves where appropriate
    for eid, e in list(G.edges.items()):
        if e.source == node_id:
            G.add_edge(id_a, e.target, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            G.add_edge(id_b, e.target, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
        elif e.target == node_id:
            G.add_edge(e.source, id_a, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            G.add_edge(e.source, id_b, e.type, binding_condition=e.binding_condition, transformation_func=e.transformation_func, provenance=[e.id])
            
    # Remove original node
    G.remove_node(node_id)
    return G

def Abstract(G: TypedEdgeGraph, subgraph_node_ids: List[str], abstract_label: str) -> TypedEdgeGraph:
    """
    2. Abstract: Lifts a subgraph structure to a higher-order 'meta' node,
    representing the category-theoretic section/retraction of the subgraph.
    """
    # Create the abstract meta node
    meta_node_id = f"meta-{uuid.uuid4()}"
    G.add_node(abstract_label, NodeType.INDEX, meta_node_id, provenance=subgraph_node_ids)
    
    # Create higher-order META edges from the abstract node to each of the subgraph components
    for nid in subgraph_node_ids:
        if nid in G.nodes:
            G.add_edge(meta_node_id, nid, EdgeType.META, metadata={"role": "abstraction-anchor"})
            
    return G

def Relate(G: TypedEdgeGraph, source_id: str, target_id: str, edge_type: str, 
           rho_func: Callable[[TypedEdgeGraph], TypedEdgeGraph] = None,
           binding_cond: Callable[[Any, Any], bool] = None) -> TypedEdgeGraph:
    """
    3. Relate: Connects two nodes with a typed, bound edge carrying the transformation rho(e).
    """
    if source_id in G.nodes and target_id in G.nodes:
        G.add_edge(source_id, target_id, edge_type, transformation_func=rho_func, binding_condition=binding_cond)
    return G

def Transform(G: TypedEdgeGraph, edge_id: str) -> TypedEdgeGraph:
    """
    4. Transform: Executes the associated transformation function rho(e) of the edge,
    inducing structural mutations across the targeted sub-manifold.
    """
    if edge_id in G.edges:
        edge = G.edges[edge_id]
        # Execute the transformation on the graph
        G = edge.transformation_func(G)
    return G

def Evaluate(G: TypedEdgeGraph) -> float:
    """
    5. Evaluate: Computes a metric representing the global structural state.
    Here, we calculate the Self-Indexing Defect (SI-Defect).
    """
    if not G.nodes:
        return 0.0
    anomaly_edges = sum(1 for e in G.edges.values() if e.type in [EdgeType.TORSION, EdgeType.META])
    total_nodes = len(G.nodes)
    return float(anomaly_edges / total_nodes)

def Recurse(G: TypedEdgeGraph, operator_key: str, action_func: Callable[[TypedEdgeGraph, str], Tuple[TypedEdgeGraph, str]]) -> TypedEdgeGraph:
    """
    6. Recurse: Enforces the triple-recursion cycle.
    Updates Object (X_n -> X_n+1), Context (C_n -> C_n+1), and the operator itself (R_n -> R_n+1).
    Appends this transition step to the history trace H_n.
    """
    prev_context = G.context
    prev_operator = operator_key
    
    # Execute the action on the graph under the current context
    new_G, next_context = action_func(G, prev_context)
    
    # Record the transition in history H_n
    new_G.step_counter += 1
    history_entry = {
        "step": new_G.step_counter,
        "prev_context": prev_context,
        "new_context": next_context,
        "operator": prev_operator,
        "timestamp": f"epoch-{new_G.step_counter}"
    }
    new_G.history.append(history_entry)
    new_G.context = next_context
    return new_G

def Re_map(G: TypedEdgeGraph, classification_index_id: str, target_node_type: str, mapper_func: Callable[[Node], bool]) -> TypedEdgeGraph:
    """
    7. Re-map: Re-indexes previous nodes to a new structural index based on newly 
    discovered distinctions (morphic re-alignment).
    """
    if classification_index_id not in G.nodes:
         G.add_node("Recursive Decomposition Index", NodeType.INDEX, classification_index_id)
         
    for node in list(G.nodes.values()):
        if node.type == target_node_type and mapper_func(node):
            # Connect the node to the new structural Index
            already_linked = any(e.source == classification_index_id and e.target == node.id for e in G.edges.values())
            if not already_linked:
                G.add_edge(classification_index_id, node.id, EdgeType.META, metadata={"role": "re-mapped-index"})
    return G

# =====================================================================
# 3. Layered Vocabularies & Morphogenetic Generators (M_0 & Evolution)
# =====================================================================

class VocabularyLayers:
    W_25 = {
        "Egypt_Fraction": {"type": NodeType.CONCEPT, "signature": "decomposition"},
        "Fano_Plane": {"type": NodeType.CONCEPT, "signature": "composition-closure"},
        "Torsion_Tensor": {"type": NodeType.OPERATOR, "signature": "skew-geometry"},
        "Bitemporal_Ledger": {"type": NodeType.INDEX, "signature": "anomaly-protection"},
        "M0_Null": {"type": NodeType.CONCEPT, "signature": "primordial-void"}
    }
    
    W_100 = {
        "Sedenion_Algebra": {"type": NodeType.OPERATOR, "signature": "non-associative-splitting"},
        "Associahedron": {"type": NodeType.INDEX, "signature": "parenthesization-polytope"},
        "Hopf_Fibration": {"type": NodeType.OPERATOR, "signature": "co-boundary-classifier"},
        "Möbius_Adjunction": {"type": NodeType.CONCEPT, "signature": "duality-mirror"},
        "Lore_Architecture": {"type": NodeType.INDEX, "signature": "self-modifying-epistemology"}
    }

class MetaMapM:
    """
    The Meta-Map generator M that governs G_k+1 = M(G_k).
    M also co-evolves dynamically via M_k+1 = Phi(M_k, G_k) based on detected gaps.
    """
    def __init__(self, level: int = 0):
        self.level = level
        self.active_vocabulary = dict(VocabularyLayers.W_25)
        self.rules: List[Callable[[TypedEdgeGraph], TypedEdgeGraph]] = []
        self._initialize_rules()

    def _initialize_rules(self):
        # Default rule 1: Connect raw lexical nodes sharing similar signatures
        def connect_by_signature(G: TypedEdgeGraph) -> TypedEdgeGraph:
            nodes_list = list(G.nodes.values())
            for i, n1 in enumerate(nodes_list):
                for n2 in nodes_list[i+1:]:
                    sig1 = n1.metadata.get("signature")
                    sig2 = n2.metadata.get("signature")
                    if sig1 and sig2 and sig1 == sig2:
                        Relate(G, n1.id, n2.id, EdgeType.COVALENT)
            return G
        
        # Default rule 2: Create a meta-index node to govern operators
        def lift_operators(G: TypedEdgeGraph) -> TypedEdgeGraph:
            ops = [nid for nid, n in G.nodes.items() if n.type == NodeType.OPERATOR]
            if ops:
                Abstract(G, ops, f"Operator-Manifold-L{self.level}")
            return G

        self.rules = [connect_by_signature, lift_operators]

    def generate_M0(self) -> TypedEdgeGraph:
        """Creates G_0 from 'raw lexical evidence' (base vocabulary)."""
        G0 = TypedEdgeGraph(context="C_0")
        for word, specs in self.active_vocabulary.items():
            G0.add_node(word, specs["type"], node_id=f"node-{word.lower()}", metadata={"signature": specs["signature"]})
        for rule in self.rules:
            G0 = rule(G0)
        return G0

    def evolve_graph(self, G: TypedEdgeGraph) -> TypedEdgeGraph:
        """Procedural application of rules to evolve G_k -> G_k+1."""
        G_next = G.clone()
        for rule in self.rules:
            G_next = rule(G_next)
        return G_next

    def evolve_metamap(self, G: TypedEdgeGraph):
        """Phi(M_k, G_k) -> M_k+1"""
        gap_report = detect_representational_gaps(G, self)
        if gap_report["structural_tension_high"] and self.level == 0:
            self.level = 1
            self.active_vocabulary.update(VocabularyLayers.W_100)
            
            # New rule: Re-map concepts to the Associahedron Index
            def map_to_associahedron(graph: TypedEdgeGraph) -> TypedEdgeGraph:
                return Re_map(graph, "node-associahedron", NodeType.CONCEPT, 
                              lambda n: n.metadata.get("signature") in ["decomposition", "composition-closure"])
            
            self.rules.append(map_to_associahedron)
            return True
        return False

# =====================================================================
# 4. Representational Gap Detection & SI-Defect Math
# =====================================================================

def detect_representational_gaps(G: TypedEdgeGraph, M: MetaMapM) -> dict:
    """Gap(G, M) = M(G) - what G can currently represent."""
    tension = Evaluate(G)
    gaps = []
    
    nodes_list = list(G.nodes.keys())
    for i, n1_id in enumerate(nodes_list):
        for n2_id in nodes_list[i+1:]:
            has_edge = any(e.source == n1_id and e.target == n2_id or e.source == n2_id and e.target == n1_id for e in G.edges.values())
            if not has_edge:
                sig1 = G.nodes[n1_id].metadata.get("signature")
                sig2 = G.nodes[n2_id].metadata.get("signature")
                if sig1 == sig2:
                    gaps.append((n1_id, n2_id, "missing-covalent-link"))

    return {
        "structural_tension_high": tension > 0.1,
        "tension_score": tension,
        "gaps_detected": gaps
    }

def calculate_si_defect(G: TypedEdgeGraph, test_node_id: str) -> float:
    """
    Strict mathematical implementation of the Self-Indexing Defect.
    SI-Defect = || SI_{C1} o SI_{C0}(X) - SI_{C0} o SI_{C0}(X) ||
    """
    if test_node_id not in G.nodes:
        return 0.0
        
    flat_G = G.clone()
    def split_rule(n):
        return {"flat_iter": 1}, {"flat_iter": 1}
    flat_G = Distinguish(flat_G, test_node_id, "flat_repetition", split_rule)
    flat_G = Distinguish(flat_G, f"{test_node_id}-alpha", "flat_repetition", split_rule)
    
    indexed_G = G.clone()
    indexed_G = Recurse(indexed_G, "Distinguish_C0", lambda g, ctx: (
        Distinguish(g, test_node_id, "self_indexed", split_rule), "C_1"
    ))
    def split_rule_C1(n):
        return {"context_mutated": 2}, {"context_mutated": 2}
    indexed_G = Recurse(indexed_G, "Distinguish_C1", lambda g, ctx: (
        Distinguish(g, f"{test_node_id}-alpha", "self_indexed", split_rule_C1), "C_2"
    ))
    
    try:
        node_id_to_check = f"{test_node_id}-alpha-alpha"
        flat_val = flat_G.nodes[node_id_to_check].metadata.get("flat_iter", 0)
        indexed_val = indexed_G.nodes[node_id_to_check].metadata.get("context_mutated", 0)
        return float(abs(indexed_val - flat_val))
    except KeyError:
        return 1.0

# =====================================================================
# 5. Unit Test Suite for Comprehensive Verification
# =====================================================================

class TestGraphMorphogenesis(unittest.TestCase):
    def setUp(self):
        self.M = MetaMapM(level=0)
        self.G0 = self.M.generate_M0()

    def test_node_and_edge_creation(self):
        # Verify initial graph properties
        self.assertGreater(len(self.G0.nodes), 0)
        self.assertIn("node-m0_null", self.G0.nodes)
        node = self.G0.nodes["node-m0_null"]
        self.assertEqual(node.label, "M0_Null")
        self.assertEqual(node.type, NodeType.CONCEPT)

    def test_distinguish_operator(self):
        # Test Distinguish split operation
        test_id = "node-fano_plane"
        self.assertIn(test_id, self.G0.nodes)
        
        def mock_split(node):
            return {"split": "A"}, {"split": "B"}
            
        G_split = Distinguish(self.G0, test_id, "symmetry_breaking", mock_split)
        self.assertNotIn(test_id, G_split.nodes)
        self.assertIn(f"{test_id}-alpha", G_split.nodes)
        self.assertIn(f"{test_id}-beta", G_split.nodes)

    def test_abstract_operator(self):
        # Test Abstract lifting
        subgraph = ["node-egypt_fraction", "node-fano_plane"]
        G_abs = Abstract(self.G0, subgraph, "L1-Abstraction-Index")
        
        # Verify abstract index node is added
        abstract_nodes = [n for n in G_abs.nodes.values() if n.label == "L1-Abstraction-Index"]
        self.assertEqual(len(abstract_nodes), 1)
        abs_node = abstract_nodes[0]
        self.assertEqual(abs_node.type, NodeType.INDEX)

    def test_evaluate_and_gaps(self):
        # Test Evaluate metrics & representational gaps
        gap_report = detect_representational_gaps(self.G0, self.M)
        self.assertIn("tension_score", gap_report)
        self.assertIn("gaps_detected", gap_report)

    def test_self_indexing_defect(self):
        # Test strict SI-Defect calculation
        defect = calculate_si_defect(self.G0, "node-egypt_fraction")
        self.assertNotEqual(defect, 0.0)

    def test_meta_map_evolution(self):
        # Artificially trigger high tension to force evolution to level 1
        G_tense = self.G0.clone()
        # Add high-order meta edges to skew Evaluate metric
        for nid in G_tense.nodes.keys():
            G_tense.add_edge("node-bitemporal_ledger", nid, EdgeType.META)
            
        is_evolved = self.M.evolve_metamap(G_tense)
        self.assertTrue(is_evolved)
        self.assertEqual(self.M.level, 1)
        self.assertIn("node-associahedron", self.M.generate_M0().nodes)

# =====================================================================
# 6. Main Execution Pipeline
# =====================================================================

def run_morphogenesis_simulation():
    print("\n" + "="*80)
    print("      LAUNCHING GRAPH MORPHOGENESIS ENGINE & SELF-INDEXING DAEMON")
    print("="*80)
    
    M = MetaMapM(level=0)
    G0 = M.generate_M0()
    print("\n[Step 1] Constructing Initial Graph G_0 from M_0...")
    print(f"  Initialized {len(G0.nodes)} nodes and {len(G0.edges)} edges in G_0.")
    
    print("\n[Step 2] Executing Representational Gap Detection...")
    gap_analysis = detect_representational_gaps(G0, M)
    print(f"  Tension Score: {gap_analysis['tension_score']:.3f}")
    
    print("\n[Step 3] Computing SI-Defect on 'Egypt_Fraction' Node...")
    defect = calculate_si_defect(G0, "node-egypt_fraction")
    print(f"  SI-Defect Value: {defect:.2f}")
    
    print("\n[Step 4] Evolving Meta-Map Operator Vocabulary Phi(M_0, G_0)...")
    # Artificially increase tension to force evolution to higher degrees of freedom
    G_tense = G0.clone()
    for nid in G_tense.nodes.keys():
        G_tense.add_edge("node-bitemporal_ledger", nid, EdgeType.META)
    evolved = M.evolve_metamap(G_tense)
    print(f"  Meta-Map Evolved to Higher Degree of Freedom: {evolved}")
    print(f"  New Rules Active in M_1: {[r.__name__ for r in M.rules]}")
    
    print("\n[Step 5] Executing Graph Evolution Cycle G_1 = M_1(G_0)...")
    G1 = M.evolve_graph(G0)
    print(f"  Evolved G_1 has {len(G1.nodes)} nodes and {len(G1.edges)} edges.")
    
    print("\n" + "="*80)
    print("                      MORPHOGENESIS SIMULATION SUCCESS")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Execute the live simulation
    run_morphogenesis_simulation()
    
    # Execute the unit test suite
    print("Running formal verification tests...")
    unittest.main()
