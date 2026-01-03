"""
Security Configuration for BHIV Central Depository
=================================================

This module defines security settings and authentication configurations.
"""

from typing import Dict, List
import os

# Security settings
SECURITY_CONFIG = {
    "enable_authentication": False,  # Set to True in production
    "jwt_secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-here"),
    "jwt_algorithm": "HS256",
    "access_token_expire_minutes": 30,
    
    # Rate limiting
    "rate_limit_enabled": False,
    "requests_per_minute": 100,
    
    # CORS settings
    "cors_origins": [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8000"
    ],
    
    # API key validation (for future use)
    "require_api_key": False,
    "valid_api_keys": [],
    
    # Authority validation
    "enforce_authority_hierarchy": True,
    "constitutional_enforcement": True
}

# Authority levels for API endpoints
ENDPOINT_PERMISSIONS = {
    # Public endpoints (no authentication required)
    "public": [
        "/health",
        "/agents",
        "/baskets"
    ],
    
    # Executor level endpoints
    "executor": [
        "/run-agent",
        "/run-basket",
        "/logs",
        "/execution-logs/*",
        "/agent-logs/*"
    ],
    
    # Strategic advisor level endpoints
    "strategic_advisor": [
        "/governance/escalate",
        "/governance/decisions",
        "/gatekeeping/escalation-evaluation"
    ],
    
    # Data sovereign level endpoints (highest security)
    "data_sovereign": [
        "/bucket/artifacts/*/version",
        "/bucket/artifacts/*",  # DELETE operations
        "/custodianship/baseline",
        "/governance/validate",
        "/owner/responsibility-confirmation"
    ]
}

def get_security_config() -> Dict:
    """Get current security configuration"""
    return SECURITY_CONFIG.copy()

def is_endpoint_public(endpoint: str) -> bool:
    """Check if endpoint is publicly accessible"""
    return endpoint in ENDPOINT_PERMISSIONS["public"]

def get_required_authority(endpoint: str) -> str:
    """Get required authority level for endpoint"""
    for authority, endpoints in ENDPOINT_PERMISSIONS.items():
        if endpoint in endpoints:
            return authority
    return "executor"  # Default to executor level