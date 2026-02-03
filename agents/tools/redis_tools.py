# AEGIS Redis Tools - v2.1 (LangGraph Compatible)
"""
Redis integration tools for AEGIS agents.
Handles Storm Shield (vector-based), Kill Switch, and governance state.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import redis
import httpx

logger = logging.getLogger("aegis.redis_tools")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# RAG Service for vector similarity
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8100")


class RedisClient:
    """Redis client for AEGIS governance and caching."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
        return cls._instance
    
    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        return self.client.set(key, value, ex=ex)
    
    def incr(self, key: str) -> int:
        return self.client.incr(key)
    
    def expire(self, key: str, seconds: int) -> bool:
        return self.client.expire(key, seconds)
    
    def hset(self, name: str, key: str, value: str) -> int:
        return self.client.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Optional[str]:
        return self.client.hget(name, key)
    
    def hgetall(self, name: str) -> Dict[str, str]:
        return self.client.hgetall(name)
    
    def lpush(self, key: str, value: str) -> int:
        return self.client.lpush(key, value)
    
    def lrange(self, key: str, start: int, end: int) -> list:
        return self.client.lrange(key, start, end)
    
    def zadd(self, name: str, mapping: dict) -> int:
        return self.client.zadd(name, mapping)
    
    def zrangebyscore(self, name: str, min: float, max: float) -> list:
        return self.client.zrangebyscore(name, min, max)


# =============================================================================
# STORM SHIELD - VECTOR SIMILARITY (v2.1)
# =============================================================================

async def check_duplicate_vector(
    text: str,
    incident_number: str,
    time_window_minutes: int = 15,
    similarity_threshold: float = 0.90
) -> Tuple[bool, Optional[str]]:
    """
    Check for semantically similar incidents using vector similarity.
    
    Args:
        text: Incident short description (scrubbed)
        incident_number: Current incident number
        time_window_minutes: Time window for duplicate detection
        similarity_threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        Tuple of (is_duplicate, parent_incident_number or None)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Call RAG service for similar incidents
            response = await client.post(
                f"{RAG_SERVICE_URL}/search/similar",
                json={
                    "query": text,
                    "collection": "incidents",
                    "time_window_minutes": time_window_minutes,
                    "threshold": similarity_threshold,
                    "exclude_id": incident_number,
                    "limit": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                if matches and len(matches) > 0:
                    match = matches[0]
                    similarity = match.get("score", 0)
                    parent_id = match.get("incident_number")
                    
                    if similarity >= similarity_threshold:
                        logger.info(
                            f"[STORM] Duplicate detected: {incident_number} -> {parent_id} "
                            f"(similarity: {similarity:.2%})"
                        )
                        # Record in Redis for stats
                        redis_client = RedisClient()
                        redis_client.incr(f"storm:duplicates:{datetime.utcnow().strftime('%Y%m%d')}")
                        return True, parent_id
        
        return False, None
        
    except Exception as e:
        logger.error(f"[STORM] Vector similarity check failed: {e}")
        # Fail open - don't block tickets if RAG service is down
        return False, None


async def record_incident_embedding(
    incident_number: str,
    text: str,
    metadata: dict = None
) -> bool:
    """
    Record incident embedding in RAG service for future duplicate detection.
    
    Args:
        incident_number: Incident number
        text: Text to embed (short_description)
        metadata: Additional metadata
        
    Returns:
        True if successful
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/embed/incident",
                json={
                    "incident_number": incident_number,
                    "text": text,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"[STORM] Failed to record embedding: {e}")
        return False


async def get_governance_state() -> dict:
    """
    Get current governance state from Redis.
    
    Returns:
        Dict with enabled, mode, and threshold values
    """
    client = RedisClient()
    
    # Check kill switch
    kill_switch = client.get("gov:killswitch")
    enabled = kill_switch != "false"
    
    # Get mode
    mode = client.get("gov:mode") or "assist"
    
    # Get thresholds
    thresholds = {
        "threshold_assign": int(client.get("gov:threshold:auto_assign") or 85),
        "threshold_categorize": int(client.get("gov:threshold:auto_categorize") or 80),
        "threshold_remediate": int(client.get("gov:threshold:auto_remediate") or 95),
    }
    
    return {
        "enabled": enabled,
        "mode": mode,
        **thresholds
    }





