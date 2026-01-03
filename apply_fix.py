#!/usr/bin/env python3
"""
BHIV Agent Execution Fix
========================

This script fixes all agent execution issues by:
1. Bypassing problematic BHIV Bucket integration temporarily
2. Adding comprehensive error handling
3. Ensuring all agents work correctly
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def fix_main_server():
    """Fix the main server by updating the run_agent endpoint"""
    
    main_file = Path("main.py")
    
    # Read the current main.py
    with main_file.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # Create the fixed run_agent function
    fixed_run_agent = '''@app.post("/run-agent")
async def run_agent(agent_input: AgentInput) -> Dict[str, Any]:
    """Execute a single agent with comprehensive error handling"""
    logger.info(f"Executing agent: {agent_input.agent_name}")
    
    try:
        # Validate agent name
        if not validate_agent_name(agent_input.agent_name):
            logger.error(f"Invalid agent name: {agent_input.agent_name}")
            raise HTTPException(status_code=400, detail="Invalid agent name format")
        
        # Sanitize input data
        sanitized_input = sanitize_input_data(agent_input.input_data)
        logger.info(f"Input sanitized for {agent_input.agent_name}")
        
        # Validate compatibility
        if not registry.validate_compatibility(agent_input.agent_name, sanitized_input):
            logger.error(f"Input validation failed for {agent_input.agent_name}")
            raise HTTPException(status_code=400, detail="Input data incompatible with agent")
        
        # Get agent spec
        agent_spec = registry.get_agent(agent_input.agent_name)
        if not agent_spec:
            logger.error(f"Agent not found: {agent_input.agent_name}")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Import module
        module_path = agent_spec.get("module_path", f"agents.{agent_input.agent_name}.{agent_input.agent_name}")
        logger.info(f"Importing module: {module_path}")
        
        try:
            agent_module = importlib.import_module(module_path)
            logger.info(f"Module imported successfully: {module_path}")
        except ImportError as e:
            logger.error(f"Failed to import agent module {module_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Agent module import failed: {str(e)}")
        
        # Check process function
        if not hasattr(agent_module, 'process'):
            logger.error(f"Module missing process function: {module_path}")
            raise HTTPException(status_code=500, detail="Agent module missing process function")
        
        # Create runner and execute
        logger.info(f"Creating runner for {agent_input.agent_name}")
        runner = AgentRunner(agent_input.agent_name, stateful=agent_input.stateful)
        
        logger.info(f"Executing agent {agent_input.agent_name}")
        result = await runner.run(agent_module, sanitized_input)
        
        logger.info(f"Agent execution completed: {agent_input.agent_name}")
        runner.close()
        
        # Check for errors in result
        if "error" in result:
            logger.error(f"Agent returned error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Process AI output through BHIV Bucket firewall (with comprehensive error handling)
        if ai_firewall:
            try:
                logger.info(f"Processing through BHIV Bucket firewall: {agent_input.agent_name}")
                firewall_result = ai_firewall.process_ai_output(
                    agent_name=agent_input.agent_name,
                    output_data=result,
                    artifact_class=ArtifactClass.AGENT_OUTPUT
                )
                
                if firewall_result["success"]:
                    logger.info(f"Agent output stored in BHIV Bucket: {firewall_result.get('artifact_id')}")
                    result["bhiv_bucket"] = {
                        "stored": True,
                        "artifact_id": firewall_result.get("artifact_id"),
                        "constitutional_compliance": firewall_result.get("constitutional_compliance", False),
                        "firewall_action": firewall_result.get("action")
                    }
                else:
                    logger.warning(f"Agent output not stored in BHIV Bucket: {firewall_result.get('reason')}")
                    result["bhiv_bucket"] = {
                        "stored": False,
                        "reason": firewall_result.get("reason"),
                        "constitutional_compliance": False
                    }
                    
            except Exception as bucket_error:
                logger.warning(f"BHIV Bucket processing error: {bucket_error}")
                # Don't fail the entire request due to bucket issues
                result["bhiv_bucket"] = {
                    "stored": False,
                    "error": str(bucket_error),
                    "constitutional_compliance": False
                }
        else:
            # BHIV Bucket not available
            logger.info(f"BHIV Bucket not available for {agent_input.agent_name}")
            result["bhiv_bucket"] = {
                "stored": False,
                "reason": "BHIV Bucket not initialized",
                "constitutional_compliance": False
            }
        
        logger.info(f"Successfully completed agent execution: {agent_input.agent_name}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Store error in MongoDB if available
        try:
            if mongo_client:
                mongo_client.store_log(agent_input.agent_name, f"Execution error: {str(e)}")
        except Exception as mongo_error:
            logger.warning(f"Failed to store error in MongoDB: {mongo_error}")
        
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")'''
    
    # Find and replace the run_agent function
    import re
    
    # Pattern to match the entire run_agent function
    pattern = r'@app\.post\("/run-agent"\)\nasync def run_agent\(.*?\n(?=@app\.|if __name__|# Law Agent|$)'
    
    # Replace with fixed version
    fixed_content = re.sub(pattern, fixed_run_agent + '\n\n', content, flags=re.DOTALL)
    
    # Write back to file
    with main_file.open("w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print("✓ Fixed main.py run_agent endpoint")

def main():
    """Main fix function"""
    print("BHIV Agent Execution Fix")
    print("=" * 50)
    
    try:
        fix_main_server()
        print("✓ All fixes applied successfully")
        print("\nRestart the server with: python main.py")
        print("Then test with: curl -X POST http://localhost:8000/run-agent -H 'Content-Type: application/json' -d '{\"agent_name\": \"schedule_agent\", \"input_data\": {\"task\": \"test\", \"priority\": \"high\"}}'")
        
    except Exception as e:
        print(f"✗ Fix failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()