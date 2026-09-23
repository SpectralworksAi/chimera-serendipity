class EvidenceClass:
    FACT = "FACT"
    ASSUMPTION = "ASSUMPTION"
    HYPOTHESIS = "HYPOTHESIS"
    PROPOSAL = "PROPOSAL"
    SPECULATION = "SPECULATION"

    # Provenance Sources
    SOURCE_USER = "SOURCE_USER"
    SOURCE_LLM = "SOURCE_LLM"
    SOURCE_EXTERNAL = "SOURCE_EXTERNAL"
    SOURCE_CONSENSUS = "SOURCE_CONSENSUS"

    @staticmethod
    def validate_promotion(current_class, target_class):
        # Rule: No silent upgrades. 
        # A SPECULATION cannot become a FACT without passing through intermediate states.
        if current_class == EvidenceClass.SPECULATION and target_class == EvidenceClass.FACT:
            raise ValueError("Invalid promotion: SPECULATION -> FACT requires intermediate validation.")
        return True
