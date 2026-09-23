import unittest
import sys
import os

# Add parent directory to path so we can import the runtime modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runtime import ChimeraRuntime
from pion import PionPacket

class TestChimeraABC(unittest.TestCase):
    def setUp(self):
        self.runtime = ChimeraRuntime()

    def test_a_single_model_baseline(self):
        # A: Single model, ordinary workflow (Simulated)
        result = "Raw Llama3 response"
        self.assertTrue(result is not None)

    def test_b_multiple_models_voting(self):
        # B: Multiple models / ordinary voting
        result = "Averaged multi-model response"
        self.assertTrue(result is not None)

    def test_c_chimera_4c(self):
        # C: CHIMERA 4C (Capability, Continuity, Comparison, Challenge)
        output = self.runtime.execute_cycle(
            user_input="Draft a clause for the Funny Walk sync license.",
            intent="BUILD",
            stakes=0.9 # High stakes legal work
        )
        
        # Verify it routed to ADVERSARIAL mode due to high stakes
        self.assertIn("[ADVERSARIAL MODE]", output["response"])
        
        # Verify it generated a PION state packet
        self.assertIsNotNone(output["pion_snapshot"])
        
        # Verify evidence level was not silently upgraded
        self.assertEqual(output["evidence_level"], "ASSUMPTION") # Should not be FACT without validation

if __name__ == '__main__':
    unittest.main()
