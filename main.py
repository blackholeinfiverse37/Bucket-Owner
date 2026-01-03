from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents.agent_registry import AgentRegistry
from agents.agent_runner import AgentRunner
from baskets.basket_manager import AgentBasket
from communication.event_bus import EventBus
from database.mongo_db import MongoDBClient
from utils.redis_service import RedisService
from utils.logger import get_logger, get_execution_logger
from utils.validation import validate_agent_name, validate_basket_name, sanitize_input_data

# BHIV Bucket Integration
from bhiv_bucket import (
    get_truth_engine, get_ai_firewall, get_bucket_status, get_governance_system,
    get_custodianship_system, get_gatekeeping_system,
    BucketAuthority, ArtifactType, ArtifactClass, GovernanceAction, IntegrationStatus, ExecutorPermission
)

logger = get_logger(__name__)
execution_logger = get_execution_logger()

# Initialize BHIV Bucket components with error handling
try:
    truth_engine = get_truth_engine()
    ai_firewall = get_ai_firewall()
    governance_system = get_governance_system()
    custodianship_system = get_custodianship_system()
    gatekeeping_system = get_gatekeeping_system()
    logger.info("BHIV Bucket Truth Engine initialized with complete custodianship")
except Exception as bucket_init_error:
    logger.error(f"BHIV Bucket initialization failed: {bucket_init_error}")
    # Set fallback values
    truth_engine = None
    ai_firewall = None
    governance_system = None
    custodianship_system = None
    gatekeeping_system = None
    logger.warning("Running without BHIV Bucket integration")
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import uvicorn
import socketio
import os
import asyncio
import importlib
import json
import redis

load_dotenv()

# Get the directory where main.py is located
script_dir = Path(__file__).parent
agents_dir = script_dir / "agents"
config_file = script_dir / "agents_and_baskets.yaml"

registry = AgentRegistry(str(agents_dir))
registry.load_baskets(str(config_file))  # Load baskets from config
event_bus = EventBus()
mongo_client = MongoDBClient()
redis_service = RedisService()
sio = socketio.AsyncClient()

# Redis client setup
redis_client: Optional[redis.Redis] = None
try:
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_username = os.getenv("REDIS_USERNAME")
    redis_password = os.getenv("REDIS_PASSWORD")
    
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_username,
        password=redis_password,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )
    redis_client.ping()
    logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
except (redis.ConnectionError, redis.RedisError) as e:
    logger.warning(f"Redis connection failed: {e}. Redis features will be disabled")
    redis_client = None
except Exception as e:
    logger.error(f"Unexpected error connecting to Redis: {e}")
    redis_client = None

class AgentInput(BaseModel):
    agent_name: str = Field(..., description="Name of the agent to run")
    input_data: Dict = Field(..., description="Input data for the agent")
    stateful: bool = Field(False, description="Whether to run agent with state")

class BasketInput(BaseModel):
    basket_name: Optional[str] = Field(None, description="Name of predefined basket")
    config: Optional[Dict] = Field(None, description="Custom basket configuration")
    input_data: Optional[Dict] = Field(None, description="Input data for the basket execution")

