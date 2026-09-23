import sys
import os
from runtime import ChimeraRuntime
from validator import EvidenceClass

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_provenance():
    print("--- Testing Evidence Provenance --- \n")
    runtime = ChimeraRuntime()
    runtime.memory.clear()

    # Cycle 1: High stakes request
    print("Cycle 1: High stakes request...")
    res1 = runtime.execute_cycle(
        user_input="Draft a clause for the Funny Walk sync license.",
        intent="BUILD",
        stakes=0.9
    )
    
    # Extract provenance from the snapshot
    snapshot = json.loads(res1["pion_snapshot"])
    provenance = snapshot.get("provenance", [])
    
    print(f"Response: {res1['response']}")
    print(f"Provenance: {provenance}\n")
    
    if len(provenance) > 0 and provenance[0]["source"] == EvidenceClass.SOURCE_LLM:
        print("SUCCESS: Provenance correctly attributed to SOURCE_LLM.")
    else:
        print("FAILURE: Provenance missing or incorrect.")

if __name__ == "__main__":
    import json
    test_provenance()
