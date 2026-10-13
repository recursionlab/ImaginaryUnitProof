import uuid
import sys
import math
from typing import Dict, List, Any, Optional, Tuple, Set

def negate_statement(stmt: str) -> str:
    """
    Linguistic negation operator.
    Prepends 'NOT: ' or strips it if already present.
    """
    if stmt.startswith("NOT: "):
        return stmt[5:]
    return f"NOT: {stmt}"

class Claim:
    """
    Represents a formal semantic node (Proposition) in the system.
    Obeys the strict 'Proof Obligation' constraint of the Prover-Verifier architecture.
    """
    def __init__(self, statement: str, source: str, quote: str, derivation: List[str], 
                 confidence: float, level: int = 0, signature: Optional[str] = None):
        self.id = uuid.uuid4()
        self.statement = statement
        self.source = source
        self.quote = quote
        self.derivation = derivation  # List of statements that this claim derives from
        self.confidence = max(0.0, min(1.0, confidence))
        self.level = level  # Stratification level (RDD: P0, P1, P2...)
        self.signature = signature or f"CLAIM-{self.id.hex[:8]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "statement": self.statement,
            "source": self.source,
            "quote": self.quote,
            "derivation": self.derivation,
            "confidence": self.confidence,
            "level": self.level,
            "signature": self.signature
        }

    def __repr__(self) -> str:
        return f"[{self.signature} (L{self.level})] '{self.statement}' [Conf={self.confidence:.2f}]"


class ReferenceCorpus:
    """
    An immutable, verified database of source documents and their exact textual content.
    Serves as the absolute 'External Anchor' for the Verifier to prevent hallucination/lying.
    """
    def __init__(self):
        # Maps source_name -> list of verified passages/quotes
        self.database: Dict[str, List[str]] = {
            "1 Modeling Semantic Spaces with Quantum Principles.pdf": [
                "We interpret hbar as a measure of semantic granularity. A smaller hbar implies a finer-grained semantic space, where the LLM can make subtle distinctions in meaning. This could correspond to a larger and more evenly distributed vocabulary, allowing for a greater number of distinct semantic states. In this scenario, the LLM is capable of resolving fine-grained semantic differences and capturing nuanced relationships between concepts.",
                "We interpret m as semantic inertia, representing the resistance of a semantic concept to transitions between distinct, quantized states.",
                "We choose the following three fundamental units: [m]: Units of semantic inertia (mass), [x]: Units of semantic distance (length), and [t]: Units of semantic time.",
                "Therefore, the units of semantic charge are [q] = sqrt(m * x) / t. We can think of semantic charge as a measure of how much semantic content is being transported."
            ],
            "A Theory of Language Learning.pdf": [
                "Each word m-script can be learnt robustly from about six learning examples.",
                "The m-script formalism can express meanings of unbounded complexity, and the syntax of adult languages.",
                "To learn a language is just to learn a set of word m-scripts."
            ],
            "GODEL SELF-DISPROVING THEORY.md": [
                "To prevent self-justifying collapse, the architecture must maintain a separate Generator (to propose claims) and a Verifier (to check them).",
                "The Self-Disprover (SD) Mandate: This system treats its own operational axioms as the highest-priority targets for torsion testing.",
                "The system utilizes a Validator (V), which has 'too much faith,' and a Self-Disprover (SD), which has '0% confidence.'",
                "SD doesn't learn 'I am right.' SD learns 'V's prediction that I am wrong is itself consistently wrong.'"
            ],
            "From Entropy to Epiplexity.pdf": [
                "Epiplexity (epistemic complexity) formally defines the amount of structural information that a computationally-bounded observer can extract from the data.",
                "Loss indicates how random the data looks to the model, while epiplexity indicates how much structure the model must acquire to explain away the non-random part."
            ]
        }

    def verify_quote(self, source: str, quote: str) -> bool:
        """
        Checks if the exact quote is contained within the verified passages of the source.
        """
        if source not in self.database:
            return False
        
        # Normalize whitespace and lowercase for robust comparison
        norm_quote = " ".join(quote.lower().replace("ℏ", "hbar").split())
        for passage in self.database[source]:
            norm_passage = " ".join(passage.lower().replace("ℏ", "hbar").split())
            if norm_quote in norm_passage:
                return True
        return False


class KnowledgeBase:
    """
    Stores verified claims and manages inference rules.
    Runs a backward-chaining engine to evaluate semantic provability.
    """
    def __init__(self):
        self.claims: Dict[str, Claim] = {}
        # Rules: List of tuples (premises, conclusion)
        self.rules: List[Tuple[List[str], str]] = []

    def add_claim(self, claim: Claim) -> None:
        self.claims[claim.statement] = claim

    def remove_claim(self, statement: str) -> None:
        if statement in self.claims:
            del self.claims[statement]

    def add_rule(self, premises: List[str], conclusion: str) -> None:
        self.rules.append((premises, conclusion))

    def is_provable(self, statement: str, visited: Optional[Set[str]] = None) -> bool:
        """
        Runs backward chaining to determine if a statement is logically provable
        under the current database of verified claims and implication rules.
        """
        if visited is None:
            visited = set()

        if statement in visited:
            return False
        visited.add(statement)

        # 1. Base Case: Directly present as a verified claim
        if statement in self.claims:
            return True

        # 2. Recursive Case: Derivable via deduction rules
        for premises, conclusion in self.rules:
            if conclusion == statement:
                if all(self.is_provable(premise, visited.copy()) for premise in premises):
                    return True
        return False


