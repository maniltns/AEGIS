# AEGIS ServiceNow Tools for CrewAI
"""
ServiceNow integration tools for AEGIS agents.
Provides CRUD operations on incidents, cases, CMDB, and KB articles.
"""

import os
import json
import httpx
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

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
        async with httpx.AsyncClient() as client:
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
        async with httpx.AsyncClient() as client:
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
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

class GetRecentIncidentsInput(BaseModel):
    """Input for getting recent incidents."""
    ci_name: Optional[str] = Field(None, description="CI name to filter by")
    category: Optional[str] = Field(None, description="Category to filter by")
    hours: int = Field(24, description="Number of hours to look back")


class GetRecentIncidentsTool(BaseTool):
    """Get recent incidents for duplicate detection."""
    name: str = "get_recent_incidents"
    description: str = "Get recent open incidents, optionally filtered by CI or category"
    args_schema: type[BaseModel] = GetRecentIncidentsInput
    
    def _run(self, ci_name: str = None, category: str = None, hours: int = 24) -> str:
        """Synchronous wrapper for async operation."""
        import asyncio
        return asyncio.run(self._async_run(ci_name, category, hours))
    
    async def _async_run(self, ci_name: str, category: str, hours: int) -> str:
        client = ServiceNowClient()
        
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
        
        return json.dumps(result.get("result", []), indent=2)


class GetUserInfoInput(BaseModel):
    """Input for getting user information."""
    email: str = Field(..., description="User email address")


class GetUserInfoTool(BaseTool):
    """Get user information from ServiceNow."""
    name: str = "get_user_info"
    description: str = "Get user details including VIP status, location, and department"
    args_schema: type[BaseModel] = GetUserInfoInput
    
    def _run(self, email: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(email))
    
    async def _async_run(self, email: str) -> str:
        client = ServiceNowClient()
        
        result = await client.get("table/sys_user", {
            "sysparm_query": f"email={email}",
            "sysparm_limit": 1,
            "sysparm_fields": "name,email,vip,department,location,manager,title"
        })
        
        users = result.get("result", [])
        if users:
            return json.dumps(users[0], indent=2)
        return json.dumps({"error": "User not found"})


class GetCIInfoInput(BaseModel):
    """Input for getting CI information."""
    ci_name: str = Field(..., description="Configuration Item name")


class GetCIInfoTool(BaseTool):
    """Get CMDB CI information."""
    name: str = "get_ci_info"
    description: str = "Get Configuration Item details from CMDB"
    args_schema: type[BaseModel] = GetCIInfoInput
    
    def _run(self, ci_name: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(ci_name))
    
    async def _async_run(self, ci_name: str) -> str:
        client = ServiceNowClient()
        
        result = await client.get("table/cmdb_ci", {
            "sysparm_query": f"nameLIKE{ci_name}",
            "sysparm_limit": 5,
            "sysparm_fields": "name,sys_class_name,operational_status,support_group,business_criticality"
        })
        
        return json.dumps(result.get("result", []), indent=2)


class SearchKBInput(BaseModel):
    """Input for KB search."""
    query: str = Field(..., description="Search query for KB articles")


class SearchKBTool(BaseTool):
    """Search ServiceNow Knowledge Base."""
    name: str = "search_kb"
    description: str = "Search Knowledge Base articles for relevant solutions"
    args_schema: type[BaseModel] = SearchKBInput
    
    def _run(self, query: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(query))
    
    async def _async_run(self, query: str) -> str:
        client = ServiceNowClient()
        
        result = await client.get("table/kb_knowledge", {
            "sysparm_query": f"short_descriptionLIKE{query}^ORtextLIKE{query}",
            "sysparm_limit": 5,
            "sysparm_fields": "number,short_description,text,kb_category"
        })
        
        return json.dumps(result.get("result", []), indent=2)


class UpdateIncidentInput(BaseModel):
    """Input for updating an incident."""
    incident_number: str = Field(..., description="Incident number (e.g., INC0012345)")
    fields: Dict[str, Any] = Field(..., description="Fields to update")


class UpdateIncidentTool(BaseTool):
    """Update a ServiceNow incident."""
    name: str = "update_incident"
    description: str = "Update incident fields including assignment, category, priority, work notes"
    args_schema: type[BaseModel] = UpdateIncidentInput
    
    def _run(self, incident_number: str, fields: Dict[str, Any]) -> str:
        import asyncio
        return asyncio.run(self._async_run(incident_number, fields))
    
    async def _async_run(self, incident_number: str, fields: Dict[str, Any]) -> str:
        client = ServiceNowClient()
        
        # First get the sys_id
        lookup = await client.get("table/incident", {
            "sysparm_query": f"number={incident_number}",
            "sysparm_limit": 1,
            "sysparm_fields": "sys_id"
        })
        
        incidents = lookup.get("result", [])
        if not incidents:
            return json.dumps({"error": f"Incident {incident_number} not found"})
        
        sys_id = incidents[0]["sys_id"]
        
        # Update the incident
        result = await client.patch(f"table/incident/{sys_id}", fields)
        
        return json.dumps({
            "success": True,
            "incident": incident_number,
            "updated_fields": list(fields.keys())
        })


