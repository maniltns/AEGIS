# AEGIS Teams Tools - v2.1 (LangGraph Compatible)
"""
Microsoft Teams integration tools for AEGIS.
Plain async functions for use with LangGraph pipeline.
"""

import os
import json
import logging
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aegis.teams_tools")

# Teams Configuration
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")


class TeamsWebhookClient:
    """Client for Teams webhook notifications."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or TEAMS_WEBHOOK_URL
    
    async def send_message(self, message: Dict) -> bool:
        """Send message to Teams webhook."""
        if not self.webhook_url:
            logger.warning("Teams webhook URL not configured")
            return False
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200


# =============================================================================
# ASYNC TOOL FUNCTIONS
# =============================================================================

async def send_notification(
    title: str,
    message: str,
    severity: str = "info",
    incident_number: str = None
) -> bool:
    """
    Send notification to MS Teams.
    
    Args:
        title: Notification title
        message: Notification message
        severity: info, warning, critical
        incident_number: Related incident
        
    Returns:
        True if sent successfully
    """
    client = TeamsWebhookClient()
    
    colors = {
        "info": "0078D7",
        "warning": "FFC107",
        "critical": "D32F2F"
    }
    
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": colors.get(severity, "0078D7"),
        "summary": title,
        "sections": [{
            "activityTitle": f"🛡️ AEGIS: {title}",
            "facts": [
                {"name": "Severity", "value": severity.upper()},
                {"name": "Time", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
            ],
            "text": message,
            "markdown": True
        }]
    }
    
    if incident_number:
        card["sections"][0]["facts"].append({
            "name": "Incident", "value": incident_number
        })
    
    try:
        return await client.send_message(card)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False


async def send_triage_card(
    incident_number: str,
    classification: str,
    priority: str,
    confidence: float,
    recommended_group: str,
    reasoning: str
) -> bool:
    """
    Send detailed adaptive card with AI triage results.
    
    Returns:
        True if sent successfully
    """
    client = TeamsWebhookClient()
    
    priority_colors = {
        "1": "D32F2F",  # Critical - Red
        "2": "FF9800",  # High - Orange
        "3": "FFC107",  # Medium - Yellow
        "4": "4CAF50",  # Low - Green
        "5": "9E9E9E"   # Planning - Gray
    }
    
    confidence_pct = int(confidence * 100)
    confidence_emoji = "🟢" if confidence_pct >= 85 else "🟡" if confidence_pct >= 70 else "🔴"
    
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": priority_colors.get(str(priority), "0078D7"),
        "summary": f"AI Triage: {incident_number}",
        "sections": [
            {
                "activityTitle": f"🧠 AI Triage Complete: {incident_number}",
                "activitySubtitle": f"Priority {priority} | {classification}",
                "facts": [
                    {"name": "Classification", "value": classification},
                    {"name": "Priority", "value": f"P{priority}"},
                    {"name": "Confidence", "value": f"{confidence_emoji} {confidence_pct}%"},
                    {"name": "Recommended Group", "value": recommended_group},
                    {"name": "Triaged At", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
                ],
                "markdown": True
            },
            {
                "activityTitle": "📋 AI Reasoning",
                "text": reasoning,
                "markdown": True
            }
        ]
    }
    
    try:
        return await client.send_message(card)
    except Exception as e:
        logger.error(f"Failed to send triage card: {e}")
        return False


async def create_swarm_notification(
    incident_number: str,
    title: str,
    experts: List[str]
) -> bool:
    """
    Send swarm activation notification for P1/P2 incidents.
    
    Returns:
        True if sent successfully
    """
    client = TeamsWebhookClient()
    
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "D32F2F",
        "summary": f"Swarm Activated: {incident_number}",
        "sections": [{
            "activityTitle": f"🚨 SWARM ACTIVATED: {incident_number}",
            "activitySubtitle": title,
            "facts": [
                {"name": "Experts Called", "value": ", ".join(experts)},
                {"name": "Swarm Started", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
            ],
            "text": "**A collaborative swarm has been initiated.** All listed experts have been notified.",
            "markdown": True
        }]
    }
    
    try:
        return await client.send_message(card)
    except Exception as e:
        logger.error(f"Failed to send swarm notification: {e}")
        return False


async def request_approval(
    incident_number: str,
    action_type: str,
    action_details: str,
    risk_level: str = "medium"
) -> bool:
    """
    Request human approval for an action via Teams.
    
    Returns:
        True if request sent successfully
    """
    client = TeamsWebhookClient()
    
    risk_colors = {
        "low": "4CAF50",
        "medium": "FFC107",
        "high": "D32F2F"
    }
    
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": risk_colors.get(risk_level, "FFC107"),
        "summary": f"Approval Required: {incident_number}",
        "sections": [{
            "activityTitle": f"⚠️ APPROVAL REQUIRED: {action_type}",
            "activitySubtitle": f"Incident: {incident_number}",
            "facts": [
                {"name": "Action", "value": action_type},
                {"name": "Risk Level", "value": f"{risk_emoji.get(risk_level, '🟡')} {risk_level.upper()}"},
                {"name": "Requested At", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
            ],
            "text": f"**Proposed Action:**\n{action_details}",
            "markdown": True
        }]
    }
    
    try:
        return await client.send_message(card)
    except Exception as e:
        logger.error(f"Failed to send approval request: {e}")
        return False


async def send_enhanced_triage_card(
    triage_id: str,
    incident_number: str,
    short_description: str,
    classification: dict,
    reasoning: str,
    kb_articles: List[dict] = None,
    user_info: dict = None,
    ticket_history: int = 0,
    servicenow_instance: str = None,
    api_base_url: str = None
) -> bool:
    """
    Send enhanced adaptive card with detailed analysis and feedback buttons.
    
    Args:
        triage_id: Triage ID for feedback tracking
        incident_number: Incident number
        short_description: Issue description
        classification: Classification dict with category, priority, assignment_group
        reasoning: AI reasoning text
        kb_articles: List of relevant KB articles (top 5)
        user_info: Caller information
        ticket_history: Number of past tickets
        servicenow_instance: ServiceNow instance URL
        api_base_url: AEGIS API base URL for feedback
    
    Returns:
        True if sent successfully
    """
    client = TeamsWebhookClient()
    
    # Extract classification details
    category = classification.get("category", "Unknown")
    priority = classification.get("priority", "3")
    assignment_group = classification.get("assignment_group", "L1-Helpdesk")
    confidence = classification.get("confidence", 0)
    
    # Priority mapping
    priority_colors = {
        "1": "D32F2F", "2": "FF9800", "3": "FFC107", "4": "4CAF50", "5": "9E9E9E"
    }
    
    confidence_pct = int(confidence * 100) if confidence <= 1 else int(confidence)
    
    # Build user info text
    user_text = "Unknown"
    if user_info:
        user_name = user_info.get("name", "Unknown")
        user_type = "VIP" if user_info.get("vip") else "External" if user_info.get("external") else "Internal"
        user_text = f"{user_name} ({user_type})"
    
    # Build KB articles section
    kb_text = "No matching articles"
    if kb_articles and len(kb_articles) > 0:
        kb_lines = []
        snow_url = servicenow_instance or os.getenv("SERVICENOW_INSTANCE", "")
        for i, kb in enumerate(kb_articles[:5], 1):
            kb_number = kb.get("number", kb.get("title", f"KB{i}"))
            kb_title = kb.get("title", kb.get("short_description", ""))[:50]
            if snow_url:
                kb_lines.append(f"{i}. [{kb_number}]({snow_url}/kb_view.do?sys_kb_id={kb.get('sys_id', '')}) - {kb_title}")
            else:
                kb_lines.append(f"{i}. {kb_number} - {kb_title}")
        kb_text = "\n".join(kb_lines)
    
    # Parse reasoning into sections
    assessment = reasoning[:200] if reasoning else "No assessment available"
    root_cause = ""
    action = ""
    
    if reasoning:
        lines = reasoning.split(".")
        if len(lines) > 1:
            assessment = lines[0] + "."
            root_cause = lines[1] + "." if len(lines) > 1 else ""
            action = ". ".join(lines[2:])[:150] if len(lines) > 2 else ""
    
    # ServiceNow link
    snow_instance = servicenow_instance or os.getenv("SERVICENOW_INSTANCE", "")
    incident_link = f"{snow_instance}/incident.do?sysparm_query=number={incident_number}" if snow_instance else "#"
    
    # API URL for feedback
    api_url = api_base_url or os.getenv("AEGIS_API_URL", "http://localhost:8080")
    
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": priority_colors.get(str(priority), "0078D7"),
        "summary": f"Analysis: {incident_number}",
        "sections": [
            {
                "activityTitle": f"🔍 Analysis: {incident_number}",
                "facts": [
                    {"name": "User", "value": user_text},
                    {"name": "Issue", "value": short_description[:80]},
                    {"name": "Priority", "value": f"{priority} / 5"},
                    {"name": "History", "value": f"{ticket_history} tickets" if ticket_history else "No history"},
                ],
                "markdown": True
            },
            {
                "activityTitle": "📋 Analysis",
                "text": f"• **Assessment:** {assessment}\n\n• **Root Cause:** {root_cause}\n\n• **Action:** {action if action else assignment_group}",
                "markdown": True
            },
            {
                "activityTitle": "📚 Suggested KB Articles",
                "text": kb_text,
                "markdown": True
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": f"View {incident_number}",
                "targets": [{"os": "default", "uri": incident_link}]
            },
            {
                "@type": "OpenUri",
                "name": "👍 Helpful",
                "targets": [{"os": "default", "uri": f"{api_url}/feedback/{triage_id}?feedback=positive&incident={incident_number}&user=Teams"}]
            },
            {
                "@type": "OpenUri",
                "name": "👎 Not Helpful",
                "targets": [{"os": "default", "uri": f"{api_url}/feedback/{triage_id}?feedback=negative&incident={incident_number}&user=Teams"}]
            }
        ]
    }
    
    try:
        success = await client.send_message(card)
        if success:
            logger.info(f"Enhanced triage card sent for {incident_number}")
        return success
    except Exception as e:
        logger.error(f"Failed to send enhanced triage card: {e}")
        return False
