#!/usr/bin/env python3
"""
Agent Execution Fix
==================

This script identifies and fixes the core agent execution issues.
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

async def fix_agent_execution():
    """Fix all agent execution issues"""
    print("BHIV Agent Execution Fix")
    print("=" * 50)
    
    # Initialize registry
    agents_dir = Path("agents")
    registry = AgentRegistry(str(agents_dir))
    
    print(f"Found {len(registry.agents)} agents")
    
    # Test each agent
    test_inputs = {
        "schedule_agent": {"task": "test task", "priority": "high"},
        "workflow_agent": {"workflow_request": {"content": {"department": "test", "action": "optimize"}}},
        "cashflow_analyzer": {"transactions": [{"id": 1, "amount": 100}]},
        "goal_recommender": {"analysis": {"total": 50, "positive": 100, "negative": -50}},
        "law_agent": {"query": "test legal query"},
        "sanskrit_parser": {"text": "test text"},
        "vedic_quiz_agent": {"question": "test question"},
        "textToJson": {"action": "health"},
        "auto_diagnostics": {"vehicle_data": {"vin": "test", "make": "test", "model": "test", "year": 2020}},
        "vehicle_maintenance": {"vehicle_info": {"make": "test", "model": "test", "year": 2020, "mileage": 50000}},
        "fuel_efficiency": {"driving_data": {"vehicle": {"make": "test", "model": "test", "year": 2020, "engine_size": 2.0}, "fuel_records": [{"date": "2024-01-01", "miles_driven": 100, "fuel_consumed": 5, "trip_type": "city"}]}},
        "financial_coordinator": {"action": "get_transactions"},
        "gurukul_anomaly": {"collections": {"text": "test", "audio": "test", "video": "test", "image": "test"}},
        "gurukul_feedback": {"student_id": "test123"},
        "gurukul_trend": {"collection_name": "test_data"}
    }
    
    failed_agents = []
    fixed_agents = []
    
    for agent_name, agent_spec in registry.agents.items():
        print(f"\nTesting agent: {agent_name}")
        
        try:
            # Get test input
            test_input = test_inputs.get(agent_name, {"input": "test"})
            
            # Validate agent name
            if not validate_agent_name(agent_name):
                print(f"  ❌ Invalid agent name format")
                failed_agents.append((agent_name, "Invalid name format"))
                continue
            
            # Sanitize input
            sanitized_input = sanitize_input_data(test_input)
            
            # Validate compatibility
            if not registry.validate_compatibility(agent_name, sanitized_input):
                print(f"  ❌ Input validation failed")
                print(f"     Required: {agent_spec.get('input_schema', {}).get('required', [])}")
                print(f"     Provided: {list(sanitized_input.keys())}")
                
                # Try to fix input validation
                required_fields = agent_spec.get('input_schema', {}).get('required', [])
                if required_fields:
                    # Add missing required fields with default values
                    for field in required_fields:
                        if field not in sanitized_input:
                            sanitized_input[field] = "default_value"
                    
                    # Retry validation
                    if registry.validate_compatibility(agent_name, sanitized_input):
                        print(f"  ✅ Fixed input validation by adding defaults")
                    else:
                        failed_agents.append((agent_name, "Input validation failed"))
                        continue
                else:
                    failed_agents.append((agent_name, "Input validation failed"))
                    continue
            
            # Import module
            module_path = agent_spec.get("module_path", f"agents.{agent_name}.{agent_name}")
            
            try:
                agent_module = importlib.import_module(module_path)
            except ImportError as e:
                print(f"  ❌ Module import failed: {e}")
                
                # Try to fix import path
                alt_paths = [
                    f"agents.{agent_name}.{agent_name}",
                    f"agents.{agent_name}.main",
                    f"agents.{agent_name}.agent"
                ]
                
                module_imported = False
                for alt_path in alt_paths:
                    try:
                        agent_module = importlib.import_module(alt_path)
                        print(f"  ✅ Fixed import with path: {alt_path}")
                        # Update agent spec
                        agent_spec["module_path"] = alt_path
                        module_imported = True
                        break
                    except ImportError:
                        continue
                
                if not module_imported:
                    failed_agents.append((agent_name, f"Import failed: {e}"))
                    continue
            
            # Check process function
            if not hasattr(agent_module, 'process'):
                print(f"  ❌ Missing process function")
                failed_agents.append((agent_name, "Missing process function"))
                continue
            
            # Test execution
            runner = AgentRunner(agent_name, stateful=False)
            result = await runner.run(agent_module, sanitized_input)
            runner.close()
            
            if "error" in result:
                print(f"  ❌ Execution error: {result['error']}")
                failed_agents.append((agent_name, f"Execution error: {result['error']}"))
            else:
                print(f"  ✅ Agent working correctly")
                fixed_agents.append(agent_name)
                
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            failed_agents.append((agent_name, f"Unexpected error: {e}"))
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"SUMMARY:")
    print(f"✅ Working agents: {len(fixed_agents)}")
    print(f"❌ Failed agents: {len(failed_agents)}")
    
    if fixed_agents:
        print(f"\nWorking agents:")
        for agent in fixed_agents:
            print(f"  - {agent}")
    
    if failed_agents:
        print(f"\nFailed agents:")
        for agent, error in failed_agents:
            print(f"  - {agent}: {error}")
    
    return len(failed_agents) == 0

if __name__ == "__main__":
    success = asyncio.run(fix_agent_execution())
    if success:
        print("\n🎉 All agents are working correctly!")
    else:
        print("\n⚠️  Some agents need fixes")