class RecordIncidentInput(BaseModel):
    """Input for recording incident in Storm Shield."""
    incident_number: str = Field(..., description="Incident number")
    short_description: str = Field(..., description="Incident short description")
    ci_name: Optional[str] = Field(None, description="CI name")
    category: Optional[str] = Field(None, description="Category")


class RecordIncidentTool(BaseTool):
    """Record incident fingerprint in Storm Shield."""
    name: str = "record_incident"
    description: str = "Record incident fingerprint for future duplicate detection"
    args_schema: type[BaseModel] = RecordIncidentInput
    
    def _run(self, incident_number: str, short_description: str, 
             ci_name: str = None, category: str = None) -> str:
        client = RedisClient()
        
        # Create fingerprint
        fingerprint_data = f"{short_description}:{ci_name or ''}:{category or ''}"
        fingerprint = hashlib.sha256(fingerprint_data.lower().encode()).hexdigest()[:16]
        
        storm_key = f"storm:fingerprint:{fingerprint}"
        
        # Store fingerprint with 4-hour TTL (storm window)
        data = {
            "incident_number": incident_number,
            "short_description": short_description,
            "ci_name": ci_name,
            "category": category,
            "recorded_at": datetime.utcnow().isoformat()
        }
        
        client.set(storm_key, json.dumps(data), ex=14400)  # 4 hours
        
        return json.dumps({
            "success": True,
            "fingerprint": fingerprint,
            "ttl_hours": 4
        })


class GetStormStatusInput(BaseModel):
    """Input for storm status check."""
    ci_name: Optional[str] = Field(None, description="CI to check for storm")


class GetStormStatusTool(BaseTool):
    """Get current storm status for a CI or globally."""
    name: str = "get_storm_status"
    description: str = "Check if there is an active alert storm for a CI or globally"
    args_schema: type[BaseModel] = GetStormStatusInput
    
    def _run(self, ci_name: str = None) -> str:
        client = RedisClient()
        
        storm_threshold = 10  # More than 10 duplicates = storm
        
        if ci_name:
            # Check CI-specific storm
            ci_hash = hashlib.sha256(ci_name.lower().encode()).hexdigest()[:8]
            storm_key = f"storm:ci:{ci_hash}:count"
            count = client.get(storm_key)
            
            if count and int(count) >= storm_threshold:
                return json.dumps({
                    "storm_active": True,
                    "ci": ci_name,
                    "incident_count": int(count),
                    "threshold": storm_threshold,
                    "message": f"STORM ACTIVE: {count} incidents for {ci_name}"
                })
        
        return json.dumps({
            "storm_active": False,
            "message": "No active storm detected"
        })


# =============================================================================
# KILL SWITCH & GOVERNANCE TOOLS
# =============================================================================

class CheckKillSwitchTool(BaseTool):
    """Check kill switch status."""
    name: str = "check_kill_switch"
    description: str = "Check if the AEGIS kill switch is active. If active, all AI actions should be halted."
    
    def _run(self) -> str:
        client = RedisClient()
        
        # gov:killswitch = "true" means system is enabled (not killed)
        # gov:killswitch = "false" means system is stopped
        status = client.get("gov:killswitch")
        
        if status == "false":
            return json.dumps({
                "kill_switch_active": True,
                "ai_enabled": False,
                "message": "KILL SWITCH ACTIVE: All AI actions are halted. Human review required."
            })
        
        # Also check mode
        mode = client.get("gov:mode") or "assist"
        
        return json.dumps({
            "kill_switch_active": False,
            "ai_enabled": True,
            "mode": mode,
            "message": f"System operational. Mode: {mode}"
        })


class GetConfidenceThresholdInput(BaseModel):
    """Input for getting confidence threshold."""
    action_type: str = Field("auto_action", description="Type of action")


