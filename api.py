# AEGIS API Server - v2.1
"""
FastAPI server for AEGIS - Autonomous IT Operations Platform
Endpoints for incident processing, webhooks, and admin operations.

v2.1: Uses Redis queue instead of BackgroundTasks for reliability.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis
import uvicorn

from utils.pii_scrubber import scrub_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("aegis.api")

# Redis client for governance and queue
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# Queue name
TRIAGE_QUEUE = "aegis:queue:triage"


# =============================================================================
# STARTUP / SHUTDOWN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🛡️ AEGIS API Server v2.1 starting...")
    
    # Initialize governance defaults if not set
    if not redis_client.get("gov:killswitch"):
        redis_client.set("gov:killswitch", "true")  # true = system enabled
    if not redis_client.get("gov:mode"):
        redis_client.set("gov:mode", "assist")  # assist = AI + human review
    
    # Log queue status
    queue_len = redis_client.llen(TRIAGE_QUEUE)
    logger.info(f"📋 Queue status: {queue_len} items pending")
    
    logger.info("✅ AEGIS API Server ready")
    yield
    logger.info("🛡️ AEGIS API Server shutting down...")


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="AEGIS API",
    description="Autonomous IT Operations & Swarming Platform (v2.1 - LangGraph)",
    version="2.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# MODELS
# =============================================================================

class IncidentPayload(BaseModel):
    """ServiceNow incident payload."""
    number: str = Field(..., description="Incident number e.g. INC0012345")
    short_description: str = Field(..., description="Short description")
    description: Optional[str] = Field(None, description="Full description")
    caller_id: Optional[str] = Field(None, description="Caller email or sys_id")
    category: Optional[str] = Field(None, description="Category")
    subcategory: Optional[str] = Field(None, description="Subcategory")
    priority: Optional[str] = Field("3", description="Priority 1-5")
    cmdb_ci: Optional[str] = Field(None, description="Configuration Item")
    assignment_group: Optional[str] = Field(None, description="Current assignment group")


class TriageResponse(BaseModel):
    """Triage response model."""
    status: str
    incident_number: str
    triage_id: str
    message: str
    queue_position: Optional[int] = None


class KillSwitchPayload(BaseModel):
    """Kill switch control payload."""
    action: str = Field(..., description="enable | disable")
    reason: str = Field(..., description="Reason for action")
    operator: str = Field(..., description="Operator email")


class ModePayload(BaseModel):
    """Operating mode payload."""
    mode: str = Field(..., description="auto | assist | monitor")
    reason: str = Field(..., description="Reason for change")


class ApprovalPayload(BaseModel):
    """Approval decision payload."""
    action: str = Field(..., description="approve | reject")
    incident: str = Field(..., description="Incident number")
    approver: str = Field(..., description="Approver email")
    reason: Optional[str] = Field(None, description="Reason")


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    queue_len = redis_client.llen(TRIAGE_QUEUE)
    
    return {
        "status": "healthy",
        "service": "aegis-api",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "redis": redis_status,
            "langgraph": "ready",
            "queue_depth": queue_len
        }
    }


@app.get("/status")
async def get_status():
    """Get AEGIS operational status."""
    kill_switch = redis_client.get("gov:killswitch")
    mode = redis_client.get("gov:mode") or "assist"
    
    # Get recent stats
    today = datetime.utcnow().strftime("%Y%m%d")
    processed_today = redis_client.get(f"stats:processed:{today}") or "0"
    blocked_today = redis_client.get(f"stats:blocked:{today}") or "0"
    
    # Queue stats
    queue_len = redis_client.llen(TRIAGE_QUEUE)
    processing_len = redis_client.llen("aegis:queue:processing")
    dead_letter_len = redis_client.llen("aegis:queue:dead_letter")
    
    return {
        "operational": kill_switch == "true",
        "mode": mode,
        "kill_switch_active": kill_switch == "false",
        "stats": {
            "processed_today": int(processed_today),
            "blocked_today": int(blocked_today)
        },
        "queue": {
            "pending": queue_len,
            "processing": processing_len,
            "dead_letter": dead_letter_len
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# INCIDENT PROCESSING ENDPOINTS (v2.1 - Redis Queue)
# =============================================================================

@app.post("/webhook/incident", response_model=TriageResponse)
async def receive_incident(incident: IncidentPayload):
    """
    Receive incident from ServiceNow webhook.
    PII is scrubbed and incident is pushed to Redis queue.
    Worker process handles actual triage.
    """
    logger.info(f"Received incident: {incident.number}")
    
    # Check kill switch
    if redis_client.get("gov:killswitch") == "false":
        logger.warning(f"Kill switch active, rejecting {incident.number}")
        raise HTTPException(
            status_code=503,
            detail="AEGIS kill switch is active. All AI processing halted."
        )
    
    # Generate triage ID
    triage_id = f"TRG{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{incident.number[-4:]}"
    
    # Convert to dict and scrub PII before queuing
    incident_data = incident.model_dump()
    incident_data["triage_id"] = triage_id
    incident_data["received_at"] = datetime.utcnow().isoformat()
    
    # Scrub PII (creates scrubbed versions of text fields)
    incident_data = scrub_dict(incident_data)
    
    # Push to Redis queue (reliable, persistent)
    queue_position = redis_client.lpush(TRIAGE_QUEUE, json.dumps(incident_data))
    
    # Increment stats
    today = datetime.utcnow().strftime("%Y%m%d")
    redis_client.incr(f"stats:processed:{today}")
    
    logger.info(f"Queued {incident.number} at position {queue_position}")
    
    return TriageResponse(
        status="queued",
        incident_number=incident.number,
        triage_id=triage_id,
        message="Incident queued for AI triage",
        queue_position=queue_position
    )


@app.get("/triage/{triage_id}")
async def get_triage_result(triage_id: str):
    """Get result of a triage operation."""
    result = redis_client.get(f"triage:result:{triage_id}")
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Triage {triage_id} not found or still processing"
        )
    
    return json.loads(result)


# =============================================================================
# GOVERNANCE ENDPOINTS
# =============================================================================

@app.post("/governance/killswitch")
async def control_kill_switch(payload: KillSwitchPayload):
    """Control the global kill switch."""
    logger.warning(f"Kill switch {payload.action} by {payload.operator}: {payload.reason}")
    
    if payload.action == "disable":
        redis_client.set("gov:killswitch", "false")
        message = "Kill switch ACTIVATED. All AI processing halted."
    elif payload.action == "enable":
        redis_client.set("gov:killswitch", "true")
        message = "Kill switch DEACTIVATED. AI processing resumed."
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'enable' or 'disable'")
    
    # Log the action
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": payload.action,
        "operator": payload.operator,
        "reason": payload.reason
    }
    redis_client.lpush("audit:killswitch", json.dumps(log_entry))
    
    return {
        "success": True,
        "kill_switch_active": payload.action == "disable",
        "message": message
    }


@app.post("/governance/mode")
async def set_operating_mode(payload: ModePayload):
    """Set the operating mode."""
    valid_modes = ["auto", "assist", "monitor"]
    
    if payload.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Use one of: {valid_modes}"
        )
    
    redis_client.set("gov:mode", payload.mode)
    
    mode_descriptions = {
        "auto": "Full automation - AI acts without human review",
        "assist": "AI assists - Human review required for actions",
        "monitor": "Monitor only - AI observes but takes no actions"
    }
    
    return {
        "success": True,
        "mode": payload.mode,
        "description": mode_descriptions[payload.mode]
    }


@app.get("/governance/thresholds")
async def get_thresholds():
    """Get current confidence thresholds."""
    thresholds = {
        "auto_assign": redis_client.get("gov:threshold:auto_assign") or "85",
        "auto_categorize": redis_client.get("gov:threshold:auto_categorize") or "80",
        "auto_remediate": redis_client.get("gov:threshold:auto_remediate") or "95"
    }
    
    return {
        "thresholds": {k: int(v) for k, v in thresholds.items()}
    }


# =============================================================================
# APPROVAL ENDPOINTS
# =============================================================================

@app.post("/approve/{incident_number}")
async def approve_action(incident_number: str, payload: ApprovalPayload):
    """Approve a pending action."""
    logger.info(f"Action approved for {incident_number} by {payload.approver}")
    
    approval = {
        "timestamp": datetime.utcnow().isoformat(),
        "incident": incident_number,
        "action": "approved",
        "approver": payload.approver,
        "reason": payload.reason
    }
    
    redis_client.set(f"approval:{incident_number}", json.dumps(approval), ex=3600)
    redis_client.lpush(f"audit:approvals", json.dumps(approval))
    
    return {"success": True, "status": "approved", "incident": incident_number}


@app.post("/reject/{incident_number}")
async def reject_action(incident_number: str, payload: ApprovalPayload):
    """Reject a pending action."""
    logger.info(f"Action rejected for {incident_number} by {payload.approver}")
    
    rejection = {
        "timestamp": datetime.utcnow().isoformat(),
        "incident": incident_number,
        "action": "rejected",
        "approver": payload.approver,
        "reason": payload.reason
    }
    
    redis_client.set(f"approval:{incident_number}", json.dumps(rejection), ex=3600)
    redis_client.lpush(f"audit:approvals", json.dumps(rejection))
    
    return {"success": True, "status": "rejected", "incident": incident_number}


# =============================================================================
# AUDIT ENDPOINTS
# =============================================================================

@app.get("/audit/incident/{incident_number}")
async def get_incident_audit(incident_number: str):
    """Get audit trail for an incident."""
    logs = redis_client.lrange(f"audit:{incident_number}", 0, 100)
    
    return {
        "incident": incident_number,
        "audit_entries": [json.loads(log) for log in logs],
        "count": len(logs)
    }


@app.get("/audit/killswitch")
async def get_killswitch_audit():
    """Get kill switch audit trail."""
    logs = redis_client.lrange("audit:killswitch", 0, 50)
    
    return {
        "audit_entries": [json.loads(log) for log in logs],
        "count": len(logs)
    }


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

# Default credentials (override via environment)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "aegis2026")


class LoginPayload(BaseModel):
    """Login payload."""
    username: str
    password: str


class AgentPayload(BaseModel):
    """Agent creation payload."""
    name: str
    role: str
    description: Optional[str] = None


@app.post("/auth/login")
async def login(payload: LoginPayload):
    """Simple username/password authentication."""
    if payload.username == ADMIN_USERNAME and payload.password == ADMIN_PASSWORD:
        token = f"aegis-token-{datetime.utcnow().timestamp()}"
        return {
            "username": payload.username,
            "token": token,
            "role": "admin"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/admin/agents")
async def get_agents():
    """Get all agents and their status."""
    agents = redis_client.hgetall("agents:status") or {}
    
    default_agents = [
        {"id": "guardian", "name": "GUARDIAN", "role": "Storm Shield", "active": True},
        {"id": "scout", "name": "SCOUT", "role": "Enrichment", "active": True},
        {"id": "sherlock", "name": "SHERLOCK", "role": "AI Triage", "active": True},
        {"id": "router", "name": "ROUTER", "role": "Assignment", "active": True},
        {"id": "arbiter", "name": "ARBITER", "role": "Governance", "active": True},
        {"id": "herald", "name": "HERALD", "role": "Notifications", "active": True},
        {"id": "scribe", "name": "SCRIBE", "role": "Audit", "active": True},
        {"id": "bridge", "name": "BRIDGE", "role": "Case→Incident", "active": True},
        {"id": "janitor", "name": "JANITOR", "role": "Remediation", "active": True},
    ]
    
    # Merge with stored status
    for agent in default_agents:
        status = agents.get(agent["id"])
        if status:
            agent["active"] = status == "true"
    
    return {"agents": default_agents}


@app.post("/admin/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, enabled: bool = True):
    """Toggle an agent on/off."""
    redis_client.hset("agents:status", agent_id, "true" if enabled else "false")
    return {"success": True, "agent": agent_id, "enabled": enabled}


@app.post("/admin/agents")
async def add_agent(payload: AgentPayload):
    """Add a new custom agent."""
    agent_id = payload.name.lower()
    agent_data = {
        "id": agent_id,
        "name": payload.name.upper(),
        "role": payload.role,
        "description": payload.description or "Custom agent",
        "active": True
    }
    redis_client.hset("agents:custom", agent_id, json.dumps(agent_data))
    redis_client.hset("agents:status", agent_id, "true")
    return {"success": True, "agent": agent_data}


@app.get("/admin/logs")
async def get_logs(filter: str = "all", limit: int = 50):
    """Get system logs."""
    logs = []
    
    # Get from Redis lists
    raw_logs = redis_client.lrange("logs:activity", 0, limit - 1)
    for entry in raw_logs:
        try:
            logs.append(json.loads(entry))
        except:
            pass
    
    # If no logs, return empty list (UI will show demo data)
    if filter != "all":
        logs = [log for log in logs if log.get("level") == filter]
    
    return {"logs": logs, "count": len(logs)}


@app.get("/admin/connectors")
async def get_connectors():
    """Get connector configurations."""
    connectors = redis_client.hgetall("connectors:config") or {}
    return {"connectors": connectors}


@app.post("/admin/connectors/{connector_id}")
async def save_connector(connector_id: str, config: Dict[str, Any]):
    """Save connector configuration."""
    redis_client.hset("connectors:config", connector_id, json.dumps(config))
    return {"success": True, "connector": connector_id}




if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
