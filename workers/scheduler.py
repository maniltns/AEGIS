"""
Scheduler Service
=================
Runs scheduled background jobs for AEGIS.
Currently schedules:
1. Weekly ServiceNow Sync (Incidents & KB)
"""

import time
import schedule
import logging
import asyncio
import os
import sys

# Ensure workers module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from servicenow_sync import run_sync
except ImportError:
    # Fallback if running from root
    from workers.servicenow_sync import run_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aegis.scheduler")

def run_snow_sync_job():
    """Wrapper to run async sync job"""
    logger.info("⏰ Starting scheduled ServiceNow Sync Job...")
    try:
        asyncio.run(run_sync())
        logger.info("✅ ServiceNow Sync Job completed successfully.")
    except Exception as e:
        logger.error(f"❌ ServiceNow Sync Job failed: {e}")

# Schedule jobs
# Run every Sunday at 02:00 AM
schedule.every().sunday.at("02:00").do(run_snow_sync_job)

logger.info("Scheduler started. Jobs configured:")
logger.info("- Weekly ServiceNow Sync (Sunday @ 02:00 AM)")

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