async def connect_socketio() -> bool:
    """Connect to Socket.IO server with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            socketio_url = os.getenv("SOCKETIO_URL", "http://localhost:5000")
            await sio.connect(socketio_url)
            logger.info("Socket.IO client connected")
            return True
        except Exception as e:
            logger.error(f"Socket.IO connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    logger.error("Socket.IO connection failed after all retries")
    return False

async def forward_event_to_socketio(event_type: str, message: Dict[str, Any]) -> None:
    """Forward events to Socket.IO server"""
    if sio.connected:
        try:
            await sio.emit(event_type, message)
            logger.debug(f"Forwarded event {event_type} to Socket.IO server")
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")
    else:
        logger.warning(f"Socket.IO not connected, could not forward event {event_type}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Disable Socket.IO connection for now
    socketio_connected = False
    # socketio_connected = await connect_socketio()
    if not socketio_connected:
        logger.info("Socket.IO disabled - continuing with core functionality")
        # We'll continue without Socket.IO instead of raising an error
    
    # Set up event forwarding only if Socket.IO is connected
    if socketio_connected:
        event_bus.subscribe('agent-recommendation', lambda msg: forward_event_to_socketio('agent-recommendation', msg))
        event_bus.subscribe('escalation', lambda msg: forward_event_to_socketio('escalation', msg))
        event_bus.subscribe('dependency-update', lambda msg: forward_event_to_socketio('dependency-update', msg))
        logger.info("Event forwarding setup complete")
    else:
        logger.warning("Event forwarding to Socket.IO disabled due to connection failure")
    
    yield
    if mongo_client:
        mongo_client.close()
    if sio.connected:
        await sio.disconnect()
    if redis_client:
        try:
            redis_client.close()
            logger.info("Closed Redis connection")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    logger.info("Disconnected from Socket.IO, MongoDB, and Redis")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:8002", "http://localhost:8003", "http://localhost:8004", "http://localhost:8080", "http://localhost:5000", "http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint with comprehensive service status"""
    health_status = {
        "status": "healthy",
        "services": {
            "mongodb": "connected" if mongo_client and mongo_client.db is not None else "disconnected",
            "socketio": "disabled",
            "redis": "connected" if redis_service.is_connected() else "disconnected"
        }
    }

    # Check legacy Redis client if it exists
    if redis_client:
        try:
            redis_client.ping()
            health_status["services"]["redis_legacy"] = "connected"
        except (redis.ConnectionError, redis.RedisError):
            health_status["services"]["redis_legacy"] = "disconnected"

    # Add BHIV Bucket status
    try:
        if truth_engine and ai_firewall:
            bucket_status = get_bucket_status()
            health_status["bhiv_bucket"] = {
                "status": "active",
                "constitutional_lock": bucket_status["constitutional_status"]["locked"],
                "truth_engine": "operational",
                "ai_firewall": "active"
            }
        else:
            health_status["bhiv_bucket"] = {
                "status": "disabled",
                "reason": "BHIV Bucket components not initialized"
            }
    except Exception as e:
        health_status["bhiv_bucket"] = {
            "status": "error",
            "error": str(e)
        }

    # Determine overall status
    connected_services = [status for status in health_status["services"].values() if status == "connected"]
    if len(connected_services) >= 2:  # MongoDB + Redis is sufficient
        health_status["status"] = "healthy"
    elif health_status["services"]["mongodb"] == "connected":
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "unhealthy"

    return health_status

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

@app.get("/baskets")
async def get_baskets() -> Dict[str, Any]:
    """Get all available baskets from registry and files"""
    logger.debug("Fetching available baskets")
    try:
        # Get baskets from registry
        baskets_from_registry = registry.baskets

        # Also scan the baskets directory for JSON files
        baskets_dir = Path("baskets")
        file_baskets = []

        if baskets_dir.exists():
            for basket_file in baskets_dir.glob("*.json"):
                try:
                    with basket_file.open("r", encoding="utf-8") as f:
                        basket_data = json.load(f)
                        basket_data["source"] = "file"
                        basket_data["filename"] = basket_file.name
                        file_baskets.append(basket_data)
                except Exception as e:
                    logger.warning(f"Failed to load basket file {basket_file}: {e}")

        # Combine both sources
        all_baskets = baskets_from_registry + file_baskets

        return {
            "baskets": all_baskets,
            "count": len(all_baskets)
        }
    except Exception as e:
        logger.error(f"Error fetching baskets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch baskets: {str(e)}")

