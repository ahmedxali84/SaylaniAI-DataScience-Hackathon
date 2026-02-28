"""
Configuration settings for CryptoVerde
"""

import os
from datetime import timedelta

class Config:
    # Supabase Configuration
    SUPABASE_URL = "https://kjchklbuvhhisqmehhda.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtqY2hrbGJ1dmhoaXNxbWVoaGRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyOTYyOTEsImV4cCI6MjA4Nzg3MjI5MX0.e-1HFubsBRykMPOTiEB9fdOwwiP_ns89BxK_Gy2HOx4"
    
    # CoinGecko API
    COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
    COINGECKO_HISTORICAL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"
    
    # API Parameters
    API_PARAMS = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": True,
        "price_change_percentage": "24h"
    }
    
    # ETL Settings
    ETL_INTERVAL_SECONDS = 300  # 5 minutes
    DASHBOARD_REFRESH_SECONDS = 60
    
    # File paths
    RAW_DATA_DIR = "raw_data"
    LOG_FILE = "crypto_etl.log"
    CACHE_FILE = "cache.json"
    
    # Cache settings
    CACHE_DURATION = timedelta(minutes=5)