#!/usr/bin/env python3
"""
Minimal Main Server - No BHIV Bucket
====================================

FastAPI server without BHIV Bucket integration for debugging.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents.agent_registry import AgentRegistry
from agents.agent_runner import AgentRunner
from utils.logger import get_logger
from utils.validation import validate_agent_name, sanitize_input_data

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import uvicorn
import os
import importlib
import json

# Load environment
from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)

# Get the directory where main.py is located
script_dir = Path(__file__).parent
agents_dir = script_dir / "agents"

registry = AgentRegistry(str(agents_dir))

class AgentInput(BaseModel):
    agent_name: str = Field(..., description="Name of the agent to run")
    input_data: Dict = Field(..., description="Input data for the agent")
    stateful: bool = Field(False, description="Whether to run agent with state")

app = FastAPI(title="BHIV Agent Server - Minimal Debug")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Minimal debug server running",
        "agents_loaded": len(registry.agents)
    }

@app.get("/agents")
async def get_agents(domain: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """Get all agents or filter by domain"""
    logger.debug(f"Fetching agents with domain: {domain}")
    try:
        if domain:
            return registry.get_agents_by_domain(domain)
        return list(registry.agents.values())
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch agents: {str(e)}")

@app.post("/run-agent")
async def run_agent(agent_input: AgentInput) -> Dict[str, Any]:
    """Execute a single agent without BHIV Bucket integration"""
    logger.info(f"[DEBUG] Starting agent execution: {agent_input.agent_name}")
    
    try:
        # Validate agent name
        if not validate_agent_name(agent_input.agent_name):
            logger.error(f"[DEBUG] Invalid agent name: {agent_input.agent_name}")
            raise HTTPException(status_code=400, detail="Invalid agent name format")
        
        logger.info(f"[DEBUG] Agent name validation passed")
        
        # Sanitize input data
        sanitized_input = sanitize_input_data(agent_input.input_data)
        logger.info(f"[DEBUG] Input sanitized: {sanitized_input}")
        
        # Validate compatibility
        if not registry.validate_compatibility(agent_input.agent_name, sanitized_input):
            logger.error(f"[DEBUG] Input validation failed for {agent_input.agent_name}")
            raise HTTPException(status_code=400, detail="Input data incompatible with agent")
        
        logger.info(f"[DEBUG] Input compatibility validated")
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_input.agent_name)
        if not agent_spec:
            logger.error(f"[DEBUG] Agent not found: {agent_input.agent_name}")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"[DEBUG] Agent spec retrieved: {agent_spec['name']}")
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_input.agent_name}.{agent_input.agent_name}")
        logger.info(f"[DEBUG] Importing module: {module_path}")
        
        try:
            agent_module = importlib.import_module(module_path)
            logger.info(f"[DEBUG] Module imported successfully")
        except ImportError as e:
            logger.error(f"[DEBUG] Failed to import agent module {module_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Agent module import failed: {str(e)}")\n        \n        # Check if process function exists
        if not hasattr(agent_module, 'process'):
            logger.error(f"[DEBUG] Module missing process function")
            raise HTTPException(status_code=500, detail="Agent module missing process function")
        
        logger.info(f"[DEBUG] Process function found")
        
        # Create runner and execute
        logger.info(f"[DEBUG] Creating agent runner")
        runner = AgentRunner(agent_input.agent_name, stateful=agent_input.stateful)
        
        logger.info(f"[DEBUG] Executing agent")
        result = await runner.run(agent_module, sanitized_input)
        
        logger.info(f"[DEBUG] Agent execution completed")
        logger.info(f"[DEBUG] Result: {result}")
        
        runner.close()
        
        # Check for errors in result
        if "error" in result:
            logger.error(f"[DEBUG] Agent returned error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Add debug metadata
        result["debug_info"] = {
            "agent_name": agent_input.agent_name,
            "module_path": module_path,
            "execution_time": datetime.now().isoformat(),
            "bhiv_bucket": "disabled"
        }
        
        logger.info(f"[DEBUG] Returning successful result")
        return result
        
    except HTTPException:
        logger.error(f"[DEBUG] Re-raising HTTP exception")
        raise
    except Exception as e:
        logger.error(f"[DEBUG] Unexpected error in agent execution: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")raceback\n        traceback.print_exc()\n        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")\n\nif __name__ == "__main__":\n    port = int(os.getenv("FASTAPI_PORT", 8002))\n    print(f"Starting minimal debug server on port {port}...")\n    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")