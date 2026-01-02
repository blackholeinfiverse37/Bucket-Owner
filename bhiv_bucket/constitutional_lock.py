"""
BHIV Bucket Constitutional Lock
===============================

This module defines the immutable constitutional foundation of the BHIV Bucket.
Once locked, these rules cannot be changed without explicit constitutional amendment.

Role: Data Sovereign Authority
Purpose: Truth Engine Foundation
"""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import json
import hashlib
from utils.logger import get_logger

logger = get_logger(__name__)

class BucketAuthority(Enum):
    """Constitutional authority levels"""
    DATA_SOVEREIGN = "data_sovereign"  # Primary bucket owner
    STRATEGIC_ADVISOR = "strategic_advisor"  # Vijay role
    EXECUTOR = "executor"  # Akanksha role
    AI_AGENT = "ai_agent"  # AI systems

class ConstitutionalLock:
    """
    Immutable constitutional foundation of BHIV Bucket
    
    This class enforces the fundamental laws of the system:
    - Immutable history
    - Provenance tracking
    - Authority hierarchy
    - Truth preservation
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.locked_at = datetime.now().isoformat()
        self.constitution_hash = self._generate_constitution_hash()
        self.is_locked = True
        
        # Constitutional Rules (IMMUTABLE)
        self.constitutional_rules = {
            "immutability": {
                "rule": "No data can be silently overwritten",
                "enforcement": "All changes create new versions",
                "authority": BucketAuthority.DATA_SOVEREIGN.value
            },
            "provenance": {
                "rule": "Every artifact must have traceable lineage",
                "enforcement": "Parent-child relationships required",
                "authority": BucketAuthority.DATA_SOVEREIGN.value
            },
            "ai_separation": {
                "rule": "AI can WRITE to Bucket, Bucket never DEPENDS on AI",
                "enforcement": "No AI logic in storage layer",
                "authority": BucketAuthority.DATA_SOVEREIGN.value
            },
            "authority_hierarchy": {
                "rule": "Data Sovereign has final authority over storage",
                "enforcement": "No bypass of constitutional authority",
                "authority": BucketAuthority.DATA_SOVEREIGN.value
            },
            "truth_preservation": {
                "rule": "Bucket stores only verifiable artifacts",
                "enforcement": "No AI hallucinations in permanent storage",
                "authority": BucketAuthority.DATA_SOVEREIGN.value
            }
        }
        
        logger.info(f"Constitutional Lock initialized - Version {self.version}")
        logger.info(f"Constitution Hash: {self.constitution_hash}")
    
    def _generate_constitution_hash(self) -> str:
        """Generate immutable hash of constitutional rules"""
        constitution_data = {
            "version": self.version,
            "rules": self.constitutional_rules,
            "locked_at": self.locked_at
        }
        constitution_str = json.dumps(constitution_data, sort_keys=True)
        return hashlib.sha256(constitution_str.encode()).hexdigest()
    
    def validate_authority(self, action: str, authority: BucketAuthority) -> bool:
        """Validate if authority level can perform action"""
        authority_hierarchy = {
            BucketAuthority.DATA_SOVEREIGN: 4,
            BucketAuthority.STRATEGIC_ADVISOR: 3,
            BucketAuthority.EXECUTOR: 2,
            BucketAuthority.AI_AGENT: 1
        }
        
        # Constitutional actions require DATA_SOVEREIGN
        constitutional_actions = [
            "modify_schema", "delete_permanently", "bypass_rules", 
            "change_authority", "unlock_constitution"
        ]
        
        if action in constitutional_actions:
            return authority == BucketAuthority.DATA_SOVEREIGN
        
        return authority_hierarchy.get(authority, 0) >= 1
    
    def enforce_immutability(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce immutability rules on operations"""
        if operation == "update":
            # Convert updates to versioned inserts
            return {
                "operation": "version_insert",
                "original_data": data,
                "version_metadata": {
                    "parent_id": data.get("id"),
                    "version_number": data.get("version", 0) + 1,
                    "created_at": datetime.now().isoformat(),
                    "change_reason": data.get("change_reason", "update")
                }
            }
        
        if operation == "delete":
            # Convert deletes to tombstones
            return {
                "operation": "tombstone",
                "original_data": data,
                "tombstone_metadata": {
                    "deleted_at": datetime.now().isoformat(),
                    "deletion_reason": data.get("deletion_reason", "user_request"),
                    "recoverable": True
                }
            }
        
        return {"operation": operation, "data": data}
    
    def validate_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate artifact meets constitutional requirements"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check provenance
        if not artifact.get("parent_id") and not artifact.get("is_root"):
            validation_result["errors"].append("Missing provenance: no parent_id or is_root flag")
        
        # Check for AI logic contamination
        ai_logic_indicators = ["reasoning", "decision", "hallucination", "inference"]
        for key in artifact.keys():
            if any(indicator in key.lower() for indicator in ai_logic_indicators):
                validation_result["warnings"].append(f"Potential AI logic in field: {key}")
        
        # Check immutability metadata
        required_fields = ["created_at", "artifact_type", "content_hash"]
        for field in required_fields:
            if field not in artifact:
                validation_result["errors"].append(f"Missing required field: {field}")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        return validation_result
    
    def get_constitutional_status(self) -> Dict[str, Any]:
        """Get current constitutional status"""
        return {
            "version": self.version,
            "locked": self.is_locked,
            "locked_at": self.locked_at,
            "constitution_hash": self.constitution_hash,
            "rules_count": len(self.constitutional_rules),
            "integrity_verified": self._verify_integrity()
        }
    
    def _verify_integrity(self) -> bool:
        """Verify constitutional integrity"""
        current_hash = self._generate_constitution_hash()
        return current_hash == self.constitution_hash

# Global constitutional lock instance
CONSTITUTIONAL_LOCK = ConstitutionalLock()