class AddWorkNoteInput(BaseModel):
    """Input for adding work note."""
    incident_number: str = Field(..., description="Incident number")
    note: str = Field(..., description="Work note content")


class AddWorkNoteTool(BaseTool):
    """Add a work note to an incident."""
    name: str = "add_work_note"
    description: str = "Add a work note to document AI reasoning and actions"
    args_schema: type[BaseModel] = AddWorkNoteInput
    
    def _run(self, incident_number: str, note: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(incident_number, note))
    
    async def _async_run(self, incident_number: str, note: str) -> str:
        client = ServiceNowClient()
        
        # Get sys_id
        lookup = await client.get("table/incident", {
            "sysparm_query": f"number={incident_number}",
            "sysparm_limit": 1,
            "sysparm_fields": "sys_id"
        })
        
        incidents = lookup.get("result", [])
        if not incidents:
            return json.dumps({"error": f"Incident {incident_number} not found"})
        
        sys_id = incidents[0]["sys_id"]
        
        # Add work note prefixed with AEGIS tag
        aegis_note = f"[AEGIS AI] {note}"
        result = await client.patch(f"table/incident/{sys_id}", {
            "work_notes": aegis_note
        })
        
        return json.dumps({"success": True, "incident": incident_number})


class GetAssignmentGroupsInput(BaseModel):
    """Input for getting assignment groups."""
    category: str = Field(..., description="Incident category")


class GetAssignmentGroupsTool(BaseTool):
    """Get assignment groups for a category."""
    name: str = "get_assignment_groups"
    description: str = "Get available assignment groups based on incident category"
    args_schema: type[BaseModel] = GetAssignmentGroupsInput
    
    def _run(self, category: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(category))
    
    async def _async_run(self, category: str) -> str:
        client = ServiceNowClient()
        
        result = await client.get("table/sys_user_group", {
            "sysparm_query": f"active=true^typeLIKE{category}",
            "sysparm_limit": 10,
            "sysparm_fields": "name,manager,email"
        })
        
        return json.dumps(result.get("result", []), indent=2)


class CreateIncidentInput(BaseModel):
    """Input for creating an incident."""
    short_description: str = Field(..., description="Short description")
    description: str = Field(..., description="Full description")
    category: str = Field(..., description="Category")
    priority: str = Field("3", description="Priority 1-5")
    caller_id: str = Field(..., description="Caller email or sys_id")


class CreateIncidentTool(BaseTool):
    """Create a new incident."""
    name: str = "create_incident"
    description: str = "Create a new incident in ServiceNow"
    args_schema: type[BaseModel] = CreateIncidentInput
    
    def _run(self, short_description: str, description: str, category: str, 
             priority: str, caller_id: str) -> str:
        import asyncio
        return asyncio.run(self._async_run(
            short_description, description, category, priority, caller_id
        ))
    
    async def _async_run(self, short_description: str, description: str, 
                         category: str, priority: str, caller_id: str) -> str:
        client = ServiceNowClient()
        
        result = await client.post("table/incident", {
            "short_description": short_description,
            "description": description,
            "category": category,
            "priority": priority,
            "caller_id": caller_id,
            "work_notes": "[AEGIS AI] Incident created by AEGIS platform"
        })
        
        incident = result.get("result", {})
        return json.dumps({
            "success": True,
            "number": incident.get("number"),
            "sys_id": incident.get("sys_id")
        })


# =============================================================================
# TOOLS FACTORY
# =============================================================================

class ServiceNowTools:
    """Factory for ServiceNow tools."""
    
    def __init__(self):
        self.get_recent_incidents = GetRecentIncidentsTool()
        self.get_user_info = GetUserInfoTool()
        self.get_ci_info = GetCIInfoTool()
        self.search_kb = SearchKBTool()
        self.update_incident = UpdateIncidentTool()
        self.add_work_note = AddWorkNoteTool()
        self.get_assignment_groups = GetAssignmentGroupsTool()
        self.create_incident = CreateIncidentTool()
        
        # Aliases for type compatibility
        self.get_case = self.get_recent_incidents
        self.link_records = self.update_incident
        self.update_audit_log = self.add_work_note
        self.get_category_mapping = self.get_assignment_groups
        self.get_group_workload = self.get_assignment_groups
        self.get_standard_changes = self.search_kb
