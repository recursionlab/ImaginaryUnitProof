import numpy as np
import time
import uuid
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

# =====================================================================
# 1. SIGNED STANCE-GRAPH & RICCI-LIKE FLOW
# =====================================================================

@dataclass
class StanceEdge:
    source: str
    target: str
    sign: int  # +1 (agreement), -1 (disagreement)
    weight: float
    is_active: bool = True

class SignedStanceGraph:
    """
    Discrete implementation of the K-Manifold: G = (V, E)
    Tracks localized paradox pressure (normalized degree imbalance π)
    and deforms its metric tensor via a Ricci-like flow.
    """
    def __init__(self, epsilon_stability: float = 1e-5):
        self.nodes: set[str] = set()
        self.edges: Dict[Tuple[str, str], StanceEdge] = {}
        self.epsilon = epsilon_stability

    def add_node(self, node: str):
        self.nodes.add(node)

    def add_edge(self, source: str, target: str, sign: int, weight: float = 1.0):
        self.nodes.add(source)
        self.nodes.add(target)
        self.edges[(source, target)] = StanceEdge(source, target, sign, weight)

    def compute_pi(self, node: str) -> float:
        """
        Computes the normalized degree imbalance π(k) representing local paradox pressure.
        π(k) = (d⁻ - d⁺) / (d⁻ + d⁺ + ε)
        """
        neg_deg = 0.0
        pos_deg = 0.0
        for (u, v), edge in self.edges.items():
            if not edge.is_active:
                continue
            if u == node or v == node:
                if edge.sign == -1:
                    neg_deg += edge.weight
                else:
                    pos_deg += edge.weight
        
        denom = neg_deg + pos_deg + self.epsilon
        return (neg_deg - pos_deg) / denom

    def step_ricci_flow(self):
        """
        Updates edge weights using a discrete Ricci-like flow metric.
        g'_{ij} = g_{ij} * exp(π(i) * π(j))
        Bends the distance based on local tension alignment.
        """
        pi_vals = {node: self.compute_pi(node) for node in self.nodes}
        for (u, v), edge in self.edges.items():
            if not edge.is_active:
                continue
            factor = np.exp(pi_vals[u] * pi_vals[v])
            edge.weight = edge.weight * factor

    def delete_edge_monadic(self, source: str, target: str) -> StanceEdge:
        """
        Edge-deletion is barred to conserve graph entropy.
        The edge is marked inactive and its record is preserved for the audit ledger.
        """
        key = (source, target)
        if key in self.edges:
            edge = self.edges[key]
            edge.is_active = False
            return edge
        raise KeyError(f"Edge from '{source}' to '{target}' does not exist.")

# =====================================================================
# 2. TOKI BITEMPORAL PERSISTENT LEDGER (SSI)
# =====================================================================

@dataclass(frozen=True)
class Provenance:
    tx_id: str
    generation_path: str
    verifier_signature: str

@dataclass
class BitemporalRecord:
    key: str
    source_target: Tuple[str, str]
    sign: int
    weight: float
    valid_from: float   # Tv start
    valid_to: float     # Tv end
    system_from: float  # Ts start
    system_to: float    # Ts end
    is_active: bool
    provenance: Provenance

