#!/usr/bin/env python3
"""
Minimal FastAPI Agent Test
=========================

Test agent execution through FastAPI without BHIV Bucket integration.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import importlib
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from agents.agent_registry import AgentRegistry
from agents.agent_runner import AgentRunner
from utils.validation import validate_agent_name, sanitize_input_data

app = FastAPI()

# Initialize registry
agents_dir = Path("agents")
registry = AgentRegistry(str(agents_dir))

class AgentInput(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]
    stateful: bool = False

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Minimal agent test server"}

@app.get("/agents")
async def get_agents():
    return list(registry.agents.keys())

@app.post("/run-agent")
async def run_agent_minimal(agent_input: AgentInput):
    """Execute agent without BHIV Bucket integration"""
    try:
        print(f"Received request: {agent_input}")
        
        # Validate agent name
        if not validate_agent_name(agent_input.agent_name):
            raise HTTPException(status_code=400, detail="Invalid agent name format")
        
        # Sanitize input data
        sanitized_input = sanitize_input_data(agent_input.input_data)
        print(f"Sanitized input: {sanitized_input}")
        
        # Validate compatibility
        if not registry.validate_compatibility(agent_input.agent_name, sanitized_input):
            raise HTTPException(status_code=400, detail="Input data incompatible with agent")
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_input.agent_name)
        if not agent_spec:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_input.agent_name}.{agent_input.agent_name}")
        print(f"Importing module: {module_path}")
        
        try:
            agent_module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Import error: {e}")
            raise HTTPException(status_code=500, detail=f"Agent module import failed: {str(e)}")
        
        # Create runner and execute
        runner = AgentRunner(agent_input.agent_name, stateful=agent_input.stateful)
        result = await runner.run(agent_module, sanitized_input)
        runner.close()
        
        print(f"Agent result: {result}")
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)