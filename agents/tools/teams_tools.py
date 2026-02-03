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
