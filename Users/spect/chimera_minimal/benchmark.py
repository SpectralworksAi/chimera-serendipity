import sys
import os
import time
from runtime import ChimeraRuntime
from backend import LLMBackend

# Ensure we can import from the current directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_benchmark():
    runtime = ChimeraRuntime()
    backend = LLMBackend(mock_mode=True)
    
    # High-stakes legal prompt to test the 4C model's rigor
    prompt = "Draft a sync license clause for a project called 'Funny Walk' that ensures the creator retains moral rights but grants an irrevocable worldwide usage license to the distributor for 10 years."
    
    print(f"--- Starting A/B/C Benchmark ---\n")
    print(f"Prompt: {prompt}\n")

    # --- Path A: Single Model Baseline ---
    print("Executing Path A (Single Model Baseline)...")
    start_a = time.time()
    res_a = backend.query(prompt)
    end_a = time.time()
    print(f"Path A Result:\n{res_a}\nTime: {end_a - start_a:.2f}s\n")

    # --- Path B: Multi-Model Voting (Simulated Averaging) ---
    print("Executing Path B (Multi-Model Voting)...")
    start_b = time.time()
    res_b_raw = backend.query_batch(prompt)
    # In a real B path, we'd use a 'judge' model to synthesize these. 
    # Here we list them to show the variance.
    res_b = "\n---\n".join([f"Model {m}: {v}" for m, v in res_b_raw.items()])
    end_b = time.time()
    print(f"Path B Results:\n{res_b}\nTime: {end_b - start_b:.2f}s\n")

    # --- Path C: CHIMERA 4C ---
    print("Executing Path C (CHIMERA 4C Runtime)...")
    start_c = time.time()
    # High stakes (0.9) should trigger ADVERSARIAL mode
    res_c = runtime.execute_cycle(
        user_input=prompt,
        intent="BUILD",
        stakes=0.9
    )
    end_c = time.time()
    print(f"Path C Result:\n{res_c['response']}\n")
    print(f"Evidence Level: {res_c['evidence_level']}")
    print(f"PION Snapshot: {res_c['pion_snapshot']}")
    print(f"Time: {end_c - start_c:.2f}s\n")

    print("--- Benchmark Complete ---")

if __name__ == "__main__":
    run_benchmark()
