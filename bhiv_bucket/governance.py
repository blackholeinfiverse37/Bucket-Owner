"""
BHIV Bucket Governance System
=============================

This module implements the authority hierarchy and escalation procedures
for the BHIV Bucket system.

Authority Levels:
- Data Sovereign: Primary bucket owner (highest authority)
- Strategic Advisor: Vijay role (advisory authority)
- Executor: Akanksha role (execution authority)
- AI Agent: AI systems (lowest authority)
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json

from .constitutional_lock import CONSTITUTIONAL_LOCK, BucketAuthority
from .truth_engine import get_truth_engine, ArtifactType
from utils.logger import get_logger

logger = get_logger(__name__)

class EscalationLevel(Enum):
    """Escalation levels for governance decisions"""
    NONE = "none"
    EXECUTOR = "executor"
    STRATEGIC_ADVISOR = "strategic_advisor"
    DATA_SOVEREIGN = "data_sovereign"

class GovernanceAction(Enum):
    """Types of governance actions"""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    DEFER = "defer"
    REQUIRE_REVIEW = "require_review"

class GovernanceDecision:
    """Represents a governance decision"""
    
    def __init__(self, action: str, authority: BucketAuthority, 
                 decision: GovernanceAction, reason: str = "",
                 escalation_required: bool = False):
        self.id = f"decision_{int(datetime.now().timestamp())}"
        self.action = action
        self.authority = authority
        self.decision = decision
        self.reason = reason
        self.escalation_required = escalation_required
        self.timestamp = datetime.now().isoformat()
        self.escalated_to = None
        self.final_decision = None

class BHIVGovernance:
    """
    Governance system for BHIV Bucket
    
    Responsibilities:
    - Enforce authority hierarchy
    - Manage escalation procedures
    - Track governance decisions
    - Prevent unauthorized actions
    """
    
    def __init__(self):
        self.truth_engine = get_truth_engine()
        
        # Authority permissions matrix
        self.authority_permissions = {
            BucketAuthority.DATA_SOVEREIGN: {
                "modify_schema": True,
                "delete_permanently": True,
                "bypass_rules": True,
                "change_authority": True,
                "unlock_constitution": True,
                "approve_escalations": True,
                "override_decisions": True,
                "access_all_artifacts": True
            },
            BucketAuthority.STRATEGIC_ADVISOR: {
                "modify_schema": False,
                "delete_permanently": False,
                "bypass_rules": False,
                "change_authority": False,
                "unlock_constitution": False,
                "approve_escalations": True,
                "override_decisions": False,
                "access_all_artifacts": True,
                "provide_guidance": True
            },
            BucketAuthority.EXECUTOR: {
                "modify_schema": False,
                "delete_permanently": False,
                "bypass_rules": False,
                "change_authority": False,
                "unlock_constitution": False,
                "approve_escalations": False,
                "override_decisions": False,
                "access_all_artifacts": False,
                "execute_approved_actions": True,
                "create_artifacts": True
            },
            BucketAuthority.AI_AGENT: {
                "modify_schema": False,
                "delete_permanently": False,
                "bypass_rules": False,
                "change_authority": False,
                "unlock_constitution": False,
                "approve_escalations": False,
                "override_decisions": False,
                "access_all_artifacts": False,
                "execute_approved_actions": False,
                "create_artifacts": True,
                "write_only": True
            }
        }
        
        # Actions requiring escalation
        self.escalation_required_actions = {
            "modify_constitutional_rules": EscalationLevel.DATA_SOVEREIGN,
            "permanent_deletion": EscalationLevel.DATA_SOVEREIGN,
            "schema_changes": EscalationLevel.STRATEGIC_ADVISOR,
            "authority_changes": EscalationLevel.DATA_SOVEREIGN,
            "bypass_firewall": EscalationLevel.STRATEGIC_ADVISOR,
            "bulk_operations": EscalationLevel.EXECUTOR,
            "external_integrations": EscalationLevel.STRATEGIC_ADVISOR
        }
        
        # Decision history
        self.decision_history = []
        
        logger.info("BHIV Governance system initialized")
    
    def validate_authority_action(self, action: str, authority: BucketAuthority) -> Dict[str, Any]:
        """
        Validate if authority can perform action
        
        Returns:
            Dict with validation result and escalation requirements
        """
        validation_result = {
            "authorized": False,
            "escalation_required": False,
            "escalation_level": EscalationLevel.NONE,
            "reason": "",
            "decision_id": None
        }
        
        try:
            # Check constitutional validation first
            constitutional_valid = CONSTITUTIONAL_LOCK.validate_authority(action, authority)
            if not constitutional_valid:
                validation_result["reason"] = "Constitutional authority validation failed"
                validation_result["escalation_required"] = True
                validation_result["escalation_level"] = EscalationLevel.DATA_SOVEREIGN
                return validation_result
            
            # Check permission matrix
            permissions = self.authority_permissions.get(authority, {})
            
            # Check if action requires escalation
            if action in self.escalation_required_actions:
                required_level = self.escalation_required_actions[action]
                validation_result["escalation_required"] = True
                validation_result["escalation_level"] = required_level
                
                # Check if current authority meets escalation level
                authority_levels = {
                    BucketAuthority.AI_AGENT: 1,
                    BucketAuthority.EXECUTOR: 2,
                    BucketAuthority.STRATEGIC_ADVISOR: 3,
                    BucketAuthority.DATA_SOVEREIGN: 4
                }
                
                escalation_levels = {
                    EscalationLevel.EXECUTOR: 2,
                    EscalationLevel.STRATEGIC_ADVISOR: 3,
                    EscalationLevel.DATA_SOVEREIGN: 4
                }
                
                current_level = authority_levels.get(authority, 0)
                required_authority_level = escalation_levels.get(required_level, 4)
                
                if current_level >= required_authority_level:
                    validation_result["authorized"] = True
                    validation_result["escalation_required"] = False
                    validation_result["reason"] = "Authority level sufficient"
                else:
                    validation_result["reason"] = f"Requires escalation to {required_level.value}"
            
            # Check specific permissions
            elif action in permissions:
                validation_result["authorized"] = permissions[action]
                validation_result["reason"] = "Permission granted" if permissions[action] else "Permission denied"
            
            # Default permission check
            else:
                # AI agents can only write, others need explicit permission
                if authority == BucketAuthority.AI_AGENT:
                    validation_result["authorized"] = action.startswith("write_") or action == "create_artifacts"
                    validation_result["reason"] = "AI agent write-only access"
                else:
                    validation_result["escalation_required"] = True
                    validation_result["escalation_level"] = EscalationLevel.STRATEGIC_ADVISOR
                    validation_result["reason"] = "Unknown action requires review"
            
            # Create governance decision record
            decision = GovernanceDecision(
                action=action,
                authority=authority,
                decision=GovernanceAction.APPROVE if validation_result["authorized"] else GovernanceAction.ESCALATE,
                reason=validation_result["reason"],
                escalation_required=validation_result["escalation_required"]
            )
            
            self.decision_history.append(decision)
            validation_result["decision_id"] = decision.id
            
            # Store decision in truth engine
            self._store_governance_decision(decision)
            
            logger.info(f"Authority validation: {action} by {authority.value} - {validation_result['reason']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Authority validation error: {e}")
            return {
                "authorized": False,
                "escalation_required": True,
                "escalation_level": EscalationLevel.DATA_SOVEREIGN,
                "reason": f"Validation error: {str(e)}",
                "decision_id": None
            }
    
    def escalate_decision(self, decision_id: str, escalation_authority: BucketAuthority,
                         escalation_decision: GovernanceAction, 
                         escalation_reason: str = "") -> Dict[str, Any]:
        """
        Escalate a governance decision to higher authority
        
        Returns:
            Dict with escalation result
        """
        try:
            # Find original decision
            original_decision = None
            for decision in self.decision_history:
                if decision.id == decision_id:
                    original_decision = decision
                    break
            
            if not original_decision:
                return {
                    "success": False,
                    "error": "Original decision not found"
                }
            
            # Validate escalation authority
            escalation_validation = self.validate_authority_action(
                f"escalate_{original_decision.action}",
                escalation_authority
            )
            
            if not escalation_validation["authorized"]:
                return {
                    "success": False,
                    "error": "Insufficient authority for escalation"
                }
            
            # Update original decision
            original_decision.escalated_to = escalation_authority
            original_decision.final_decision = escalation_decision
            
            # Create escalation record
            escalation_record = {
                "original_decision_id": decision_id,
                "escalation_authority": escalation_authority.value,
                "escalation_decision": escalation_decision.value,
                "escalation_reason": escalation_reason,
                "escalated_at": datetime.now().isoformat()
            }
            
            # Store escalation in truth engine
            self.truth_engine.store_artifact(
                artifact_type=ArtifactType.SYSTEM_LOG,
                content=escalation_record,
                authority=escalation_authority,
                metadata={"governance_escalation": True}
            )
            
            logger.info(f"Decision escalated: {decision_id} to {escalation_authority.value}")
            
            return {
                "success": True,
                "escalation_decision": escalation_decision.value,
                "escalated_to": escalation_authority.value,
                "final_authority": True if escalation_authority == BucketAuthority.DATA_SOVEREIGN else False
            }
            
        except Exception as e:
            logger.error(f"Escalation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_governance_checklist(self, authority: BucketAuthority) -> Dict[str, Any]:
        """
        Get governance checklist for authority level
        
        Returns:
            Dict with allowed actions and restrictions
        """
        permissions = self.authority_permissions.get(authority, {})
        
        checklist = {
            "authority_level": authority.value,
            "allowed_actions": [],
            "restricted_actions": [],
            "escalation_actions": [],
            "constitutional_compliance": True
        }
        
        for action, allowed in permissions.items():
            if allowed:
                checklist["allowed_actions"].append(action)
            else:
                checklist["restricted_actions"].append(action)
        
        # Add escalation actions
        for action, escalation_level in self.escalation_required_actions.items():
            checklist["escalation_actions"].append({
                "action": action,
                "requires_escalation_to": escalation_level.value
            })
        
        return checklist
    
    def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent governance decisions"""
        recent_decisions = self.decision_history[-limit:] if limit else self.decision_history
        
        return [
            {
                "id": decision.id,
                "action": decision.action,
                "authority": decision.authority.value,
                "decision": decision.decision.value,
                "reason": decision.reason,
                "timestamp": decision.timestamp,
                "escalated": decision.escalated_to.value if decision.escalated_to else None,
                "final_decision": decision.final_decision.value if decision.final_decision else None
            }
            for decision in recent_decisions
        ]
    
    def _store_governance_decision(self, decision: GovernanceDecision):
        """Store governance decision in truth engine"""
        try:
            decision_data = {
                "decision_id": decision.id,
                "action": decision.action,
                "authority": decision.authority.value,
                "decision": decision.decision.value,
                "reason": decision.reason,
                "escalation_required": decision.escalation_required,
                "timestamp": decision.timestamp
            }
            
            self.truth_engine.store_artifact(
                artifact_type=ArtifactType.SYSTEM_LOG,
                content=decision_data,
                authority=BucketAuthority.DATA_SOVEREIGN,  # Governance decisions are sovereign
                metadata={"governance_decision": True}
            )
            
        except Exception as e:
            logger.warning(f"Failed to store governance decision: {e}")
    
    def get_governance_stats(self) -> Dict[str, Any]:
        """Get governance system statistics"""
        try:
            total_decisions = len(self.decision_history)
            escalated_decisions = sum(1 for d in self.decision_history if d.escalation_required)
            
            decisions_by_authority = {}
            for decision in self.decision_history:
                auth = decision.authority.value
                decisions_by_authority[auth] = decisions_by_authority.get(auth, 0) + 1
            
            return {
                "total_decisions": total_decisions,
                "escalated_decisions": escalated_decisions,
                "escalation_rate": escalated_decisions / total_decisions if total_decisions > 0 else 0,
                "decisions_by_authority": decisions_by_authority,
                "constitutional_compliance": CONSTITUTIONAL_LOCK._verify_integrity(),
                "governance_active": True
            }
            
        except Exception as e:
            logger.error(f"Failed to get governance stats: {e}")
            return {
                "error": str(e),
                "governance_active": False
            }

# Global governance instance
governance_system = None

def get_governance_system() -> BHIVGovernance:
    """Get global governance system instance"""
    global governance_system
    if governance_system is None:
        governance_system = BHIVGovernance()
    return governance_system