"""
Database manager for CryptoVerde
"""

import logging
import streamlit as st
import pandas as pd
from supabase import create_client
from contextlib import contextmanager
from config import Config

logger = logging.getLogger("CryptoVerde.DB")

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            self.table = "crypto_market"
            logger.info("✅ Database connected")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            st.error(f"Database Error: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database transactions"""
        try:
            yield self.supabase
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise
    
    def save_coins(self, coins_data):
        """Save coins with UPSERT"""
        try:
            if not coins_data:
                return False
            
            with self.get_connection() as conn:
                conn.table(self.table)\
                    .upsert(coins_data, on_conflict='coin_id')\
                    .execute()
                
                logger.info(f"✅ Saved {len(coins_data)} coins")
                return True
        except Exception as e:
            logger.error(f"❌ Save failed: {e}")
            return False
    
    def get_coins(self):
        """Get latest coins"""
        try:
            with self.get_connection() as conn:
                result = conn.table(self.table)\
                    .select("*")\
                    .order("extracted_at", desc=True)\
                    .execute()
                
                # Get unique coins
                seen = {}
                for coin in result.data:
                    if coin['coin_id'] not in seen:
                        seen[coin['coin_id']] = coin
                
                return list(seen.values())
        except Exception as e:
            logger.error(f"❌ Fetch failed: {e}")
            return []