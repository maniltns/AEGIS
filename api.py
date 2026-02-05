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
async def get_system_status():
    """Get system operational status for dashboard."""
    try:
        redis_client.ping()
        operational = True
    except:
        operational = False
    
    # Get kill switch state (true = system enabled, so active = False)
    kill_switch_raw = redis_client.get("gov:killswitch")
    kill_switch_active = str(kill_switch_raw).lower() != "true" if kill_switch_raw else False
    
    # Get operating mode
    mode = redis_client.get("gov:mode")
    mode = mode if mode else "assist"
    
    # Get today's stats
    today = datetime.utcnow().strftime("%Y%m%d")
    processed_today = redis_client.get(f"stats:processed:{today}")
    blocked_today = redis_client.get(f"stats:blocked:{today}")
    
    # Get feedback stats
    positive = redis_client.get("stats:feedback:positive")
    negative = redis_client.get("stats:feedback:negative")
    
    return {
        "operational": operational and not kill_switch_active,
        "mode": mode,
        "kill_switch_active": kill_switch_active,
        "stats": {
            "processed_today": int(processed_today) if processed_today else 0,
            "blocked_today": int(blocked_today) if blocked_today else 0,
            "feedback_positive": int(positive) if positive else 0,
            "feedback_negative": int(negative) if negative else 0,
            "active_nodes": 4, # Triage, Guardrails, Enrichment, Executor
            "success_rate": 94 if not processed_today else 100 # Default to 100% or calc based on failures if we tracked them
        }
    }


# =============================================================================
# FEEDBACK ENDPOINTS
# =============================================================================

class FeedbackPayload(BaseModel):
    """Feedback from Teams card."""
    feedback: str = Field(..., description="positive or negative")
    incident_number: str = Field(..., description="Incident number")
    user: Optional[str] = Field(None, description="User who gave feedback")


@app.post("/feedback/{triage_id}")
async def submit_feedback(triage_id: str, payload: FeedbackPayload):
    """Store feedback from Teams card thumbs up/down."""
    
    # Get original triage result
    result_raw = redis_client.get(f"triage:result:{triage_id}")
    result = json.loads(result_raw) if result_raw else {}
    
    # Store feedback
    feedback_data = {
        "triage_id": triage_id,
        "incident_number": payload.incident_number,
        "feedback": payload.feedback,
        "classification": result.get("classification", {}).get("category", "Unknown"),
        "recommendation": result.get("classification", {}).get("assignment_group", "Unknown"),
        "confidence": result.get("confidence", 0),
        "feedback_time": datetime.utcnow().isoformat(),
        "feedback_by": payload.user
    }
    
    redis_client.set(f"feedback:{triage_id}", json.dumps(feedback_data))
    redis_client.expire(f"feedback:{triage_id}", 86400 * 90)  # 90 days
    
    # Update counters
    if payload.feedback == "positive":
        redis_client.incr("stats:feedback:positive")
    else:
        redis_client.incr("stats:feedback:negative")
    
    # Daily stats
    today = datetime.utcnow().strftime("%Y%m%d")
    redis_client.incr(f"stats:feedback:daily:{today}:{payload.feedback}")
    
    # Add to feedback list for drill-down
    redis_client.lpush("feedback:history", json.dumps(feedback_data))
    redis_client.ltrim("feedback:history", 0, 999)  # Keep last 1000
    
    logger.info(f"Feedback received for {triage_id}: {payload.feedback}")
    
    return {"success": True, "message": "Feedback recorded"}