class GetConfidenceThresholdTool(BaseTool):
    """Get confidence threshold for action types."""
    name: str = "get_confidence_threshold"
    description: str = "Get the minimum confidence threshold required for automated actions"
    args_schema: type[BaseModel] = GetConfidenceThresholdInput
    
    def _run(self, action_type: str = "auto_action") -> str:
        client = RedisClient()
        
        # Get threshold from Redis or use defaults
        threshold_key = f"gov:threshold:{action_type}"
        threshold = client.get(threshold_key)
        
        if not threshold:
            # Default thresholds
            defaults = {
                "auto_assign": 85,
                "auto_categorize": 80,
                "auto_remediate": 95,
                "auto_action": 85
            }
            threshold = defaults.get(action_type, 85)
        
        return json.dumps({
            "action_type": action_type,
            "threshold": int(threshold),
            "message": f"Minimum confidence required: {threshold}%"
        })


# =============================================================================
# AUDIT & LOGGING TOOLS
# =============================================================================

class LogDecisionInput(BaseModel):
    """Input for logging decision."""
    incident_number: str = Field(..., description="Incident number")
    agent: str = Field(..., description="Agent name")
    decision_type: str = Field(..., description="Type of decision")
    decision: str = Field(..., description="Decision made")
    confidence: Optional[int] = Field(None, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Reasoning")


class LogDecisionTool(BaseTool):
    """Log an AI decision for audit trail."""
    name: str = "log_decision"
    description: str = "Log an AI decision to the audit trail for compliance"
    args_schema: type[BaseModel] = LogDecisionInput
    
    def _run(self, incident_number: str, agent: str, decision_type: str,
             decision: str, confidence: int = None, reasoning: str = None) -> str:
        client = RedisClient()
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_number": incident_number,
            "agent": agent,
            "decision_type": decision_type,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning
        }
        
        # Store in incident-specific audit log
        log_key = f"audit:{incident_number}"
        client.lpush(log_key, json.dumps(log_entry))
        
        # Also store in global audit log (with 7-year retention simulated by keeping recent)
        global_key = f"audit:global:{datetime.utcnow().strftime('%Y%m%d')}"
        client.lpush(global_key, json.dumps(log_entry))
        
        return json.dumps({
            "success": True,
            "log_id": f"{incident_number}:{datetime.utcnow().timestamp()}",
            "message": "Decision logged to audit trail"
        })


class LogRemediationInput(BaseModel):
    """Input for logging remediation action."""
    incident_number: str = Field(..., description="Incident number")
    action: str = Field(..., description="Remediation action taken")
    result: str = Field(..., description="Result of remediation")
    reversible: bool = Field(True, description="Whether action is reversible")


class LogRemediationTool(BaseTool):
    """Log a remediation action."""
    name: str = "log_remediation"
    description: str = "Log a remediation action to the audit trail"
    args_schema: type[BaseModel] = LogRemediationInput
    
    def _run(self, incident_number: str, action: str, result: str, 
             reversible: bool = True) -> str:
        client = RedisClient()
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_number": incident_number,
            "action": action,
            "result": result,
            "reversible": reversible,
            "agent": "JANITOR"
        }
        
        log_key = f"remediation:{incident_number}"
        client.lpush(log_key, json.dumps(log_entry))
        
        return json.dumps({
            "success": True,
            "log_id": f"rem:{incident_number}:{datetime.utcnow().timestamp()}"
        })


# =============================================================================
# TOOLS FACTORY
# =============================================================================

class RedisTools:
    """Factory for Redis tools."""
    
    def __init__(self):
        self.check_duplicate = CheckDuplicateTool()
        self.record_incident = RecordIncidentTool()
        self.get_storm_status = GetStormStatusTool()
        self.check_kill_switch = CheckKillSwitchTool()
        self.get_confidence_threshold = GetConfidenceThresholdTool()
        self.log_decision = LogDecisionTool()
        self.log_remediation = LogRemediationTool()
