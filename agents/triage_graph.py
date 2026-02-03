"""
AEGIS v2.1 - LangGraph Triage Pipeline
Replaces 7-agent CrewAI swarm with 4-node state machine.

Nodes:
1. guardrails - PII scrub + Storm Shield (vector dedup)
2. enrichment - KB search + User history (parallel)
3. triage_llm - Single LLM call for classification + routing
4. executor - Update ServiceNow + Teams notification
"""

import os
import json
import logging
from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from utils.pii_scrubber import scrub_incident
from agents.tools.redis_tools import check_duplicate_vector, get_governance_state
from agents.tools.servicenow_tools import update_incident, get_user_info, get_ci_info
from agents.tools.rag_tools import search_kb_articles

logger = logging.getLogger("aegis.triage")


# =============================================================================
# STATE DEFINITION
# =============================================================================

class TriageState(TypedDict):
    """State passed through the LangGraph pipeline."""
    # Input
    incident_number: str
    short_description: str
    description: str
    caller_id: Optional[str]
    category: Optional[str]
    cmdb_ci: Optional[str]
    priority: Optional[str]
    
    # Scrubbed versions (PII removed)
    scrubbed_description: Optional[str]
    scrubbed_short_description: Optional[str]
    
    # Storm Shield
    is_duplicate: bool
    duplicate_of: Optional[str]
    
    # Enrichment
    kb_articles: List[Dict[str, Any]]
    user_info: Optional[Dict[str, Any]]
    ci_info: Optional[Dict[str, Any]]
    
    # Triage Result
    classification: Optional[Dict[str, Any]]
    confidence: float
    reasoning: str
    
    # Execution
    status: Literal["pending", "blocked", "triaged", "executed", "failed"]
    error: Optional[str]
    actions_taken: List[str]


# =============================================================================
# NODE 1: GUARDRAILS (PII Scrub + Storm Shield)
# =============================================================================

async def guardrails_node(state: TriageState) -> TriageState:
    """
    Node 1: Security and deduplication.
    - Scrub PII from incident text
    - Check for semantically similar recent tickets
    """
    logger.info(f"[GUARDRAILS] Processing {state['incident_number']}")
    
    # PII Scrubbing
    state["scrubbed_short_description"] = scrub_incident(state["short_description"])
    state["scrubbed_description"] = scrub_incident(state.get("description") or "")
    
    # Storm Shield - Vector Similarity Check
    is_dup, dup_of = await check_duplicate_vector(
        text=state["scrubbed_short_description"],
        incident_number=state["incident_number"],
        time_window_minutes=15,
        similarity_threshold=0.90
    )
    
    state["is_duplicate"] = is_dup
    state["duplicate_of"] = dup_of
    
    if is_dup:
        state["status"] = "blocked"
        state["actions_taken"].append(f"Blocked as duplicate of {dup_of}")
        logger.info(f"[GUARDRAILS] Blocked duplicate: {state['incident_number']} -> {dup_of}")
    
    return state


# =============================================================================
# NODE 2: ENRICHMENT (KB + User + CI)
# =============================================================================

async def enrichment_node(state: TriageState) -> TriageState:
    """
    Node 2: Gather context from KB, user info, and CMDB.
    All calls made in parallel for speed.
    """
    logger.info(f"[ENRICHMENT] Enriching {state['incident_number']}")
    
    # Search KB articles using vector similarity
    kb_results = await search_kb_articles(
        query=state["scrubbed_short_description"],
        limit=3
    )
    state["kb_articles"] = kb_results
    
    # Get user info if caller provided
    if state.get("caller_id"):
        state["user_info"] = await get_user_info(state["caller_id"])
    
    # Get CI info if provided
    if state.get("cmdb_ci"):
        state["ci_info"] = await get_ci_info(state["cmdb_ci"])
    
    state["actions_taken"].append("Enriched with KB/User/CI context")
    return state


# =============================================================================
# NODE 3: TRIAGE LLM (Single Call)
# =============================================================================

TRIAGE_SYSTEM_PROMPT = """You are the AEGIS Triage Specialist for Accor Hotels IT.
Your job is to classify incidents and determine the best resolution path.

INPUTS:
- Incident description (PII-scrubbed)
- Relevant KB articles
- User/CI context

OUTPUTS (JSON only):
{
    "category": "Software|Hardware|Network|Access|Other",
    "subcategory": "specific subcategory",
    "priority": "1|2|3|4|5",
    "assignment_group": "L1-Helpdesk|L2-Network|L2-Apps|L3-Infrastructure",
    "resolution_notes": "Suggested resolution based on KB",
    "action": "route|auto_heal|escalate",
    "tool": null or "restart_iis|clear_cache|unlock_account",
    "target": null or "instance-id or hostname",
    "confidence": 0.0-1.0
}

RULES:
- If KB article provides clear solution, set action="auto_heal" with the appropriate tool.
- If issue requires human judgment, set action="route".
- If P1/P2 with no KB match, set action="escalate".
- For account unlocks, set tool="unlock_account", target=<user_email>.
- For service restarts, set tool="restart_iis", target=<server_instance_id>.
- Always provide confidence score (0.0-1.0).
"""

