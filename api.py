# AEGIS API Server
"""
FastAPI server for AEGIS - Autonomous IT Operations Platform
Endpoints for incident processing, webhooks, and admin operations.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis
import uvicorn

from agents.crew import AEGISCrew, process_incident

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("aegis.api")

# Redis client for governance
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


# =============================================================================
# STARTUP / SHUTDOWN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🛡️ AEGIS API Server starting...")
    
    # Initialize governance defaults if not set
    if not redis_client.get("gov:killswitch"):
        redis_client.set("gov:killswitch", "true")  # true = system enabled
    if not redis_client.get("gov:mode"):
        redis_client.set("gov:mode", "assist")  # assist = AI + human review
    
    logger.info("✅ AEGIS API Server ready")
    yield
    logger.info("🛡️ AEGIS API Server shutting down...")


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="AEGIS API",
    description="Autonomous IT Operations & Swarming Platform",
    version="2.0.0",
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
    
    return {
        "status": "healthy",
        "service": "aegis-api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "redis": redis_status,
            "crewai": "ready"
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
    
    return {
        "operational": kill_switch == "true",
        "mode": mode,
        "kill_switch_active": kill_switch == "false",
        "stats": {
            "processed_today": int(processed_today),
            "blocked_today": int(blocked_today)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# INCIDENT PROCESSING ENDPOINTS
# =============================================================================

@app.post("/webhook/incident", response_model=TriageResponse)
async def receive_incident(
    incident: IncidentPayload,
    background_tasks: BackgroundTasks
):
    """
    Receive incident from ServiceNow webhook.
    Triggers async processing through AEGIS agent crew.
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
    
    # Queue for background processing
    background_tasks.add_task(
        process_incident_async,
        incident.model_dump(),
        triage_id
    )
    
    # Increment stats
    today = datetime.utcnow().strftime("%Y%m%d")
    redis_client.incr(f"stats:processed:{today}")
    
    return TriageResponse(
        status="accepted",
        incident_number=incident.number,
        triage_id=triage_id,
        message="Incident queued for AI triage"
    )


async def process_incident_async(incident: Dict[str, Any], triage_id: str):
    """Background task to process incident through CrewAI."""
    logger.info(f"Processing {incident['number']} with triage ID {triage_id}")
    
    try:
        result = await process_incident(incident)
        logger.info(f"Completed processing {incident['number']}: {result['status']}")
        
        # Store result
        redis_client.set(
            f"triage:result:{triage_id}",
            json.dumps(result),
            ex=86400  # 24 hour TTL
        )
    except Exception as e:
        logger.error(f"Error processing {incident['number']}: {e}")
        redis_client.set(
            f"triage:result:{triage_id}",
            json.dumps({"status": "error", "error": str(e)}),
            ex=86400
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
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
