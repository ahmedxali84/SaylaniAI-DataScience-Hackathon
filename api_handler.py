"""
CoinGecko API handler for CryptoVerde
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from config import Config
from utils import save_json, format_timestamp

logger = logging.getLogger("CryptoVerde.API")

class CoinGeckoAPI:
    """Handles all API interactions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        try:
            import os, json
            if os.path.exists(Config.CACHE_FILE):
                with open(Config.CACHE_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            import json
            with open(Config.CACHE_FILE, 'w') as f:
                json.dump(self.cache, f)
        except:
            pass
    
    def get_top_coins(self):
        """Fetch top 100 coins"""
        try:
            logger.info("📡 Fetching from CoinGecko...")
            
            response = self.session.get(
                Config.COINGECKO_API,
                params=Config.API_PARAMS,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Got {len(data)} coins")
            
            # Save raw data
            self.save_raw_data(data)
            
            return data
        except Exception as e:
            logger.error(f"❌ API error: {e}")
            return None
    
    def get_historical_data(self, coin_id, days=30):
        """Get historical price data"""
        try:
            # Check cache
            cache_key = f"{coin_id}_{days}"
            if cache_key in self.cache:
                cache_time = datetime.fromisoformat(self.cache[cache_key]['time'])
                if datetime.now() - cache_time < timedelta(minutes=5):
                    return pd.DataFrame(self.cache[cache_key]['data'])
            
            url = Config.COINGECKO_HISTORICAL.format(coin_id)
            params = {
                "vs_currency": "usd",
                "days": days
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process data
            ohlc = self._process_historical_data(data, days)
            
            # Cache results
            self.cache[cache_key] = {
                'time': datetime.now().isoformat(),
                'data': ohlc.to_dict()
            }
            self.save_cache()
            
            return ohlc
        except Exception as e:
            logger.error(f"❌ Historical error: {e}")
            return None
    
    def _process_historical_data(self, data, days):
        """Process raw historical data into OHLC"""
        # Price data
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Create OHLC based on timeframe
        if days <= 7:
            ohlc = df['price'].resample('1H').ohlc()
        elif days <= 30:
            ohlc = df['price'].resample('4H').ohlc()
        else:
            ohlc = df['price'].resample('1D').ohlc()
        
        ohlc = ohlc.dropna()
        
        # Add volume data
        if 'total_volumes' in data:
            volumes = data['total_volumes']
            vol_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            vol_df['timestamp'] = pd.to_datetime(vol_df['timestamp'], unit='ms')
            vol_df.set_index('timestamp', inplace=True)
            
            if days <= 7:
                ohlc['volume'] = vol_df['volume'].resample('1H').sum()
            elif days <= 30:
                ohlc['volume'] = vol_df['volume'].resample('4H').sum()
            else:
                ohlc['volume'] = vol_df['volume'].resample('1D').sum()
        
        return ohlc
    
    def save_raw_data(self, data):
        """Save raw API data for logging"""
        try:
            filename = f"{Config.RAW_DATA_DIR}/raw_{format_timestamp()}.json"
            save_json(data, filename)
        except Exception as e:
            logger.error(f"Failed to save raw data: {e}")