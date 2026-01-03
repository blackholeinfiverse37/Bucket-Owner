#!/usr/bin/env python3
"""
Simple Agent Test
================

Test agents without Unicode characters to identify core issues.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from agents.agent_registry import AgentRegistry
from agents.agent_runner import AgentRunner
from utils.validation import validate_agent_name, sanitize_input_data
import importlib

async def test_single_agent(agent_name: str, test_input: dict):
    """Test a single agent"""
    try:
        print(f"Testing {agent_name}...")
        
        # Initialize registry
        agents_dir = Path("agents")
        registry = AgentRegistry(str(agents_dir))
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_name)
        if not agent_spec:
            return f"Agent {agent_name} not found"
        
        # Sanitize input
        sanitized_input = sanitize_input_data(test_input)
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_name}.{agent_name}")
        agent_module = importlib.import_module(module_path)
        
        # Execute
        runner = AgentRunner(agent_name, stateful=False)
        result = await runner.run(agent_module, sanitized_input)
        runner.close()
        
        if "error" in result:
            return f"ERROR: {result['error']}"
        else:
            return "SUCCESS"
            
    except Exception as e:
        return f"EXCEPTION: {str(e)}"

async def main():
    """Test key agents"""
    print("Testing key agents...")
    
    test_cases = [
        ("schedule_agent", {"task": "test task", "priority": "high"}),
        ("workflow_agent", {"workflow_request": {"content": {"department": "test", "action": "optimize"}}}),
        ("cashflow_analyzer", {}),
        ("goal_recommender", {}),
    ]
    
    for agent_name, test_input in test_cases:
        result = await test_single_agent(agent_name, test_input)
        print(f"{agent_name}: {result}")

if __name__ == "__main__":
    asyncio.run(main())