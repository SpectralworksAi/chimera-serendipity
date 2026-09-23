import asyncio
import httpx
import json
from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="CHIMERA Σ v5.52 - Governed Runtime")

# --- GOVERNANCE CONSTANTS ---
class EvidenceClass(IntEnum):
    SPECULATION = 1
    PROPOSAL = 2
    HYPOTHESIS = 3
    ASSUMPTION = 4
    FACT = 5

LENSES_CONFIG = {
    "logic": {"model": "llama3.1:8b", "temp": 0.7, "scope": "orchestration"},
    "synth": {"model": "mistral:7b", "temp": 0.7, "scope": "specialization"},
    "reason": {"model": "deepseek-r1:8b", "temp": 0.7, "scope": "identity"},
    "compact": {"model": "phi3:3.5", "temp": 0.7, "scope": "specialization"},
    "code": {"model": "qwen2.5:7b", "temp": 0.1, "scope": "LegalKernel"}, # DETERMINISM
    "critic": {"model": "gemma2:9b", "temp": 0.3, "scope": "orchestration"},
    "legacy": {"model": "mistral-nemo:12b", "temp": 0.7, "scope": "identity"},
    "lateral": {"model": "solar:10b", "temp": 0.9, "scope": "specialization"},
}

ANCHOR_REGISTRY = {
    "LEGAL": {"id": "user_counsel_01", "name": "Legal Counsel X", "expertise": ["contracts", "compliance", "liability"]},
    "RUNTIME": {"id": "user_eng_01", "name": "Engineer Y", "expertise": ["latency", "k8s", "vram_optimization"]},
    "STRATEGY": {"id": "user_arch_01", "name": "Architect Z", "expertise": ["trajectory", "cognitive_specialization"]},
    "IDENTITY": {"id": "user_phil_01", "name": "Philosopher W", "expertise": ["alignment", "continuity", "ethics"]},
}

OLLAMA_URL = "http://localhost:11434/api/generate"
LEDGER_FILE = "chimera_ledger.jsonl"
DECISION_STORE: Dict[str, Any] = {}

# --- MODELS ---
class DeliberationRequest(BaseModel):
    prompt: str
    stakes: float = 0.0
    decision_id: str
    anchor_bound: bool = False

class BindRequest(BaseModel):
    decision_id: str
    anchor_id: str
    rationale: str

# --- CORE SYSTEMS ---

async def log_to_ledger(event_type: str, payload: Dict[str, Any]):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        **payload
    }
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

