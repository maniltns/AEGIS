# AEGIS ServiceNow Tools - v2.1 (LangGraph Compatible)
"""
ServiceNow integration tools for AEGIS.
Plain async functions for use with LangGraph pipeline.
"""

import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aegis.servicenow")

# ServiceNow Configuration
SNOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE", "accordev.service-now.com")
SNOW_USER = os.getenv("SERVICENOW_USER")
SNOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")


class ServiceNowClient:
    """HTTP client for ServiceNow REST API."""
    
    def __init__(self):
        self.base_url = f"https://{SNOW_INSTANCE}/api/now"
        self.auth = (SNOW_USER, SNOW_PASSWORD)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """GET request to ServiceNow API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request to ServiceNow API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def patch(self, endpoint: str, data: Dict) -> Dict:
        """PATCH request to ServiceNow API."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()


# =============================================================================
# ASYNC TOOL FUNCTIONS
# =============================================================================

async def get_user_info(email_or_id: str) -> Optional[Dict[str, Any]]:
    """Get user information from ServiceNow."""
    client = ServiceNowClient()
    
    try:
        result = await client.get("table/sys_user", {
            "sysparm_query": f"email={email_or_id}^ORsys_id={email_or_id}",
            "sysparm_limit": 1,
            "sysparm_fields": "name,email,vip,department,location,manager,title"
        })
        
        users = result.get("result", [])
        if users:
            return users[0]
        return None
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return None


async def get_ci_info(ci_name: str) -> Optional[Dict[str, Any]]:
    """Get CMDB CI information."""
    client = ServiceNowClient()
    
    try:
        result = await client.get("table/cmdb_ci", {
            "sysparm_query": f"nameLIKE{ci_name}^ORsys_id={ci_name}",
            "sysparm_limit": 1,
            "sysparm_fields": "name,sys_class_name,operational_status,support_group,business_criticality"
        })
        
        cis = result.get("result", [])
        if cis:
            return cis[0]
        return None
    except Exception as e:
        logger.error(f"Failed to get CI info: {e}")
        return None


async def update_incident(incident_number: str, fields: Dict[str, Any]) -> bool:
    """Update a ServiceNow incident."""
    client = ServiceNowClient()
    
    try:
        # First get the sys_id
        lookup = await client.get("table/incident", {
            "sysparm_query": f"number={incident_number}",
            "sysparm_limit": 1,
            "sysparm_fields": "sys_id"
        })
        
        incidents = lookup.get("result", [])
        if not incidents:
            logger.error(f"Incident {incident_number} not found")
            return False
        
        sys_id = incidents[0]["sys_id"]
        
        # Update the incident
        await client.patch(f"table/incident/{sys_id}", fields)
        logger.info(f"Updated incident {incident_number}: {list(fields.keys())}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update incident {incident_number}: {e}")
        return False


async def add_work_note(incident_number: str, note: str) -> bool:
    """Add a work note to an incident."""
    aegis_note = f"[AEGIS AI] {note}"
    return await update_incident(incident_number, {"work_notes": aegis_note})


async def get_recent_incidents(
    ci_name: str = None, 
    category: str = None, 
    hours: int = 24
) -> List[Dict[str, Any]]:
    """Get recent open incidents."""
    client = ServiceNowClient()
    
    try:
        query = "state!=6^state!=7"  # Not resolved, not closed
        if ci_name:
            query += f"^cmdb_ci.nameLIKE{ci_name}"
        if category:
            query += f"^category={category}"
        
        result = await client.get("table/incident", {
            "sysparm_query": query,
            "sysparm_limit": 50,
            "sysparm_fields": "number,short_description,category,priority,state,sys_created_on"
        })
        
        return result.get("result", [])
    except Exception as e:
        logger.error(f"Failed to get recent incidents: {e}")
        return []


async def search_kb_servicenow(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search ServiceNow Knowledge Base."""
    client = ServiceNowClient()
    
    try:
        result = await client.get("table/kb_knowledge", {
            "sysparm_query": f"short_descriptionLIKE{query}^ORtextLIKE{query}",
            "sysparm_limit": limit,
            "sysparm_fields": "number,short_description,text,kb_category"
        })
        
        return result.get("result", [])
    except Exception as e:
        logger.error(f"Failed to search KB: {e}")
        return []


async def get_assignment_groups(category: str) -> List[Dict[str, Any]]:
    """Get assignment groups for a category."""
    client = ServiceNowClient()
    
    try:
        result = await client.get("table/sys_user_group", {
            "sysparm_query": f"active=true^typeLIKE{category}",
            "sysparm_limit": 10,
            "sysparm_fields": "name,manager,email"
        })
        
        return result.get("result", [])
    except Exception as e:
        logger.error(f"Failed to get assignment groups: {e}")
        return []


async def create_incident(
    short_description: str,
    description: str,
    category: str,
    priority: str = "3",
    caller_id: str = None
) -> Optional[Dict[str, Any]]:
    """Create a new incident in ServiceNow."""
    client = ServiceNowClient()
    
    try:
        result = await client.post("table/incident", {
            "short_description": short_description,
            "description": description,
            "category": category,
            "priority": priority,
            "caller_id": caller_id,
            "work_notes": "[AEGIS AI] Incident created by AEGIS platform"
        })
        
        return result.get("result", {})
    except Exception as e:
        logger.error(f"Failed to create incident: {e}")
        return None
