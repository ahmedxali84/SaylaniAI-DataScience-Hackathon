"""
Background scheduler for CryptoVerde
"""

import threading
import time
import logging
from etl_pipeline import ETLPipeline
from config import Config

logger = logging.getLogger("CryptoVerde.Scheduler")

class SchedulerManager:
    """Manages scheduled ETL runs"""
    
    def __init__(self):
        self.etl = ETLPipeline()
        self.running = True
        self.thread = None
    
    def start(self):
        """Start scheduler in background"""
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("🔄 Scheduler started (5-minute intervals)")
    
    def _run_scheduler(self):
        """Run scheduler loop"""
        while self.running:
            try:
                # Run ETL
                self.etl.run()
                
                # Wait for next interval
                for _ in range(Config.ETL_INTERVAL_SECONDS):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ Scheduler stopped")