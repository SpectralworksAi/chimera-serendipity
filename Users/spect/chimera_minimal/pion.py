import json
from datetime import datetime

class PionPacket:
    def __init__(self, goal, current_state, constraints, decisions, open_questions, next_action, provenance=None):
        self.goal = goal
        self.current_state = current_state
        self.constraints = constraints
        self.decisions = decisions
        self.open_questions = open_questions
        self.next_action = next_action
        # provenance should be a list of dicts: [{"claim": "...", "level": "FACT", "source": "SOURCE_USER"}]
        self.provenance = provenance or []
        self.timestamp = datetime.utcnow().isoformat()

    def to_json(self):
        return json.dumps(self.__dict__, indent=2)

    @classmethod
    def from_json(cls, data):
        parsed = json.loads(data)
        return cls(
            goal=parsed["goal"],
            current_state=parsed["current_state"],
            constraints=parsed["constraints"],
            decisions=parsed["decisions"],
            open_questions=parsed["open_questions"],
            next_action=parsed["next_action"],
            provenance=parsed.get("provenance", [])
        )