class Prover:
    """
    The 'Proposer' (Generator) agent of the split.
    Proposes claims and builds derivation trees for the Verifier to audit.
    """
    def __init__(self, name: str = "Proposer-Core"):
        self.name = name

    def propose_claim(self, statement: str, source: str, quote: str, 
                      derivation: List[str], confidence: float, level: int = 0) -> Claim:
        """
        Assembles a formal Claim object with explicit proof obligations.
        """
        return Claim(
            statement=statement,
            source=source,
            quote=quote,
            derivation=derivation,
            confidence=confidence,
            level=level
        )


class Verifier:
    """
    The 'Verifier' (Auditor) agent of the split.
    Enforces absolute compliance, verifies quotes against the reference corpus,
    checks derivation chains, runs the phi pathology check, and measures NNR.
    """
    def __init__(self, corpus: ReferenceCorpus, energy_limit: float = 100.0):
        self.corpus = corpus
        self.energy_limit = energy_limit
        self.energy_spent = 0.0

    def consume_energy(self, amount: float) -> None:
        self.energy_spent += amount
        if self.energy_spent > self.energy_limit:
            raise RuntimeError("CRITICAL RECURSION FAILURE: ENERGY BUDGET EXCEEDED (BUDGET-EXCEEDED)")

    def phi_operator(self, kb: KnowledgeBase, statement: str) -> int:
        """
        The phi pathology operator.
        Returns:
            1: Pathology detected (either Gödel independence or absolute contradiction)
            0: Consistent/Decidable (either clean proof or clean refutation)
        """
        self.consume_energy(2.0)
        prov_a = kb.is_provable(statement)
        prov_not_a = kb.is_provable(negate_statement(statement))

        if prov_a == prov_not_a:
            # Both True (Contradiction) or both False (Independence)
            return 1
        return 0

    def verify_claim(self, claim: Claim, kb: KnowledgeBase) -> Tuple[bool, str]:
        """
        Performs a ruthless multi-stage audit on a proposed claim.
        """
        self.consume_energy(5.0)

        # 1. External Anchor Check: Verify if quote exists in the source
        if not self.corpus.verify_quote(claim.source, claim.quote):
            return False, f"VERIFICATION-FAIL: Hallucinated quote or invalid source anchor in '{claim.source}'."

        # 2. Derivation Coherence Check: Are all claimed premises provable?
        for premise in claim.derivation:
            self.consume_energy(1.0)
            if not kb.is_provable(premise):
                return False, f"VERIFICATION-FAIL: Derivation path broken. Premise '{premise}' is not provable."

        # 3. Pathology Protection: Does adding this claim trigger a phi-pathology?
        # To test, we temporarily insert the claim and run phi_operator
        temp_kb = KnowledgeBase()
        temp_kb.claims = kb.claims.copy()
        temp_kb.rules = kb.rules.copy()
        temp_kb.add_claim(claim)

        if self.phi_operator(temp_kb, claim.statement) == 1:
            # Double-check if it's because both are provable (Inconsistency)
            if temp_kb.is_provable(claim.statement) and temp_kb.is_provable(negate_statement(claim.statement)):
                return False, f"VERIFICATION-FAIL: Adding '{claim.statement}' triggers absolute system contradiction."
            else:
                return False, f"VERIFICATION-FAIL: Claim '{claim.statement}' lies in Gödelian Independence space (unprovable under axioms)."

        # 4. Non-Negative Redundancy (NNR) Check: Does this add structural information?
        # If the statement is already fully provable without this claim, and doesn't lift our confidence,
        # it is considered redundant under the NNR policy.
        if kb.is_provable(claim.statement):
            existing_claim = kb.claims.get(claim.statement)
            if existing_claim and existing_claim.confidence >= claim.confidence:
                return False, "VERIFICATION-FAIL: Rejected under NNR policy. Claim is redundant and adds no structural entropy."

        return True, "VERIFICATION-SUCCESS: Claim is structurally sound and dually anchored."


