"""
ETL Pipeline for CryptoVerde
"""

import time
import logging
import pandas as pd
from api_handler import CoinGeckoAPI
from data_processor import DataProcessor
from database import DatabaseManager
from analysis_engine import AnalysisEngine

logger = logging.getLogger("CryptoVerde.ETL")

class ETLPipeline:
    """Orchestrates the ETL process"""
    
    def __init__(self):
        self.api = CoinGeckoAPI()
        self.processor = DataProcessor()
        self.db = DatabaseManager()
        self.analysis = AnalysisEngine(self.db)
    
    def run(self):
        """Run complete ETL pipeline"""
        logger.info("="*60)
        logger.info("🚀 STARTING ETL PIPELINE")
        start_time = time.time()
        
        try:
            # EXTRACT
            logger.info("📡 Step 1: Extracting...")
            raw_data = self.api.get_top_coins()
            if not raw_data:
                logger.error("❌ Extraction failed")
                return False
            
            # TRANSFORM
            logger.info("🔄 Step 2: Transforming...")
            transformed = self.processor.process(raw_data)
            if not transformed:
                logger.error("❌ Transformation failed")
                return False
            
            # LOAD
            logger.info("💾 Step 3: Loading...")
            success = self.db.save_coins(transformed)
            
            elapsed = time.time() - start_time
            
            if success:
                logger.info(f"✅ ETL COMPLETED in {elapsed:.2f}s")
                
                # Show stats
                coins = self.db.get_coins()
                if coins:
                    df = pd.DataFrame(coins)
                    stats = self.analysis.calculate_market_stats(df)
                    logger.info(f"📊 Total Market Cap: ${stats['total_market_cap']:,.0f}")
                    logger.info(f"📊 Active Coins: {stats['total_coins']}")
                
                return True
            else:
                logger.error("❌ Load failed")
                return False
        except Exception as e:
            logger.error(f"❌ ETL failed: {e}")
            return False