# AEGIS RAG Tools - v2.1 (LangGraph Compatible)
"""
RAG (Retrieval Augmented Generation) tools for AEGIS.
Plain async functions for use with LangGraph pipeline.
"""

import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger("aegis.rag_tools")

# RAG Service Configuration
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8100")


class RAGClient:
    """HTTP client for AEGIS RAG Service."""
    
    def __init__(self):
        self.base_url = RAG_SERVICE_URL
        self.headers = {"Content-Type": "application/json"}
    
    async def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request to RAG service."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """GET request to RAG service."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()


# =============================================================================
# ASYNC TOOL FUNCTIONS
# =============================================================================

async def search_kb_articles(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for KB articles using vector similarity.
    
    Args:
        query: Search query text
        limit: Max number of results
        
    Returns:
        List of matching KB articles with title, summary, score
    """
    client = RAGClient()
    
    try:
        result = await client.post("search", {
            "query": query,
            "collection": "kb_articles",
            "top_k": limit
        })
        
        return result.get("results", [])
    except Exception as e:
        logger.error(f"KB search failed: {e}")
        return []


async def search_similar_incidents(
    query: str, 
    limit: int = 5,
    time_window_hours: int = None
) -> List[Dict[str, Any]]:
    """
    Search for similar past incidents using vector similarity.
    
    Args:
        query: Incident description
        limit: Max number of results
        time_window_hours: Optional time filter
        
    Returns:
        List of similar incidents with score
    """
    client = RAGClient()
    
    try:
        payload = {
            "query": query,
            "collection": "incidents",
            "top_k": limit
        }
        
        if time_window_hours:
            payload["time_window_hours"] = time_window_hours
        
        result = await client.post("search", payload)
        
        return result.get("results", [])
    except Exception as e:
        logger.error(f"Similar incidents search failed: {e}")
        return []


async def analyze_incident(
    short_description: str,
    description: str,
    category: str = None,
    ci_name: str = None
) -> Dict[str, Any]:
    """
    Analyze incident using RAG for classification.
    
    Returns:
        Dict with classification, priority, root_cause, confidence
    """
    client = RAGClient()
    
    try:
        result = await client.post("analyze", {
            "short_description": short_description,
            "description": description,
            "current_category": category,
            "ci_name": ci_name
        })
        
        return {
            "classification": result.get("classification"),
            "priority": result.get("priority"),
            "root_cause": result.get("root_cause"),
            "confidence": result.get("confidence", 0),
            "reasoning": result.get("reasoning"),
            "similar_incidents": result.get("similar_incidents", [])
        }
    except Exception as e:
        logger.error(f"Incident analysis failed: {e}")
        return {"error": str(e)}


async def get_resolution_recommendations(
    incident_number: str,
    classification: str,
    root_cause: str = None
) -> Dict[str, Any]:
    """
    Get resolution recommendations based on similar past incidents.
    
    Returns:
        Dict with recommendations, kb_articles, auto_remediation_eligible
    """
    client = RAGClient()
    
    try:
        result = await client.post("recommend", {
            "incident_number": incident_number,
            "classification": classification,
            "root_cause": root_cause
        })
        
        return {
            "recommendations": result.get("recommendations", []),
            "kb_articles": result.get("kb_articles", []),
            "auto_remediation_eligible": result.get("auto_remediation_eligible", False),
            "confidence": result.get("confidence", 0)
        }
    except Exception as e:
        logger.error(f"Resolution recommendations failed: {e}")
        return {"recommendations": [], "error": str(e)}


async def ingest_document(
    document_type: str,
    content: str,
    metadata: Dict[str, Any] = None
) -> Optional[str]:
    """
    Ingest document into RAG knowledge base.
    
    Args:
        document_type: Type (incident, kb_article, resolution)
        content: Document content
        metadata: Additional metadata
        
    Returns:
        Document ID if successful
    """
    client = RAGClient()
    
    try:
        result = await client.post("ingest", {
            "document_type": document_type,
            "content": content,
            "metadata": metadata or {}
        })
        
        return result.get("document_id")
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        return None
