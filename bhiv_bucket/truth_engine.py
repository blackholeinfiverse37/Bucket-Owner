"""
BHIV Bucket Truth Engine
========================

The Truth Engine is the core storage system that enforces constitutional rules.
It ensures immutability, provenance, and truth preservation for all artifacts.

This is the foundational data vault that stores everything the AI ever produces.
"""

import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .constitutional_lock import CONSTITUTIONAL_LOCK, BucketAuthority
from utils.logger import get_logger
from database.mongo_db import MongoDBClient
from utils.redis_service import RedisService

logger = get_logger(__name__)

class ArtifactType(Enum):
    """Types of artifacts that can be stored in the bucket"""
    AI_OUTPUT = "ai_output"
    USER_INPUT = "user_input"
    SYSTEM_LOG = "system_log"
    AGENT_STATE = "agent_state"
    BASKET_EXECUTION = "basket_execution"
    MEDIA_FILE = "media_file"
    CONFIGURATION = "configuration"
    PERSONA_DATA = "persona_data"

@dataclass
class BucketArtifact:
    """Immutable artifact stored in the BHIV Bucket"""
    id: str
    artifact_type: ArtifactType
    content: Dict[str, Any]
    content_hash: str
    created_at: str
    parent_id: Optional[str] = None
    version: int = 1
    authority: BucketAuthority = BucketAuthority.AI_AGENT
    metadata: Dict[str, Any] = None
    is_root: bool = False
    is_tombstone: bool = False
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TruthEngine:
    """
    Core Truth Engine for BHIV Bucket
    
    Responsibilities:
    - Enforce constitutional rules
    - Maintain immutable history
    - Track provenance
    - Validate artifacts
    - Prevent data corruption
    """
    
    def __init__(self, mongo_client: Optional[MongoDBClient] = None, 
                 redis_service: Optional[RedisService] = None):
        self.mongo_client = mongo_client or MongoDBClient()
        self.redis_service = redis_service or RedisService()
        self.collection_name = "bhiv_bucket_artifacts"
        
        # Initialize bucket if not exists
        self._initialize_bucket()
        
        logger.info("Truth Engine initialized with constitutional enforcement")
    
    def _initialize_bucket(self):
        """Initialize the bucket with constitutional foundation"""
        try:
            if self.mongo_client and self.mongo_client.db is not None:
                # Create constitutional record if not exists
                constitutional_record = {
                    "id": "constitutional_lock",
                    "artifact_type": ArtifactType.CONFIGURATION.value,
                    "content": CONSTITUTIONAL_LOCK.get_constitutional_status(),
                    "content_hash": CONSTITUTIONAL_LOCK.constitution_hash,
                    "created_at": CONSTITUTIONAL_LOCK.locked_at,
                    "is_root": True,
                    "authority": BucketAuthority.DATA_SOVEREIGN.value,
                    "metadata": {"immutable": True, "constitutional": True}
                }
                
                # Check if constitutional record exists
                existing = self.mongo_client.db[self.collection_name].find_one(
                    {"id": "constitutional_lock"}
                )
                
                if not existing:
                    self.mongo_client.db[self.collection_name].insert_one(constitutional_record)
                    logger.info("Constitutional foundation established in bucket")
                else:
                    logger.info("Constitutional foundation already exists")
                    
        except Exception as e:
            logger.warning(f"Could not initialize bucket in MongoDB: {e}")
    
    def _generate_content_hash(self, content: Dict[str, Any]) -> str:
        """Generate immutable hash of content"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _validate_authority_for_action(self, action: str, authority: BucketAuthority) -> bool:
        """Validate authority can perform action"""
        return CONSTITUTIONAL_LOCK.validate_authority(action, authority)
    
    def store_artifact(self, artifact_type: ArtifactType, content: Dict[str, Any],
                      authority: BucketAuthority = BucketAuthority.AI_AGENT,
                      parent_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store artifact in bucket with constitutional enforcement
        
        Returns:
            Dict containing artifact_id and storage status
        """
        try:
            # Generate artifact ID and hash
            artifact_id = str(uuid.uuid4())
            content_hash = self._generate_content_hash(content)
            
            # Create artifact
            artifact = BucketArtifact(
                id=artifact_id,
                artifact_type=artifact_type,
                content=content,
                content_hash=content_hash,
                created_at=datetime.now().isoformat(),
                parent_id=parent_id,
                authority=authority,
                metadata=metadata or {},
                is_root=parent_id is None
            )
            
            # Constitutional validation
            validation_result = CONSTITUTIONAL_LOCK.validate_artifact(asdict(artifact))
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Constitutional validation failed",
                    "details": validation_result["errors"]
                }
            
            # Store in MongoDB
            if self.mongo_client and self.mongo_client.db is not None:
                # Convert artifact to dict and handle enum serialization
                artifact_dict = asdict(artifact)
                artifact_dict['artifact_type'] = artifact.artifact_type.value
                artifact_dict['authority'] = artifact.authority.value
                
                self.mongo_client.db[self.collection_name].insert_one(artifact_dict)
                logger.info(f"Artifact stored in MongoDB: {artifact_id}")
            
            # Cache in Redis for fast access
            if self.redis_service and self.redis_service.is_connected():
                cache_key = f"bucket:artifact:{artifact_id}"
                # Convert artifact to dict with enum values for caching
                cache_data = asdict(artifact)
                cache_data['artifact_type'] = artifact.artifact_type.value
                cache_data['authority'] = artifact.authority.value
                
                self.redis_service.client.set(
                    cache_key, 
                    json.dumps(cache_data), 
                    ex=3600  # 1 hour cache
                )
                logger.debug(f"Artifact cached in Redis: {artifact_id}")
            
            # Log constitutional compliance
            logger.info(f"Artifact stored with constitutional compliance: {artifact_id}")
            if validation_result.get("warnings"):
                logger.warning(f"Artifact warnings: {validation_result['warnings']}")
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "content_hash": content_hash,
                "constitutional_compliance": True,
                "warnings": validation_result.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to store artifact: {e}")
            return {
                "success": False,
                "error": str(e),
                "constitutional_compliance": False
            }
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve artifact by ID"""
        try:
            # Try Redis cache first
            if self.redis_service and self.redis_service.is_connected():
                cache_key = f"bucket:artifact:{artifact_id}"
                cached = self.redis_service.client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            # Fallback to MongoDB
            if self.mongo_client and self.mongo_client.db is not None:
                artifact = self.mongo_client.db[self.collection_name].find_one(
                    {"id": artifact_id}
                )
                if artifact:
                    # Remove MongoDB _id field
                    artifact.pop("_id", None)
                    return artifact
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve artifact {artifact_id}: {e}")
            return None
    
    def get_artifact_lineage(self, artifact_id: str) -> List[Dict[str, Any]]:
        """Get complete lineage (ancestry) of an artifact"""
        try:
            lineage = []
            current_id = artifact_id
            
            while current_id:
                artifact = self.get_artifact(current_id)
                if not artifact:
                    break
                    
                lineage.append(artifact)
                current_id = artifact.get("parent_id")
            
            return lineage
            
        except Exception as e:
            logger.error(f"Failed to get lineage for {artifact_id}: {e}")
            return []
    
    def get_artifact_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all children of an artifact"""
        try:
            if not self.mongo_client or self.mongo_client.db is None:
                return []
            
            children = list(self.mongo_client.db[self.collection_name].find(
                {"parent_id": parent_id}
            ))
            
            # Remove MongoDB _id fields
            for child in children:
                child.pop("_id", None)
            
            return children
            
        except Exception as e:
            logger.error(f"Failed to get children for {parent_id}: {e}")
            return []
    
    def create_version(self, parent_id: str, content: Dict[str, Any],
                      authority: BucketAuthority = BucketAuthority.AI_AGENT,
                      change_reason: str = "version_update") -> Dict[str, Any]:
        """Create new version of existing artifact"""
        try:
            # Get parent artifact
            parent = self.get_artifact(parent_id)
            if not parent:
                return {
                    "success": False,
                    "error": "Parent artifact not found"
                }
            
            # Calculate new version number
            children = self.get_artifact_children(parent_id)
            version_numbers = [child.get("version", 1) for child in children]
            new_version = max(version_numbers + [parent.get("version", 1)]) + 1
            
            # Add version metadata
            version_metadata = {
                "change_reason": change_reason,
                "parent_version": parent.get("version", 1),
                "version_created_at": datetime.now().isoformat()
            }
            
            # Store new version
            result = self.store_artifact(
                artifact_type=ArtifactType(parent["artifact_type"]),
                content=content,
                authority=authority,
                parent_id=parent_id,
                metadata=version_metadata
            )
            
            if result["success"]:
                # Update version number
                if self.mongo_client and self.mongo_client.db is not None:
                    self.mongo_client.db[self.collection_name].update_one(
                        {"id": result["artifact_id"]},
                        {"$set": {"version": new_version}}
                    )
                
                result["version"] = new_version
                logger.info(f"Created version {new_version} of artifact {parent_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_tombstone(self, artifact_id: str, 
                        authority: BucketAuthority = BucketAuthority.DATA_SOVEREIGN,
                        deletion_reason: str = "user_request") -> Dict[str, Any]:
        """Create tombstone instead of deleting (constitutional enforcement)"""
        try:
            # Validate authority for deletion
            if not self._validate_authority_for_action("delete", authority):
                return {
                    "success": False,
                    "error": "Insufficient authority for deletion"
                }
            
            # Get original artifact
            original = self.get_artifact(artifact_id)
            if not original:
                return {
                    "success": False,
                    "error": "Artifact not found"
                }
            
            # Create tombstone content
            tombstone_content = {
                "original_artifact_id": artifact_id,
                "deletion_reason": deletion_reason,
                "deleted_at": datetime.now().isoformat(),
                "recoverable": True,
                "original_content_hash": original["content_hash"]
            }
            
            # Store tombstone
            result = self.store_artifact(
                artifact_type=ArtifactType.SYSTEM_LOG,
                content=tombstone_content,
                authority=authority,
                parent_id=artifact_id,
                metadata={"is_tombstone": True}
            )
            
            if result["success"]:
                # Mark original as tombstoned (but don't delete)
                if self.mongo_client and self.mongo_client.db is not None:
                    self.mongo_client.db[self.collection_name].update_one(
                        {"id": artifact_id},
                        {"$set": {"is_tombstone": True, "tombstoned_at": datetime.now().isoformat()}}
                    )
                
                logger.info(f"Created tombstone for artifact {artifact_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create tombstone: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """Get comprehensive bucket statistics"""
        try:
            stats = {
                "constitutional_status": CONSTITUTIONAL_LOCK.get_constitutional_status(),
                "total_artifacts": 0,
                "artifacts_by_type": {},
                "artifacts_by_authority": {},
                "total_versions": 0,
                "total_tombstones": 0,
                "storage_health": "unknown"
            }
            
            if self.mongo_client and self.mongo_client.db is not None:
                collection = self.mongo_client.db[self.collection_name]
                
                # Total artifacts
                stats["total_artifacts"] = collection.count_documents({})
                
                # By type
                pipeline = [
                    {"$group": {"_id": "$artifact_type", "count": {"$sum": 1}}}
                ]
                for result in collection.aggregate(pipeline):
                    stats["artifacts_by_type"][result["_id"]] = result["count"]
                
                # By authority
                pipeline = [
                    {"$group": {"_id": "$authority", "count": {"$sum": 1}}}
                ]
                for result in collection.aggregate(pipeline):
                    stats["artifacts_by_authority"][result["_id"]] = result["count"]
                
                # Versions and tombstones
                stats["total_versions"] = collection.count_documents({"version": {"$gt": 1}})
                stats["total_tombstones"] = collection.count_documents({"is_tombstone": True})
                
                stats["storage_health"] = "healthy"
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get bucket stats: {e}")
            return {
                "constitutional_status": CONSTITUTIONAL_LOCK.get_constitutional_status(),
                "error": str(e),
                "storage_health": "error"
            }

# Global Truth Engine instance
truth_engine = None

def get_truth_engine() -> TruthEngine:
    """Get global Truth Engine instance"""
    global truth_engine
    if truth_engine is None:
        truth_engine = TruthEngine()
    return truth_engine