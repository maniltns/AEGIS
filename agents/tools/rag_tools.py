# AEGIS RAG Tools for CrewAI
"""
RAG (Retrieval Augmented Generation) tools for AEGIS agents.
Integrates with ChromaDB for vector search and AWS Bedrock for embeddings.
"""

import os
import json
import httpx
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

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
# RAG TOOL DEFINITIONS
# =============================================================================

class SearchSimilarIncidentsInput(BaseModel):
    """Input for searching similar incidents."""
    query: str = Field(..., description="Search query or incident description")
    top_k: int = Field(5, description="Number of results to return")


class SearchSimilarIncidentsTool(BaseTool):
    """Search for similar past incidents using vector similarity."""
    name: str = "search_similar_incidents"
    description: str = "Search for similar past incidents using AI-powered semantic search"
    args_schema: type[BaseModel] = SearchSimilarIncidentsInput
    
    def _run(self, query: str, top_k: int = 5) -> str:
        import asyncio
        return asyncio.run(self._async_run(query, top_k))
    
    async def _async_run(self, query: str, top_k: int) -> str:
        client = RAGClient()
        
        try:
            result = await client.post("search", {
                "query": query,
                "collection": "incidents",
                "top_k": top_k
            })
            
            return json.dumps({
                "success": True,
                "matches": result.get("results", []),
                "count": len(result.get("results", []))
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "matches": []
            })


class AnalyzeIncidentInput(BaseModel):
    """Input for incident analysis."""
    short_description: str = Field(..., description="Incident short description")
    description: str = Field(..., description="Full incident description")
    category: Optional[str] = Field(None, description="Current category if any")
    ci_name: Optional[str] = Field(None, description="CI name if known")


class AnalyzeIncidentTool(BaseTool):
    """Analyze incident using RAG for intelligent triage."""
    name: str = "analyze_incident"
    description: str = "Perform AI-powered analysis of incident for classification, root cause, and resolution"
    args_schema: type[BaseModel] = AnalyzeIncidentInput
    
    def _run(self, short_description: str, description: str,
             category: str = None, ci_name: str = None) -> str:
        import asyncio
        return asyncio.run(self._async_run(short_description, description, category, ci_name))
    
    async def _async_run(self, short_description: str, description: str,
                         category: str, ci_name: str) -> str:
        client = RAGClient()
        
        try:
            result = await client.post("analyze", {
                "short_description": short_description,
                "description": description,
                "current_category": category,
                "ci_name": ci_name
            })
            
            return json.dumps({
                "success": True,
                "classification": result.get("classification"),
                "priority": result.get("priority"),
                "root_cause": result.get("root_cause"),
                "confidence": result.get("confidence"),
                "reasoning": result.get("reasoning"),
                "similar_incidents": result.get("similar_incidents", [])
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


class GetResolutionRecommendationsInput(BaseModel):
    """Input for resolution recommendations."""
    incident_number: str = Field(..., description="Incident number")
    classification: str = Field(..., description="Incident classification")
    root_cause: Optional[str] = Field(None, description="Identified root cause")


class GetResolutionRecommendationsTool(BaseTool):
    """Get resolution recommendations based on similar past incidents."""
    name: str = "get_resolution_recommendations"
    description: str = "Get recommended resolution steps based on similar past incidents and KB articles"
    args_schema: type[BaseModel] = GetResolutionRecommendationsInput
    
    def _run(self, incident_number: str, classification: str, 
             root_cause: str = None) -> str:
        import asyncio
        return asyncio.run(self._async_run(incident_number, classification, root_cause))
    
    async def _async_run(self, incident_number: str, classification: str,
                         root_cause: str) -> str:
        client = RAGClient()
        
        try:
            result = await client.post("recommend", {
                "incident_number": incident_number,
                "classification": classification,
                "root_cause": root_cause
            })
            
            return json.dumps({
                "success": True,
                "recommendations": result.get("recommendations", []),
                "kb_articles": result.get("kb_articles", []),
                "auto_remediation_eligible": result.get("auto_remediation_eligible", False),
                "confidence": result.get("confidence", 0)
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "recommendations": []
            })


class IngestDocumentInput(BaseModel):
    """Input for document ingestion."""
    document_type: str = Field(..., description="Type: incident, kb_article, resolution")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class IngestDocumentTool(BaseTool):
    """Ingest document into RAG knowledge base."""
    name: str = "ingest_document"
    description: str = "Add a new document (incident, KB article, resolution) to the RAG knowledge base"
    args_schema: type[BaseModel] = IngestDocumentInput
    
    def _run(self, document_type: str, content: str, 
             metadata: Dict[str, Any] = None) -> str:
        import asyncio
        return asyncio.run(self._async_run(document_type, content, metadata or {}))
    
    async def _async_run(self, document_type: str, content: str,
                         metadata: Dict[str, Any]) -> str:
        client = RAGClient()
        
        try:
            result = await client.post("ingest", {
                "document_type": document_type,
                "content": content,
                "metadata": metadata
            })
            
            return json.dumps({
                "success": True,
                "document_id": result.get("document_id"),
                "message": "Document ingested successfully"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })


# =============================================================================
# TOOLS FACTORY
# =============================================================================

class RAGTools:
    """Factory for RAG tools."""
    
    def __init__(self):
        self.search_similar_incidents = SearchSimilarIncidentsTool()
        self.analyze_incident = AnalyzeIncidentTool()
        self.get_resolution_recommendations = GetResolutionRecommendationsTool()
        self.ingest_document = IngestDocumentTool()
