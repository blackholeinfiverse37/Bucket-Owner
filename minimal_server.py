#!/usr/bin/env python3
"""
Minimal Agent Server
===================

FastAPI server without BHIV Bucket integration for testing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import importlib
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from agents.agent_registry import AgentRegistry
from agents.agent_runner import AgentRunner
from utils.validation import validate_agent_name, sanitize_input_data

app = FastAPI(title="BHIV Agent Server - Minimal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize registry
agents_dir = Path("agents")
registry = AgentRegistry(str(agents_dir))

class AgentInput(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    stateful: bool = False

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Minimal agent server running",
        "agents_loaded": len(registry.agents)
    }

@app.get("/agents")
async def get_agents():
    return list(registry.agents.keys())

@app.post("/run-agent")
async def run_agent_minimal(agent_input: AgentInput):
    """Execute agent without BHIV Bucket integration"""
    try:
        print(f"[DEBUG] Received request for agent: {agent_input.agent_name}")
        print(f"[DEBUG] Input data: {agent_input.input_data}")
        
        # Validate agent name
        if not validate_agent_name(agent_input.agent_name):
            print(f"[DEBUG] Invalid agent name: {agent_input.agent_name}")
            raise HTTPException(status_code=400, detail="Invalid agent name format")
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_input.agent_name)
        if not agent_spec:
            print(f"[DEBUG] Agent not found: {agent_input.agent_name}")
            print(f"[DEBUG] Available agents: {list(registry.agents.keys())}")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        print(f"[DEBUG] Agent spec found: {agent_spec['name']}")
        
        # Sanitize input data
        sanitized_input = sanitize_input_data(agent_input.input_data)
        print(f"[DEBUG] Sanitized input: {sanitized_input}")
        
        # Validate compatibility
        if not registry.validate_compatibility(agent_input.agent_name, sanitized_input):
            print(f"[DEBUG] Input validation failed")
            print(f"[DEBUG] Required fields: {agent_spec.get('input_schema', {}).get('required', [])}")
            print(f"[DEBUG] Provided fields: {list(sanitized_input.keys())}")
            raise HTTPException(status_code=400, detail="Input data incompatible with agent")
        
        print(f"[DEBUG] Input validation passed")
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_input.agent_name}.{agent_input.agent_name}")
        print(f"[DEBUG] Importing module: {module_path}")
        
        try:
            agent_module = importlib.import_module(module_path)
            print(f"[DEBUG] Module imported successfully")
        except ImportError as e:
            print(f"[DEBUG] Import error: {e}")
            raise HTTPException(status_code=500, detail=f"Agent module import failed: {str(e)}")
        
        # Check process function
        if not hasattr(agent_module, 'process'):
            print(f"[DEBUG] Missing process function")
            raise HTTPException(status_code=500, detail="Agent module missing process function")
        
        print(f"[DEBUG] Process function found")
        
        # Create runner and execute
        print(f"[DEBUG] Creating runner...")
        runner = AgentRunner(agent_input.agent_name, stateful=agent_input.stateful)
        
        print(f"[DEBUG] Executing agent...")
        result = await runner.run(agent_module, sanitized_input)
        
        print(f"[DEBUG] Agent execution completed")
        print(f"[DEBUG] Result: {result}")
        
        runner.close()
        
        if "error" in result:
            print(f"[DEBUG] Agent returned error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        print(f"[DEBUG] Returning successful result")
        return result
        
    except HTTPException:
        print(f"[DEBUG] Re-raising HTTP exception")
        raise
    except Exception as e:
        print(f"[DEBUG] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal agent server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")