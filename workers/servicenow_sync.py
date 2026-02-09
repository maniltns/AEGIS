"""
ServiceNow Sync Worker
======================
Fetches closed incidents and published KB articles from ServiceNow
and ingests them into the RAG vector database.
"""

import os
import sys
import json
import logging
import time
import httpx
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path to import RAG service models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("snow-sync")

# Configuration
SNOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
SNOW_USER = os.getenv("SERVICENOW_USER")
SNOW_PASS = os.getenv("SERVICENOW_PASSWORD")
RAG_URL = os.getenv("RAG_SERVICE_URL", "http://rag-service:8000")

class ServiceNowSync:
    def __init__(self):
        if not all([SNOW_INSTANCE, SNOW_USER, SNOW_PASS]):
            logger.warning("ServiceNow credentials not set. Sync will be skipped.")
            self.configured = False
        else:
            self.configured = True
            self.base_url = f"https://{SNOW_INSTANCE}/api/now/table"
            self.auth = (SNOW_USER, SNOW_PASS)
            
    async def fetch_incidents(self, days_back=7):
        """Fetch closed incidents from the last N days"""
        if not self.configured: return []
        
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Query parameters
        # state=7 (Closed), resolved within last N days
        query = f"state=7^closed_at>={start_date}"
        
        logger.info(f"Fetching incidents since {start_date}...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/incident",
                    auth=self.auth,
                    params={
                        "sysparm_query": query,
                        "sysparm_limit": 100,
                        "sysparm_fields": "number,short_description,description,close_notes,closed_at,sys_id,resolution_code"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", [])
            except Exception as e:
                logger.error(f"Failed to fetch incidents: {e}")
                return []

    async def fetch_kb_articles(self, days_back=7):
        """Fetch published KB articles updated in the last N days"""
        if not self.configured: return []
        
        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # workflow_state=published
        query = f"workflow_state=published^sys_updated_on>={start_date}"
        
        logger.info(f"Fetching KB articles since {start_date}...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/kb_knowledge",
                    auth=self.auth,
                    params={
                        "sysparm_query": query,
                        "sysparm_limit": 50,
                        "sysparm_fields": "number,short_description,text,sys_id,topic,category,sys_updated_on"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", [])
            except Exception as e:
                logger.error(f"Failed to fetch KB articles: {e}")
                return []

    async def ingest_to_rag(self, items, doc_type):
        """Ingest items into RAG service"""
        if not items:
            logger.info(f"No {doc_type} items to ingest.")
            return
            
        async with httpx.AsyncClient() as client:
            for item in items:
                try:
                    if doc_type == "ticket":
                        doc_id = item.get("number")
                        title = item.get("short_description")
                        # Combine description and resolution
                        content = f"Description:\n{item.get('description', '')}\n\nResolution:\n{item.get('close_notes', '')}"
                        metadata = {
                            "incident_number": doc_id,
                            "closed_at": item.get("closed_at"),
                            "resolution_code": item.get("resolution_code")
                        }
                    else: # KB
                        doc_id = item.get("number")
                        title = item.get("short_description")
                        content = item.get("text", "")
                        metadata = {
                            "kb_number": doc_id,
                            "category": item.get("category"),
                            "topic": item.get("topic"),
                            "updated_on": item.get("sys_updated_on")
                        }
                    
                    payload = {
                        "document_type": doc_type,
                        "document_id": doc_id,
                        "title": title,
                        "content": content,
                        "metadata": metadata
                    }
                    
                    logger.info(f"Ingesting {doc_type}: {doc_id}")
                    resp = await client.post(f"{RAG_URL}/api/v1/ingest", json=payload, timeout=10.0)
                    resp.raise_for_status()
                    
                except Exception as e:
                    logger.error(f"Failed to ingest {item.get('number', 'unknown')}: {e}")

async def run_sync():
    """Main sync execution"""
    syncer = ServiceNowSync()
    
    # 1. Sync Incidents
    incidents = await syncer.fetch_incidents(days_back=7)
    logger.info(f"Found {len(incidents)} closed incidents.")
    await syncer.ingest_to_rag(incidents, "ticket")
    
    # 2. Sync KB Articles
    kb_articles = await syncer.fetch_kb_articles(days_back=7)
    logger.info(f"Found {len(kb_articles)} published KB articles.")
    await syncer.ingest_to_rag(kb_articles, "kb")
    
    logger.info("Sync complete.")

if __name__ == "__main__":
    asyncio.run(run_sync())