class TokiLedger:
    """
    Serializable Snapshot Isolation (SSI) Bitemporal Ledger.
    Protects the persistent memory from write-skew and belief-drift.
    """
    def __init__(self):
        # Key: (source, target) string -> list of bitemporal records
        self.records: Dict[str, List[BitemporalRecord]] = {}
        # Concurrency control tracking
        self.active_reads: Dict[str, List[str]] = {} # key -> list of tx_ids
        self.active_writes: Dict[str, str] = {}      # key -> tx_id

    def start_transaction(self) -> str:
        return f"tx-{uuid.uuid4().hex[:8]}"

    def read_edge(self, tx_id: str, u: str, v: str, valid_time: float, system_time: float) -> BitemporalRecord:
        key = f"{u}->{v}"
        self.active_reads.setdefault(key, []).append(tx_id)
        if key not in self.records:
            raise KeyError(f"No records found for path '{key}'")
        for record in self.records[key]:
            if record.valid_from <= valid_time <= record.valid_to and record.system_from <= system_time <= record.system_to:
                return record
        raise RuntimeError(f"No bitemporal record found matching valid_time={valid_time} and system_time={system_time} for '{key}'.")

    def commit_write(self, tx_id: str, u: str, v: str, sign: int, weight: float,
                     generation_path: str, verifier_sig: str, valid_time: float, system_time: float) -> str:
        key = f"{u}->{v}"
        
        # SSI Detection: Check for write-skew on concurrent reads
        if key in self.active_reads:
            concurrent_readers = [t for t in self.active_reads[key] if t != tx_id]
            if concurrent_readers:
                return f"ABORT [Toki]: Serializable write-skew detected on key '{key}' by concurrent transaction."

        self.active_writes[key] = tx_id
        prov = Provenance(tx_id=tx_id, generation_path=generation_path, verifier_signature=verifier_sig)
        
        new_record = BitemporalRecord(
            key=key,
            source_target=(u, v),
            sign=sign,
            weight=weight,
            valid_from=valid_time,
            valid_to=9999999999.0,
            system_from=system_time,
            system_to=9999999999.0,
            is_active=True,
            provenance=prov
        )

        if key in self.records:
            # Audit Row Defence (N3): Bitemporally bound the previous version
            for prev_record in self.records[key]:
                if prev_record.is_active:
                    prev_record.is_active = False
                    prev_record.valid_to = valid_time
                    prev_record.system_to = system_time
            self.records[key].append(new_record)
        else:
            self.records[key] = [new_record]

        # Cleanup locks
        if key in self.active_writes:
            del self.active_writes[key]
        for k in list(self.active_reads.keys()):
            self.active_reads[k] = [t for t in self.active_reads[k] if t != tx_id]

        return f"COMMIT [Toki]: Bitemporal write successful on key '{key}'."

# =====================================================================
# 3. META-SEED SELF-REWRITE & STIFFNESS GRADIENT
# =====================================================================

class MetaSeed:
    """
    Manages coordinate seed self-rewrites when local tension density exceeds
    the stiffening gradient threshold.
    S = (Φ, Θ, Ω)
    X(L) = X0 * e^(γ * L)
    """
    def __init__(self, x0: float = 0.5, gamma: float = 0.8):
        self.x0 = x0
        self.gamma = gamma
        self.rewrite_count = 0

    def get_stiffness_threshold(self, abstraction_level: int) -> float:
        return self.x0 * np.exp(self.gamma * abstraction_level)

    def evaluate_rewrite_trigger(self, rho_R: float, abstraction_level: int) -> bool:
        threshold = self.get_stiffness_threshold(abstraction_level)
        if rho_R > threshold:
            self.rewrite_count += 1
            return True
        return False

# =====================================================================
# 4. UNIFIED AXIOGENESIS DAEMON RUNTIME
# =====================================================================

