# AEGIS Tools Package - v2.1
"""Async tool functions for AEGIS LangGraph pipeline."""

from .servicenow_tools import (
    get_user_info,
    get_ci_info,
    update_incident,
    add_work_note,
    get_recent_incidents,
    search_kb_servicenow,
    get_assignment_groups,
    create_incident
)

from .redis_tools import (
    RedisClient,
    check_duplicate_vector,
    record_incident_embedding,
    get_governance_state
)

from .rag_tools import (
    search_kb_articles,
    search_similar_incidents,
    analyze_incident,
    get_resolution_recommendations,
    ingest_document
)

from .teams_tools import (
    send_notification,
    send_triage_card,
    create_swarm_notification,
    request_approval
)

__all__ = [
    # ServiceNow
    "get_user_info",
    "get_ci_info",
    "update_incident",
    "add_work_note",
    "get_recent_incidents",
    "search_kb_servicenow",
    "get_assignment_groups",
    "create_incident",
    # Redis
    "RedisClient",
    "check_duplicate_vector",
    "record_incident_embedding",
    "get_governance_state",
    # RAG
    "search_kb_articles",
    "search_similar_incidents",
    "analyze_incident",
    "get_resolution_recommendations",
    "ingest_document",
    # Teams
    "send_notification",
    "send_triage_card",
    "create_swarm_notification",
    "request_approval"
]
