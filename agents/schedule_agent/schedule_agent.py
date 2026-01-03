"""
Schedule Agent - Task Scheduling and Workflow Optimization
=========================================================

This agent handles task scheduling and workflow optimization.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

async def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process scheduling request and provide optimized schedule
    
    Args:
        input_data: Dictionary containing task, priority, and deadline
        
    Returns:
        Dictionary with scheduling recommendations and timeline
    """
    try:
        task = input_data.get("task", "")
        priority = input_data.get("priority", "medium")
        deadline = input_data.get("deadline", "")
        
        if not task:
            return {"error": "Task description is required"}
        
        # Generate schedule based on priority
        schedule = generate_schedule(task, priority, deadline)
        
        result = {
            "task": task,
            "priority": priority,
            "deadline": deadline,
            "schedule": schedule,
            "recommendations": generate_recommendations(priority),
            "estimated_duration": estimate_duration(task),
            "status": "scheduled"
        }
        
        logger.info(f"Schedule agent processed task: {task}")
        return result
        
    except Exception as e:
        logger.error(f"Schedule agent error: {e}")
        return {"error": str(e)}

def generate_schedule(task: str, priority: str, deadline: str) -> Dict[str, Any]:
    """Generate optimized schedule for the task"""
    now = datetime.now()
    
    # Priority-based scheduling
    if priority == "high":
        start_time = now + timedelta(hours=1)
        buffer_time = timedelta(hours=2)
    elif priority == "medium":
        start_time = now + timedelta(hours=4)
        buffer_time = timedelta(hours=4)
    else:  # low priority
        start_time = now + timedelta(days=1)
        buffer_time = timedelta(hours=8)
    
    return {
        "start_time": start_time.isoformat(),
        "buffer_time": str(buffer_time),
        "recommended_duration": "2-4 hours",
        "best_time_slot": "Morning (9-11 AM)" if priority == "high" else "Afternoon (2-4 PM)"
    }

def generate_recommendations(priority: str) -> list:
    """Generate scheduling recommendations based on priority"""
    base_recommendations = [
        "Break task into smaller subtasks",
        "Allocate focused time blocks",
        "Minimize interruptions during execution"
    ]
    
    if priority == "high":
        base_recommendations.extend([
            "Schedule during peak productivity hours",
            "Notify stakeholders of high-priority work",
            "Prepare backup resources"
        ])
    elif priority == "medium":
        base_recommendations.extend([
            "Balance with other medium-priority tasks",
            "Schedule regular progress check-ins"
        ])
    else:
        base_recommendations.extend([
            "Schedule during low-demand periods",
            "Consider batching with similar tasks"
        ])
    
    return base_recommendations

def estimate_duration(task: str) -> str:
    """Estimate task duration based on task description"""
    task_lower = task.lower()
    
    if any(word in task_lower for word in ["optimize", "analyze", "review"]):
        return "2-4 hours"
    elif any(word in task_lower for word in ["implement", "develop", "create"]):
        return "4-8 hours"
    elif any(word in task_lower for word in ["plan", "design", "strategy"]):
        return "1-3 hours"
    else:
        return "2-3 hours"