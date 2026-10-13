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
    Obeys the strict 'Proof Obligation' constraint of the Prover-Validator-Verifier-SD architecture.
    """
    def __init__(self, statement: str, source: str, quote: str, derivation: List[str], 
                 confidence: float, level: int = 0, signature: Optional[str] = None):
        self.id = uuid.uuid4()
        self.statement = statement
        self.source = source
        self.quote = quote
        self.derivation = derivation  # Premises required to derive this claim
        self.confidence = max(0.0, min(1.0, confidence))
        self.level = level  # Stratification level (P0, P1, P2...)
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
        """Checks if the exact quote is contained within the verified passages."""
        if source not in self.database:
            return False
        
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
        self.rules: List[Tuple[List[str], str]] = []

    def add_claim(self, claim: Claim) -> None:
        self.claims[claim.statement] = claim

    def remove_claim(self, statement: str) -> None:
        if statement in self.claims:
            del self.claims[statement]

    def add_rule(self, premises: List[str], conclusion: str) -> None:
        self.rules.append((premises, conclusion))

    def is_provable(self, statement: str, visited: Optional[Set[str]] = None) -> bool:
        if visited is None:
            visited = set()

        if statement in visited:
            return False
        visited.add(statement)

        if statement in self.claims:
            return True

        for premises, conclusion in self.rules:
            if conclusion == statement:
                if all(self.is_provable(premise, visited.copy()) for premise in premises):
                    return True
        return False


class Proposer:
    """
    Agent 1: The Proposer (Generator).
    Assembles candidate claims and derivation paths.
    """
    def __init__(self, name: str = "Proposer-Core"):
        self.name = name

    def propose_claim(self, statement: str, source: str, quote: str, 
                      derivation: List[str], confidence: float, level: int = 0) -> Claim:
        return Claim(
            statement=statement,
            source=source,
            quote=quote,
            derivation=derivation,
            confidence=confidence,
            level=level
        )


class Validator:
    """
    Agent 2: The Validator (V).
    Holds local subjective prior beliefs (initialized with V_0 = 0.5 default prior).
    Affirms propositions locally, stacks cases, and adjusts subjective faith under challenge.
    Unlike the Verifier, Validator represents the subjective hypothesis state.
    """
    def __init__(self, name: str = "Validator-Prior", default_prior: float = 0.5):
        self.name = name
        self.default_prior = default_prior
        self.priors: Dict[str, float] = {}
        self.case_stack: List[str] = []

    def get_prior(self, statement: str) -> float:
        return self.priors.get(statement, self.default_prior)

    def set_prior(self, statement: str, val: float) -> None:
        self.priors[statement] = max(0.0, min(1.0, val))

    def evaluate_contradiction(self, stmt_a: str, stmt_b: str) -> str:
        """
        When faced with contradiction (A vs NOT: A), Validator cannot validate both.
        It must choose a local prior or favor one based on case-stacking.
        """
        prior_a = self.get_prior(stmt_a)
        prior_b = self.get_prior(stmt_b)

        if prior_a >= prior_b:
            self.case_stack.append(stmt_a)
            return stmt_a
        else:
            self.case_stack.append(stmt_b)
            return stmt_b

    def update_on_failure(self, statement: str, penalty: float = 0.1) -> float:
        """Updates Validator prior downward when a claim fails structural verification."""
        curr = self.get_prior(statement)
        updated = max(0.0, curr - penalty)
        self.priors[statement] = updated
        return updated


class Verifier:
    """
    Agent 3: The Verifier (Objective Proof Auditor).
    Completely neutral, non-subjective auditor.
    Checks explicit proof obligations:
    1. External Anchor Check (Corpus exact match)
    2. Derivation Coherence Check
    3. Phi-Pathology Audit (Gödel independence or contradiction)
    4. Non-Negative Redundancy (NNR) Policy
    """
    def __init__(self, corpus: ReferenceCorpus, energy_limit: float = 250.0):
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
            1: Pathology detected (Gödel independence or contradiction)
            0: Consistent/Decidable (clean proof or clean refutation)
        """
        self.consume_energy(2.0)
        prov_a = kb.is_provable(statement)
        prov_not_a = kb.is_provable(negate_statement(statement))

        if prov_a == prov_not_a:
            return 1  # Pathology!
        return 0

    def verify_claim(self, claim: Claim, kb: KnowledgeBase) -> Tuple[bool, str]:
        """Performs a multi-stage objective audit on a proposed claim."""
        self.consume_energy(5.0)

        # 1. External Anchor Check
        if not self.corpus.verify_quote(claim.source, claim.quote):
            return False, f"VERIFIER-AUDIT-FAIL: Hallucinated quote or invalid source anchor in '{claim.source}'."

        # 2. Derivation Coherence Check
        for premise in claim.derivation:
            self.consume_energy(1.0)
            if not kb.is_provable(premise):
                return False, f"VERIFIER-AUDIT-FAIL: Derivation path broken. Premise '{premise}' is unprovable."

        # 3. Phi-Pathology Protection
        temp_kb = KnowledgeBase()
        temp_kb.claims = kb.claims.copy()
        temp_kb.rules = kb.rules.copy()
        temp_kb.add_claim(claim)

        if self.phi_operator(temp_kb, claim.statement) == 1:
            if temp_kb.is_provable(claim.statement) and temp_kb.is_provable(negate_statement(claim.statement)):
                return False, f"VERIFIER-AUDIT-FAIL: Adding '{claim.statement}' triggers absolute contradiction."
            else:
                return False, f"VERIFIER-AUDIT-FAIL: Claim '{claim.statement}' lies in Gödelian Independence space."

        # 4. Non-Negative Redundancy (NNR) Check
        if kb.is_provable(claim.statement):
            existing_claim = kb.claims.get(claim.statement)
            if existing_claim and existing_claim.confidence >= claim.confidence:
                return False, "VERIFIER-AUDIT-FAIL: Rejected under NNR policy. Claim is redundant."

        return True, "VERIFIER-AUDIT-SUCCESS: Claim satisfies all structural proof obligations."


