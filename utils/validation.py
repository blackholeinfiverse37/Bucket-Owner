"""
Input Validation Utilities for BHIV Central Depository
=====================================================

This module provides validation functions for API inputs and data integrity.
"""

import re
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

def validate_agent_name(agent_name: str) -> bool:
    """Validate agent name format"""
    if not agent_name or not isinstance(agent_name, str):
        return False
    
    # Agent names should be alphanumeric with underscores
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, agent_name))

def validate_basket_name(basket_name: str) -> bool:
    """Validate basket name format"""
    if not basket_name or not isinstance(basket_name, str):
        return False
    
    # Basket names should be alphanumeric with underscores and hyphens
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, basket_name))

def validate_artifact_id(artifact_id: str) -> bool:
    """Validate artifact ID format (UUID)"""
    if not artifact_id or not isinstance(artifact_id, str):
        return False
    
    # UUID pattern
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, artifact_id.lower()))

def sanitize_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent injection attacks"""
    if not isinstance(data, dict):
        return {}
    
    sanitized = {}
    for key, value in data.items():
        # Sanitize key
        if isinstance(key, str) and len(key) <= 100:
            clean_key = re.sub(r'[^\w\-_.]', '', key)
            
            # Sanitize value
            if isinstance(value, str):
                # Remove potentially dangerous characters
                clean_value = re.sub(r'[<>"\']', '', value)
                sanitized[clean_key] = clean_value[:1000]  # Limit length
            elif isinstance(value, (int, float, bool)):
                sanitized[clean_key] = value
            elif isinstance(value, dict):
                sanitized[clean_key] = sanitize_input_data(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    sanitize_input_data(item) if isinstance(item, dict) 
                    else str(item)[:100] if isinstance(item, str)
                    else item
                    for item in value[:10]  # Limit list size
                ]
    
    return sanitized

def validate_authority_level(authority: str) -> bool:
    """Validate authority level"""
    valid_authorities = ["data_sovereign", "strategic_advisor", "executor", "ai_agent"]
    return authority.lower() in valid_authorities

def validate_json_structure(data: Any, max_depth: int = 10, current_depth: int = 0) -> bool:
    """Validate JSON structure to prevent deeply nested objects"""
    if current_depth > max_depth:
        return False
    
    if isinstance(data, dict):
        if len(data) > 100:  # Limit number of keys
            return False
        for key, value in data.items():
            if not isinstance(key, str) or len(key) > 100:
                return False
            if not validate_json_structure(value, max_depth, current_depth + 1):
                return False
    elif isinstance(data, list):
        if len(data) > 100:  # Limit list size
            return False
        for item in data:
            if not validate_json_structure(item, max_depth, current_depth + 1):
                return False
    elif isinstance(data, str):
        if len(data) > 10000:  # Limit string length
            return False
    
    return True