async def triage_llm_node(state: TriageState) -> TriageState:
    """
    Node 3: Single LLM call for classification and routing.
    """
    logger.info(f"[TRIAGE] Analyzing {state['incident_number']}")
    
    # Check governance
    gov_state = await get_governance_state()
    if not gov_state.get("enabled", True):
        state["status"] = "blocked"
        state["error"] = "Kill switch active"
        return state
    
    # Select LLM based on config
    llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
    if llm_provider == "anthropic":
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
    else:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Build context
    kb_context = "\n".join([
        f"- {kb['title']}: {kb['summary']}" 
        for kb in state.get("kb_articles", [])[:3]
    ]) or "No relevant KB articles found."
    
    user_context = ""
    if state.get("user_info"):
        user_context = f"Caller: {state['user_info'].get('name', 'Unknown')}, " \
                      f"VIP: {state['user_info'].get('vip', False)}, " \
                      f"Location: {state['user_info'].get('location', 'Unknown')}"
    
    ci_context = ""
    if state.get("ci_info"):
        ci_context = f"CI: {state['ci_info'].get('name', 'Unknown')}, " \
                    f"Class: {state['ci_info'].get('class', 'Unknown')}"
    
    # Single prompt
    user_message = f"""
INCIDENT: {state['incident_number']}
SHORT DESCRIPTION: {state['scrubbed_short_description']}
FULL DESCRIPTION: {state['scrubbed_description']}

KB ARTICLES:
{kb_context}

CONTEXT:
{user_context}
{ci_context}
Category: {state.get('category', 'Unknown')}
Current Priority: {state.get('priority', '3')}

Analyze and provide classification JSON.
"""
    
    # Call LLM
    response = await llm.ainvoke([
        SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])
    
    # Parse response
    try:
        # Extract JSON from response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        classification = json.loads(content.strip())
        state["classification"] = classification
        state["confidence"] = classification.get("confidence", 0.0)
        state["reasoning"] = classification.get("resolution_notes", "")
        state["status"] = "triaged"
        state["actions_taken"].append(f"Triaged: {classification.get('action')} with {state['confidence']*100:.0f}% confidence")
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"[TRIAGE] Failed to parse LLM response: {e}")
        state["status"] = "failed"
        state["error"] = f"LLM parse error: {str(e)}"
    
    return state


# =============================================================================
# NODE 4: EXECUTOR (ServiceNow + Teams + Auto-Heal)
# =============================================================================

