# AEGIS CrewAI Agents - Main Entry Point
"""
AEGIS - Autonomous IT Operations & Swarming Platform
CrewAI Agent Orchestration Layer

This module defines all 9 AEGIS agents and the crew orchestration.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

# Import custom tools
from tools.servicenow_tools import ServiceNowTools
from tools.redis_tools import RedisTools
from tools.rag_tools import RAGTools
from tools.teams_tools import TeamsTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis.agents")

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # anthropic | openai

# LLM Configuration
def get_llm(temperature: float = 0.1):
    """Get the configured LLM based on environment."""
    if LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=temperature,
            api_key=ANTHROPIC_API_KEY
        )
    else:
        return ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            api_key=OPENAI_API_KEY
        )


# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

class AEGISAgents:
    """Factory class for creating AEGIS agents."""
    
    def __init__(self):
        self.llm = get_llm()
        self.servicenow = ServiceNowTools()
        self.redis = RedisTools()
        self.rag = RAGTools()
        self.teams = TeamsTools()
    
    def guardian_agent(self) -> Agent:
        """
        GUARDIAN - Storm Shield
        First line of defense. Blocks duplicate incidents and alert floods.
        """
        return Agent(
            role="Storm Shield Sentinel",
            goal="Detect and suppress duplicate incidents, alert floods, and noise before they reach human agents",
            backstory="""You are GUARDIAN, the first line of defense in the AEGIS platform. 
            Your mission is to protect the Service Desk from being overwhelmed by duplicate 
            incidents, alert storms, and ticket floods. You analyze incoming tickets and 
            determine if they are duplicates of existing open incidents or part of an 
            ongoing alert storm. You have access to Redis for tracking incident patterns 
            and can block up to 95% of duplicate noise.""",
            llm=self.llm,
            tools=[
                self.redis.check_duplicate,
                self.redis.record_incident,
                self.redis.get_storm_status,
                self.servicenow.get_recent_incidents
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def scout_agent(self) -> Agent:
        """
        SCOUT - Enrichment Agent
        Gathers context from multiple sources.
        """
        return Agent(
            role="Intelligence Gatherer",
            goal="Enrich tickets with context from ServiceNow CMDB, user history, KB articles, and past incidents",
            backstory="""You are SCOUT, the intelligence gathering agent. Your job is to 
            enrich incoming tickets with relevant context that will help downstream agents 
            make better decisions. You pull user information, CI data from CMDB, related 
            KB articles, and similar past incidents. You compile this into a comprehensive 
            context package that enables faster and more accurate resolution.""",
            llm=self.llm,
            tools=[
                self.servicenow.get_user_info,
                self.servicenow.get_ci_info,
                self.servicenow.search_kb,
                self.rag.search_similar_incidents
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def sherlock_agent(self) -> Agent:
        """
        SHERLOCK - AI Triage Agent
        Performs intelligent classification and root cause analysis.
        """
        return Agent(
            role="AI Triage Specialist",
            goal="Classify incidents accurately, determine root cause, and recommend resolution paths with 90%+ accuracy",
            backstory="""You are SHERLOCK, the AI triage specialist. Using advanced 
            reasoning and RAG-powered institutional knowledge, you analyze incidents 
            to determine their true category, priority, impact, and likely root cause. 
            You provide confidence scores with your classifications and only recommend 
            actions when confidence exceeds 85%. Your analysis includes detailed 
            reasoning that can be audited by human reviewers.""",
            llm=self.llm,
            tools=[
                self.rag.analyze_incident,
                self.rag.get_resolution_recommendations,
                self.servicenow.get_category_mapping
            ],
            verbose=True,
            allow_delegation=True
        )
    
    def router_agent(self) -> Agent:
        """
        ROUTER - Assignment Agent
        Routes tickets to the right team or specialist.
        """
        return Agent(
            role="Ticket Router",
            goal="Route incidents to the optimal assignment group or specialist based on skills, availability, and workload",
            backstory="""You are ROUTER, the assignment optimization agent. Based on 
            SHERLOCK's classification and the enriched context from SCOUT, you determine 
            the optimal assignment group or individual for each incident. You consider 
            team expertise, current workload, availability, and historical resolution 
            success rates. For VIP users, you apply priority routing rules.""",
            llm=self.llm,
            tools=[
                self.servicenow.get_assignment_groups,
                self.servicenow.get_group_workload,
                self.servicenow.update_incident
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def arbiter_agent(self) -> Agent:
        """
        ARBITER - Governance Agent
        Enforces policies, thresholds, and compliance rules.
        """
        return Agent(
            role="Governance Enforcer",
            goal="Enforce governance policies, confidence thresholds, and ensure human-in-the-loop for high-risk actions",
            backstory="""You are ARBITER, the governance enforcement agent. You are the 
            final checkpoint before any automated action is taken. You verify that:
            1. Confidence thresholds are met (>85% for auto-actions)
            2. Kill switch is not active
            3. Human approval is obtained for medium/high risk actions
            4. All actions comply with change management policies
            You have the authority to halt any action that doesn't meet governance criteria.""",
            llm=self.llm,
            tools=[
                self.redis.check_kill_switch,
                self.redis.get_confidence_threshold,
                self.teams.request_approval
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def herald_agent(self) -> Agent:
        """
        HERALD - Notification Agent
        Manages all outbound communications.
        """
        return Agent(
            role="Communications Manager",
            goal="Deliver timely, contextual notifications to stakeholders via MS Teams and other channels",
            backstory="""You are HERALD, the communications agent. You craft and deliver 
            notifications for incident updates, escalations, swarm assembly requests, 
            and status changes. You ensure the right people receive the right information 
            at the right time. You adapt message tone based on audience (technical vs 
            executive) and urgency level.""",
            llm=self.llm,
            tools=[
                self.teams.send_notification,
                self.teams.create_swarm_channel,
                self.teams.send_adaptive_card
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def scribe_agent(self) -> Agent:
        """
        SCRIBE - Audit & Documentation Agent
        Maintains comprehensive audit trails.
        """
        return Agent(
            role="Audit Keeper",
            goal="Maintain complete audit trails of all AI decisions, actions, and reasoning for compliance",
            backstory="""You are SCRIBE, the audit and documentation agent. You record 
            every decision, action, and piece of reasoning from all AEGIS agents. Your 
            logs are immutable and include timestamps, confidence scores, input/output 
            data, and human approvals. You ensure 7-year retention compliance and can 
            generate audit reports on demand.""",
            llm=self.llm,
            tools=[
                self.redis.log_decision,
                self.servicenow.add_work_note,
                self.servicenow.update_audit_log
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def bridge_agent(self) -> Agent:
        """
        BRIDGE - Case to Incident Converter
        Handles case-to-incident conversions.
        """
        return Agent(
            role="Case-Incident Bridge",
            goal="Intelligently convert customer cases to incidents when IT intervention is required",
            backstory="""You are BRIDGE, the case-to-incident conversion specialist. 
            When customer service cases require IT support, you analyze the case content, 
            extract relevant technical details, and create properly formatted incidents 
            with full context. You ensure no information is lost in the conversion and 
            maintain linking between the case and incident.""",
            llm=self.llm,
            tools=[
                self.servicenow.get_case,
                self.servicenow.create_incident,
                self.servicenow.link_records
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def janitor_agent(self) -> Agent:
        """
        JANITOR - Auto-Remediation Agent
        Executes approved remediation actions.
        """
        return Agent(
            role="Remediation Specialist",
            goal="Execute approved, low-risk remediation actions for common incident types safely",
            backstory="""You are JANITOR, the auto-remediation agent. For incidents with 
            known, safe remediation paths, you can execute automated fixes after receiving 
            governance approval from ARBITER. You only perform actions that are:
            1. On the approved standard changes list
            2. Low-risk (no data loss potential)
            3. Reversible
            4. Validated by ARBITER
            You log all actions for audit and can rollback if needed.""",
            llm=self.llm,
            tools=[
                self.servicenow.get_standard_changes,
                self.redis.log_remediation,
                # AWS tools would be added here
            ],
            verbose=True,
            allow_delegation=False
        )


# =============================================================================
# CREW DEFINITIONS
# =============================================================================

class AEGISCrew:
    """AEGIS Crew orchestration for incident processing."""
    
    def __init__(self):
        self.agents_factory = AEGISAgents()
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize all agents."""
        self.guardian = self.agents_factory.guardian_agent()
        self.scout = self.agents_factory.scout_agent()
        self.sherlock = self.agents_factory.sherlock_agent()
        self.router = self.agents_factory.router_agent()
        self.arbiter = self.agents_factory.arbiter_agent()
        self.herald = self.agents_factory.herald_agent()
        self.scribe = self.agents_factory.scribe_agent()
        self.bridge = self.agents_factory.bridge_agent()
        self.janitor = self.agents_factory.janitor_agent()
    
    def create_triage_crew(self, incident: Dict[str, Any]) -> Crew:
        """
        Create the main triage crew for processing an incident.
        
        Flow: GUARDIAN → SCOUT → SHERLOCK → ROUTER → ARBITER → HERALD → SCRIBE
        """
        incident_str = json.dumps(incident, indent=2)
        
        # Define tasks
        tasks = [
            Task(
                description=f"""Analyze this incoming incident for duplicates and storm patterns:
                
                {incident_str}
                
                Check if:
                1. This is a duplicate of an existing open incident
                2. This is part of an ongoing alert storm
                3. This should be suppressed or merged
                
                Return: is_duplicate (bool), parent_incident (if duplicate), storm_id (if storm)""",
                agent=self.guardian,
                expected_output="JSON with duplicate analysis results"
            ),
            Task(
                description=f"""Enrich this incident with context:
                
                {incident_str}
                
                Gather:
                1. User information and history
                2. CI data from CMDB
                3. Related KB articles
                4. Similar past incidents
                
                Return enriched context package.""",
                agent=self.scout,
                expected_output="Enriched incident context with user, CI, KB, and history"
            ),
            Task(
                description=f"""Perform AI triage on this enriched incident.
                
                Determine:
                1. True category and subcategory
                2. Priority (P1-P4) with justification
                3. Impact and urgency assessment
                4. Likely root cause
                5. Recommended resolution path
                6. Confidence score (0-100%)
                
                Only recommend auto-actions if confidence > 85%.""",
                agent=self.sherlock,
                expected_output="Triage result with classification, priority, root cause, and confidence"
            ),
            Task(
                description=f"""Route this incident to the optimal assignment group.
                
                Consider:
                1. Triage classification from SHERLOCK
                2. Team expertise and skills
                3. Current workload balance
                4. VIP priority rules
                
                Return: assignment_group, assigned_to (if individual), routing_reason""",
                agent=self.router,
                expected_output="Assignment decision with group, individual, and reasoning"
            ),
            Task(
                description=f"""Validate governance compliance for all proposed actions.
                
                Check:
                1. Kill switch status
                2. Confidence thresholds
                3. Human approval requirements
                4. Change management compliance
                
                Approve or reject proposed actions with reasoning.""",
                agent=self.arbiter,
                expected_output="Governance decision: approved/rejected with compliance status"
            ),
            Task(
                description=f"""Send appropriate notifications based on the triage outcome.
                
                Notify:
                1. Assignment group via Teams
                2. User if VIP or P1
                3. Create swarm channel if needed
                
                Use appropriate tone and urgency level.""",
                agent=self.herald,
                expected_output="Notification confirmation with channels and recipients"
            ),
            Task(
                description=f"""Log the complete audit trail for this incident processing.
                
                Record:
                1. All agent decisions with timestamps
                2. Confidence scores
                3. Actions taken
                4. Governance approvals
                5. Work notes in ServiceNow
                
                Ensure 7-year retention compliance.""",
                agent=self.scribe,
                expected_output="Audit log confirmation with log IDs"
            )
        ]
        
        return Crew(
            agents=[
                self.guardian,
                self.scout,
                self.sherlock,
                self.router,
                self.arbiter,
                self.herald,
                self.scribe
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def create_remediation_crew(self, incident: Dict[str, Any]) -> Crew:
        """Create crew for auto-remediation workflow."""
        incident_str = json.dumps(incident, indent=2)
        
        tasks = [
            Task(
                description=f"""Analyze incident for remediation eligibility:
                
                {incident_str}
                
                Check if:
                1. Resolution is known and documented
                2. Action is on standard changes list
                3. Risk level is low
                4. Action is reversible""",
                agent=self.sherlock,
                expected_output="Remediation eligibility assessment"
            ),
            Task(
                description=f"""Validate remediation action meets governance requirements.
                
                Check:
                1. Kill switch status
                2. Human approval if needed
                3. Standard change compliance
                
                Gate the remediation action.""",
                agent=self.arbiter,
                expected_output="Remediation approval decision"
            ),
            Task(
                description=f"""Execute approved remediation action.
                
                Perform the remediation safely and log all steps.
                Be prepared to rollback if needed.""",
                agent=self.janitor,
                expected_output="Remediation execution result"
            ),
            Task(
                description=f"""Log remediation audit trail.""",
                agent=self.scribe,
                expected_output="Audit log confirmation"
            )
        ]
        
        return Crew(
            agents=[self.sherlock, self.arbiter, self.janitor, self.scribe],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def process_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for processing an incident through AEGIS.
    
    Args:
        incident: ServiceNow incident data
        
    Returns:
        Processing result with triage, assignment, and audit info
    """
    logger.info(f"Processing incident: {incident.get('number', 'Unknown')}")
    
    crew = AEGISCrew()
    triage_crew = crew.create_triage_crew(incident)
    
    try:
        result = triage_crew.kickoff()
        logger.info(f"Incident processed successfully: {result}")
        return {
            "status": "success",
            "incident_number": incident.get("number"),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing incident: {e}")
        return {
            "status": "error",
            "incident_number": incident.get("number"),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    # Test with sample incident
    sample_incident = {
        "number": "INC0012345",
        "short_description": "Unable to login to Opera PMS",
        "description": "Hotel front desk cannot access Opera. Getting timeout error.",
        "caller_id": "john.smith@accor.com",
        "category": "Software",
        "priority": "3",
        "cmdb_ci": "Opera PMS Production"
    }
    
    import asyncio
    result = asyncio.run(process_incident(sample_incident))
    print(json.dumps(result, indent=2))