class SelfDisprover:
    """
    Agent 4: The Self-Disprover (SD).
    Operates with 0% initial confidence (SD_0 = 0.0).
    Applies negation indiscriminately to challenge Validator's assertions.
    Builds second-order meta-confidence from Validator's predictable mis-calibrations,
    asymptotic to the 72.9% Lacunon Ceiling.
    """
    def __init__(self):
        self.meta_confidence: float = 0.0  # SD_0 = 0.0
        self.audit_log: List[str] = []

    def challenge(self, claim: Claim, validator: Validator, kb: KnowledgeBase, verifier: Verifier) -> Tuple[bool, str]:
        """
        Challenges a claim affirmed by Validator (V) by asserting its negation.
        Uses Verifier's objective phi-operator to test the system's reaction.
        """
        negated = negate_statement(claim.statement)
        self.audit_log.append(f"SD-CHALLENGE: Negating '{claim.statement}' -> '{negated}'")

        test_kb = KnowledgeBase()
        test_kb.claims = kb.claims.copy()
        test_kb.rules = kb.rules.copy()
        test_kb.add_claim(Claim(negated, "SD-Torsion", "Adversarial Injection", [], 1.0))

        # Check if the adversarial injection causes a phi-pathology
        if verifier.phi_operator(test_kb, claim.statement) == 1:
            # Assertion of negation triggers contradiction -> V's affirmation was valid.
            # SD learns that V's prediction that SD is wrong was correct!
            # Second-order calibration update
            delta = 0.05 * (0.729 - self.meta_confidence)  # Asymptotic toward 72.9% Lacunon ceiling
            self.meta_confidence += delta
            return True, f"SD-RESOLUTION: Negation of '{claim.statement}' triggers contradiction. V was correct. SD meta-conf -> {self.meta_confidence:.4f}"
        else:
            # System quietly accepts negation -> Claim lies in independent/vulnerable space.
            # V was over-confident! SD updates V's prior downward and adjusts calibration.
            validator.update_on_failure(claim.statement, penalty=0.15)
            self.meta_confidence = max(0.0, self.meta_confidence - 0.02)
            return False, f"SD-RESOLUTION: Negation of '{claim.statement}' is consistent. Claim is vulnerable. V prior penalized."