async def resolve_capability_match(prompt: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resolver_prompt = (
            f"Analyze this request: '{prompt}'. "
            f"Categorize it into EXACTLY one of these domains: LEGAL, RUNTIME, STRATEGY, IDENTITY. "
            f"Return ONLY the word."
        )
        try:
            response = await client.post(
                OLLAMA_URL,
                json={"model": "llama3.1:8b", "prompt": resolver_prompt, "stream": False},
                timeout=30.0
            )
            domain = response.json().get("response", "").strip().upper()
            anchor = ANCHOR_REGISTRY.get(domain, ANCHOR_REGISTRY["STRATEGY"])
            return {
                "domain": domain,
                "anchor": anchor,
                "selection_rationale": f"Prompt matched to {domain} domain via Logic Lens."
            }
        except Exception as e:
            return {"domain": "UNKNOWN", "anchor": ANCHOR_REGISTRY["STRATEGY"], "selection_rationale": f"Error: {str(e)}"}

async def query_lens(client: httpx.AsyncClient, name: str, config: Dict, prompt: str, feedback: str = None):
    full_prompt = prompt
    if feedback:
        full_prompt = f"Original Prompt: {prompt}\\n\\nCRITIC FEEDBACK: {feedback}\\n\\nRefine your previous answer to address these gaps."

    gov_prompt = (
        f"{full_prompt}\\n\\n---\\n"
        f"You are the '{name}' lens. Respond in JSON: "
        f'{{\\"response\\": \\"analysis\\", \\"evidence\\": \\"FACT|ASSUMPTION|HYPOTHESIS|PROPOSAL|SPECULATION\\"}}'
    )
    try:
        resp = await client.post(
            OLLAMA_URL, 
            json={"model": config["model"], "prompt": gov_prompt, "stream": False, "options": {"temperature": config["temp"]}}, 
            timeout=60.0
        )
        data = resp.json().get("response", "")
        try:
            parsed = json.loads(data)
            return {name: {"text": parsed.get("response", data), "evidence": parsed.get("evidence", "SPECULATION"), "scope": config["scope"]}}
        except json.JSONDecodeError:
            return {name: {"text": data, "evidence": "SPECULATION", "scope": config["scope"]}}
    except Exception as e:
        return {name: {"text": f"Error: {str(e)}", "evidence": "SPECULATION", "scope": config["scope"]}}

async def run_vadre_cycle(client: httpx.AsyncClient, request: DeliberationRequest, iteration: int, current_perspectives: Dict = None):
    if iteration == 0:
        tasks = [query_lens(client, name, config, request.prompt) for name, config in LENSES_CONFIG.items()]
        results = await asyncio.gather(*tasks)
        perspectives = {k: v for res in results for k, v in res.items()}
    else:
        critic_prompt = f"Analyze these perspectives for contradictions or evidence gaps: {json.dumps(current_perspectives)}. Does this satisfy the prompt: '{request.prompt}'?"
        critic_resp = await client.post(OLLAMA_URL, json={"model": LENSES_CONFIG["critic"]["model"], "prompt": critic_prompt, "stream": False}, timeout=60.0)
        feedback = critic_resp.json().get("response", "")
        
        if "READY" in feedback.upper():
            return current_perspectives
        
        tasks = [query_lens(client, name, config, request.prompt, feedback=feedback) for name, config in LENSES_CONFIG.items()]
        results = await asyncio.gather(*tasks)
        perspectives = {k: v for res in results for k, v in res.items()}

    await log_to_ledger("VADRE_ITERATION", {"decision_id": request.decision_id, "iteration": iteration, "status": "COMPLETED"})
    if iteration < 3: 
        return await run_vadre_cycle(client, request, iteration + 1, current_perspectives=perspectives)
    return perspectives

# --- ENDPOINTS ---

@app.post("/chimera/deliberate")
async def deliberate(request: DeliberationRequest):
    if request.stakes >= 1.0 and not request.anchor_bound:
        resolution = await resolve_capability_match(request.prompt)
        anchor = resolution["anchor"]
        DECISION_STORE[request.decision_id] = {
            "prompt": request.prompt,
            "status": "PENDING",
            "suggested_anchor": anchor["id"],
            "domain": resolution["domain"],
            "stakes": request.stakes
        }
        await log_to_ledger("HALT_AND_LEDGER", {
            "decision_id": request.decision_id,
            "suggested_anchor": anchor["id"],
            "reason": "High stakes decision without bound Human Anchor.",
            "status": "REVIEW_PENDING"
        })
        raise HTTPException(
            status_code=403, 
            detail={
                "error": "HALT_AND_LEDGER",
                "message": "Human Anchor binding required.",
                "suggested_anchor": anchor["name"],
                "decision_id": request.decision_id
            }
        )

    async with httpx.AsyncClient() as client:
        final_perspectives = await run_vadre_cycle(client, request, iteration=0)

    await log_to_ledger("CHIMERA_Σ_FINAL", {"decision_id": request.decision_id, "stakes": request.stakes})

    return {
        "status": "CHIMERA_SYNTHESIS_COMPLETE",
        "decision_id": request.decision_id,
        "vadre_cycles": "Completed",
        "perspectives": final_perspectives,
        "pion_payload": "READY_FOR_KERNEL_FILTER"
    }

@app.post("/chimera/anchor/bind")
async def bind_anchor(request: BindRequest):
    if request.decision_id not in DECISION_STORE:
        raise HTTPException(status_code=404, detail="Decision ID not found.")
    
    decision = DECISION_STORE[request.decision_id]
    if request.anchor_id != decision["suggested_anchor"]:
        await log_to_ledger("ANCHOR_DIVERGENCE", {"decision_id": request.decision_id, "expected": decision["suggested_anchor"], "actual": request.anchor_id})

    decision["status"] = "BOUND"
    decision["bound_anchor"] = request.anchor_id
    
    await log_to_ledger("HUMAN_ANCHOR_BOUND", {
        "decision_id": request.decision_id,
        "anchor_id": request.anchor_id,
        "rationale": request.rationale,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"status": "DECISION_UNLOCKED", "decision_id": request.decision_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