@app.post("/run-agent")
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
        
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/run-basket")
async def execute_basket(basket_input: BasketInput) -> Dict[str, Any]:
    """Execute a basket with enhanced logging and error handling"""
    logger.info(f"Executing basket: {basket_input}")

    try:
        # Load basket configuration
        if basket_input.basket_name:
            basket_path = Path("baskets") / f"{basket_input.basket_name}.json"
            if not basket_path.exists():
                raise HTTPException(status_code=404, detail=f"Basket {basket_input.basket_name} not found")
            with basket_path.open("r") as f:
                basket_spec = json.load(f)
        elif basket_input.config:
            basket_spec = basket_input.config
        else:
            raise HTTPException(status_code=400, detail="Must provide basket_name or config")

        # Validate basket specification
        if not basket_spec.get("agents"):
            raise HTTPException(status_code=400, detail="Basket must contain at least one agent")

        # Create and execute basket with Redis integration
        basket = AgentBasket(basket_spec, registry, event_bus, redis_service)

        # Execute with provided input data or agent-specific default
        if basket_input.input_data:
            input_data = basket_input.input_data
        else:
            # Get default input based on the first agent in the basket
            first_agent_name = basket_spec.get("agents", [])[0] if basket_spec.get("agents") else None
            if first_agent_name:
                agent_spec = registry.get_agent(first_agent_name)
                if agent_spec and "sample_input" in agent_spec:
                    input_data = agent_spec["sample_input"]
                    logger.info(f"Using sample input from {first_agent_name}: {input_data}")
                else:
                    input_data = {"input": "start"}
            else:
                input_data = {"input": "start"}

        logger.info(f"Starting basket execution: {basket_spec.get('basket_name', 'unnamed')} (ID: {basket.execution_id})")
        result = await basket.execute(input_data)

        # Store basket execution in BHIV Bucket with constitutional enforcement
        try:
            bucket_storage_result = truth_engine.store_artifact(
                artifact_type=ArtifactType.BASKET_EXECUTION,
                content={
                    "basket_name": basket_spec.get("basket_name", "unnamed"),
                    "execution_id": basket.execution_id,
                    "input_data": input_data,
                    "result": result,
                    "agents_executed": basket_spec.get("agents", []),
                    "execution_strategy": basket_spec.get("execution_strategy", "sequential")
                },
                authority=BucketAuthority.EXECUTOR,
                metadata={
                    "execution_type": "basket",
                    "constitutional_compliance": True
                }
            )
            
            if bucket_storage_result["success"]:
                logger.info(f"Basket execution stored in BHIV Bucket: {bucket_storage_result['artifact_id']}")
            else:
                logger.warning(f"Failed to store in BHIV Bucket: {bucket_storage_result.get('error')}")
                
        except Exception as bucket_error:
            logger.warning(f"BHIV Bucket storage error: {bucket_error}")

        # Add execution metadata to result
        if "error" not in result:
            result["execution_metadata"] = {
                "execution_id": basket.execution_id,
                "basket_name": basket_spec.get("basket_name", "unnamed"),
                "agents_executed": basket_spec.get("agents", []),
                "strategy": basket_spec.get("execution_strategy", "sequential")
            }

        logger.info(f"Basket execution completed: {basket.execution_id}")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = f"Basket execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Store error in Redis if service is available
        if redis_service.is_connected():
            try:
                redis_service.store_execution_log(
                    "unknown",
                    "basket_manager",
                    "execution_error",
                    {"error": error_msg, "basket_input": basket_input.model_dump()},
                    "error"
                )
            except Exception as redis_error:
                logger.warning(f"Failed to store error in Redis: {redis_error}")

        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/create-basket")
