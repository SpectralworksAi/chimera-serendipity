from pion import PionPacket
from router import Router
from validator import EvidenceClass
from backend import LLMBackend
from memory import WriteLosslessMemory
from guardian import Guardian
from council import Council

class ChimeraRuntime:
    def __init__(self):
        self.current_pion = None
        self.router = Router()
        self.backend = LLMBackend(mock_mode=True)
        self.memory = WriteLosslessMemory()
        self.guardian = Guardian()
        self.council = Council(self.backend)

    def execute_cycle(self, user_input, intent, stakes):
        """
        The VADRE Loop: Verify -> Analyze -> Decide -> Review -> Execute
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
        print("[D] Deciding lane...")
        lane, system_prompt = self._decide(analysis_report, intent, stakes)
        print(f"    Lane: {lane}")

        # 4. REVIEW (R)
        print("[R] Reviewing proposal...")
        
        # Use Council Consensus for high-stakes or adversarial lanes
        if lane == "ADVERSARIAL" or stakes > 0.7:
            print("    Using Council Consensus...")
            consensus_result = self.council.debate(verified_input, system_prompt)
            response_content = consensus_result["final_response"]
            proposed_source = EvidenceClass.SOURCE_CONSENSUS
        else:
            print("    Using Direct Backend...")
            response_content = self.backend.query(verified_input, system_prompt=system_prompt)
            proposed_source = EvidenceClass.SOURCE_LLM

        # Determine proposed evidence level based on lane
        proposed_evidence = EvidenceClass.ASSUMPTION
        
        if lane == "RELAY":
            proposed_evidence = EvidenceClass.FACT
            # RELAY mode normally requires a known FACT from state,
            # but here it's coming from LLM (which should actually be lower)
        elif lane == "ADVERSARIAL":
            proposed_evidence = EvidenceClass.HYPOTHESIS
        # Restore current evidence for comparison
        prior_state = self.memory.recall_latest()
        current_evidence = EvidenceClass.SPECULATION
        if prior_state:
            current_evidence = EvidenceClass.ASSUMPTION

        is_permitted, reason = self.guardian.evaluate_proposal(
            current_evidence=current_evidence,
            proposed_evidence=proposed_evidence,
            proposal_content=response_content
        )

        if not is_permitted:
            print(f"    [VETO] {reason}")
            proposed_evidence = current_evidence
            response = f"[VETOED] [{lane} MODE] {response_content}\n(Guardian Note: {reason})"
        else:
            print(f"    [APPROVED] {reason}")
            response = f"[{lane} MODE] {response_content}"

        # Create provenance claim for this cycle
        provenance_entry = {
            "claim": response_content[:50] + "...",
            "level": proposed_evidence,
            "source": proposed_source
        }

        # 5. EXECUTE (E)
        print("[E] Executing commit...")
        self.current_pion = PionPacket(
            goal=f"Process: {verified_input}",
            current_state={"input": verified_input, "history_len": len(self.memory.recall_all())},
            constraints=["Emotional Continuity > Logical Sequence", "No silent upgrades"],
            decisions=[f"Lane: {lane}", f"Evidence: {proposed_evidence}"],
            open_questions=["Does this match human anchor's expectation?"],
            next_action="Await next input",
            provenance=[provenance_entry]
        )
        self.memory.commit(self.current_pion)
        print(f"--- VADRE Loop Complete ---\n")
        return {
            "response": response,
            "evidence_level": proposed_evidence,
            "pion_snapshot": self.current_pion.to_json()
        }

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