class SelfDisprover:
    """
    The Self-Disprover (SD) engine.
    Maintains 0% confidence, challenges all validations, and tests V's predictions to build meta-confidence.
    """
    def __init__(self):
        self.meta_confidence = 0.5  # Evolving calibration
        self.audit_log: List[str] = []

    def challenge(self, claim: Claim, kb: KnowledgeBase, verifier: Verifier) -> Tuple[bool, str]:
        """
        Challenges a claim validated by V by asserting its negation and testing the system response.
        If asserting the negation triggers a system contradiction, V was correct to affirm it.
        """
        negated = negate_statement(claim.statement)
        self.audit_log.append(f"SD-CHALLENGE: Negating '{claim.statement}' -> '{negated}'")

        # Temporarily force negate_claim into KB
        test_kb = KnowledgeBase()
        test_kb.claims = kb.claims.copy()
        test_kb.rules = kb.rules.copy()
        
        # Insert the negation
        test_kb.add_claim(Claim(negated, "SD-Torsion", "Adversarial Injection", [], 1.0))
        
        # Run pathology check
        if verifier.phi_operator(test_kb, claim.statement) == 1:
            # Inconsistency triggered! The negation cannot coexist with the system axioms.
            # This means V was correct, and SD's attempt to disprove was logically rejected.
            # SD learns that V's prediction that SD is wrong was correct, which calibrates SD's meta-confidence.
            self.meta_confidence = min(1.0, self.meta_confidence + 0.05)
            return True, f"SD-RESOLUTION: Negation of '{claim.statement}' triggers system contradiction. Claim is robust."
        else:
            # The system quietly accepted the negation without contradiction!
            # This indicates the claim is independent of the axioms (Gödelian space).
            self.meta_confidence = max(0.0, self.meta_confidence - 0.05)
            return False, f"SD-RESOLUTION: Negation of '{claim.statement}' is consistent with axioms. Claim is vulnerable."


if __name__ == "__main__":
    print("================================================================================")
    print("                 PROVER-VERIFIER SYSTEM COMPLIANCE ENGINE                       ")
    print("================================================================================")

    # 1. Initialize core infrastructure
    corpus = ReferenceCorpus()
    kb = KnowledgeBase()
    prover = Prover()
    verifier = Verifier(corpus, energy_limit=250.0)
    sd = SelfDisprover()

    # 2. Add baseline rules of inference
    # Rule 1: Large Vocabulary + Low hbar => Fine-Grained Distinctions
    kb.add_rule(["Large Vocabulary", "Low hbar"], "Fine-Grained Distinctions")
    # Rule 2: High mass => High resistance to change
    kb.add_rule(["High mass"], "High Semantic Inertia")

    print("\n--- Phase 1: Proposing and Verifying Axiomatic Claims (P0) ---")
    
    # Proposal A: True claim with valid source and quote
    claim_a = prover.propose_claim(
        statement="Large Vocabulary",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="A smaller hbar implies a finer-grained semantic space, where the LLM can make subtle distinctions in meaning. This could correspond to a larger and more evenly distributed vocabulary",
        derivation=[],
        confidence=0.95
    )
    
    success, msg = verifier.verify_claim(claim_a, kb)
    print(f"Verifying Claim A: {claim_a}")
    print(f"Result: {msg}")
    if success:
        kb.add_claim(claim_a)

    # Proposal B: Lying claim (hallucinated quote)
    claim_b = prover.propose_claim(
        statement="Low hbar",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="Hbar is secretly equal to forty-two.", # Lying quote
        derivation=[],
        confidence=0.99
    )
    
    success, msg = verifier.verify_claim(claim_b, kb)
    print(f"\nVerifying Claim B: {claim_b}")
    print(f"Result: {msg}")
    if success:
        kb.add_claim(claim_b)
    else:
        print("-> Verifier successfully blocked the hallucinated quote!")

    # Proposal C: True claim to complete the derivation premises
    claim_c = prover.propose_claim(
        statement="Low hbar",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="We interpret hbar as a measure of semantic granularity. A smaller hbar implies a finer-grained semantic space",
        derivation=[],
        confidence=0.90
    )
    success, msg = verifier.verify_claim(claim_c, kb)
    print(f"\nVerifying and adding Claim C: {claim_c}")
    print(f"Result: {msg}")
    if success:
        kb.add_claim(claim_c)

    print("\n--- Phase 2: Evaluating Derivation Chains ---")
    print(f"Is 'Fine-Grained Distinctions' provable before adding derivative claim? {kb.is_provable('Fine-Grained Distinctions')}")

    # Propose derivative claim (P1)
    claim_d = prover.propose_claim(
        statement="Fine-Grained Distinctions",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="the LLM is capable of resolving fine-grained semantic differences",
        derivation=["Large Vocabulary", "Low hbar"],
        confidence=0.88,
        level=1
    )
    success, msg = verifier.verify_claim(claim_d, kb)
    print(f"Verifying derivative Claim D: {claim_d}")
    print(f"Result: {msg}")
    if success:
        kb.add_claim(claim_d)

    print(f"Is 'Fine-Grained Distinctions' provable after adding verified derivative claim? {kb.is_provable('Fine-Grained Distinctions')}")

    print("\n--- Phase 3: Adversarial Challenge via Self-Disprover ---")
    success_sd, res_sd = sd.challenge(claim_a, kb, verifier)
    print(res_sd)
    print(f"SD Meta-Confidence: {sd.meta_confidence:.2f}")

    print("\n--- Phase 4: Energy Budget Test ---")
    try:
        print("Simulating high-energy recursion chain...")
        for i in range(100):
            verifier.consume_energy(4.0)
    except RuntimeError as e:
        print(f"Caught Expected Exception: {e}")
    
    print("================================================================================")
