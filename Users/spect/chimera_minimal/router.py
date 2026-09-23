class Router:
    def select_lane(self, intent, stakes):
        """
        Basic routing based on AI-IQM principles.
        """
        if stakes > 0.8 or intent == "ADVERSARIAL":
            return "ADVERSARIAL" # High stakes, reason out loud
        elif stakes < 0.3:
            return "RELAY" # Low stakes, direct answer
        else:
            return "CHECK" # Moderate stakes, state assumptions
