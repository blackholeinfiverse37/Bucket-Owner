"""
BHIV Bucket Gatekeeping System
==============================

This module implements integration gatekeeping and executor lane enforcement:
- Prevents silent integrations
- Enforces integration approval process
- Manages executor permissions (Akanksha)
- Escalation protocols (Vijay)
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from enum import Enum

from .constitutional_lock import CONSTITUTIONAL_LOCK, BucketAuthority
from .truth_engine import get_truth_engine, ArtifactType
from .governance import get_governance_system, GovernanceAction, EscalationLevel
from utils.logger import get_logger

logger = get_logger(__name__)

class IntegrationStatus(Enum):
    """Integration request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_ESCALATION = "requires_escalation"

class ExecutorPermission(Enum):
    """Executor permission levels"""
    ALLOWED = "allowed"
    REQUIRES_APPROVAL = "requires_approval"
    FORBIDDEN = "forbidden"

class IntegrationGatekeeper:
    """Prevents unauthorized integrations with BHIV Bucket"""
    
    def __init__(self):
        self.truth_engine = get_truth_engine()
        self.governance_system = get_governance_system()
        
        # Integration gate checklist
        self.gate_checklist = {
            "technical_requirements": [
                "respects_write_only_boundary",
                "no_reverse_dependencies",
                "uses_approved_artifact_classes",
                "implements_error_handling",
                "follows_constitutional_rules"
            ],
            "governance_requirements": [
                "formal_integration_request",
                "authority_level_specified",
                "business_justification_provided",
                "risk_assessment_completed",
                "rollback_plan_documented"
            ],
            "compliance_requirements": [
                "data_privacy_compliant",
                "audit_trail_maintained",
                "provenance_preserved",
                "retention_policy_respected",
                "constitutional_alignment_verified"
            ]
        }
        
        # Automatic rejection criteria
        self.rejection_criteria = [
            "attempts_bucket_logic_modification",
            "bypasses_constitutional_rules",
            "creates_reverse_dependencies",
            "violates_authority_hierarchy",
            "compromises_data_integrity",
            "lacks_proper_authorization"
        ]
        
        # Integration history
        self.integration_requests = []
        
        logger.info("Integration Gatekeeper initialized")
    
    def evaluate_integration_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate integration request against gate checklist"""
        evaluation = {
            "request_id": f"integration_{int(datetime.now().timestamp())}",
            "status": IntegrationStatus.PENDING,
            "checklist_results": {},
            "rejection_reasons": [],
            "approval_conditions": [],
            "escalation_required": False,
            "decision_rationale": ""
        }
        
        try:
            # Extract request details
            integration_name = request.get("integration_name", "unnamed")
            requesting_authority = BucketAuthority(request.get("authority", "ai_agent"))
            integration_type = request.get("integration_type", "unknown")
            
            # Evaluate technical requirements
            tech_score = self._evaluate_technical_requirements(request)
            evaluation["checklist_results"]["technical"] = tech_score
            
            # Evaluate governance requirements
            gov_score = self._evaluate_governance_requirements(request)
            evaluation["checklist_results"]["governance"] = gov_score
            
            # Evaluate compliance requirements
            compliance_score = self._evaluate_compliance_requirements(request)
            evaluation["checklist_results"]["compliance"] = compliance_score
            
            # Check for automatic rejection criteria
            rejection_flags = self._check_rejection_criteria(request)
            if rejection_flags:
                evaluation["status"] = IntegrationStatus.REJECTED
                evaluation["rejection_reasons"] = rejection_flags
                evaluation["decision_rationale"] = "Failed automatic rejection criteria"
            
            # Calculate overall score
            overall_score = (tech_score["score"] + gov_score["score"] + compliance_score["score"]) / 3
            
            # Make decision based on score and authority
            if evaluation["status"] == IntegrationStatus.PENDING:
                if overall_score >= 0.8:
                    # High score - check authority level
                    if requesting_authority in [BucketAuthority.DATA_SOVEREIGN, BucketAuthority.STRATEGIC_ADVISOR]:
                        evaluation["status"] = IntegrationStatus.APPROVED
                        evaluation["decision_rationale"] = "High score with sufficient authority"
                    else:
                        evaluation["status"] = IntegrationStatus.REQUIRES_ESCALATION
                        evaluation["escalation_required"] = True
                        evaluation["decision_rationale"] = "High score but requires higher authority approval"
                
                elif overall_score >= 0.6:
                    # Medium score - requires escalation
                    evaluation["status"] = IntegrationStatus.REQUIRES_ESCALATION
                    evaluation["escalation_required"] = True
                    evaluation["decision_rationale"] = "Medium score requires strategic review"
                
                else:
                    # Low score - rejected
                    evaluation["status"] = IntegrationStatus.REJECTED
                    evaluation["rejection_reasons"].append("Insufficient overall score")
                    evaluation["decision_rationale"] = "Low score fails minimum requirements"
            
            # Store evaluation
            self.integration_requests.append(evaluation)
            
            # Store in truth engine
            self.truth_engine.store_artifact(
                artifact_type=ArtifactType.SYSTEM_LOG,
                content={
                    "integration_evaluation": evaluation,
                    "request_details": request
                },
                authority=BucketAuthority.DATA_SOVEREIGN,
                metadata={"integration_gatekeeping": True}
            )
            
            logger.info(f"Integration evaluation completed: {integration_name} - {evaluation['status'].value}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Integration evaluation failed: {e}")
            return {
                "request_id": "error",
                "status": IntegrationStatus.REJECTED,
                "rejection_reasons": [f"Evaluation error: {str(e)}"],
                "decision_rationale": "System error during evaluation"
            }
    
    def _evaluate_technical_requirements(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate technical requirements"""
        score = 0
        max_score = len(self.gate_checklist["technical_requirements"])
        details = {}
        
        for requirement in self.gate_checklist["technical_requirements"]:
            passed = request.get(f"technical_{requirement}", False)
            details[requirement] = passed
            if passed:
                score += 1
        
        return {
            "score": score / max_score,
            "details": details,
            "passed": score == max_score
        }
    
    def _evaluate_governance_requirements(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate governance requirements"""
        score = 0
        max_score = len(self.gate_checklist["governance_requirements"])
        details = {}
        
        for requirement in self.gate_checklist["governance_requirements"]:
            passed = request.get(f"governance_{requirement}", False)
            details[requirement] = passed
            if passed:
                score += 1
        
        return {
            "score": score / max_score,
            "details": details,
            "passed": score == max_score
        }
    
    def _evaluate_compliance_requirements(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate compliance requirements"""
        score = 0
        max_score = len(self.gate_checklist["compliance_requirements"])
        details = {}
        
        for requirement in self.gate_checklist["compliance_requirements"]:
            passed = request.get(f"compliance_{requirement}", False)
            details[requirement] = passed
            if passed:
                score += 1
        
        return {
            "score": score / max_score,
            "details": details,
            "passed": score == max_score
        }
    
    def _check_rejection_criteria(self, request: Dict[str, Any]) -> List[str]:
        """Check for automatic rejection criteria"""
        violations = []
        
        for criterion in self.rejection_criteria:
            if request.get(f"violation_{criterion}", False):
                violations.append(criterion)
        
        return violations
    
    def get_integration_gate_checklist(self) -> Dict[str, Any]:
        """Get complete integration gate checklist"""
        return {
            "checklist": self.gate_checklist,
            "rejection_criteria": self.rejection_criteria,
            "evaluation_process": {
                "technical_weight": 0.33,
                "governance_weight": 0.33,
                "compliance_weight": 0.34,
                "minimum_score": 0.6,
                "approval_score": 0.8
            },
            "authority_requirements": {
                "automatic_approval": ["data_sovereign"],
                "escalation_required": ["executor", "ai_agent"],
                "advisory_consultation": ["strategic_advisor"]
            }
        }

class ExecutorLaneEnforcement:
    """Manages executor permissions and enforcement"""
    
    def __init__(self):
        self.truth_engine = get_truth_engine()
        
        # Akanksha's executor permissions
        self.executor_permissions = {
            # Allowed without approval
            "allowed_actions": [
                "run_existing_baskets",
                "execute_approved_agents",
                "create_standard_artifacts",
                "view_execution_logs",
                "generate_reports",
                "perform_routine_maintenance"
            ],
            
            # Requires owner approval
            "approval_required": [
                "create_new_baskets",
                "modify_agent_configurations",
                "change_system_settings",
                "access_governance_functions",
                "perform_bulk_operations",
                "integrate_external_systems"
            ],
            
            # Forbidden actions
            "forbidden_actions": [
                "modify_constitutional_rules",
                "change_authority_hierarchy",
                "bypass_firewall_rules",
                "delete_artifacts_permanently",
                "modify_schema_structure",
                "override_governance_decisions"
            ]
        }
        
        # Review checkpoints
        self.review_checkpoints = {
            "daily_review": ["execution_summary", "error_reports", "performance_metrics"],
            "weekly_review": ["system_health", "compliance_status", "governance_decisions"],
            "monthly_review": ["integration_requests", "authority_usage", "constitutional_compliance"]
        }
        
        logger.info("Executor Lane Enforcement initialized")
    
    def validate_executor_action(self, action: str, executor: str = "akanksha") -> Dict[str, Any]:
        """Validate if executor can perform action"""
        validation = {
            "action": action,
            "executor": executor,
            "permission": ExecutorPermission.FORBIDDEN,
            "rationale": "",
            "approval_required": False,
            "escalation_needed": False
        }
        
        try:
            # Check allowed actions
            if action in self.executor_permissions["allowed_actions"]:
                validation["permission"] = ExecutorPermission.ALLOWED
                validation["rationale"] = "Action in allowed list"
            
            # Check approval required actions
            elif action in self.executor_permissions["approval_required"]:
                validation["permission"] = ExecutorPermission.REQUIRES_APPROVAL
                validation["approval_required"] = True
                validation["rationale"] = "Action requires owner approval"
            
            # Check forbidden actions
            elif action in self.executor_permissions["forbidden_actions"]:
                validation["permission"] = ExecutorPermission.FORBIDDEN
                validation["escalation_needed"] = True
                validation["rationale"] = "Action forbidden for executor role"
            
            # Unknown action - requires approval
            else:
                validation["permission"] = ExecutorPermission.REQUIRES_APPROVAL
                validation["approval_required"] = True
                validation["rationale"] = "Unknown action requires review"
            
            # Log validation
            logger.info(f"Executor validation: {action} - {validation['permission'].value}")
            
            return validation
            
        except Exception as e:
            logger.error(f"Executor validation error: {e}")
            return {
                "action": action,
                "executor": executor,
                "permission": ExecutorPermission.FORBIDDEN,
                "rationale": f"Validation error: {str(e)}",
                "approval_required": True,
                "escalation_needed": True
            }
    
    def get_executor_instructions(self) -> Dict[str, Any]:
        """Get executor instruction note"""
        return {
            "executor_role": "Akanksha Pandey",
            "authority_level": "executor",
            "permissions": self.executor_permissions,
            "review_checkpoints": self.review_checkpoints,
            "escalation_protocol": {
                "immediate_escalation": self.executor_permissions["forbidden_actions"],
                "approval_required": self.executor_permissions["approval_required"],
                "owner_contact": "ashmit@bhiv.com"
            },
            "operational_guidelines": [
                "Always validate action permissions before execution",
                "Document all significant actions in execution logs",
                "Escalate immediately if unsure about permissions",
                "Never attempt to bypass constitutional rules",
                "Maintain detailed records for review checkpoints"
            ]
        }

class EscalationProtocol:
    """Manages escalation to strategic advisor (Vijay)"""
    
    def __init__(self):
        self.truth_engine = get_truth_engine()
        
        # Escalation triggers
        self.escalation_triggers = {
            "technical_complexity": "High-risk technical decisions",
            "business_impact": "Significant business implications",
            "constitutional_questions": "Constitutional interpretation needed",
            "integration_approval": "Major integration requests",
            "governance_disputes": "Authority or governance conflicts",
            "strategic_decisions": "Long-term strategic implications"
        }
        
        # Response expectations
        self.response_expectations = {
            "acknowledgment_time": "24 hours",
            "response_time": "72 hours",
            "escalation_format": "structured_recommendation",
            "decision_authority": "advisory_only"
        }
        
        logger.info("Escalation Protocol initialized")
    
    def evaluate_escalation_need(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if situation requires escalation to Vijay"""
        evaluation = {
            "escalation_needed": False,
            "triggers_matched": [],
            "urgency_level": "normal",
            "recommended_action": "",
            "escalation_rationale": ""
        }
        
        try:
            # Check escalation triggers
            for trigger, description in self.escalation_triggers.items():
                if situation.get(f"trigger_{trigger}", False):
                    evaluation["triggers_matched"].append({
                        "trigger": trigger,
                        "description": description
                    })
            
            # Determine if escalation needed
            if evaluation["triggers_matched"]:
                evaluation["escalation_needed"] = True
                evaluation["recommended_action"] = "escalate_to_strategic_advisor"
                evaluation["escalation_rationale"] = f"Matched {len(evaluation['triggers_matched'])} escalation triggers"
                
                # Determine urgency
                high_priority_triggers = ["constitutional_questions", "governance_disputes"]
                if any(t["trigger"] in high_priority_triggers for t in evaluation["triggers_matched"]):
                    evaluation["urgency_level"] = "high"
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Escalation evaluation error: {e}")
            return {
                "escalation_needed": True,
                "triggers_matched": [{"trigger": "system_error", "description": str(e)}],
                "urgency_level": "high",
                "recommended_action": "escalate_immediately",
                "escalation_rationale": "System error during evaluation"
            }
    
    def get_escalation_protocol(self) -> Dict[str, Any]:
        """Get complete escalation protocol"""
        return {
            "strategic_advisor": "Vijay Dhawan",
            "escalation_triggers": self.escalation_triggers,
            "response_expectations": self.response_expectations,
            "escalation_process": [
                "Evaluate situation against triggers",
                "Document escalation rationale",
                "Submit structured escalation request",
                "Await advisory response within 72 hours",
                "Implement recommendation with owner approval"
            ],
            "authority_boundaries": {
                "vijay_role": "advisory_only",
                "final_authority": "data_sovereign",
                "no_parallel_authority": True
            }
        }

class GatekeepingSystem:
    """Complete gatekeeping and enforcement system"""
    
    def __init__(self):
        self.integration_gatekeeper = IntegrationGatekeeper()
        self.executor_enforcement = ExecutorLaneEnforcement()
        self.escalation_protocol = EscalationProtocol()
        self.truth_engine = get_truth_engine()
        
        logger.info("Gatekeeping System initialized")
    
    def evaluate_integration_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate integration request"""
        return self.integration_gatekeeper.evaluate_integration_request(request)
    
    def validate_executor_action(self, action: str, executor: str = "akanksha") -> Dict[str, Any]:
        """Validate executor action"""
        return self.executor_enforcement.validate_executor_action(action, executor)
    
    def evaluate_escalation_need(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate escalation need"""
        return self.escalation_protocol.evaluate_escalation_need(situation)
    
    def get_complete_gatekeeping_status(self) -> Dict[str, Any]:
        """Get complete gatekeeping system status"""
        return {
            "integration_gate": self.integration_gatekeeper.get_integration_gate_checklist(),
            "executor_instructions": self.executor_enforcement.get_executor_instructions(),
            "escalation_protocol": self.escalation_protocol.get_escalation_protocol(),
            "system_status": "active",
            "constitutional_compliance": True
        }

# Global gatekeeping system
gatekeeping_system = None

def get_gatekeeping_system() -> GatekeepingSystem:
    """Get global gatekeeping system instance"""
    global gatekeeping_system
    if gatekeeping_system is None:
        gatekeeping_system = GatekeepingSystem()
    return gatekeeping_system