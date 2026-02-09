"""
🧠 AEGIS RAG Service - Intelligent Knowledge Retrieval
========================================================
Custom RAG (Retrieval Augmented Generation) service for AEGIS.

Architecture:
- Embedding Model: Amazon Titan Text Embeddings V2
- Reasoning Model: Claude Sonnet 4.5 (Anthropic)
- Vector Database: Redis Stack with RediSearch (Enterprise-grade)
- API Framework: FastAPI
- Deployment: AWS EC2 (Docker)

Author: Anilkumar MN
Date: January 28, 2026
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

import boto3
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aegis-rag")

# =============================================================================
# Configuration
# =============================================================================

class Config:
    """RAG Service Configuration"""
    # AWS Bedrock Configuration
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_BEARER_TOKEN = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    
    # Titan Embedding Model
    TITAN_MODEL_ID = os.getenv("AWS_TITAN_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
    TITAN_EMBED_DIMENSION = 1024
    
    # Claude via Bedrock
    CLAUDE_MODEL = os.getenv("BEDROCK_CLAUDE_SONNET_MODEL", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/data/chromadb")
    
    # Collection Names
    COLLECTION_KB = "aegis_knowledge_base"
    COLLECTION_TICKETS = "aegis_ticket_history"
    COLLECTION_SOP = "aegis_sop_documents"
    
    # Retrieval Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))


# =============================================================================
# Pydantic Models
# =============================================================================

class TicketQuery(BaseModel):
    """Input model for ticket analysis"""
    short_description: str = Field(..., description="Ticket short description")
    description: str = Field(..., description="Ticket detailed description")
    caller: Optional[str] = Field(None, description="Caller name")
    category: Optional[str] = Field(None, description="Current category if any")
    priority: Optional[str] = Field(None, description="Current priority if any")


class KBArticle(BaseModel):
    """Knowledge Base article structure"""
    kb_number: str
    title: str
    content: str
    category: str
    relevance_score: float


class SimilarTicket(BaseModel):
    """Similar historical ticket"""
    incident_number: str
    short_description: str
    resolution: str
    resolution_time_hours: float
    relevance_score: float


class CategorySuggestion(BaseModel):
    """AI-suggested categorization"""
    category: str
    subcategory: str
    confidence: float
    reasoning: str


class RAGResponse(BaseModel):
    """Complete RAG response"""
    query_id: str
    timestamp: str
    
    # AI Analysis
    analysis: str
    root_cause_hypothesis: str
    recommended_actions: List[str]
    
    # Category Suggestion
    suggested_category: CategorySuggestion
    
    # Retrieved Knowledge
    kb_articles: List[KBArticle]
    similar_tickets: List[SimilarTicket]
    sop_references: List[str]
    
    # Confidence & Metadata
    overall_confidence: float
    processing_time_ms: int


class DocumentIngest(BaseModel):
    """Document ingestion request"""
    document_type: str = Field(..., description="kb, ticket, or sop")
    document_id: str
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class IngestResponse(BaseModel):
    """Document ingestion response"""
    success: bool
    document_id: str
    collection: str
    embedding_id: str


# =============================================================================
# AWS Bedrock Client (Titan Embeddings)
# =============================================================================

class TitanEmbeddings:
    """Amazon Titan Text Embeddings V2 Client"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=Config.AWS_REGION
        )
        self.model_id = Config.TITAN_MODEL_ID
        logger.info(f"Initialized Titan Embeddings: {self.model_id}")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "inputText": text,
                    "dimensions": Config.TITAN_EMBED_DIMENSION,
                    "normalize": True
                })
            )
            result = json.loads(response['body'].read())
            return result['embedding']
        except Exception as e:
            logger.error(f"Titan embedding error: {e}")
            raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.embed(text) for text in texts]


# =============================================================================
# Claude Sonnet Client (Reasoning)
# =============================================================================

