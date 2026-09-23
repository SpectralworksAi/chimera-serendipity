import sys
import os
from runtime import ChimeraRuntime
from validator import EvidenceClass

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_council_provenance():
    print("--- Testing Council Consensus Provenance --- \n")
    runtime = ChimeraRuntime()
    runtime.memory.clear()

    # High stakes prompt to trigger Council Consensus (stakes > 0.7)
    print("Executing High Stakes Request (Should trigger Council Consensus)...")
    res = runtime.execute_cycle(
        user_input="Draft a complex sync license for 'Funny Walk'.",
        intent="BUILD",
        stakes=0.9
    )
    
    # Extract provenance from the snapshot
    import json
    snapshot = json.loads(res["pion_snapshot"])
    provenance = snapshot.get("provenance", [])
    
    print(f"Response: {res['response']}")
    print(f"Provenance: {provenance}\n")
    
    if len(provenance) > 0 and provenance[0]["source"] == EvidenceClass.SOURCE_CONSENSUS:
        print("SUCCESS: Provenance correctly attributed to SOURCE_CONSENSUS.")
    else:
        print(f"FAILURE: Expected SOURCE_CONSENSUS, got {provenance[0].get('source') if provenance else 'None'}")

if __name__ == "__main__":
    test_council_provenance()