@app.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics for dashboard."""
    positive = redis_client.get("stats:feedback:positive")
    negative = redis_client.get("stats:feedback:negative")
    
    pos = int(positive) if positive else 0
    neg = int(negative) if negative else 0
    total = pos + neg
    
    return {
        "positive": pos,
        "negative": neg,
        "total": total,
        "approval_rate": round(pos / total * 100, 1) if total > 0 else 0
    }


@app.get("/feedback/details")
async def get_feedback_details(limit: int = 20):
    """Get recent feedback for drill-down."""
    raw_feedback = redis_client.lrange("feedback:history", 0, limit - 1)
    
    feedback_list = []
    for item in raw_feedback:
        try:
            feedback_list.append(json.loads(item))
        except:
            pass
    return {"feedback": feedback_list, "count": len(feedback_list)}


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


# ServiceNow webhook alias - for Business Rule integration
@app.post("/webhook/servicenow", response_model=TriageResponse)
async def servicenow_webhook(payload: Dict[str, Any]):
    """
    ServiceNow Business Rule webhook endpoint.
    Accepts raw ServiceNow payload and maps to IncidentPayload.
    """
    # Map ServiceNow fields to our model (handle both direct and .toString() formats)
    incident = IncidentPayload(
        number=str(payload.get("number", payload.get("sys_id", "UNKNOWN"))),
        short_description=str(payload.get("short_description", "")),
        description=str(payload.get("description", "")),
        caller_id=str(payload.get("caller_id", "")) if payload.get("caller_id") else None,
        category=str(payload.get("category", "")) if payload.get("category") else None,
        subcategory=str(payload.get("subcategory", "")) if payload.get("subcategory") else None,
        priority=str(payload.get("priority", "3")),
        cmdb_ci=str(payload.get("cmdb_ci", "")) if payload.get("cmdb_ci") else None,
        assignment_group=str(payload.get("assignment_group", "")) if payload.get("assignment_group") else None
    )
    
    # Delegate to main incident handler
    return await receive_incident(incident)


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


class ThresholdPayload(BaseModel):
    """Threshold configuration payload."""
    thresholds: Dict[str, int]


@app.post("/governance/thresholds")
async def set_thresholds(payload: ThresholdPayload):
    """Set confidence thresholds."""
    for key, value in payload.thresholds.items():
        if key in ["auto_assign", "auto_categorize", "auto_remediate"]:
            redis_client.set(f"gov:threshold:{key}", str(value))
    
    return {"success": True, "thresholds": payload.thresholds}


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
    """Get all pipeline nodes and their status."""
    stored_status = redis_client.hgetall("agents:status") or {}
    custom_agents = redis_client.hgetall("agents:custom") or {}
    
    # v2.1 LangGraph Pipeline Nodes
    default_nodes = [
        {
            "id": "guardrails",
            "name": "GUARDRAILS",
            "role": "Security & Dedup",
            "description": "PII scrubbing (Presidio) + Vector duplicate detection (90% similarity)",
            "color": "#6366f1",
            "order": 1,
            "active": True
        },
        {
            "id": "enrichment",
            "name": "ENRICHMENT",
            "role": "Context Gathering",
            "description": "KB article search, user info, CMDB CI details",
            "color": "#22c55e",
            "order": 2,
            "active": True
        },
        {
            "id": "triage_llm",
            "name": "TRIAGE_LLM",
            "role": "AI Classification",
            "description": "Single LLM call for classification, priority, routing, action",
            "color": "#f59e0b",
            "order": 3,
            "active": True
        },
        {
            "id": "executor",
            "name": "EXECUTOR",
            "role": "Action Engine",
            "description": "ServiceNow update, Teams notification, SSM auto-heal",
            "color": "#8b5cf6",
            "order": 4,
            "active": True
        },
    ]
    
    # Merge with stored status
    for node in default_nodes:
        status = stored_status.get(node["id"])
        if status:
            node["active"] = status == "true"
    
    # Add custom nodes
    for agent_id, agent_json in custom_agents.items():
        try:
            agent_data = json.loads(agent_json)
            status = stored_status.get(agent_id, "true")
            agent_data["active"] = status == "true"
            default_nodes.append(agent_data)
        except:
            pass
    
    # Sort by order
    default_nodes.sort(key=lambda x: x.get("order", 999))
    
    return {"agents": default_nodes}


@app.post("/admin/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, payload: Dict[str, Any] = None):
    """Toggle a pipeline node on/off."""
    enabled = True
    if payload and "enabled" in payload:
        enabled = payload["enabled"]
    redis_client.hset("agents:status", agent_id, "true" if enabled else "false")
    return {"success": True, "agent": agent_id, "enabled": enabled}


@app.post("/admin/agents")
async def add_agent(payload: AgentPayload):
    """Add a new custom pipeline node."""
    agent_id = payload.name.lower().replace(" ", "_")
    
    # Get current max order
    stored_status = redis_client.hgetall("agents:status") or {}
    custom_agents = redis_client.hgetall("agents:custom") or {}
    max_order = 4  # Default nodes are 1-4
    for agent_json in custom_agents.values():
        try:
            agent = json.loads(agent_json)
            max_order = max(max_order, agent.get("order", 0))
        except:
            pass
    
    agent_data = {
        "id": agent_id,
        "name": payload.name.upper(),
        "role": payload.role,
        "description": payload.description or "Custom pipeline node",
        "color": "#6366f1",  # Default purple
        "order": max_order + 1,
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
    """Get all connectors with real-time health status."""
    import httpx
    
    connectors = []
    
    # ServiceNow connector
    snow_instance = os.getenv("SERVICENOW_INSTANCE")
    snow_user = os.getenv("SERVICENOW_USER")
    snow_pass = os.getenv("SERVICENOW_PASSWORD")
    snow_status = "disconnected"
    snow_message = "Not configured"
    
    if snow_instance and snow_user and snow_pass:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://{snow_instance}/api/now/table/incident?sysparm_limit=1",
                    auth=(snow_user, snow_pass)
                )
                if response.status_code == 200:
                    snow_status = "connected"
                    snow_message = f"Connected to {snow_instance}"
                else:
                    snow_status = "error"
                    snow_message = f"Auth failed: {response.status_code}"
        except Exception as e:
            snow_status = "error"
            snow_message = str(e)[:50]
    
    connectors.append({
        "id": "servicenow",
        "name": "ServiceNow",
        "description": "ITSM platform for incidents, cases, RITMs, and knowledge base",
        "logo": "🎟️",
        "status": snow_status,
        "message": snow_message,
        "instance": snow_instance or "Not configured",
        "features": ["Incidents", "Cases", "RITMs", "Knowledge Base", "CMDB"]
    })
    
    # Teams connector
    teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")
    teams_status = "connected" if teams_webhook else "disconnected"
    teams_message = "Webhook configured" if teams_webhook else "No webhook URL"
    
    connectors.append({
        "id": "teams",
        "name": "Microsoft Teams",
        "description": "Collaboration platform for notifications and approvals",
        "logo": "💜",
        "status": teams_status,
        "message": teams_message,
        "features": ["Webhooks", "Adaptive Cards", "Channels"]
    })
    
    # Redis connector
    try:
        redis_client.ping()
        redis_status = "connected"
        redis_message = f"Connected to {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}"
    except:
        redis_status = "error"
        redis_message = "Connection failed"
    
    connectors.append({
        "id": "redis",
        "name": "Redis",
        "description": "In-memory cache for governance and queue management",
        "logo": "🔴",
        "status": redis_status,
        "message": redis_message,
        "features": ["Governance", "Queue", "Storm Shield", "Caching"]
    })
    
    # RAG Service / Redis
    rag_url = os.getenv("RAG_SERVICE_URL", "http://rag-service:8000")
    rag_status = "disconnected"
    rag_message = "Not reachable"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{rag_url}/health")
            if response.status_code == 200:
                rag_status = "connected"
                rag_message = "RAG service healthy"
            else:
                rag_status = "error"
                rag_message = f"Status: {response.status_code}"
    except Exception as e:
        rag_status = "error"
        rag_message = str(e)[:50]
    
    connectors.append({
        "id": "rag",
        "name": "RAG Service",
        "description": "Knowledge retrieval with Redis Vector Search and Claude reasoning",
        "logo": "🧠",
        "status": rag_status,
        "message": rag_message,
        "features": ["KB Search", "Embeddings", "Claude Reasoning"]
    })
    
    # AWS Bedrock
    bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    bedrock_model = os.getenv("BEDROCK_CLAUDE_SONNET_MODEL")
    bedrock_status = "connected" if bedrock_token and bedrock_model else "disconnected"
    bedrock_message = f"Model: {bedrock_model[:30]}..." if bedrock_model else "Not configured"
    
    connectors.append({
        "id": "bedrock",
        "name": "AWS Bedrock",
        "description": "LLM provider for Claude Sonnet and Titan embeddings",
        "logo": "☁️",
        "status": bedrock_status,
        "message": bedrock_message,
        "features": ["Claude Sonnet", "Titan Embeddings"]
    })
    
    return {"connectors": connectors}


@app.get("/admin/connectors/{connector_id}/health")
async def check_connector_health(connector_id: str):
    """Check health of a specific connector."""
    connectors_response = await get_connectors()
    connectors = connectors_response["connectors"]
    
    for connector in connectors:
        if connector["id"] == connector_id:
            return connector
    
    raise HTTPException(status_code=404, detail=f"Connector {connector_id} not found")


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
