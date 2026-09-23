from validator import EvidenceClass

class Guardian:
    """
    The Guardian is the proactive gatekeeper of the CHIMERA state.
    Its primary role is to ensure that no state upgrade occurs without 
    explicit, verifiable evidence—preventing 'Silent Promotions'.
    """
    def __init__(self):
        # Define the strict hierarchy of evidence
        # Higher index = Higher certainty/authority
        self.hierarchy = [
            EvidenceClass.SPECULATION,
            EvidenceClass.PROPOSAL,
            EvidenceClass.HYPOTHESIS,
            EvidenceClass.ASSUMPTION,
            EvidenceClass.FACT
        ]

    def evaluate_proposal(self, current_evidence, proposed_evidence, proposal_content):
        """
        Evaluates whether a proposed evidence upgrade is permitted.
        Returns (is_permitted, reason)
        """
        if current_evidence == proposed_evidence:
            return True, "Evidence level maintained."

        try:
            current_idx = self.hierarchy.index(current_evidence)
            proposed_idx = self.hierarchy.index(proposed_evidence)
        except ValueError:
            return False, "Unknown evidence class provided."

        # Rule: Downgrades are always permitted (increased skepticism).
        if proposed_idx < current_idx:
            return True, "Evidence downgrade permitted (increased skepticism)."

        # Rule: Upgrades must be incremental.
        # A jump of more than 1 level is considered a 'Silent Promotion' 
        # and is strictly forbidden without an external validation trigger.
        promotion_gap = proposed_idx - current_idx
        if promotion_gap > 1:
            return False, f"Silent Promotion detected: Jump from {current_evidence} to {proposed_evidence} exceeds permitted gap."

        # For 1-level jumps, we check for validation markers in the content
        # In a full implementation, this would call a specialized validation agent.
        if self._has_validation_evidence(proposal_content):
            return True, "Incremental promotion validated by content analysis."
        else:
            return False, f"Incremental promotion from {current_evidence} to {proposed_evidence} lacks supporting evidence."

    def _has_validation_evidence(self, content):
        """
        Internal heuristic to check if the proposal contains 
        the necessary reasoning to justify an upgrade.
        """
        # Simple keyword check for the minimal reference implementation.
        # In the full version, this would be a separate LLM call.
        markers = ["verified", "confirmed", "evidence", "source", "cross-referenced"]
        return any(marker in content.lower() for marker in markers)
