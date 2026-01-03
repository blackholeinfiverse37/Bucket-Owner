#!/usr/bin/env python3
"""
Test Agent Execution Fix
========================

Test the fixed agent execution system.
"""

import requests
import json
import time

def test_agent_execution():
    """Test agent execution with the fixes"""
    base_url = "http://localhost:8000"
    
    print("Testing BHIV Agent Execution Fix")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            health_data = response.json()
            print(f"  Status: {health_data.get('status')}")
            print(f"  BHIV Bucket: {health_data.get('bhiv_bucket', {}).get('status')}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test agents endpoint
    try:
        response = requests.get(f"{base_url}/agents")
        if response.status_code == 200:
            agents = response.json()
            print(f"✓ Agents endpoint working ({len(agents)} agents)")
        else:
            print(f"✗ Agents endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Agents endpoint error: {e}")
        return False
    
    # Test agent execution
    test_cases = [
        {
            "name": "schedule_agent",
            "data": {"task": "test task", "priority": "high"}
        },
        {
            "name": "workflow_agent", 
            "data": {"workflow_request": {"content": {"department": "test", "action": "optimize"}}}
        },
        {
            "name": "cashflow_analyzer",
            "data": {}
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        agent_name = test_case["name"]
        input_data = test_case["data"]
        
        print(f"\nTesting {agent_name}...")
        
        try:
            payload = {
                "agent_name": agent_name,
                "input_data": input_data,
                "stateful": False
            }
            
            response = requests.post(
                f"{base_url}/run-agent",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ {agent_name} executed successfully")
                
                # Check if BHIV Bucket info is present
                if "bhiv_bucket" in result:
                    bucket_status = result["bhiv_bucket"]["stored"]
                    print(f"  BHIV Bucket: {'stored' if bucket_status else 'not stored'}")
                
                success_count += 1
            else:
                print(f"✗ {agent_name} failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"  Error: {error_detail.get('detail', 'Unknown error')}")
                except:
                    print(f"  Raw response: {response.text}")
        
        except Exception as e:
            print(f"✗ {agent_name} error: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"RESULTS: {success_count}/{len(test_cases)} agents working")
    
    if success_count == len(test_cases):
        print("🎉 All agents are working correctly!")
        return True
    else:
        print("⚠️  Some agents still have issues")
        return False

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_agent_execution()
    exit(0 if success else 1)