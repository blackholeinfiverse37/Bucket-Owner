#!/usr/bin/env python3
"""
Debug Agent Execution
====================

Simple script to debug agent execution issues.
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

async def test_agent(agent_name: str, input_data: dict):
    """Test agent execution with detailed error reporting"""
    print(f"Testing agent: {agent_name}")
    print(f"Input data: {input_data}")
    
    try:
        # Initialize registry
        agents_dir = Path("agents")
        registry = AgentRegistry(str(agents_dir))
        
        # Validate agent name
        if not validate_agent_name(agent_name):
            print(f"Invalid agent name: {agent_name}")
            return
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_name)
        if not agent_spec:
            print(f"Agent not found: {agent_name}")
            print(f"Available agents: {list(registry.agents.keys())}")
            return
        
        print(f"Agent spec found: {agent_spec['name']}")
        
        # Sanitize input
        sanitized_input = sanitize_input_data(input_data)
        print(f"Input sanitized: {sanitized_input}")
        
        # Validate compatibility
        if not registry.validate_compatibility(agent_name, sanitized_input):
            print(f"Input incompatible with agent")
            return
        
        print(f"Input validation passed")
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_name}.{agent_name}")
        print(f"Importing module: {module_path}")
        
        try:
            agent_module = importlib.import_module(module_path)
            print(f"Module imported successfully")
        except ImportError as e:
            print(f"Module import failed: {e}")
            traceback.print_exc()
            return
        
        # Check if process function exists
        if not hasattr(agent_module, 'process'):
            print(f"Module missing 'process' function")
            return
        
        print(f"Process function found")
        
        # Create runner and execute
        runner = AgentRunner(agent_name, stateful=False)
        print(f"Runner created")
        
        result = await runner.run(agent_module, sanitized_input)
        print(f"Agent execution completed")
        print(f"Result: {result}")
        
        runner.close()
        return result
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return {"error": str(e)}

async def main():
    """Main test function"""
    print("BHIV Agent Debug Tool")
    print("=" * 50)
    
    # Test schedule_agent
    test_data = {
        "task": "test task",
        "priority": "high"
    }
    
    result = await test_agent("schedule_agent", test_data)
    
    if result and "error" not in result:
        print("\nAgent test PASSED")
    else:
        print(f"\nAgent test FAILED: {result}")

if __name__ == "__main__":
    asyncio.run(main())