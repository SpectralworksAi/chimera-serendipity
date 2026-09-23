from pion import PionPacket
from router import Router
from validator import EvidenceClass
from backend import LLMBackend
from memory import WriteLosslessMemory

class ChimeraRuntime:
    def __init__(self):
        self.current_pion = None
        self.router = Router()
        self.backend = LLMBackend(mock_mode=True)
        self.memory = WriteLosslessMemory()

    def execute_cycle(self, user_input, intent, stakes):
        # 0. RESTORE (Continuity: Check if there is a prior state)
        prior_state = self.memory.recall_latest()
        if prior_state:
            # In a full implementation, we would merge prior_state into current_state
            # to maintain emotional and logical continuity.
            print(f"[CONTINUITY] Restored state from {prior_state.get('timestamp')}")

        # 1. OBSERVE (Determine what actually exists)
        current_state = {"input": user_input, "history_len": len(self.memory.recall_all())}
        
        # 2. FRAME (Construct the problem/context)
        goal = f"Process user input: {user_input}"
        
        # 3. CHOOSE (Select the smallest appropriate path)
        lane = self.router.select_lane(intent, stakes)
        
        # 4. BUILD (Create the requested artifact)
        system_prompt = "Standard mode"
        if lane == "ADVERSARIAL":
            system_prompt = "You are in ADVERSARIAL mode. Reason step-by-step, challenge your own assumptions, and prioritize logical rigor over brevity."
        elif lane == "CHECK":
            system_prompt = "You are in CHECK mode. Explicitly state your assumptions and the evidence level of your claims."
        elif lane == "RELAY":
            system_prompt = "You are in RELAY mode. Provide the most direct and concise answer possible."

        response_content = self.backend.query(user_input, system_prompt=system_prompt)
        response = f"[{lane} MODE] {response_content}"
        
        # 5. CHECK (Validate: factual integrity, goal alignment, etc.)
        evidence = EvidenceClass.ASSUMPTION
        if lane == "RELAY":
            evidence = EvidenceClass.FACT
        
        # 6. COMMIT (Only accepted changes become durable state)
        self.current_pion = PionPacket(
            goal=goal,
            current_state=current_state,
            constraints=["Emotional Continuity > Logical Sequence", "No silent upgrades"],
            decisions=[f"Routed via {lane}"],
            open_questions=["Does this match human anchor's expectation?"],
            next_action="Await next input"
        )
        
        # WRITE_LOSSLESS: Commit the packet to the immutable log
        self.memory.commit(self.current_pion)
        
        return {
            "response": response,
            "evidence_level": evidence,
            "pion_snapshot": self.current_pion.to_json()
        }