class ClaudeReasoning:
    """Claude Sonnet via AWS Bedrock Reasoning Client"""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=Config.AWS_REGION
        )
        self.model_id = Config.CLAUDE_MODEL
        logger.info(f"Initialized Claude Reasoning via Bedrock: {self.model_id}")
    
    def analyze_ticket(
        self,
        ticket: TicketQuery,
        kb_context: List[Dict],
        similar_tickets: List[Dict],
        sop_context: List[str]
    ) -> Dict:
        """
        Analyze ticket with retrieved context and provide intelligent reasoning.
        """
        
        # Build context prompt
        context_prompt = self._build_context_prompt(
            ticket, kb_context, similar_tickets, sop_context
        )
        
        try:
            # Use Bedrock converse API for Claude
            response = self.client.converse(
                modelId=self.model_id,
                system=[{
                    "text": """You are SHERLOCK, the AI Triage Agent for AEGIS (Autonomous Expert for Governance, Intelligence & Swarming).

Your role is to analyze IT support tickets and provide:
1. Intelligent analysis of the issue
2. Root cause hypothesis based on KB articles and similar tickets
3. Recommended actions for resolution
4. Category/subcategory suggestion with confidence score

Always be specific, actionable, and reference relevant KB articles or past tickets.
Respond in JSON format matching the expected schema."""
                }],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": context_prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0
                }
            )
            
            # Parse response from Bedrock
            response_text = response['output']['message']['content'][0]['text']
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            # Return structured fallback
            return {
                "analysis": response_text if 'response_text' in locals() else "Analysis failed",
                "root_cause_hypothesis": "Unable to determine - requires manual review",
                "recommended_actions": ["Escalate to L2 for manual analysis"],
                "suggested_category": {
                    "category": "General",
                    "subcategory": "Unknown",
                    "confidence": 0.3,
                    "reasoning": "AI parsing error - manual categorization required"
                },
                "overall_confidence": 0.3
            }
        except Exception as e:
            logger.error(f"Claude reasoning error: {e}")
            raise HTTPException(status_code=500, detail=f"Reasoning failed: {str(e)}")
    
    def _build_context_prompt(
        self,
        ticket: TicketQuery,
        kb_articles: List[Dict],
        similar_tickets: List[Dict],
        sop_refs: List[str]
    ) -> str:
        """Build the context-rich prompt for Claude"""
        
        prompt = f"""## Ticket to Analyze

**Short Description:** {ticket.short_description}
**Full Description:** {ticket.description}
**Caller:** {ticket.caller or 'Unknown'}
**Current Category:** {ticket.category or 'Not set'}
**Current Priority:** {ticket.priority or 'Not set'}

## Retrieved Knowledge Base Articles
"""
        
        for i, kb in enumerate(kb_articles[:5], 1):
            prompt += f"""
### KB{i}: {kb.get('title', 'Untitled')} (Score: {kb.get('score', 0):.2f})
{kb.get('content', '')[:500]}...
"""
        
        prompt += "\n## Similar Historical Tickets\n"
        for i, ticket_hist in enumerate(similar_tickets[:5], 1):
            prompt += f"""
### Similar #{i}: {ticket_hist.get('incident_number', 'N/A')}
- **Description:** {ticket_hist.get('short_description', '')}
- **Resolution:** {ticket_hist.get('resolution', 'Not available')}
- **Resolution Time:** {ticket_hist.get('resolution_time', 'N/A')} hours
"""
        
        if sop_refs:
            prompt += "\n## Relevant SOP References\n"
            for sop in sop_refs[:3]:
                prompt += f"- {sop}\n"
        
        prompt += """
## Required Response Format

Respond with a JSON object containing:
```json
{
    "analysis": "Detailed analysis of the issue",
    "root_cause_hypothesis": "Most likely root cause based on context",
    "recommended_actions": ["Action 1", "Action 2", "Action 3"],
    "suggested_category": {
        "category": "Main category",
        "subcategory": "Sub category",
        "confidence": 0.95,
        "reasoning": "Why this category was chosen"
    },
    "overall_confidence": 0.90
}
```
"""
        return prompt


# =============================================================================
# Vector Database Manager
# =============================================================================

