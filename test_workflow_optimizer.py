#!/usr/bin/env python3
"""
Test Workflow Optimizer Basket
==============================

This script tests the workflow_optimizer basket to ensure it works correctly.
"""

import asyncio
import aiohttp
import json

async def test_workflow_optimizer():
    """Test the workflow_optimizer basket"""
    base_url = "http://localhost:8000"
    
    # Test data
    test_input = {
        "task": "Optimize workflow processes",
        "priority": "high",
        "deadline": "2024-02-01"
    }
    
    print("🧪 Testing Workflow Optimizer Basket")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the basket execution
            payload = {
                "basket_name": "workflow_optimizer",
                "input_data": test_input
            }
            
            print(f"📤 Sending request: {json.dumps(payload, indent=2)}")
            
            async with session.post(
                f"{base_url}/run-basket",
                json=payload,
                timeout=60
            ) as response:
                
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ Basket execution successful!")
                    print(f"📋 Result: {json.dumps(result, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ Basket execution failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

async def test_individual_agents():
    """Test individual agents in the workflow_optimizer basket"""
    base_url = "http://localhost:8000"
    
    print("\n🔧 Testing Individual Agents")
    print("=" * 50)
    
    # Test schedule_agent
    print("\n1. Testing schedule_agent...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "agent_name": "schedule_agent",
                "input_data": {
                    "task": "Optimize workflow processes",
                    "priority": "high",
                    "deadline": "2024-02-01"
                }
            }
            
            async with session.post(
                f"{base_url}/run-agent",
                json=payload,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ schedule_agent works!")
                    print(f"📋 Output: {json.dumps(result, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ schedule_agent failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ schedule_agent test failed: {e}")
    
    # Test workflow_agent
    print("\n2. Testing workflow_agent...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "agent_name": "workflow_agent",
                "input_data": {
                    "task": "Optimize workflow processes",
                    "priority": "high"
                }
            }
            
            async with session.post(
                f"{base_url}/run-agent",
                json=payload,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ workflow_agent works!")
                    print(f"📋 Output: {json.dumps(result, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"❌ workflow_agent failed: {error_text}")
                    
    except Exception as e:
        print(f"❌ workflow_agent test failed: {e}")

async def main():
    """Run all tests"""
    await test_individual_agents()
    await test_workflow_optimizer()
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(main())