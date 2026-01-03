"""
Suggestion Bot - Intelligent Suggestions and Recommendations
===========================================================

This agent provides intelligent suggestions and recommendations based on context.
"""

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

async def process(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process suggestion request and provide intelligent recommendations
    
    Args:
        input_data: Dictionary containing context, category, and optional schedule
        
    Returns:
        Dictionary with suggestions and recommendations
    """
    try:
        context = input_data.get("context", "")
        category = input_data.get("category", "general")
        schedule = input_data.get("schedule", {})
        
        if not context:
            return {"error": "Context is required for suggestions"}
        
        # Generate suggestions based on context and category
        suggestions = generate_suggestions(context, category, schedule)
        
        result = {
            "context": context,
            "category": category,
            "suggestions": suggestions,
            "priority_suggestions": get_priority_suggestions(suggestions),
            "implementation_tips": get_implementation_tips(category),
            "next_steps": generate_next_steps(context, schedule),
            "status": "suggestions_generated"
        }
        
        logger.info(f"Suggestion bot processed context: {context[:50]}...")
        return result
        
    except Exception as e:
        logger.error(f"Suggestion bot error: {e}")
        return {"error": str(e)}

def generate_suggestions(context: str, category: str, schedule: Dict) -> List[str]:
    """Generate suggestions based on context and category"""
    context_lower = context.lower()
    suggestions = []
    
    # Base suggestions by category
    if category == "workflow":
        suggestions.extend([
            "Implement automated task routing",
            "Create standardized process templates",
            "Set up progress tracking dashboards",
            "Establish clear communication channels",
            "Define role-based access controls"
        ])
        
        if "optimize" in context_lower:
            suggestions.extend([
                "Conduct workflow analysis to identify bottlenecks",
                "Implement parallel processing where possible",
                "Reduce manual handoffs between teams"
            ])
            
    elif category == "productivity":
        suggestions.extend([
            "Use time-blocking techniques",
            "Implement the Pomodoro Technique",
            "Create distraction-free work environments",
            "Set up automated reminders and notifications",
            "Use productivity tracking tools"
        ])
        
    elif category == "optimization":
        suggestions.extend([
            "Analyze current performance metrics",
            "Identify and eliminate redundant processes",
            "Implement continuous improvement cycles",
            "Use data-driven decision making",
            "Establish performance benchmarks"
        ])
        
    else:  # general
        suggestions.extend([
            "Break complex tasks into smaller components",
            "Prioritize tasks based on impact and urgency",
            "Establish regular review and feedback cycles",
            "Document processes for future reference",
            "Create backup plans for critical activities"
        ])
    
    # Add schedule-aware suggestions
    if schedule and schedule.get("priority") == "high":
        suggestions.extend([
            "Allocate additional resources for high-priority tasks",
            "Set up real-time monitoring and alerts",
            "Prepare contingency plans for potential delays"
        ])
    
    return suggestions[:8]  # Limit to top 8 suggestions

def get_priority_suggestions(suggestions: List[str]) -> List[str]:
    """Get top priority suggestions"""
    # Simple priority ranking based on keywords
    priority_keywords = ["automat", "standard", "track", "analyz"]
    
    priority_suggestions = []
    for suggestion in suggestions:
        if any(keyword in suggestion.lower() for keyword in priority_keywords):
            priority_suggestions.append(suggestion)
    
    return priority_suggestions[:3]  # Top 3 priority suggestions

def get_implementation_tips(category: str) -> List[str]:
    """Get implementation tips based on category"""
    tips = {
        "workflow": [
            "Start with pilot testing on a small scale",
            "Get stakeholder buy-in before implementation",
            "Document all process changes",
            "Provide training for affected team members"
        ],
        "productivity": [
            "Start with one technique at a time",
            "Track your progress and adjust as needed",
            "Create accountability systems",
            "Celebrate small wins to maintain motivation"
        ],
        "optimization": [
            "Establish baseline metrics before changes",
            "Implement changes incrementally",
            "Monitor impact continuously",
            "Be prepared to rollback if needed"
        ],
        "general": [
            "Plan implementation in phases",
            "Communicate changes clearly to all stakeholders",
            "Gather feedback regularly",
            "Be flexible and ready to adapt"
        ]
    }
    
    return tips.get(category, tips["general"])

def generate_next_steps(context: str, schedule: Dict) -> List[str]:
    """Generate actionable next steps"""
    next_steps = [
        "Review and prioritize the suggested recommendations",
        "Identify required resources and stakeholders",
        "Create an implementation timeline"
    ]
    
    if schedule:
        task = schedule.get("task", "")
        if task:
            next_steps.extend([
                f"Begin planning for: {task}",
                "Set up progress tracking mechanisms",
                "Schedule regular check-ins with team members"
            ])
    
    next_steps.append("Monitor implementation progress and adjust as needed")
    
    return next_steps