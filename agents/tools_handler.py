"""
Tool Registry & Execution Sandbox
=================================
Implements the "Tool Registry" pattern for governed AI actions.
Reads allowed tools from registry.yaml and enforces standard change controls.
"""

import os
import yaml
import logging
import boto3
import json
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger("aegis.tools")

class ToolRegistry:
    """Manages allowed tools and their definitions"""
    
    def __init__(self, registry_path: str = None):
        if not registry_path:
            # Default to agents/tools/registry.yaml
            base_dir = os.path.dirname(os.path.abspath(__file__))
            registry_path = os.path.join(base_dir, "tools", "registry.yaml")
            
        self.registry_path = registry_path
        self.tools = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load tools from YAML file"""
        try:
            with open(self.registry_path, 'r') as f:
                tools_list = yaml.safe_load(f)
                # Convert list to dict for O(1) access
                return {tool['name']: tool for tool in tools_list}
        except Exception as e:
            logger.error(f"Failed to load user tool registry: {e}")
            return {}
            
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool definition by name"""
        return self.tools.get(tool_name)
        
    def list_tools(self) -> list:
        """List all available tools"""
        return list(self.tools.values())


class ExecutionSandbox:
    """Safely executes tools with governance checks"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        # Initialize AWS clients
        self.ssm = boto3.client('ssm', region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
        
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], operator: str = "AI_Worker") -> Dict[str, Any]:
        """
        Execute a registered tool.
        1. Validate tool exists
        2. Validate parameters
        3. Check governance (Standard Change)
        4. Execute via appropriate handler
        """
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
            return {"success": False, "error": f"Tool '{tool_name}' not found in registry."}
            
        # 1. Parameter Validation (Basic)
        required_params = tool_def.get("parameters", {})
        for param_name, param_schema in required_params.items():
            if param_name not in parameters:
                # Check for default
                if "default" in param_schema:
                    parameters[param_name] = param_schema["default"]
                else:
                    return {"success": False, "error": f"Missing required parameter: {param_name}"}
                    
        # 2. Governance Check
        try:
            self._enforce_governance(tool_def, parameters, operator)
        except Exception as e:
            return {"success": False, "error": f"Governance check failed: {str(e)}"}
            
        # 3. Execution
        handler = tool_def.get("handler")
        if handler == "aws_ssm":
            return self._execute_ssm(tool_def, parameters)
        else:
            return {"success": False, "error": f"Unknown handler: {handler}"}
            
    def _enforce_governance(self, tool_def: Dict[str, Any], parameters: Dict[str, Any], operator: str):
        """
        Enforce governance rules.
        - If mapped to Standard Change, create CR.
        - If requires manual approval, check existing approval (Mocked for now).
        """
        std_change = tool_def.get("standard_change_template")
        
        if std_change:
            logger.info(f"Creating Standard Change {std_change} for {tool_def['name']}...")
            # TODO: Call ServiceNow API to create Change Request
            # mock_create_change(std_change, parameters)
            pass
        elif tool_def.get("risk_level") == "high":
             raise PermissionError("High risk action requires manual Change Request approval.")
             
    def _execute_ssm(self, tool_def: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute command via AWS SSM Run Command.
        Does NOT run local shell commands.
        """
        target_id = parameters.get("target_id")
        
        # Build command based on tool name
        # This mapping should ideally also be in registry or a separate handler map
        if tool_def["name"] == "restart_windows_service":
            service = parameters.get("service_name")
            cmd = f"Restart-Service -Name '{service}' -Force"
            document = "AWS-RunPowerShellScript"
            
        elif tool_def["name"] == "clear_iis_logs":
            days = parameters.get("days_to_keep", 30)
            cmd = f"forfiles /p 'C:\\inetpub\\logs\\LogFiles' /s /m *.* /c 'cmd /c Del @path' /d -{days}"
            document = "AWS-RunPowerShellScript"
            
        elif tool_def["name"] == "check_disk_space":
            cmd = "Get-Volume"
            document = "AWS-RunPowerShellScript"
            
        else:
            return {"success": False, "error": "No SSM command mapping found"}
            
        logger.info(f"Dispatching SSM command to {target_id}: {cmd}")
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[target_id],
                DocumentName=document,
                Parameters={'commands': [cmd]}
            )
            command_id = response['Command']['CommandId']
            return {
                "success": True, 
                "message": "Command sent to SSM", 
                "command_id": command_id,
                "status": "Pending"
            }
        except Exception as e:
            logger.error(f"SSM Dispatch failed: {e}")
            return {"success": False, "error": str(e)}