if __name__ == "__main__":
    print("================================================================================")
    print("      DECOUPLED FOUR-AGENT RING ENGINE: PROPOSER-VALIDATOR-VERIFIER-SD          ")
    print("================================================================================")

    # 1. Initialize core agents
    corpus = ReferenceCorpus()
    kb = KnowledgeBase()
    proposer = Proposer("Proposer-Core")
    validator = Validator("Validator-Priors", default_prior=0.5)  # V_0 = 0.5
    verifier = Verifier(corpus, energy_limit=300.0)             # Objective Verifier
    sd = SelfDisprover()                                         # SD_0 = 0.0

    print(f"\n[Agent Initial States]")
    print(f"  Validator Default Prior V_0 : {validator.default_prior:.2f}")
    print(f"  Self-Disprover Meta-Conf SD_0: {sd.meta_confidence:.2f}")
    print(f"  Verifier Energy Budget      : {verifier.energy_limit:.1f}")

    # 2. Add inference rules
    kb.add_rule(["Large Vocabulary", "Low hbar"], "Fine-Grained Distinctions")
    kb.add_rule(["High mass"], "High Semantic Inertia")

    print("\n--- Phase 1: Proposing & Validating Axiomatic Claims (P0) ---")

    # Claim A
    claim_a = proposer.propose_claim(
        statement="Large Vocabulary",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="A smaller hbar implies a finer-grained semantic space, where the LLM can make subtle distinctions in meaning. This could correspond to a larger and more evenly distributed vocabulary",
        derivation=[],
        confidence=0.95
    )
    
    # Validator sets local prior belief
    validator.set_prior(claim_a.statement, 0.95)
    print(f"Proposer -> Claim A: {claim_a}")
    print(f"Validator -> Assigned Subjective Prior V('{claim_a.statement}') = {validator.get_prior(claim_a.statement):.2f}")

    # Verifier runs objective audit
    success, v_msg = verifier.verify_claim(claim_a, kb)
    print(f"Verifier  -> Audit Result: {v_msg}")
    if success:
        kb.add_claim(claim_a)

    # Claim B (Hallucinated quote)
    claim_b = proposer.propose_claim(
        statement="Low hbar",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="Hbar is secretly equal to forty-two.", # Fake quote
        derivation=[],
        confidence=0.99
    )
    validator.set_prior(claim_b.statement, 0.99)
    print(f"\nProposer -> Claim B: {claim_b}")
    print(f"Validator -> Assigned Subjective Prior V('{claim_b.statement}') = {validator.get_prior(claim_b.statement):.2f}")

    success_b, v_msg_b = verifier.verify_claim(claim_b, kb)
    print(f"Verifier  -> Audit Result: {v_msg_b}")
    if not success_b:
        validator.update_on_failure(claim_b.statement, penalty=0.5)
        print(f"Validator -> Updated Subjective Prior V('{claim_b.statement}') after failure = {validator.get_prior(claim_b.statement):.2f}")

    # Claim C (Valid claim for Low hbar)
    claim_c = proposer.propose_claim(
        statement="Low hbar",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="We interpret hbar as a measure of semantic granularity. A smaller hbar implies a finer-grained semantic space",
        derivation=[],
        confidence=0.90
    )
    validator.set_prior(claim_c.statement, 0.90)
    success_c, v_msg_c = verifier.verify_claim(claim_c, kb)
    if success_c:
        kb.add_claim(claim_c)
        print(f"\nVerifier -> Claim C Verified & Ingested into Knowledge Base.")

    print("\n--- Phase 2: Derivation Chain Evaluation ---")
    claim_d = proposer.propose_claim(
        statement="Fine-Grained Distinctions",
        source="1 Modeling Semantic Spaces with Quantum Principles.pdf",
        quote="the LLM is capable of resolving fine-grained semantic differences",
        derivation=["Large Vocabulary", "Low hbar"],
        confidence=0.88,
        level=1
    )
    success_d, v_msg_d = verifier.verify_claim(claim_d, kb)
    print(f"Derivative Claim D: {claim_d}")
    print(f"Verifier Audit: {v_msg_d}")
    if success_d:
        kb.add_claim(claim_d)

    print("\n--- Phase 3: Adversarial Challenge via Self-Disprover (SD_0 = 0.0) ---")
    print(f"Initial SD Meta-Confidence: {sd.meta_confidence:.4f}")
    
    # SD challenges Claim A
    sd_success, sd_msg = sd.challenge(claim_a, validator, kb, verifier)
    print(f"SD Challenge 1: {sd_msg}")
    print(f"Post-Challenge SD Meta-Confidence: {sd.meta_confidence:.4f}")

    print("\n--- Phase 4: Contradiction Handling by Validator ---")
    stmt_choice = validator.evaluate_contradiction("Large Vocabulary", "NOT: Large Vocabulary")
    print(f"Validator Contradiction Resolution (favoring prior): Selected '{stmt_choice}'")

    print("\n================================================================================")
