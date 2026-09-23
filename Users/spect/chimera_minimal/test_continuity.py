import sys
import os
from runtime import ChimeraRuntime
from memory import WriteLosslessMemory

# Ensure we can import from the current directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_continuity():
    print("--- Testing WRITE_LOSSLESS Continuity ---\n")
    
    # 1. Initial Run
    print("Cycle 1: Initializing first interaction...")
    runtime1 = ChimeraRuntime()
    # Ensure memory is clean for the test
    runtime1.memory.clear()
    
    res1 = runtime1.execute_cycle(
        user_input="Initialize project 'Funny Walk'.",
        intent="BUILD",
        stakes=0.5
    )
    print(f"Cycle 1 Response: {res1['response']}")
    print(f"PION Timestamp: {runtime1.current_pion.timestamp}\n")

    # 2. Simulate Runtime Restart
    print("Simulating Runtime Restart (Creating new ChimeraRuntime instance)...\n")
    runtime2 = ChimeraRuntime()
    
    # 3. Second Run - Should trigger [CONTINUITY] restore
    print("Cycle 2: Second interaction (should recall previous state)...")
    res2 = runtime2.execute_cycle(
        user_input="Add a sync license to 'Funny Walk'.",
        intent="BUILD",
        stakes=0.9
    )
    print(f"Cycle 2 Response: {res2['response']}")
    
    # Verify history length incremented
    history_len = len(runtime2.memory.recall_all())
    print(f"Total State Ledger Length: {history_len}")
    
    if history_len == 2:
        print("\nSUCCESS: Continuity Verified. State persisted across runtime boundaries.")
    else:
        print(f"\nFAILURE: Continuity Broken. Expected length 2, got {history_len}")

if __name__ == "__main__":
    test_continuity()
