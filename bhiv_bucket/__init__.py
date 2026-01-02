"""
BHIV Bucket - Truth Engine for AI Avatar/Assistant Platform
===========================================================

This module implements the foundational data vault that stores everything 
the AI ever produces with constitutional enforcement.

Components:
- Constitutional Lock: Immutable rules and authority hierarchy
- Truth Engine: Core storage system with provenance tracking
- AI Firewall: Prevents AI logic contamination
- Governance System: Authority validation and escalation

This is the combination of AWS + GitHub + Legal Ledger + Audit Log
for AI systems.
"""

from .constitutional_lock import CONSTITUTIONAL_LOCK, BucketAuthority, ConstitutionalLock
from .truth_engine import get_truth_engine, TruthEngine, ArtifactType, BucketArtifact
from .ai_firewall import get_ai_firewall, AIIntegrationFirewall, ArtifactClass, AIFirewallAction
from .governance import get_governance_system, BHIVGovernance, GovernanceAction, EscalationLevel
from .custodianship import get_custodianship_system, CustodianshipSystem
from .gatekeeping import get_gatekeeping_system, GatekeepingSystem, IntegrationStatus, ExecutorPermission

__version__ = "1.0.0"
__author__ = "BHIV Central Depository"
__description__ = "Truth Engine for AI Avatar/Assistant Platform"

# Export main components
__all__ = [
    # Constitutional Foundation
    "CONSTITUTIONAL_LOCK",
    "BucketAuthority", 
    "ConstitutionalLock",
    
    # Truth Engine
    "get_truth_engine",
    "TruthEngine",
    "ArtifactType",
    "BucketArtifact",
    
    # AI Firewall
    "get_ai_firewall",
    "AIIntegrationFirewall", 
    "ArtifactClass",
    "AIFirewallAction",
    
    # Governance System
    "get_governance_system",
    "BHIVGovernance",
    "GovernanceAction",
    "EscalationLevel",
    
    # Custodianship System
    "get_custodianship_system",
    "CustodianshipSystem",
    
    # Gatekeeping System
    "get_gatekeeping_system",
    "GatekeepingSystem",
    "IntegrationStatus",
    "ExecutorPermission"
]

def get_bucket_status():
    """Get comprehensive BHIV Bucket status"""
    truth_engine = get_truth_engine()
    ai_firewall = get_ai_firewall()
    governance_system = get_governance_system()
    custodianship_system = get_custodianship_system()
    gatekeeping_system = get_gatekeeping_system()
    
    return {
        "version": __version__,
        "constitutional_status": CONSTITUTIONAL_LOCK.get_constitutional_status(),
        "bucket_stats": truth_engine.get_bucket_stats(),
        "firewall_active": True,
        "governance_stats": governance_system.get_governance_stats(),
        "custodianship_status": custodianship_system.get_custodianship_status(),
        "gatekeeping_active": True,
        "components": {
            "constitutional_lock": "active",
            "truth_engine": "active", 
            "ai_firewall": "active",
            "governance_system": "active",
            "custodianship_system": "active",
            "gatekeeping_system": "active"
        }
    }