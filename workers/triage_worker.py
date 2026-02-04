"""
AEGIS Triage Worker
Polls Redis queue and processes incidents through LangGraph pipeline.

Run as a separate process from the API server for reliability.
"""

import os
import sys
import json
import signal
import logging
import asyncio
from datetime import datetime
from typing import Optional

import redis

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.triage_graph import process_incident

# Configure logging (stdout only for Docker compatibility)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("aegis.worker")

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

QUEUE_NAME = "aegis:queue:triage"
DEAD_LETTER_QUEUE = "aegis:queue:dead_letter"
PROCESSING_QUEUE = "aegis:queue:processing"

# Graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


class TriageWorker:
    """
    Redis-based worker that processes incidents from a queue.
    
    Features:
    - Reliable queue processing (BRPOPLPUSH pattern)
    - Dead letter queue for failed items
    - Graceful shutdown
    - Retry logic
    """
    
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        self.running = True
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    async def start(self):
        """Start the worker loop."""
        logger.info(f"🚀 AEGIS Triage Worker starting...")
        logger.info(f"   Redis: {REDIS_HOST}:{REDIS_PORT}")
        logger.info(f"   Queue: {QUEUE_NAME}")
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        while not shutdown_requested:
            try:
                await self._process_next()
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(self.retry_delay)
        
        logger.info("Worker shutdown complete")
    
    async def _process_next(self):
        """Process the next item from the queue."""
        # Use BRPOPLPUSH for reliable processing
        # Move item to processing queue atomically
        raw_item = self.redis.brpoplpush(
            QUEUE_NAME,
            PROCESSING_QUEUE,
            timeout=5  # 5 second timeout
        )
        
        if raw_item is None:
            # No items in queue
            return
        
        try:
            # Parse incident
            incident = json.loads(raw_item)
            incident_number = incident.get("number", "UNKNOWN")
            
            logger.info(f"📥 Processing: {incident_number}")
            
            # Process through LangGraph
            result = await process_incident(incident)
            
            # Save result for API retrieval (/triage/{triage_id})
            triage_id = incident.get("triage_id")
            if triage_id:
                self.redis.setex(
                    f"triage:result:{triage_id}",
                    86400,  # 24 hour TTL
                    json.dumps(result)
                )
                logger.info(f"💾 Saved result: triage:result:{triage_id}")
            
            # Log result
            self._log_result(incident_number, result)
            
            # Remove from processing queue on success
            self.redis.lrem(PROCESSING_QUEUE, 1, raw_item)
            
            logger.info(f"✅ Completed: {incident_number} -> {result.get('status')}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in queue: {e}")
            self._move_to_dead_letter(raw_item, str(e))
            
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            
            # Check retry count
            retry_count = self._get_retry_count(raw_item)
            
            if retry_count < self.max_retries:
                # Increment retry count and re-queue
                self._requeue_with_retry(raw_item, retry_count + 1)
                logger.info(f"Re-queued for retry ({retry_count + 1}/{self.max_retries})")
            else:
                # Move to dead letter queue
                self._move_to_dead_letter(raw_item, str(e))
                logger.error(f"Moved to dead letter queue after {self.max_retries} retries")
    
    def _log_result(self, incident_number: str, result: dict):
        """Log processing result to Redis."""
        timestamp = datetime.utcnow().isoformat()
        
        # Determine log level based on status
        status = result.get("status", "unknown")
        level = "success" if status == "executed" else "warning" if status == "blocked" else "error" if status == "failed" else "info"
        
        # Log individual actions for better visibility
        actions = result.get("actions_taken", [])
        for action in actions:
            # Determine which node performed this action
            if "PII" in action or "duplicate" in action.lower() or "Blocked" in action:
                agent = "GUARDRAILS"
            elif "KB" in action or "Enriched" in action or "CMDB" in action:
                agent = "ENRICHMENT"
            elif "Triaged" in action or "confidence" in action.lower():
                agent = "TRIAGE_LLM"
            else:
                agent = "EXECUTOR"
            
            log_entry = {
                "id": f"{incident_number}_{len(actions)}",
                "timestamp": timestamp,
                "agent": agent,
                "incident": incident_number,
                "action": action,
                "level": level,
                "details": result.get("reasoning", "")
            }
            self.redis.lpush("logs:activity", json.dumps(log_entry))
        
        # Trim to keep last 1000 entries
        self.redis.ltrim("logs:activity", 0, 999)
        
        # Update stats
        self.redis.hincrby("stats:daily", datetime.utcnow().strftime("%Y-%m-%d"), 1)
        
        # Update processed count for today
        today = datetime.utcnow().strftime("%Y%m%d")
        self.redis.incr(f"stats:processed:{today}")
    
    def _get_retry_count(self, raw_item: str) -> int:
        """Get retry count from item metadata."""
        try:
            item = json.loads(raw_item)
            return item.get("_retry_count", 0)
        except:
            return 0
    
    def _requeue_with_retry(self, raw_item: str, retry_count: int):
        """Re-queue item with incremented retry count."""
        try:
            item = json.loads(raw_item)
            item["_retry_count"] = retry_count
            item["_last_retry"] = datetime.utcnow().isoformat()
            
            # Remove from processing queue
            self.redis.lrem(PROCESSING_QUEUE, 1, raw_item)
            
            # Add back to main queue
            self.redis.lpush(QUEUE_NAME, json.dumps(item))
            
        except Exception as e:
            logger.error(f"Failed to requeue: {e}")
    
    def _move_to_dead_letter(self, raw_item: str, error: str):
        """Move failed item to dead letter queue."""
        try:
            item = json.loads(raw_item)
            item["_error"] = error
            item["_failed_at"] = datetime.utcnow().isoformat()
            
            # Remove from processing queue
            self.redis.lrem(PROCESSING_QUEUE, 1, raw_item)
            
            # Add to dead letter queue
            self.redis.lpush(DEAD_LETTER_QUEUE, json.dumps(item))
            
        except Exception as e:
            logger.error(f"Failed to move to dead letter: {e}")
    
    def get_queue_stats(self) -> dict:
        """Get current queue statistics."""
        return {
            "pending": self.redis.llen(QUEUE_NAME),
            "processing": self.redis.llen(PROCESSING_QUEUE),
            "dead_letter": self.redis.llen(DEAD_LETTER_QUEUE)
        }


async def main():
    """Entry point."""
    worker = TriageWorker()
    
    # Log initial stats
    stats = worker.get_queue_stats()
    logger.info(f"Queue stats: {stats}")
    
    # Start processing
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
