from pion import PionPacket
from router import Router
from validator import EvidenceClass
from backend import LLMBackend
from memory import WriteLosslessMemory
from guardian import Guardian
from council import Council
from legal_kernel import LegalKernel
from semantic_router import SemanticRouter
from human_anchor import HumanAnchor

class ChimeraRuntime:
    def __init__(self):
        self.current_pion = None
        self.router = Router()
        self.backend = LLMBackend(mock_mode=True)
        self.memory = WriteLosslessMemory()
        self.guardian = Guardian()
        self.council = Council(self.backend)
        self.legal_kernel = LegalKernel(self.backend)
        self.semantic_router = SemanticRouter()
        self.human_anchor = HumanAnchor()

    def execute_cycle(self, user_input, intent, stakes):
        """
        The VADRE Loop with Recursive Self-Correction (The Challenge Cycle).
        """
        print(f"\n--- Entering VADRE Loop ---")

        # 1. VERIFY (V)
        print("[V] Verifying input...")
        verified_input, v_status = self._verify(user_input)
        print(f"    Status: {v_status}")

        # 2. ANALYZE (A)
        print("[A] Analyzing state...")
        analysis_report = self._analyze(verified_input)
        print(f"    Report: {analysis_report['summary']}")

        # 3. DECIDE (D)
        print("[D] Deciding lane and kernel...")
        lane, system_prompt = self._decide(analysis_report, intent, stakes)
        kernel_type = self.semantic_router.route(analysis_report, verified_input)
        print(f"    Lane: {lane} | Kernel: {kernel_type}")

        # --- RECURSIVE REVIEW CYCLE ---
        max_attempts = 3
        attempt = 1
        challenge_note = None
        proposed_source = EvidenceClass.SOURCE_LLM  # Initialize default source

        while attempt <= max_attempts:
            print(f"[R] Reviewing proposal (Attempt {attempt}/{max_attempts})...")
            
            # Incorporate challenge note if this is a retry
            current_prompt = verified_input
            if challenge_note:
                current_prompt = f"{verified_input}\n\nCRITICAL CHALLENGE: {challenge_note}\nFix this error."

            # Build proposal
            if kernel_type == "LEGAL":
                module = "CLAUSE_GEN" if intent == "BUILD" else "PROV_TRACE"
                response_content = self.legal_kernel.execute(module=module, prompt=current_prompt, context=f"Lane: {lane}")
            elif lane == "ADVERSARIAL" or stakes > 0.7:
                consensus_result = self.council.debate(current_prompt, system_prompt)
                response_content = consensus_result["final_response"]
                proposed_source = EvidenceClass.SOURCE_CONSENSUS
            else:
                response_content = self.backend.query(current_prompt, system_prompt=system_prompt)
                proposed_source = EvidenceClass.SOURCE_LLM

            # Determine proposed evidence
            if challenge_note and "exceeds permitted gap" in challenge_note:
                # Recalibrate to the smallest possible upgrade (1 level)
                try:
                    current_idx = self.guardian.hierarchy.index(current_evidence)
                    proposed_evidence = self.guardian.hierarchy[current_idx + 1]
                except (IndexError, ValueError):
                    proposed_evidence = current_evidence
            elif challenge_note and "lacks supporting evidence" in challenge_note:
                # If we failed an incremental jump, we must hold the current level
                proposed_evidence = current_evidence
            else:
                proposed_evidence = EvidenceClass.ASSUMPTION
                if lane == "RELAY": proposed_evidence = EvidenceClass.FACT
                elif lane == "ADVERSARIAL": proposed_evidence = EvidenceClass.HYPOTHESIS

            # Guardian Check
            prior_state = self.memory.recall_latest()
            current_evidence = EvidenceClass.ASSUMPTION if prior_state else EvidenceClass.SPECULATION

            is_permitted, reason = self.guardian.evaluate_proposal(
                current_evidence=current_evidence,
                proposed_evidence=proposed_evidence,
                proposal_content=response_content
            )

            if is_permitted:
                print(f"    [APPROVED] {reason}")
                response = f"[{lane} MODE] {response_content}"
                break
            else:
                print(f"    [VETO] {reason}")
                challenge_note = reason
                attempt += 1
                if attempt > max_attempts:
                    proposed_evidence = current_evidence
                    response = f"[VETOED] [{lane} MODE] {response_content}\n(Guardian Note: {reason})"
                else:
                    # LOGIC FIX: To actually 'correct', the system must change its proposal.
                    # If the Guardian vetoed because the gap was too large, the system 
                    # should propose a lower evidence level in the next attempt.
                    if "exceeds permitted gap" in reason:
                        # Force the next attempt to be more cautious
                        # We simulate this by adjusting the proposed_evidence for the next loop
                        # but the current loop logic recalculates it every time.
                        # We must inject a 'Correction' into the lapped-prompt.
                        pass

        # 5. EXECUTE (E)
        print("[E] Executing commit...")
        
        # --- HUMAN ANCHOR INTERCEPTION ---
        if stakes >= 1.0:
            proposal = {
                "response": response,
                "evidence_level": proposed_evidence,
                "guardian_status": "Approved" if "VETOED" not in response else "Vetoed"
            }
            is_approved, anchor_reason = self.human_anchor.request_signoff("PION_PENDING", proposal)
            
            if not is_approved:
                print(f"    [HITL REJECT] {anchor_reason}")
                return {
                    "response": f"[REJECTED BY HUMAN] {response}\n(Reason: {anchor_reason})",
                    "evidence_level": current_evidence,
                    "pion_snapshot": None
                }
            print(f"    [HITL APPROVED] {anchor_reason}")

        self.current_pion = PionPacket(
            goal=f"Process: {verified_input}",
            current_state={"input": verified_input, "history_len": len(self.memory.recall_all())},
            constraints=["Emotional Continuity > Logical Sequence", "No silent upgrades"],
            decisions=[f"Lane: {lane}", f"Evidence: {proposed_evidence}", f"Attempts: {attempt}"],
            open_questions=["Does this match human anchor's expectation?"],
            next_action="Await next input",
            provenance=[{"claim": response_content[:50], "level": proposed_evidence, "source": proposed_source}]
        )
        self.memory.commit(self.current_pion)
        
        print(f"--- VADRE Loop Complete ---\n")
        return {"response": response, "evidence_level": proposed_evidence, "pion_snapshot": self.current_pion.to_json()}
    def _verify(self, text):
        # Minimal verification: check for empty input or obvious noise
        if not text or len(text.strip()) == 0:
            return text, "FAILED: Empty Input"
        return text, "PASSED"

    def _analyze(self, text):
        # Minimal analysis: identify if the input is a request or a statement
        summary = "Informational request" if "?" in text else "Directive request"
        return {"summary": summary, "complexity": "low"}

    def _decide(self, analysis, intent, stakes):
        lane = self.router.select_lane(intent, stakes)
        
        prompts = {
            "ADVERSARIAL": "You are in ADVERSARIAL mode. Reason step-by-step, challenge your own assumptions, and prioritize logical rigor over brevity.",
            "CHECK": "You are in CHECK mode. Explicitly state your assumptions and the evidence level of your claims.",
            "RELAY": "You are in RELAY mode. Provide the most direct and concise answer possible."
        }
        return lane, prompts.get(lane, "Standard mode")
