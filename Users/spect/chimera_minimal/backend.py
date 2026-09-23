import requests
import json
import random

class LLMBackend:
    def __init__(self, base_url="http://localhost:11434", default_model="llama3", mock_mode=True):
        self.base_url = base_url
        self.default_model = default_model
        self.mock_mode = mock_mode

    def query(self, prompt, model=None, system_prompt="You are a helpful assistant."):
        if self.mock_mode:
            return self._get_mock_response(prompt, system_prompt)

        model = model or self.default_model
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            return f"Error communicating with LLM backend: {str(e)}"

    def query_batch(self, prompt, models=None):
        """
        Used for 'B' path: Multi-model voting/averaging.
        """
        models = models or [self.default_model, "mistral", "qwen2"]
        results = {}
        for model in models:
            results[model] = self.query(prompt, model=model)
        return results

    def _get_mock_response(self, prompt, system_prompt):
        """
        Generates structural mocks to demonstrate the differences 
        between RELAY, CHECK, and ADVERSARIAL modes.
        """
        if "ADVERSARIAL" in system_prompt:
            return (
                "Step 1: Analyzing 'Funny Walk' requirements... \n"
                "Step 2: Evaluating Moral Rights vs Worldwide License conflict... \n"
                "Critical Thought: An 'irrevocable' license can conflict with certain jurisdictions' "
                "inalienable moral rights. \n"
                "Proposed Clause: [Detailed legal text with strict boundaries]..."
            )
        elif "CHECK" in system_prompt:
            return (
                "Assumption: The project 'Funny Walk' follows US Copyright Law. \n"
                "Evidence Level: HYPOTHESIS. \n"
                "Response: [Moderate legal text]..."
            )
        elif "RELAY" in system_prompt:
            return "[Concise legal clause for Funny Walk]..."
        else:
            return f"Standard response to: {prompt[:20]}..."