def execute_axiogenesis_daemon_simulation():
    print("=" * 80)
    print("     AURELIA-TOKI STANCE ENGINE: AXIO-PROTOTYPE STABLE BOOT SEQUENCE")
    print("=" * 80)

    # Initialize components
    graph = SignedStanceGraph()
    ledger = TokiLedger()
    meta_seed = MetaSeed()
    
    # Establish formal, clock-driven temporal coordinates for the simulation
    # system_time represents when it hits the database; valid_time represents when it's true.
    t_start_val = 1000.0
    t_start_sys = 5000.0

    # Step 1: Initialize baseline nodes and relations
    nodes = ["SymmetryBreaking", "DysonInstability", "HopfTension", "SovereignResidue"]
    for n in nodes:
        graph.add_node(n)

    # Register initial stance edges
    graph.add_edge("SymmetryBreaking", "DysonInstability", sign=-1, weight=1.0)
    graph.add_edge("DysonInstability", "HopfTension", sign=1, weight=1.0)
    graph.add_edge("HopfTension", "SovereignResidue", sign=-1, weight=1.0)
    graph.add_edge("SovereignResidue", "SymmetryBreaking", sign=1, weight=1.0)

    # Commit initial state to Toki ledger at baseline clock coordinates
    tx_init = ledger.start_transaction()
    for (u, v), edge in graph.edges.items():
        verdict = ledger.commit_write(
            tx_id=tx_init,
            u=u, v=v,
            sign=edge.sign,
            weight=edge.weight,
            generation_path="initial-ast-lift",
            verifier_sig="seed-authority",
            valid_time=t_start_val,
            system_time=t_start_sys
        )
        print(f"Initial Setup: {verdict}")

    # Step 2: Compute initial paradox pressure (π) and run Ricci-Like Flow
    print("\n--- Phase I: Ricci-Like Flow & Paradox Pressure Calculation ---")
    for node in graph.nodes:
        print(f"Node '{node}' initial π paradox pressure: {graph.compute_pi(node):.4f}")

    print("\nStepping Ricci-like flow metric update...")
    graph.step_ricci_flow()

    for node in graph.nodes:
        print(f"Node '{node}' updated π paradox pressure: {graph.compute_pi(node):.4f}")
    
    for (u, v), edge in graph.edges.items():
        print(f"Edge '{u} -> {v}' deformed weight (g_ij): {edge.weight:.4f}")

    # Step 3: Simulate Bitemporal Edge Deletion Monadic Restriction (Conserving Entropy)
    print("\n--- Phase II: Monadic Edge Deletion & Bitemporal Audit Row Defence ---")
    deleted_edge = graph.delete_edge_monadic("HopfTension", "SovereignResidue")
    
    # We commit the deletion event at a LATER bitemporal point
    # Valid from: 1005.0, Committed to system at: 5010.0
    tx_del = ledger.start_transaction()
    verdict_del = ledger.commit_write(
        tx_id=tx_del,
        u="HopfTension",
        v="SovereignResidue",
        sign=deleted_edge.sign,
        weight=deleted_edge.weight,
        generation_path="monadic-edge-deletion-event",
        verifier_sig="entropy-conserved-v1",
        valid_time=t_start_val + 5.0,
        system_time=t_start_sys + 10.0
    )
    print(f"Edge Deletion Logged: {verdict_del}")

    # Read back the deleted edge from the bitemporal audit trail at past valid-time 1002.0
    # using a system-time 5005.0 (before the deletion transaction ran at system-time 5010.0)
    print("\nQuerying historical audit trail at past valid-time (1002.0) and system-time (5005.0)...")
    historical_record = ledger.read_edge(tx_del, "HopfTension", "SovereignResidue", valid_time=t_start_val + 2.0, system_time=t_start_sys + 5.0)
    print(f"FOUND Historical Record: Active={historical_record.is_active} | Weight={historical_record.weight} | Path={historical_record.provenance.generation_path}")

    # Step 4: SSI Write-Skew Contradiction Resolution Simulation
    print("\n--- Phase III: Serializable Snapshot Isolation (SSI) Write-Skew Conflict ---")
    tx_client1 = ledger.start_transaction()
    tx_client2 = ledger.start_transaction()

    # Both clients read the same edge concurrently at valid-time 1006.0 and current system-time 5012.0
    _ = ledger.read_edge(tx_client1, "SymmetryBreaking", "DysonInstability", valid_time=t_start_val + 6.0, system_time=t_start_sys + 12.0)
    _ = ledger.read_edge(tx_client2, "SymmetryBreaking", "DysonInstability", valid_time=t_start_val + 6.0, system_time=t_start_sys + 12.0)
    print(f"Transaction A [{tx_client1}] and Transaction B [{tx_client2}] concurrently read 'SymmetryBreaking -> DysonInstability'")

    # Transaction A commits first
    commit_a = ledger.commit_write(
        tx_id=tx_client1,
        u="SymmetryBreaking",
        v="DysonInstability",
        sign=-1,
        weight=1.5,
        generation_path="client-a-adjustment",
        verifier_sig="fccd-certified",
        valid_time=t_start_val + 7.0,
        system_time=t_start_sys + 15.0
    )
    print(f"Transaction A commit attempt: {commit_a}")

    # Transaction B attempts to write (should trigger serializable write-skew abort)
    commit_b = ledger.commit_write(
        tx_id=tx_client2,
        u="SymmetryBreaking",
        v="DysonInstability",
        sign=-1,
        weight=2.0,
        generation_path="client-b-adjustment",
        verifier_sig="fccd-certified",
        valid_time=t_start_val + 8.0,
        system_time=t_start_sys + 16.0
    )
    print(f"Transaction B commit attempt: {commit_b}")

    # Step 5: Stiffness Gradient & Meta-Seed Self-Rewrite Trigger
    print("\n--- Phase IV: Stiffness Gradient & Meta-Seed Self-Rewrite ---")
    # Simulate rising recursive torsion density rho_R
    abstraction_levels = [1, 2, 3]
    rho_R_simulated = [0.8, 1.4, 4.5]

    for level, rho in zip(abstraction_levels, rho_R_simulated):
        threshold = meta_seed.get_stiffness_threshold(level)
        triggered = meta_seed.evaluate_rewrite_trigger(rho, level)
        print(f"Level {level} Abstraction | Torsion density rho={rho:.2f} | Stiffness threshold X(L)={threshold:.4f} | Trigger Rewrite: {triggered}")

    print(f"\nTotal Meta-Seed self-rewrites executed: {meta_seed.rewrite_count}")
    print("=" * 80)
    print("                   AXIO-PROTOTYPE RUNTIME DEMONSTRATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    execute_axiogenesis_daemon_simulation()