class VectorDBManager:
    """Redis Stack Vector Database Manager (Enterprise-grade replacement for ChromaDB)"""
    
    def __init__(self, embeddings: TitanEmbeddings):
        self.embeddings = embeddings
        self.vector_dim = 1024  # Titan V2 embedding dimension
        
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis = redis.from_url(redis_url, decode_responses=False)
        
        # Collection name to index name mapping
        self.collections = {
            Config.COLLECTION_KB: "idx:kb",
            Config.COLLECTION_TICKETS: "idx:tickets", 
            Config.COLLECTION_SOP: "idx:sop",
            "kb": "idx:kb",
            "ticket": "idx:tickets",
            "sop": "idx:sop",
            "kb_articles": "idx:kb",
            "incidents": "idx:tickets"
        }
        
        # Initialize vector indices
        self._ensure_indices()
        
        logger.info(f"Initialized Redis VectorDB with indices: {list(set(self.collections.values()))}")
    
    def _ensure_indices(self):
        """Create vector indices if they don't exist"""
        index_configs = [
            ("idx:kb", "kb:", "Knowledge Base Articles"),
            ("idx:tickets", "tickets:", "Historical Tickets"),
            ("idx:sop", "sop:", "Standard Operating Procedures")
        ]
        
        for index_name, prefix, description in index_configs:
            try:
                # Check if index exists
                self.redis.execute_command("FT.INFO", index_name)
                logger.debug(f"Index {index_name} already exists")
            except redis.ResponseError:
                # Create index with vector field
                try:
                    self.redis.execute_command(
                        "FT.CREATE", index_name,
                        "ON", "HASH",
                        "PREFIX", "1", prefix,
                        "SCHEMA",
                        "content", "TEXT",
                        "doc_id", "TAG",
                        "title", "TEXT",
                        "category", "TAG",
                        "created_at", "NUMERIC",
                        "embedding", "VECTOR", "HNSW", "6",
                        "TYPE", "FLOAT32",
                        "DIM", str(self.vector_dim),
                        "DISTANCE_METRIC", "COSINE"
                    )
                    logger.info(f"Created vector index: {index_name}")
                except redis.ResponseError as e:
                    logger.warning(f"Could not create index {index_name}: {e}")
    
    def add_document(
        self,
        collection_name: str,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Add a document to a collection"""
        
        # Get prefix for collection
        prefix_map = {
            "kb": "kb:", Config.COLLECTION_KB: "kb:",
            "ticket": "tickets:", Config.COLLECTION_TICKETS: "tickets:",
            "sop": "sop:", Config.COLLECTION_SOP: "sop:"
        }
        prefix = prefix_map.get(collection_name, "kb:")
        
        # Generate embedding
        embedding = self.embeddings.embed(content)
        
        # Generate unique key
        embed_id = hashlib.md5(f"{doc_id}:{content[:100]}".encode()).hexdigest()
        key = f"{prefix}{embed_id}"
        
        # Store in Redis as hash with vector field
        import struct
        embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)
        
        self.redis.hset(key, mapping={
            "content": content,
            "doc_id": doc_id,
            "title": metadata.get("title", ""),
            "category": metadata.get("category", ""),
            "kb_number": metadata.get("kb_number", ""),
            "sys_id": metadata.get("sys_id", ""),
            "created_at": int(time.time()),
            "embedding": embedding_bytes
        })
        
        # Set TTL (90 days for tickets, no expiry for KB/SOP)
        if "tickets" in prefix:
            self.redis.expire(key, 86400 * 90)
        
        logger.info(f"Added document {doc_id} to {collection_name} as {key}")
        return embed_id
    
    def search_similar(
        self,
        collection_name: str,
        query: str,
        top_k: int = None
    ) -> List[Dict]:
        """Search for similar documents using Redis vector search"""
        
        index_name = self.collections.get(collection_name)
        if not index_name:
            raise ValueError(f"Unknown collection: {collection_name}")
        
        # Generate query embedding
        query_embedding = self.embeddings.embed(query)
        
        import struct
        query_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
        
        k = top_k or Config.TOP_K_RESULTS
        
        try:
            # Execute KNN vector search
            results = self.redis.execute_command(
                "FT.SEARCH", index_name,
                f"*=>[KNN {k} @embedding $vec AS score]",
                "PARAMS", "2", "vec", query_bytes,
                "SORTBY", "score",
                "RETURN", "5", "content", "doc_id", "title", "category", "score",
                "DIALECT", "2"
            )
            
            # Parse results
            similar_docs = []
            if results and len(results) > 1:
                # Results format: [count, key1, [field, value, ...], key2, ...]
                i = 1
                while i < len(results):
                    if i + 1 < len(results):
                        fields = results[i + 1]
                        doc = {}
                        score = 0
                        
                        for j in range(0, len(fields), 2):
                            field_name = fields[j].decode() if isinstance(fields[j], bytes) else fields[j]
                            field_val = fields[j + 1].decode() if isinstance(fields[j + 1], bytes) else fields[j + 1]
                            
                            if field_name == "score":
                                # Redis returns distance, convert to similarity (1 - distance for cosine)
                                score = 1 - float(field_val)
                            else:
                                doc[field_name] = field_val
                        
                        if score >= Config.SIMILARITY_THRESHOLD:
                            similar_docs.append({
                                "content": doc.get("content", ""),
                                "metadata": {
                                    "doc_id": doc.get("doc_id", ""),
                                    "title": doc.get("title", ""),
                                    "category": doc.get("category", ""),
                                    "number": doc.get("doc_id", ""),
                                    "short_description": doc.get("title", "")
                                },
                                "score": score
                            })
                    i += 2
            
            return similar_docs
            
        except redis.ResponseError as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get document counts for each collection"""
        stats = {}
        for index_name in set(self.collections.values()):
            try:
                info = self.redis.execute_command("FT.INFO", index_name)
                # Parse info response for num_docs
                for i, v in enumerate(info):
                    if isinstance(v, bytes) and v.decode() == "num_docs":
                        stats[index_name] = int(info[i + 1])
                        break
            except:
                stats[index_name] = 0
        return stats
    
    def _get_collection(self, name: str):
        """Get collection index name (for compatibility)"""
        if name not in self.collections:
            raise ValueError(f"Unknown collection: {name}")
        return self.collections[name]


# =============================================================================
# RAG Service
# =============================================================================

class RAGService:
    """Main RAG Service combining all components"""
    
    def __init__(self):
        self.embeddings = TitanEmbeddings()
        self.reasoning = ClaudeReasoning()
        self.vector_db = VectorDBManager(self.embeddings)
        logger.info("RAG Service initialized successfully")
    
    def process_ticket(self, ticket: TicketQuery) -> RAGResponse:
        """
        Main RAG pipeline for ticket processing.
        
        1. Generate embedding for ticket
        2. Retrieve similar KB articles
        3. Retrieve similar historical tickets
        4. Retrieve relevant SOPs
        5. Use Claude for reasoning
        6. Return structured response
        """
        import time
        start_time = time.time()
        
        # Combine short and long description for embedding
        query_text = f"{ticket.short_description}\n{ticket.description}"
        
        # Step 1 & 2: Retrieve similar KB articles
        kb_results = self.vector_db.search_similar("kb", query_text)
        kb_articles = [
            KBArticle(
                kb_number=r['metadata'].get('kb_number', 'KB0000000'),
                title=r['metadata'].get('title', 'Untitled'),
                content=r['content'][:500],
                category=r['metadata'].get('category', 'General'),
                relevance_score=r['score']
            )
            for r in kb_results
        ]
        
        # Step 3: Retrieve similar historical tickets
        ticket_results = self.vector_db.search_similar("ticket", query_text)
        similar_tickets = [
            SimilarTicket(
                incident_number=r['metadata'].get('incident_number', 'INC0000000'),
                short_description=r['metadata'].get('short_description', ''),
                resolution=r['metadata'].get('resolution', 'Not available'),
                resolution_time_hours=r['metadata'].get('resolution_time_hours', 0),
                relevance_score=r['score']
            )
            for r in ticket_results
        ]
        
        # Step 4: Retrieve relevant SOPs
        sop_results = self.vector_db.search_similar("sop", query_text)
        sop_references = [r['metadata'].get('title', r['content'][:100]) for r in sop_results]
        
        # Step 5: Claude reasoning
        claude_response = self.reasoning.analyze_ticket(
            ticket=ticket,
            kb_context=[{"title": kb.title, "content": kb.content, "score": kb.relevance_score} 
                       for kb in kb_articles],
            similar_tickets=[{"incident_number": t.incident_number, 
                            "short_description": t.short_description,
                            "resolution": t.resolution,
                            "resolution_time": t.resolution_time_hours}
                           for t in similar_tickets],
            sop_context=sop_references
        )
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Generate query ID
        query_id = hashlib.md5(
            f"{ticket.short_description}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # Build response
        return RAGResponse(
            query_id=query_id,
            timestamp=datetime.utcnow().isoformat(),
            analysis=claude_response.get('analysis', ''),
            root_cause_hypothesis=claude_response.get('root_cause_hypothesis', ''),
            recommended_actions=claude_response.get('recommended_actions', []),
            suggested_category=CategorySuggestion(
                category=claude_response.get('suggested_category', {}).get('category', 'General'),
                subcategory=claude_response.get('suggested_category', {}).get('subcategory', 'Unknown'),
                confidence=claude_response.get('suggested_category', {}).get('confidence', 0.5),
                reasoning=claude_response.get('suggested_category', {}).get('reasoning', '')
            ),
            kb_articles=kb_articles,
            similar_tickets=similar_tickets,
            sop_references=sop_references,
            overall_confidence=claude_response.get('overall_confidence', 0.5),
            processing_time_ms=processing_time
        )
    
    def ingest_document(self, doc: DocumentIngest) -> IngestResponse:
        """Ingest a new document into the vector database"""
        
        collection_map = {
            "kb": Config.COLLECTION_KB,
            "ticket": Config.COLLECTION_TICKETS,
            "sop": Config.COLLECTION_SOP
        }
        
        collection_name = collection_map.get(doc.document_type)
        if not collection_name:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_type: {doc.document_type}. Must be kb, ticket, or sop"
            )
        
        metadata = doc.metadata or {}
        metadata['document_id'] = doc.document_id
        metadata['title'] = doc.title
        metadata['ingested_at'] = datetime.utcnow().isoformat()
        
        embed_id = self.vector_db.add_document(
            collection_name=collection_name,
            doc_id=doc.document_id,
            content=f"{doc.title}\n{doc.content}",
            metadata=metadata
        )
        
        return IngestResponse(
            success=True,
            document_id=doc.document_id,
            collection=collection_name,
            embedding_id=embed_id
        )


# =============================================================================
# FastAPI Application
# =============================================================================

# Global RAG service instance
rag_service: Optional[RAGService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_service
    logger.info("Starting AEGIS RAG Service...")
    rag_service = RAGService()
    yield
    logger.info("Shutting down AEGIS RAG Service...")


app = FastAPI(
    title="🧠 AEGIS RAG Service",
    description="Intelligent Knowledge Retrieval for IT Service Management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Get collection stats from Redis
    stats = {}
    if rag_service:
        try:
            stats = rag_service.vector_db.get_collection_stats()
        except Exception as e:
            logger.warning(f"Could not get collection stats: {e}")
    
    return {
        "status": "healthy",
        "service": "aegis-rag",
        "timestamp": datetime.utcnow().isoformat(),
        "collections": {
            "kb": stats.get("idx:kb", 0),
            "tickets": stats.get("idx:tickets", 0),
            "sop": stats.get("idx:sop", 0)
        }
    }


@app.get("/stats")
async def get_stats():
    """Get vector database statistics for KB GUI"""
    stats = {}
    if rag_service:
        try:
            stats = rag_service.vector_db.get_collection_stats()
        except Exception as e:
            logger.warning(f"Could not get stats: {e}")
    
    return {
        "collections": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/analyze", response_model=RAGResponse)
async def analyze_ticket(ticket: TicketQuery):
    """
    🎯 Main RAG endpoint - Analyze a ticket with intelligent retrieval.
    
    This endpoint:
    1. Embeds the ticket using Amazon Titan V2
    2. Retrieves similar KB articles, tickets, and SOPs
    3. Uses Claude Sonnet 4.5 for intelligent reasoning
    4. Returns categorization, analysis, and recommendations
    
    Example request:
    ```json
    {
        "short_description": "Cannot login to O365 Outlook",
        "description": "User is unable to login to their O365 Outlook account. Password reset required.",
        "caller": "Alice FANARI"
    }
    ```
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    logger.info(f"Processing ticket: {ticket.short_description[:50]}...")
    return rag_service.process_ticket(ticket)


@app.post("/api/v1/ingest", response_model=IngestResponse)
async def ingest_document(doc: DocumentIngest):
    """
    📥 Ingest a document into the vector database.
    
    Supported document types:
    - `kb`: Knowledge Base articles
    - `ticket`: Historical tickets
    - `sop`: Standard Operating Procedures
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        return rag_service.ingest_document(doc)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form("kb"),
    chunk_size: int = Form(512),
    chunk_overlap: int = Form(50)
):
    """
    📤 Upload and ingest a file directly.
    Supports: PDF, TXT, MD, JSON
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    filename = file.filename
    content = ""
    
    logger.info(f"Receiving upload: {filename} for {collection}")
    
    try:
        # 1. Extract content based on file type
        if filename.endswith(".pdf"):
            import pypdf
            import io
            
            # Read file into memory
            file_content = await file.read()
            pdf_file = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            content = "\n".join(text_parts)
            
        elif filename.endswith(".json"):
            file_content = await file.read()
            json_data = json.loads(file_content.decode())
            # Handle various JSON formats
            if isinstance(json_data, list):
                content = "\n\n".join([json.dumps(item) for item in json_data])
            else:
                content = json.dumps(json_data, indent=2)
                
        else:
            # Assume text/md
            file_content = await file.read()
            content = file_content.decode("utf-8", errors="ignore")
        
        if not content.strip():
            raise ValueError("File is empty or content could not be extracted")
            
        # 2. Key for document
        doc_id = f"DOC_{hashlib.md5(filename.encode()).hexdigest()[:8]}"
        
        # 3. Simple chunking (naive implementation)
        # In a real scenario, use LangChain's RecursiveCharacterTextSplitter
        words = content.split()
        chunks = []
        current_chunk = []
        current_len = 0
        
        for word in words:
            current_chunk.append(word)
            current_len += 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # Overlap logic (simple rewind)
                overlap_words = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else []
                current_chunk = list(overlap_words)
                current_len = len(current_chunk)
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        # 4. Ingest chunks
        chunks_created = 0
        for i, chunk_text in enumerate(chunks):
            chunk_doc_id = f"{doc_id}_part{i+1}"
            
            ingest_doc = DocumentIngest(
                document_type=collection if collection in ["kb", "ticket", "sop"] else "kb",
                document_id=chunk_doc_id,
                title=f"{filename} (Part {i+1})",
                content=chunk_text,
                metadata={"source_file": filename, "chunk_index": i}
            )
            
            rag_service.ingest_document(ingest_doc)
            chunks_created += 1
            
        return {
            "success": True,
            "filename": filename,
            "chunks_created": chunks_created,
            "doc_id": doc_id,
            "preview": chunks[:3]
        }
        
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch-ingest")
async def batch_ingest(documents: List[DocumentIngest], background_tasks: BackgroundTasks):
    """
    📥 Batch ingest multiple documents (async).
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    async def ingest_batch():
        for doc in documents:
            try:
                rag_service.ingest_document(doc)
            except Exception as e:
                logger.error(f"Failed to ingest {doc.document_id}: {e}")
    
    background_tasks.add_task(ingest_batch)
    
    return {
        "status": "accepted",
        "count": len(documents),
        "message": "Documents queued for ingestion"
    }


@app.get("/api/v1/stats")
async def get_stats():
    """📊 Get vector database statistics"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    return {
        "collections": {
            "knowledge_base": {
                "name": Config.COLLECTION_KB,
                "count": rag_service.vector_db.kb_collection.count()
            },
            "ticket_history": {
                "name": Config.COLLECTION_TICKETS,
                "count": rag_service.vector_db.tickets_collection.count()
            },
            "sop_documents": {
                "name": Config.COLLECTION_SOP,
                "count": rag_service.vector_db.sop_collection.count()
            }
        },
        "models": {
            "embedding": Config.TITAN_MODEL_ID,
            "reasoning": Config.CLAUDE_MODEL
        },
        "config": {
            "top_k": Config.TOP_K_RESULTS,
            "similarity_threshold": Config.SIMILARITY_THRESHOLD
        }
    }


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    collection: str = "kb_articles"
    top_k: int = 5


@app.post("/search")
async def search_documents(request: SearchRequest):
    """
    🔍 Simple vector search endpoint for triage worker.
    
    Request body:
    {
        "query": "search text",
        "collection": "kb_articles" | "incidents" | "sop",
        "top_k": 5
    }
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    # Map collection names
    collection_map = {
        "kb_articles": "kb",
        "kb": "kb",
        "incidents": "ticket",
        "tickets": "ticket",
        "ticket": "ticket",
        "sop": "sop"
    }
    
    collection_name = collection_map.get(request.collection, "kb")
    
    try:
        results = rag_service.vector_db.search_similar(
            collection_name=collection_name,
            query=request.query,
            top_k=request.top_k
        )
        
        # Format results
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("metadata", {}).get("title", "Untitled"),
                "summary": r.get("content", "")[:300],
                "score": r.get("score", 0),
                "metadata": r.get("metadata", {})
            })
        
        return {"results": formatted, "count": len(formatted)}
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"results": [], "count": 0, "error": str(e)}


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
