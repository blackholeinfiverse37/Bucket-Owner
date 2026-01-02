"""
BHIV Bucket AI Integration Firewall
===================================

This module enforces the constitutional rule:
"AI can WRITE to Bucket, Bucket never DEPENDS on AI"

It prevents:
- AI logic leaking into storage
- AI overwriting its own past
- Feedback loops that destroy truth
- AI hallucinations in permanent storage
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime
import json
import re

from .constitutional_lock import CONSTITUTIONAL_LOCK, BucketAuthority
from .truth_engine import get_truth_engine, ArtifactType
from utils.logger import get_logger

logger = get_logger(__name__)

class AIFirewallAction(Enum):
    """Actions the AI firewall can take"""
    ALLOW = "allow"
    SANITIZE = "sanitize"
    REJECT = "reject"
    QUARANTINE = "quarantine"

class ArtifactClass(Enum):
    """Approved artifact classes for AI storage"""
    EXECUTION_RESULT = "execution_result"
    AGENT_OUTPUT = "agent_output"
    USER_INTERACTION = "user_interaction"
    SYSTEM_STATE = "system_state"
    MEDIA_CONTENT = "media_content"
    CONFIGURATION_DATA = "configuration_data"

class AIIntegrationFirewall:
    """
    Firewall that enforces safe AI-to-storage communication
    
    Responsibilities:
    - Validate AI outputs before storage
    - Sanitize AI logic contamination
    - Enforce artifact class restrictions
    - Prevent feedback loops
    - Block AI hallucinations
    """
    
    def __init__(self):
        self.truth_engine = get_truth_engine()
        
        # AI logic contamination patterns
        self.contamination_patterns = {
            "reasoning_fields": [
                "reasoning", "thought_process", "internal_logic", "decision_tree",
                "inference_chain", "cognitive_process", "mental_model"
            ],
            "hallucination_indicators": [
                "i_think", "i_believe", "probably", "might_be", "seems_like",
                "appears_to", "likely", "uncertain", "guess", "assume"
            ],
            "temporal_confusion": [
                "remember", "recall", "previously_said", "earlier_mentioned",
                "last_time", "before", "history_shows"
            ],
            "self_reference": [
                "my_previous", "i_generated", "i_created", "my_output",
                "i_stored", "my_memory", "i_learned"
            ]
        }
        
        # Approved artifact schemas
        self.approved_schemas = {
            ArtifactClass.EXECUTION_RESULT: {
                "required_fields": ["result", "status", "execution_id"],
                "allowed_fields": ["result", "status", "execution_id", "metadata", "timestamp"],
                "forbidden_fields": ["reasoning", "thought_process", "internal_state"]
            },
            ArtifactClass.AGENT_OUTPUT: {
                "required_fields": ["output", "agent_name"],
                "allowed_fields": ["output", "agent_name", "input_hash", "timestamp", "version"],
                "forbidden_fields": ["decision_process", "inference", "belief"]
            },
            ArtifactClass.USER_INTERACTION: {
                "required_fields": ["user_input", "timestamp"],
                "allowed_fields": ["user_input", "timestamp", "session_id", "context"],
                "forbidden_fields": ["ai_interpretation", "inferred_intent"]
            }
        }
        
        logger.info("AI Integration Firewall initialized")
    
    def validate_ai_artifact(self, artifact_data: Dict[str, Any], 
                           artifact_class: ArtifactClass) -> Dict[str, Any]:
        """
        Validate AI artifact against firewall rules
        
        Returns:
            Dict with validation result and recommended action
        """
        validation_result = {
            "action": AIFirewallAction.ALLOW,
            "valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_data": None,
            "contamination_detected": False
        }
        
        try:
            # Check for AI logic contamination
            contamination_check = self._detect_contamination(artifact_data)
            if contamination_check["contaminated"]:
                validation_result["contamination_detected"] = True
                validation_result["warnings"].extend(contamination_check["issues"])
                
                if contamination_check["severity"] == "high":
                    validation_result["action"] = AIFirewallAction.REJECT
                    validation_result["valid"] = False
                    validation_result["errors"].append("High-severity AI logic contamination detected")
                else:
                    validation_result["action"] = AIFirewallAction.SANITIZE
                    validation_result["sanitized_data"] = self._sanitize_artifact(artifact_data)
            
            # Validate against approved schema
            schema_validation = self._validate_schema(artifact_data, artifact_class)
            if not schema_validation["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].extend(schema_validation["errors"])
                if validation_result["action"] == AIFirewallAction.ALLOW:
                    validation_result["action"] = AIFirewallAction.REJECT
            
            # Check for feedback loop risks
            feedback_check = self._check_feedback_loops(artifact_data)
            if feedback_check["risk_detected"]:
                validation_result["warnings"].extend(feedback_check["warnings"])
                if feedback_check["severity"] == "high":
                    validation_result["action"] = AIFirewallAction.QUARANTINE
            
            # Final constitutional validation
            if validation_result["valid"]:
                constitutional_check = CONSTITUTIONAL_LOCK.validate_artifact({
                    "artifact_type": ArtifactType.AI_OUTPUT.value,
                    "content": validation_result.get("sanitized_data", artifact_data),
                    "created_at": datetime.now().isoformat(),
                    "content_hash": "placeholder",
                    "is_root": True
                })
                
                if not constitutional_check["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(constitutional_check["errors"])
                    validation_result["action"] = AIFirewallAction.REJECT
            
            logger.info(f"AI artifact validation: {validation_result['action'].value}")
            return validation_result
            
        except Exception as e:
            logger.error(f"AI artifact validation failed: {e}")
            return {
                "action": AIFirewallAction.REJECT,
                "valid": False,
                "errors": [f"Validation system error: {str(e)}"],
                "warnings": [],
                "contamination_detected": False
            }
    
    def _detect_contamination(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect AI logic contamination in data"""
        contamination_result = {
            "contaminated": False,
            "severity": "low",
            "issues": []
        }
        
        data_str = json.dumps(data).lower()
        
        # Check for reasoning fields
        for pattern in self.contamination_patterns["reasoning_fields"]:
            if pattern in data_str:
                contamination_result["contaminated"] = True
                contamination_result["issues"].append(f"Reasoning field detected: {pattern}")
                contamination_result["severity"] = "high"
        
        # Check for hallucination indicators
        hallucination_count = 0
        for pattern in self.contamination_patterns["hallucination_indicators"]:
            if pattern in data_str:
                hallucination_count += 1
                contamination_result["contaminated"] = True
                contamination_result["issues"].append(f"Hallucination indicator: {pattern}")
        
        if hallucination_count > 2:
            contamination_result["severity"] = "high"
        
        # Check for temporal confusion
        for pattern in self.contamination_patterns["temporal_confusion"]:
            if pattern in data_str:
                contamination_result["contaminated"] = True
                contamination_result["issues"].append(f"Temporal confusion: {pattern}")
                contamination_result["severity"] = "medium"
        
        # Check for self-reference
        for pattern in self.contamination_patterns["self_reference"]:
            if pattern in data_str:
                contamination_result["contaminated"] = True
                contamination_result["issues"].append(f"AI self-reference: {pattern}")
                contamination_result["severity"] = "high"
        
        return contamination_result
    
    def _sanitize_artifact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize artifact by removing AI logic contamination"""
        sanitized = data.copy()
        
        # Remove reasoning fields
        reasoning_fields = [
            "reasoning", "thought_process", "internal_logic", "decision_tree",
            "inference_chain", "cognitive_process", "mental_model", "analysis",
            "interpretation", "belief", "assumption", "guess"
        ]
        
        for field in reasoning_fields:
            if field in sanitized:
                del sanitized[field]
                logger.info(f"Removed contaminated field: {field}")
        
        # Sanitize text content
        for key, value in sanitized.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_artifact(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_artifact(item) if isinstance(item, dict) 
                    else self._sanitize_text(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
        
        return sanitized
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text content"""
        # Remove hallucination indicators
        hallucination_patterns = [
            r'\bi think\b', r'\bi believe\b', r'\bprobably\b', r'\bmight be\b',
            r'\bseems like\b', r'\bappears to\b', r'\blikely\b', r'\buncertain\b'
        ]
        
        sanitized_text = text
        for pattern in hallucination_patterns:
            sanitized_text = re.sub(pattern, '[SANITIZED]', sanitized_text, flags=re.IGNORECASE)
        
        return sanitized_text
    
    def _validate_schema(self, data: Dict[str, Any], 
                        artifact_class: ArtifactClass) -> Dict[str, Any]:
        """Validate data against approved schema"""
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        if artifact_class not in self.approved_schemas:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unknown artifact class: {artifact_class}")
            return validation_result
        
        schema = self.approved_schemas[artifact_class]
        
        # Check required fields
        for field in schema["required_fields"]:
            if field not in data:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Check forbidden fields
        for field in schema["forbidden_fields"]:
            if field in data:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Forbidden field detected: {field}")
        
        # Check allowed fields
        for field in data.keys():
            if field not in schema["allowed_fields"]:
                validation_result["errors"].append(f"Unexpected field: {field}")
        
        return validation_result
    
    def _check_feedback_loops(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for potential feedback loop risks"""
        feedback_result = {
            "risk_detected": False,
            "severity": "low",
            "warnings": []
        }
        
        data_str = json.dumps(data).lower()
        
        # Check for self-modification attempts
        self_modification_patterns = [
            "update_self", "modify_behavior", "change_parameters", "learn_from",
            "adapt_based_on", "improve_performance", "optimize_self"
        ]
        
        for pattern in self_modification_patterns:
            if pattern in data_str:
                feedback_result["risk_detected"] = True
                feedback_result["severity"] = "high"
                feedback_result["warnings"].append(f"Self-modification risk: {pattern}")
        
        # Check for recursive references
        if "recursive" in data_str or "self_reference" in data_str:
            feedback_result["risk_detected"] = True
            feedback_result["warnings"].append("Recursive reference detected")
        
        return feedback_result
    
    def process_ai_output(self, agent_name: str, output_data: Dict[str, Any],
                         artifact_class: ArtifactClass = ArtifactClass.AGENT_OUTPUT) -> Dict[str, Any]:
        """
        Process AI output through firewall and store if approved
        
        Returns:
            Dict with processing result and storage status
        """
        try:
            # Validate through firewall
            validation = self.validate_ai_artifact(output_data, artifact_class)
            
            if validation["action"] == AIFirewallAction.REJECT:
                logger.warning(f"AI output rejected for {agent_name}: {validation['errors']}")
                return {
                    "success": False,
                    "action": "rejected",
                    "reason": validation["errors"],
                    "constitutional_compliance": False
                }
            
            # Determine final data to store
            final_data = output_data
            if validation["action"] == AIFirewallAction.SANITIZE:
                final_data = validation["sanitized_data"]
                logger.info(f"AI output sanitized for {agent_name}")
            
            if validation["action"] == AIFirewallAction.QUARANTINE:
                # Store in quarantine with special metadata
                storage_result = self.truth_engine.store_artifact(
                    artifact_type=ArtifactType.AI_OUTPUT,
                    content=final_data,
                    authority=BucketAuthority.AI_AGENT,
                    metadata={
                        "quarantined": True,
                        "quarantine_reason": validation["warnings"],
                        "agent_name": agent_name,
                        "firewall_action": validation["action"].value
                    }
                )
            else:
                # Normal storage
                storage_result = self.truth_engine.store_artifact(
                    artifact_type=ArtifactType.AI_OUTPUT,
                    content=final_data,
                    authority=BucketAuthority.AI_AGENT,
                    metadata={
                        "agent_name": agent_name,
                        "firewall_action": validation["action"].value,
                        "contamination_detected": validation["contamination_detected"]
                    }
                )
            
            if storage_result["success"]:
                logger.info(f"AI output stored for {agent_name}: {storage_result['artifact_id']}")
                return {
                    "success": True,
                    "action": validation["action"].value,
                    "artifact_id": storage_result["artifact_id"],
                    "constitutional_compliance": True,
                    "warnings": validation.get("warnings", [])
                }
            else:
                return {
                    "success": False,
                    "action": "storage_failed",
                    "reason": storage_result.get("error", "Unknown storage error"),
                    "constitutional_compliance": False
                }
                
        except Exception as e:
            logger.error(f"AI output processing failed for {agent_name}: {e}")
            return {
                "success": False,
                "action": "processing_error",
                "reason": str(e),
                "constitutional_compliance": False
            }

# Global firewall instance
ai_firewall = None

def get_ai_firewall() -> AIIntegrationFirewall:
    """Get global AI Integration Firewall instance"""
    global ai_firewall
    if ai_firewall is None:
        ai_firewall = AIIntegrationFirewall()
    return ai_firewall