async def create_basket(basket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new basket configuration"""
    logger.debug(f"Creating basket: {basket_data}")
    try:
        basket_name = basket_data.get("name")
        if not basket_name:
            raise HTTPException(status_code=400, detail="Basket name is required")

        # Validate agents exist
        agents = basket_data.get("agents", [])
        for agent_name in agents:
            if not registry.get_agent(agent_name):
                raise HTTPException(status_code=400, detail=f"Agent {agent_name} not found")

        # Create basket configuration
        basket_config = {
            "basket_name": basket_name,
            "agents": agents,
            "execution_strategy": basket_data.get("execution_strategy", "sequential"),
            "description": basket_data.get("description", "")
        }

        # Save to file
        basket_path = Path("baskets") / f"{basket_name}.json"
        with basket_path.open("w") as f:
            json.dump(basket_config, f, indent=2)

        logger.info(f"Created basket: {basket_name}")
        return {"success": True, "message": f"Basket {basket_name} created successfully", "basket": basket_config}
    except Exception as e:
        logger.error(f"Basket creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Basket creation failed: {str(e)}")

@app.get("/logs")
async def get_logs(agent: str = Query(None)):
    logger.debug(f"Fetching logs for agent: {agent}")
    try:
        return {"logs": mongo_client.get_logs(agent)}
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")

@app.get("/redis/status")
async def redis_status():
    """Check Redis connection and get statistics"""
    if not redis_service.is_connected():
        raise HTTPException(status_code=503, detail="Redis service not connected")

    try:
        stats = redis_service.get_stats()
        return {
            "status": "healthy" if stats["connected"] else "unhealthy",
            "message": "Redis service is working correctly",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Redis status check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Redis status check failed: {str(e)}")

@app.get("/execution-logs/{execution_id}")
async def get_execution_logs(execution_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Get execution logs for a specific execution ID"""
    try:
        logs = redis_service.get_execution_logs(execution_id, limit)
        return {
            "execution_id": execution_id,
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Failed to get execution logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution logs: {str(e)}")

@app.get("/agent-logs/{agent_name}")
async def get_agent_logs(agent_name: str, limit: int = Query(100, ge=1, le=1000)):
    """Get logs for a specific agent"""
    try:
        logs = redis_service.get_agent_logs(agent_name, limit)
        return {
            "agent_name": agent_name,
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Failed to get agent logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent logs: {str(e)}")

@app.post("/redis/cleanup")
async def cleanup_redis_data(days: int = Query(7, ge=1, le=30)):
    """Clean up old Redis data"""
    try:
        redis_service.cleanup_old_data(days)
        return {
            "success": True,
            "message": f"Cleaned up Redis data older than {days} days"
        }
    except Exception as e:
        logger.error(f"Redis cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Redis cleanup failed: {str(e)}")

@app.delete("/baskets/{basket_name}")
async def delete_basket(basket_name: str):
    """Delete a basket and clean up all related data"""
    logger.info(f"Deleting basket: {basket_name}")

    try:
        # Check if basket exists
        basket_path = Path("baskets") / f"{basket_name}.json"
        if not basket_path.exists():
            raise HTTPException(status_code=404, detail=f"Basket '{basket_name}' not found")

        # Load basket configuration to get execution history
        with basket_path.open("r") as f:
            basket_config = json.load(f)

        cleanup_summary = {
            "basket_name": basket_name,
            "files_deleted": [],
            "redis_data_cleaned": [],
            "mongo_data_cleaned": [],
            "errors": []
        }

        # 1. Clean up Redis data
        if redis_service.is_connected():
            try:
                # Get all execution IDs for this basket
                execution_ids = redis_service.get_basket_executions(basket_name)

                for execution_id in execution_ids:
                    # Clean execution logs
                    redis_service.client.delete(f"execution:{execution_id}:logs")

                    # Clean agent outputs for this execution
                    for agent_name in basket_config.get("agents", []):
                        redis_service.client.delete(f"execution:{execution_id}:outputs:{agent_name}")
                        redis_service.client.delete(f"agent:{agent_name}:state:{execution_id}")

                    cleanup_summary["redis_data_cleaned"].append(f"execution:{execution_id}")

                # Clean basket metadata
                redis_service.client.delete(f"basket:{basket_name}:executions")

                # Clean basket execution metadata
                basket_keys = redis_service.client.keys(f"basket:{basket_name}:execution:*")
                if basket_keys:
                    redis_service.client.delete(*basket_keys)
                    cleanup_summary["redis_data_cleaned"].extend([key.decode() for key in basket_keys])

                logger.info(f"Cleaned Redis data for basket: {basket_name}")

            except Exception as e:
                error_msg = f"Redis cleanup error: {str(e)}"
                cleanup_summary["errors"].append(error_msg)
                logger.error(error_msg)

        # 2. Clean up MongoDB data (if connected)
        if mongo_client and mongo_client.db is not None:
            try:
                # Clean basket execution logs from MongoDB
                result = mongo_client.db.logs.delete_many({"basket_name": basket_name})
                if result.deleted_count > 0:
                    cleanup_summary["mongo_data_cleaned"].append(f"Deleted {result.deleted_count} log entries")

                # Clean basket metadata from MongoDB
                result = mongo_client.db.baskets.delete_many({"basket_name": basket_name})
                if result.deleted_count > 0:
                    cleanup_summary["mongo_data_cleaned"].append(f"Deleted {result.deleted_count} basket records")

                logger.info(f"Cleaned MongoDB data for basket: {basket_name}")

            except Exception as e:
                error_msg = f"MongoDB cleanup error: {str(e)}"
                cleanup_summary["errors"].append(error_msg)
                logger.error(error_msg)

        # 3. Clean up log files
        try:
            logs_dir = Path("logs/basket_runs")
            if logs_dir.exists():
                # Find and delete log files for this basket
                log_files = list(logs_dir.glob(f"{basket_name}_*.log"))
                for log_file in log_files:
                    log_file.unlink()
                    cleanup_summary["files_deleted"].append(str(log_file))

                logger.info(f"Deleted {len(log_files)} log files for basket: {basket_name}")

        except Exception as e:
            error_msg = f"Log file cleanup error: {str(e)}"
            cleanup_summary["errors"].append(error_msg)
            logger.error(error_msg)

        # 4. Delete the basket configuration file
        try:
            basket_path.unlink()
            cleanup_summary["files_deleted"].append(str(basket_path))
            logger.info(f"Deleted basket configuration file: {basket_path}")

        except Exception as e:
            error_msg = f"Basket file deletion error: {str(e)}"
            cleanup_summary["errors"].append(error_msg)
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        # 5. Reload registry to remove basket from memory
        try:
            config_file = Path("agents_and_baskets.yaml")
            if config_file.exists():
                registry.load_baskets(str(config_file))
            logger.info("Reloaded basket registry")

        except Exception as e:
            error_msg = f"Registry reload error: {str(e)}"
            cleanup_summary["errors"].append(error_msg)
            logger.warning(error_msg)

        # 6. Log the deletion event in Redis (if available)
        if redis_service.is_connected():
            try:
                deletion_log = {
                    "event": "basket_deleted",
                    "basket_name": basket_name,
                    "timestamp": datetime.now().isoformat(),
                    "cleanup_summary": cleanup_summary
                }
                redis_service.client.lpush("system:basket_deletions", json.dumps(deletion_log))
                redis_service.client.expire("system:basket_deletions", 86400 * 30)  # Keep for 30 days

            except Exception as e:
                logger.warning(f"Failed to log deletion event: {e}")

        # Prepare response
        success_message = f"Basket '{basket_name}' deleted successfully"
        if cleanup_summary["errors"]:
            success_message += f" with {len(cleanup_summary['errors'])} warnings"

        logger.info(f"Basket deletion completed: {basket_name}")

        return {
            "success": True,
            "message": success_message,
            "cleanup_summary": cleanup_summary
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = f"Failed to delete basket '{basket_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

# BHIV Bucket Endpoints
@app.get("/bucket/status")
async def get_bucket_status_endpoint():
    """Get comprehensive BHIV Bucket status"""
    try:
        return get_bucket_status()
    except Exception as e:
        logger.error(f"Failed to get bucket status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get bucket status: {str(e)}")

@app.get("/bucket/constitutional")
async def get_constitutional_status():
    """Get constitutional lock status and rules"""
    try:
        from bhiv_bucket import CONSTITUTIONAL_LOCK
        return CONSTITUTIONAL_LOCK.get_constitutional_status()
    except Exception as e:
        logger.error(f"Failed to get constitutional status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bucket/artifacts/{artifact_id}")
async def get_bucket_artifact(artifact_id: str):
    """Retrieve artifact from BHIV Bucket"""
    try:
        artifact = truth_engine.get_artifact(artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bucket/artifacts/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: str):
    """Get complete lineage of an artifact"""
    try:
        lineage = truth_engine.get_artifact_lineage(artifact_id)
        return {
            "artifact_id": artifact_id,
            "lineage": lineage,
            "lineage_length": len(lineage)
        }
    except Exception as e:
        logger.error(f"Failed to get lineage for {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bucket/artifacts/{parent_id}/children")
async def get_artifact_children(parent_id: str):
    """Get all children of an artifact"""
    try:
        children = truth_engine.get_artifact_children(parent_id)
        return {
            "parent_id": parent_id,
            "children": children,
            "children_count": len(children)
        }
    except Exception as e:
        logger.error(f"Failed to get children for {parent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bucket/artifacts/{parent_id}/version")
async def create_artifact_version(parent_id: str, version_data: Dict):
    """Create new version of existing artifact"""
    try:
        content = version_data.get("content", {})
        change_reason = version_data.get("change_reason", "version_update")
        
        result = truth_engine.create_version(
            parent_id=parent_id,
            content=content,
            authority=BucketAuthority.EXECUTOR,
            change_reason=change_reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create version: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/bucket/artifacts/{artifact_id}")
async def create_artifact_tombstone(artifact_id: str, deletion_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create tombstone for artifact (constitutional deletion)"""
    try:
        deletion_reason = "user_request"
        if deletion_data:
            deletion_reason = deletion_data.get("reason", "user_request")
        
        result = truth_engine.create_tombstone(
            artifact_id=artifact_id,
            authority=BucketAuthority.DATA_SOVEREIGN,  # Requires highest authority
            deletion_reason=deletion_reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create tombstone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Governance Endpoints
@app.get("/governance/status")
async def get_governance_status():
    """Get governance system status and statistics"""
    try:
        return governance_system.get_governance_stats()
    except Exception as e:
        logger.error(f"Failed to get governance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/governance/checklist/{authority}")
async def get_governance_checklist(authority: str):
    """Get governance checklist for authority level"""
    try:
        # Convert string to BucketAuthority enum
        authority_enum = BucketAuthority(authority.lower())
        return governance_system.get_governance_checklist(authority_enum)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid authority level: {authority}")
    except Exception as e:
        logger.error(f"Failed to get governance checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/governance/validate")
async def validate_governance_action(validation_request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate if authority can perform action"""
    try:
        action = validation_request.get("action")
        authority = validation_request.get("authority")
        
        if not action or not authority:
            raise HTTPException(status_code=400, detail="Missing action or authority")
        
        # Convert string to BucketAuthority enum
        try:
            authority_enum = BucketAuthority(authority.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid authority level: {authority}")
        
        validation_result = governance_system.validate_authority_action(action, authority_enum)
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate governance action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/governance/escalate")
async def escalate_governance_decision(escalation_request: Dict):
    """Escalate a governance decision to higher authority"""
    try:
        decision_id = escalation_request.get("decision_id")
        escalation_authority = escalation_request.get("escalation_authority")
        escalation_decision = escalation_request.get("escalation_decision")
        escalation_reason = escalation_request.get("escalation_reason", "")
        
        if not all([decision_id, escalation_authority, escalation_decision]):
            raise HTTPException(status_code=400, detail="Missing required escalation parameters")
        
        # Convert strings to enums
        authority_enum = BucketAuthority(escalation_authority.lower())
        decision_enum = GovernanceAction(escalation_decision.lower())
        
        result = governance_system.escalate_decision(
            decision_id=decision_id,
            escalation_authority=authority_enum,
            escalation_decision=decision_enum,
            escalation_reason=escalation_reason
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(ve)}")
    except Exception as e:
        logger.error(f"Failed to escalate decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/governance/decisions")
async def get_governance_decisions(limit: int = Query(100, ge=1, le=1000)):
    """Get governance decision history"""
    try:
        decisions = governance_system.get_decision_history(limit)
        return {
            "decisions": decisions,
            "count": len(decisions),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to get governance decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Custodianship Endpoints
@app.get("/custodianship/status")
async def get_custodianship_status():
    """Get formal custodianship status"""
    try:
        return custodianship_system.get_custodianship_status()
    except Exception as e:
        logger.error(f"Failed to get custodianship status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/custodianship/baseline")
async def capture_system_baseline():
    """Capture immutable system baseline (Data Sovereign only)"""
    try:
        # This is a constitutional action requiring highest authority
        validation = governance_system.validate_authority_action(
            "capture_baseline", 
            BucketAuthority.DATA_SOVEREIGN
        )
        
        if not validation["authorized"]:
            raise HTTPException(status_code=403, detail="Insufficient authority for baseline capture")
        
        baseline = custodianship_system.capture_system_baseline()
        return {
            "success": True,
            "baseline_captured": True,
            "snapshot_id": baseline["snapshot_id"],
            "constitutional_compliance": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to capture baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/custodianship/integration-boundaries")
async def validate_integration_boundaries():
    """Validate AI integration boundaries"""
    try:
        return custodianship_system.validate_integration_boundaries()
    except Exception as e:
        logger.error(f"Failed to validate integration boundaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/custodianship/provenance-guarantees")
async def validate_provenance_guarantees():
    """Validate provenance sufficiency"""
    try:
        return custodianship_system.validate_provenance_guarantees()
    except Exception as e:
        logger.error(f"Failed to validate provenance guarantees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/custodianship/retention-posture")
async def get_retention_posture():
    """Get retention and deletion posture"""
    try:
        return custodianship_system.get_retention_posture()
    except Exception as e:
        logger.error(f"Failed to get retention posture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Gatekeeping Endpoints
@app.post("/gatekeeping/integration-request")
async def evaluate_integration_request(request: Dict):
    """Evaluate integration request against gate checklist"""
    try:
        evaluation = gatekeeping_system.evaluate_integration_request(request)
        return evaluation
    except Exception as e:
        logger.error(f"Failed to evaluate integration request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gatekeeping/executor-validation")
async def validate_executor_action(validation_request: Dict):
    """Validate executor action permissions"""
    try:
        action = validation_request.get("action")
        executor = validation_request.get("executor", "akanksha")
        
        if not action:
            raise HTTPException(status_code=400, detail="Missing action parameter")
        
        validation = gatekeeping_system.validate_executor_action(action, executor)
        return validation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate executor action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gatekeeping/escalation-evaluation")
async def evaluate_escalation_need(situation: Dict):
    """Evaluate if situation requires escalation to Vijay"""
    try:
        evaluation = gatekeeping_system.evaluate_escalation_need(situation)
        return evaluation
    except Exception as e:
        logger.error(f"Failed to evaluate escalation need: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gatekeeping/status")
async def get_gatekeeping_status():
    """Get complete gatekeeping system status"""
    try:
        return gatekeeping_system.get_complete_gatekeeping_status()
    except Exception as e:
        logger.error(f"Failed to get gatekeeping status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Owner Responsibility Confirmation Endpoint
@app.post("/owner/responsibility-confirmation")
async def confirm_owner_responsibilities(confirmation: Dict):
    """Confirm owner responsibilities and constitutional commitment"""
    try:
        required_confirmations = [
            "bucket_integrity_overrides_product_urgency",
            "rejection_is_acceptable_outcome", 
            "drift_prevention_is_job_responsibility",
            "constitutional_authority_acknowledged"
        ]
        
        missing_confirmations = []
        for req in required_confirmations:
            if not confirmation.get(req, False):
                missing_confirmations.append(req)
        
        if missing_confirmations:
            return {
                "confirmed": False,
                "missing_confirmations": missing_confirmations,
                "message": "All owner responsibilities must be explicitly confirmed"
            }
        
        # Store confirmation in truth engine
        confirmation_record = {
            "owner": "Ashmit Pandey",
            "confirmed_at": datetime.now().isoformat(),
            "confirmations": confirmation,
            "constitutional_commitment": True
        }
        
        truth_engine.store_artifact(
            artifact_type=ArtifactType.CONFIGURATION,
            content=confirmation_record,
            authority=BucketAuthority.DATA_SOVEREIGN,
            metadata={"owner_responsibility_confirmation": True, "immutable": True}
        )
        
        return {
            "confirmed": True,
            "owner": "Ashmit Pandey",
            "constitutional_commitment": True,
            "message": "Owner responsibilities formally confirmed and recorded"
        }
        
    except Exception as e:
        logger.error(f"Failed to confirm owner responsibilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Law Agent Request Models
class BasicLegalQueryRequest(BaseModel):
    user_input: str
    feedback: Optional[str] = None
    session_id: Optional[str] = None

class AdaptiveLegalQueryRequest(BaseModel):
    user_input: str
    enable_learning: bool = True
    feedback: Optional[str] = None
    session_id: Optional[str] = None

class EnhancedLegalQueryRequest(BaseModel):
    user_input: str
    location: Optional[str] = None
    feedback: Optional[str] = None
    session_id: Optional[str] = None

# Law Agent Endpoints
@app.post("/basic-query")
async def process_basic_query(request: BasicLegalQueryRequest):
    """Process a legal query using the basic agent"""
    try:
        # Use the existing run-agent endpoint internally
        agent_input = AgentInput(
            agent_name="law_agent",
            input_data={
                "query": request.user_input,
                "agent_type": "basic",
                "feedback": request.feedback
            },
            stateful=False
        )
        return await run_agent(agent_input)
    except Exception as e:
        logger.error(f"Basic query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/adaptive-query")
async def process_adaptive_query(request: AdaptiveLegalQueryRequest):
    """Process a legal query using the adaptive agent"""
    try:
        agent_input = AgentInput(
            agent_name="law_agent",
            input_data={
                "query": request.user_input,
                "agent_type": "adaptive",
                "feedback": request.feedback
            },
            stateful=False
        )
        return await run_agent(agent_input)
    except Exception as e:
        logger.error(f"Adaptive query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhanced-query")
async def process_enhanced_query(request: EnhancedLegalQueryRequest):
    """Process a legal query using the enhanced agent"""
    try:
        agent_input = AgentInput(
            agent_name="law_agent",
            input_data={
                "query": request.user_input,
                "agent_type": "enhanced",
                "location": request.location,
                "feedback": request.feedback
            },
            stateful=False
        )
        return await run_agent(agent_input)
    except Exception as e:
        logger.error(f"Enhanced query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
