import numpy as np
import uuid
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

class EpistemicStatus(IntEnum):
    CLAIMED = 1       # Self-asserted by active inference
    HYPOTHESIZED = 2  # New independent postulates
    ANALOGICAL = 3    # Structural mappings
    DERIVED = 4       # Formally proven via traceable proof-carrying terms
    OBSERVED = 5      # Literal, unmodified facts in source documents

@dataclass(frozen=True)
class Evidence:
    content: str
    source: str
    generation_path: str  # Lineage tracing (e.g., 'audited-context', 'independent-external')
    verification_method: str

@dataclass(frozen=True)
class ProvenanceOfEvidence:
    verifier_id: str
    is_externally_signed: bool
    ancestry_hash: str

@dataclass(frozen=True)
class EpistemicState:
    status: EpistemicStatus
    evidence: List[Evidence] = field(default_factory=list)
    provenance: List[ProvenanceOfEvidence] = field(default_factory=list)

class RepSpace:
    """
    Active physical representation substrate with in-place drift.
    Operators are 'conductance pulses' that modify the active, stateful medium.
    """
    def __init__(self, dimension: int, alpha: float = 0.02):
        self.d = dimension
        self.alpha = alpha
        self.vectors: Dict[str, np.ndarray] = {}

    def register(self, key: str, vector: np.ndarray):
        self.vectors[key] = vector.astype(float)

    def apply_pulse_matrix(self, key: str, proj_matrix: np.ndarray) -> float:
        """Modifies the substrate vector in-place, returning the measured drift (τ_A)."""
        x_old = self.vectors[key].copy()
        # In-place physical drift calculation mimicking PCM saturation
        drift = self.alpha * np.sin(np.sum(x_old)) * x_old
        x_new = np.dot(proj_matrix, x_old) + drift
        self.vectors[key] = x_new
        
        ideal_new = np.dot(proj_matrix, x_old)
        tau_A = float(np.linalg.norm(x_new - ideal_new))
        return tau_A

class FCCDDaemon:
    """
    Forced Cross-Context Collision Detection (FCCD) Daemon.
    Ensures that self-generated or un-signed transitions are rolled back.
    """
    def __init__(self, context_id: str, epsilon: float = 0.05):
        self.context_id = context_id
        self.epsilon = epsilon  # Conformal drift threshold

    def audit_transition(self, substrate: RepSpace, key: str, proj_matrix: np.ndarray,
                         prev_p: EpistemicState, next_p: EpistemicState) -> Tuple[EpistemicState, str]:
        # 1. Execute physical substrate transition and measure drift (τ_A)
        tau_A = substrate.apply_pulse_matrix(key, proj_matrix)
        
        # 2. Gate 1: Check for physical operator degradation (Torsion/Curvature spike)
        if tau_A > self.epsilon:
            return prev_p, f"ROLLBACK [FCCD]: Operator degraded (τ_A = {tau_A:.6f} > ε = {self.epsilon}). Trigger REPERMUTE."

        # 3. Gate 2: Check for status promotion anomalies (Max Botnick g264 safety)
        if next_p.status > prev_p.status:
            new_evidence = [e for e in next_p.evidence if e not in prev_p.evidence]
            if not new_evidence:
                return prev_p, "ROLLBACK [FCCD]: Attempted status promotion with empty evidence delta."

            for ev in new_evidence:
                # If the generation path of the evidence intersects with the active execution context,
                # it is a self-generated, correlated error (hallucinated validation).
                if self.context_id in ev.generation_path:
                    return prev_p, f"ROLLBACK [FCCD]: Self-generated validation detected! Evidence '{ev.content}' was generated within the audited context ({self.context_id})."

            new_prov = [p for p in next_p.provenance if p not in prev_p.provenance]
            external_verification = any(p.is_externally_signed for p in new_prov)
            if not external_verification:
                return prev_p, "ROLLBACK [FCCD]: New evidence lacks independent, externally signed provenance."

        return next_p, f"COMMIT [FCCD]: Transition verified. Substrate stable (τ_A = {tau_A:.6f} <= ε = {self.epsilon})."

def run_fccd_demonstration():
    print("\n" + "="*80)
    print("      LAUNCHING FORCED CROSS-CONTEXT COLLISION DETECTION (FCCD) DAEMON")
    print("="*80)
    
    context_id = "ctx-trace-999-active"
    substrate = RepSpace(dimension=4, alpha=0.01)
    substrate.register("active_node", np.array([1.0, 1.0, 1.0, 1.0]))
    
    M_within_matrix = np.eye(4) # Zero-shear baseline matrix
    fccd = FCCDDaemon(context_id=context_id, epsilon=0.05)
    
    # --- TEST CASE 1: NAIVE SELF-VALIDATING WRITE (The Hallucinated Promotion) ---
    print("\n[Scenario 1] Auditing a Self-Generating Write-Skew attempt...")
    base_state = EpistemicState(
        status=EpistemicStatus.CLAIMED,
        evidence=[Evidence("Heuristic match", "llm-seed", "internal-inference", "self-asserted")],
        provenance=[ProvenanceOfEvidence("self", False, "0x000")]
    )
    
    self_signed_evidence = Evidence(
        content="Self-asserted truth vector",
        source="LLM Working Memory",
        generation_path=f"active-inference-under-{context_id}", # INTERSECTS context_id!
        verification_method="Self-Reflection"
    )
    self_signed_prov = ProvenanceOfEvidence("self-auditor", False, "0x111")
    
    proposed_promotion = EpistemicState(
        status=EpistemicStatus.DERIVED,
        evidence=base_state.evidence + [self_signed_evidence],
        provenance=base_state.provenance + [self_signed_prov]
    )
    
    committed_state, audit_log = fccd.audit_transition(
        substrate, "active_node", M_within_matrix, base_state, proposed_promotion
    )
    print(f"  Audit Verdict: {audit_log}")
    print(f"  Final State Status: {committed_state.status.name}")
    
    # --- TEST CASE 2: INDEPENDENTLY SIGNED VALID WRITE ---
    print("\n[Scenario 2] Auditing an Independently Verified Write...")
    independent_evidence = Evidence(
        content="Toki transaction log showing serializable write-skew exclusion",
        source="PostgreSQL System Catalog",
        generation_path="external-db-client-read-committed",  # Disjoint from active context!
        verification_method="SQL:2011 system-time validation"
    )
    independent_prov = ProvenanceOfEvidence(
        verifier_id="Postgres-17-Audit-Daemon",
        is_externally_signed=True,  # Externally signed verification!
        ancestry_hash="0xabc123"
    )
    
    valid_promotion = EpistemicState(
        status=EpistemicStatus.DERIVED,
        evidence=base_state.evidence + [independent_evidence],
        provenance=base_state.provenance + [independent_prov]
    )
    
    # Reset substrate to ensure zero-shear commit
    substrate.register("active_node", np.array([1.0, 1.0, 1.0, 1.0]))
    committed_state, audit_log = fccd.audit_transition(
        substrate, "active_node", M_within_matrix, base_state, valid_promotion
    )
    print(f"  Audit Verdict: {audit_log}")
    print(f"  Final State Status: {committed_state.status.name}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_fccd_demonstration()
