from validator import EvidenceClass

class CouncilMember:
    """
    A CouncilMember represents a specialized agent role within the 13-Council.
    Each member has a specific perspective (e.g., Skeptic, Legalist, Creative).
    """
    def __init__(self, name, role, perspective):
        self.name = name
        self.role = role
        self.perspective = perspective

    def propose(self, prompt, system_prompt, backend):
        """
        Generates a proposal from the member's specific perspective.
        """
        # Combine the global system prompt with the member's specific perspective
        combined_prompt = f"{system_prompt}\n\nPerspective: {self.perspective}"
        return backend.query(prompt, system_prompt=combined_prompt)

class Council:
    """
    The 13-Council manages a group of specialized agents to achieve 
    consensus on a proposal.
    """
    def __init__(self, backend):
        self.backend = backend
        self.members = self._initialize_council()

    def _initialize_council(self):
        # For the Minimal Reference, we'll implement 3 core roles instead of 13
        return [
            CouncilMember("The Skeptic", "CRITIC", "Challenge every assumption. Find the flaws in the logic. Prioritize safety and risk."),
            CouncilMember("The Legalist", "COMPLIANCE", "Focus on strict adherence to constraints and legal precision. No ambiguity."),
            CouncilMember("The Synthesis", "INTEGRATOR", "Merge the best parts of the other views into a coherent, balanced final response.")
        ]

    def debate(self, prompt, system_prompt):
        """
        The Consensus Protocol:
        1. Members propose independently.
        2. The Integrator synthesizes the results.
        """
        proposals = {}
        
        # 1. Independent Proposals
        for member in self.members:
            if member.role != "INTEGRATOR":
                proposals[member.name] = member.propose(prompt, system_prompt, self.backend)
        
        # 2. Synthesis
        debate_context = "\n\n".join([f"{name}: {text}" for name, text in proposals.items()])
        synthesis_prompt = (
            f"You are The Synthesis. Review the following debate and provide the final, "
            f"most rigorous version of the response. Resolve contradictions and ensure all constraints are met.\n\n"
            f"Debate:\n{debate_context}\n\nOriginal Prompt: {prompt}"
        )
        
        final_response = self.backend.query(
            prompt=synthesis_prompt, 
            system_prompt="You are the final authority of the Council."
        )
        
        return {
            "final_response": final_response,
            "debate_log": proposals
        }
