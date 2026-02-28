"""
Data processing for CryptoVerde
"""

import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger("CryptoVerde.Processor")

class DataProcessor:
    """Transforms and cleans data"""
    
    def process(self, raw_data):
        """Process raw API data"""
        if not raw_data:
            return []
        
        processed = []
        timestamp = datetime.now().isoformat()
        
        for coin in raw_data:
            try:
                coin_id = str(coin.get('id', ''))
                if not coin_id:
                    continue
                
                symbol = str(coin.get('symbol', '')).upper() or 'UNKNOWN'
                name = str(coin.get('name', '')) or 'Unknown'
                
                # Handle numeric fields
                current_price = float(coin.get('current_price') or 0)
                market_cap = int(coin.get('market_cap') or 0)
                volume = int(coin.get('total_volume') or 0)
                price_change_24h = float(coin.get('price_change_percentage_24h') or 0)
                market_cap_rank = int(coin.get('market_cap_rank') or 999)
                
                # Feature engineering: volatility score
                try:
                    volatility = abs(price_change_24h) * volume / 1_000_000
                    if pd.isna(volatility):
                        volatility = 0.0
                except:
                    volatility = 0.0
                
                processed.append({
                    'coin_id': coin_id,
                    'symbol': symbol,
                    'name': name,
                    'current_price': current_price,
                    'market_cap': market_cap,
                    'total_volume': volume,
                    'price_change_24h': price_change_24h,
                    'market_cap_rank': market_cap_rank,
                    'volatility_score': volatility,
                    'extracted_at': timestamp
                })
            except Exception as e:
                logger.warning(f"⚠️ Skipped {coin.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Processed {len(processed)} coins")
        return processed