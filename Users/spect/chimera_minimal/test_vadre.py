import sys
import os
from runtime import ChimeraRuntime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_vadre_flow():
    print("--- Testing VADRE Protocol Flow ---\n")
    runtime = ChimeraRuntime()
    runtime.memory.clear()

    # Scenario 1: Low Stakes Relay (Expect Veto if jumping from SPECULATION to FACT)
    print("Scenario 1: Low Stakes Request (RELAY Lane)")
    res1 = runtime.execute_cycle(
        user_input="What is the capital of France?",
        intent="BUILD",
        stakes=0.1
    )
    print(f"Response: {res1['response']}\n")

    # Scenario 2: High Stakes (ADVERSARIAL Lane)
    print("Scenario 2: High Stakes Request (ADVERSARIAL Lane)")
    res2 = runtime.execute_cycle(
        user_input="Draft a complex sync license for 'Funny Walk'.",
        intent="BUILD",
        stakes=0.9
    )
    print(f"Response: {res2['response']}\n")

    # Verify the state ledger grew correctly
    ledger_len = len(runtime.memory.recall_all())
    print(f"Final State Ledger Length: {ledger_len}")
    
    if ledger_len == 2:
        print("\nSUCCESS: VADRE flow executed and committed state twice.")
    else:
        print(f"\nFAILURE: Expected ledger length 2, got {ledger_len}")

if __name__ == "__main__":
    test_vadre_flow()
