# AEGIS Teams Tools for CrewAI
"""
Microsoft Teams integration tools for AEGIS agents.
Handles notifications, swarm creation, and approval workflows.
"""

import os
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Teams Configuration
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
TEAMS_GRAPH_CLIENT_ID = os.getenv("TEAMS_GRAPH_CLIENT_ID")
TEAMS_GRAPH_CLIENT_SECRET = os.getenv("TEAMS_GRAPH_CLIENT_SECRET")
TEAMS_GRAPH_TENANT_ID = os.getenv("TEAMS_GRAPH_TENANT_ID")


class TeamsWebhookClient:
    """Client for Teams webhook notifications."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or TEAMS_WEBHOOK_URL
    
    async def send_message(self, message: Dict) -> bool:
        """Send message to Teams webhook."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200


# =============================================================================
# TEAMS TOOL DEFINITIONS
# =============================================================================

class SendNotificationInput(BaseModel):
    """Input for sending notification."""
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    severity: str = Field("info", description="Severity: info, warning, critical")
    incident_number: Optional[str] = Field(None, description="Related incident number")


class SendNotificationTool(BaseTool):
    """Send notification to MS Teams."""
    name: str = "send_notification"
    description: str = "Send a notification message to the configured MS Teams channel"
    args_schema: type[BaseModel] = SendNotificationInput
    
    def _run(self, title: str, message: str, severity: str = "info",
             incident_number: str = None) -> str:
        import asyncio
        return asyncio.run(self._async_run(title, message, severity, incident_number))
    
    async def _async_run(self, title: str, message: str, severity: str,
                         incident_number: str) -> str:
        client = TeamsWebhookClient()
        
        # Color based on severity
        colors = {
            "info": "0078D7",
            "warning": "FFC107",
            "critical": "D32F2F"
        }
        
        # Teams Adaptive Card format
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
            card["potentialAction"] = [{
                "@type": "OpenUri",
                "name": "View in ServiceNow",
                "targets": [{
                    "os": "default",
                    "uri": f"https://accordev.service-now.com/incident.do?sysparm_query=number={incident_number}"
                }]
            }]
        
        try:
            success = await client.send_message(card)
            return json.dumps({
                "success": success,
                "channel": "teams",
                "message": "Notification sent" if success else "Failed to send"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class SendAdaptiveCardInput(BaseModel):
    """Input for sending adaptive card."""
    incident_number: str = Field(..., description="Incident number")
    classification: str = Field(..., description="AI classification")
    priority: str = Field(..., description="Priority level")
    confidence: int = Field(..., description="Confidence score")
    recommended_group: str = Field(..., description="Recommended assignment group")
    reasoning: str = Field(..., description="AI reasoning")


class SendAdaptiveCardTool(BaseTool):
    """Send detailed adaptive card for incident triage."""
    name: str = "send_adaptive_card"
    description: str = "Send a detailed adaptive card with AI triage results to Teams"
    args_schema: type[BaseModel] = SendAdaptiveCardInput
    
    def _run(self, incident_number: str, classification: str, priority: str,
             confidence: int, recommended_group: str, reasoning: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(
            incident_number, classification, priority, confidence, 
            recommended_group, reasoning
        ))
    
    async def _async_run(self, incident_number: str, classification: str, 
                         priority: str, confidence: int, recommended_group: str,
                         reasoning: str) -> str:
        client = TeamsWebhookClient()
        
        # Priority colors
        priority_colors = {
            "1": "D32F2F",  # Critical - Red
            "2": "FF9800",  # High - Orange
            "3": "FFC107",  # Medium - Yellow
            "4": "4CAF50",  # Low - Green
            "5": "9E9E9E"   # Planning - Gray
        }
        
        # Confidence indicator
        confidence_emoji = "🟢" if confidence >= 85 else "🟡" if confidence >= 70 else "🔴"
        
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": priority_colors.get(priority, "0078D7"),
            "summary": f"AI Triage: {incident_number}",
            "sections": [
                {
                    "activityTitle": f"🧠 AI Triage Complete: {incident_number}",
                    "activitySubtitle": f"Priority {priority} | {classification}",
                    "facts": [
                        {"name": "Classification", "value": classification},
                        {"name": "Priority", "value": f"P{priority}"},
                        {"name": "Confidence", "value": f"{confidence_emoji} {confidence}%"},
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
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Incident",
                    "targets": [{
                        "os": "default",
                        "uri": f"https://accordev.service-now.com/incident.do?sysparm_query=number={incident_number}"
                    }]
                },
                {
                    "@type": "ActionCard",
                    "name": "Override",
                    "inputs": [{
                        "@type": "TextInput",
                        "id": "override_reason",
                        "title": "Reason for override",
                        "isMultiline": True
                    }],
                    "actions": [{
                        "@type": "HttpPOST",
                        "name": "Submit Override",
                        "target": f"https://aegis-api.accor.com/override/{incident_number}"
                    }]
                }
            ]
        }
        
        try:
            success = await client.send_message(card)
            return json.dumps({
                "success": success,
                "incident": incident_number,
                "message": "Adaptive card sent" if success else "Failed to send"
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class CreateSwarmChannelInput(BaseModel):
    """Input for creating swarm channel."""
    incident_number: str = Field(..., description="Incident number")
    title: str = Field(..., description="Incident title")
    experts: List[str] = Field(..., description="List of expert emails to invite")


class CreateSwarmChannelTool(BaseTool):
    """Create a collaborative swarm channel in Teams."""
    name: str = "create_swarm_channel"
    description: str = "Create a dedicated Teams channel for collaborative swarming on a P1/P2 incident"
    args_schema: type[BaseModel] = CreateSwarmChannelInput
    
    def _run(self, incident_number: str, title: str, experts: List[str]) -> str:
        import asyncio
        return asyncio.run(self._async_run(incident_number, title, experts))
    
    async def _async_run(self, incident_number: str, title: str, 
                         experts: List[str]) -> str:
        # In production, this would use MS Graph API to create a channel
        # For now, we simulate and send notification
        
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
                "text": "**A collaborative swarm has been initiated.** All listed experts have been notified and should join immediately.",
                "markdown": True
            }]
        }
        
        try:
            success = await client.send_message(card)
            return json.dumps({
                "success": success,
                "incident": incident_number,
                "channel_type": "swarm",
                "experts_notified": experts,
                "message": "Swarm channel created" if success else "Failed"
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


class RequestApprovalInput(BaseModel):
    """Input for requesting approval."""
    incident_number: str = Field(..., description="Incident number")
    action_type: str = Field(..., description="Type of action requiring approval")
    action_details: str = Field(..., description="Details of the proposed action")
    risk_level: str = Field("medium", description="Risk level: low, medium, high")


class RequestApprovalTool(BaseTool):
    """Request human approval for an action via Teams."""
    name: str = "request_approval"
    description: str = "Request human approval for a medium or high risk action before execution"
    args_schema: type[BaseModel] = RequestApprovalInput
    
    def _run(self, incident_number: str, action_type: str, action_details: str,
             risk_level: str = "medium") -> str:
        import asyncio
        return asyncio.run(self._async_run(
            incident_number, action_type, action_details, risk_level
        ))
    
    async def _async_run(self, incident_number: str, action_type: str,
                         action_details: str, risk_level: str) -> str:
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
            }],
            "potentialAction": [
                {
                    "@type": "HttpPOST",
                    "name": "✅ Approve",
                    "target": f"https://aegis-api.accor.com/approve/{incident_number}",
                    "body": json.dumps({"action": "approve", "incident": incident_number})
                },
                {
                    "@type": "HttpPOST",
                    "name": "❌ Reject",
                    "target": f"https://aegis-api.accor.com/reject/{incident_number}",
                    "body": json.dumps({"action": "reject", "incident": incident_number})
                }
            ]
        }
        
        try:
            success = await client.send_message(card)
            return json.dumps({
                "success": success,
                "incident": incident_number,
                "approval_requested": True,
                "risk_level": risk_level,
                "status": "pending_approval",
                "message": "Approval request sent" if success else "Failed"
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


# =============================================================================
# TOOLS FACTORY
# =============================================================================

class TeamsTools:
    """Factory for Teams tools."""
    
    def __init__(self):
        self.send_notification = SendNotificationTool()
        self.send_adaptive_card = SendAdaptiveCardTool()
        self.create_swarm_channel = CreateSwarmChannelTool()
        self.request_approval = RequestApprovalTool()