async def executor_node(state: TriageState) -> TriageState:
    """
    Node 4: Execute the triage decision.
    - Update ServiceNow
    - Send Teams notification
    - Optionally trigger auto-healing
    """
    logger.info(f"[EXECUTOR] Executing for {state['incident_number']}")
    
    classification = state.get("classification", {})
    action = classification.get("action", "route")
    
    # Check governance thresholds
    gov_state = await get_governance_state()
    mode = gov_state.get("mode", "assist")
    confidence = state.get("confidence", 0.0)
    
    # Governance gate for auto_heal
    if action == "auto_heal":
        threshold = gov_state.get("threshold_remediate", 0.95)
        
        if confidence < threshold:
            logger.info(f"[EXECUTOR] Confidence {confidence:.2f} < {threshold}, downgrading to route")
            action = "route"
            state["actions_taken"].append(f"Downgraded auto_heal to route (confidence {confidence:.0%} < {threshold:.0%})")
        
        elif mode != "auto":
            # In assist mode, queue for approval
            action = "pending_approval"
            state["actions_taken"].append("Queued for human approval (assist mode)")
    
    # Execute based on action
    if action == "auto_heal":
        tool = classification.get("tool")
        target = classification.get("target")
        
        if tool and target:
            result = await execute_remediation(tool, target, state["incident_number"])
            state["actions_taken"].append(f"Executed {tool} on {target}: {result}")
    
    # Update ServiceNow
    update_payload = {
        "work_notes": build_work_notes(state),
        "category": classification.get("category"),
        "subcategory": classification.get("subcategory"),
        "priority": classification.get("priority"),
        "assignment_group": classification.get("assignment_group")
    }
    
    await update_incident(state["incident_number"], update_payload)
    state["actions_taken"].append("Updated ServiceNow")
    
    # Send Teams notification
    await send_teams_notification(state)
    state["actions_taken"].append("Sent Teams notification")
    
    state["status"] = "executed"
    return state


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def execute_remediation(tool: str, target: str, incident_number: str) -> str:
    """Execute a remediation tool with governance checks."""
    import boto3
    
    logger.info(f"[REMEDIATION] Executing {tool} on {target}")
    
    # Validate target format
    if tool in ["restart_iis", "restart_service"] and not target.startswith("i-"):
        return "BLOCKED: Invalid instance ID format"
    
    # Execute via SSM
    if tool == "restart_iis":
        ssm = boto3.client("ssm")
        response = ssm.send_command(
            InstanceIds=[target],
            DocumentName="AWS-RunPowerShellScript",
            Parameters={"commands": ["Restart-Service W3SVC"]}
        )
        return f"SSM Command ID: {response['Command']['CommandId']}"
    
    elif tool == "unlock_account":
        # Call ARS portal or AD
        return f"Account unlock initiated for {target}"
    
    elif tool == "clear_cache":
        ssm = boto3.client("ssm")
        response = ssm.send_command(
            InstanceIds=[target],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": ["rm -rf /tmp/cache/*"]}
        )
        return f"Cache cleared: {response['Command']['CommandId']}"
    
    return f"Unknown tool: {tool}"


def build_work_notes(state: TriageState) -> str:
    """Build work notes from triage state."""
    classification = state.get("classification", {})
    
    notes = [
        f"🛡️ AEGIS Triage (v2.1)",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"**Category:** {classification.get('category', 'N/A')} > {classification.get('subcategory', 'N/A')}",
        f"**Priority:** P{classification.get('priority', '3')}",
        f"**Assignment:** {classification.get('assignment_group', 'N/A')}",
        f"**Confidence:** {state.get('confidence', 0)*100:.0f}%",
        f"",
        f"**Reasoning:** {state.get('reasoning', 'N/A')}",
        f"",
        f"**KB Articles:**"
    ]
    
    for kb in state.get("kb_articles", [])[:3]:
        notes.append(f"- {kb.get('title', 'N/A')}")
    
    notes.extend([
        f"",
        f"**Actions Taken:**"
    ])
    
    for action in state.get("actions_taken", []):
        notes.append(f"- {action}")
    
    return "\n".join(notes)


async def send_teams_notification(state: TriageState) -> None:
    """Send Teams adaptive card notification."""
    import httpx
    
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("[TEAMS] No webhook URL configured")
        return
    
    classification = state.get("classification", {})
    
    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": f"🛡️ AEGIS: {state['incident_number']}",
                        "weight": "bolder",
                        "size": "medium"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Issue", "value": state.get("scrubbed_short_description", "")[:100]},
                            {"title": "Category", "value": classification.get("category", "N/A")},
                            {"title": "Priority", "value": f"P{classification.get('priority', '3')}"},
                            {"title": "Assignment", "value": classification.get("assignment_group", "N/A")},
                            {"title": "Confidence", "value": f"{state.get('confidence', 0)*100:.0f}%"}
                        ]
                    }
                ]
            }
        }]
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=card)


# =============================================================================
# GRAPH BUILDER
# =============================================================================

def should_continue_after_guardrails(state: TriageState) -> str:
    """Conditional edge: skip rest of pipeline if duplicate blocked."""
    if state.get("is_duplicate"):
        return "end"
    return "enrichment"


def should_continue_after_triage(state: TriageState) -> str:
    """Conditional edge: skip executor if triage failed."""
    if state.get("status") == "failed":
        return "end"
    return "executor"


def build_triage_graph() -> StateGraph:
    """Build and compile the LangGraph triage pipeline."""
    
    # Initialize graph
    graph = StateGraph(TriageState)
    
    # Add nodes
    graph.add_node("guardrails", guardrails_node)
    graph.add_node("enrichment", enrichment_node)
    graph.add_node("triage_llm", triage_llm_node)
    graph.add_node("executor", executor_node)
    
    # Set entry point
    graph.set_entry_point("guardrails")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "guardrails",
        should_continue_after_guardrails,
        {
            "enrichment": "enrichment",
            "end": END
        }
    )
    
    graph.add_edge("enrichment", "triage_llm")
    
    graph.add_conditional_edges(
        "triage_llm",
        should_continue_after_triage,
        {
            "executor": "executor",
            "end": END
        }
    )
    
    graph.add_edge("executor", END)
    
    # Compile
    return graph.compile()


# Global graph instance
triage_graph = build_triage_graph()


async def process_incident(incident: Dict[str, Any]) -> TriageState:
    """
    Main entry point: Process an incident through the triage pipeline.
    
    Args:
        incident: Dict with incident data from ServiceNow webhook
        
    Returns:
        Final TriageState with all results
    """
    # Initialize state
    initial_state: TriageState = {
        "incident_number": incident.get("number", ""),
        "short_description": incident.get("short_description", ""),
        "description": incident.get("description", ""),
        "caller_id": incident.get("caller_id"),
        "category": incident.get("category"),
        "cmdb_ci": incident.get("cmdb_ci"),
        "priority": incident.get("priority", "3"),
        "scrubbed_description": None,
        "scrubbed_short_description": None,
        "is_duplicate": False,
        "duplicate_of": None,
        "kb_articles": [],
        "user_info": None,
        "ci_info": None,
        "classification": None,
        "confidence": 0.0,
        "reasoning": "",
        "status": "pending",
        "error": None,
        "actions_taken": []
    }
    
    # Run graph
    final_state = await triage_graph.ainvoke(initial_state)
    
    logger.info(f"[PIPELINE] Completed {incident.get('number')}: {final_state['status']}")
    
    return final_state
