"""
Analysis engine for CryptoVerde
"""

import pandas as pd
import logging
import numpy as np

logger = logging.getLogger("CryptoVerde.Analysis")

class AnalysisEngine:
    """Performs data analysis"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def clean_dataframe(self, df):
        """Clean dataframe - remove NaN, fill missing values"""
        if df.empty:
            return df
        
        df = df.copy()
        
        # Define numeric columns
        numeric_cols = ['current_price', 'market_cap', 'total_volume', 
                       'price_change_24h', 'volatility_score', 'market_cap_rank']
        
        # Fill NaN values with appropriate defaults
        for col in numeric_cols:
            if col in df.columns:
                if col == 'market_cap_rank':
                    df[col] = df[col].fillna(999)
                elif col == 'price_change_24h':
                    df[col] = df[col].fillna(0.0)
                else:
                    df[col] = df[col].fillna(0)
        
        # Remove any rows with critical missing data
        df = df.dropna(subset=['coin_id', 'name', 'symbol'])
        
        return df
    
    def get_top_gainers(self, df, n=5):
        """Get top gainers"""
        try:
            if df.empty or 'price_change_24h' not in df.columns:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            result = df.nlargest(n, 'price_change_24h')[
                ['name', 'symbol', 'price_change_24h', 'current_price']
            ].copy()
            
            result['price_change_24h'] = result['price_change_24h'].fillna(0)
            result['current_price'] = result['current_price'].fillna(0)
            
            return result
        except Exception as e:
            logger.error(f"Error in get_top_gainers: {e}")
            return pd.DataFrame()
    
    def get_top_losers(self, df, n=5):
        """Get top losers"""
        try:
            if df.empty or 'price_change_24h' not in df.columns:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            result = df.nsmallest(n, 'price_change_24h')[
                ['name', 'symbol', 'price_change_24h', 'current_price']
            ].copy()
            
            result['price_change_24h'] = result['price_change_24h'].fillna(0)
            result['current_price'] = result['current_price'].fillna(0)
            
            return result
        except Exception as e:
            logger.error(f"Error in get_top_losers: {e}")
            return pd.DataFrame()
    
    def get_top_by_market_cap(self, df, n=5):
        """Get top by market cap"""
        try:
            if df.empty or 'market_cap' not in df.columns:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            result = df.nlargest(n, 'market_cap')[
                ['name', 'symbol', 'market_cap', 'current_price']
            ].copy()
            
            result['market_cap'] = result['market_cap'].fillna(0)
            result['current_price'] = result['current_price'].fillna(0)
            
            return result
        except Exception as e:
            logger.error(f"Error in get_top_by_market_cap: {e}")
            return pd.DataFrame()
    
    def get_most_volatile(self, df, n=5):
        """Get most volatile coins"""
        try:
            if df.empty or 'volatility_score' not in df.columns:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            result = df.nlargest(n, 'volatility_score')[
                ['name', 'symbol', 'volatility_score', 'price_change_24h']
            ].copy()
            
            result['volatility_score'] = result['volatility_score'].fillna(0)
            result['price_change_24h'] = result['price_change_24h'].fillna(0)
            
            return result
        except Exception as e:
            logger.error(f"Error in get_most_volatile: {e}")
            return pd.DataFrame()
    
    def calculate_market_stats(self, df):
        """Calculate market statistics"""
        default_stats = {
            'total_market_cap': 0,
            'avg_market_cap': 0,
            'total_volume': 0,
            'avg_price': 0,
            'median_price': 0,
            'total_coins': 0,
            'avg_volatility': 0,
            'total_gainers': 0,
            'total_losers': 0,
            'market_dominance': {}
        }
        
        try:
            if df.empty:
                return default_stats
            
            df = self.clean_dataframe(df)
            
            stats = {
                'total_market_cap': float(df['market_cap'].sum()),
                'avg_market_cap': float(df['market_cap'].mean()),
                'total_volume': float(df['total_volume'].sum()),
                'avg_price': float(df['current_price'].mean()),
                'median_price': float(df['current_price'].median()),
                'total_coins': len(df),
                'avg_volatility': float(df['volatility_score'].mean()),
                'total_gainers': int((df['price_change_24h'] > 0).sum()),
                'total_losers': int((df['price_change_24h'] < 0).sum()),
            }
            
            # Calculate market dominance (top 5)
            if not df.empty and 'market_cap' in df.columns:
                total = stats['total_market_cap']
                if total > 0:
                    top_5 = df.nlargest(5, 'market_cap')
                    dominance = {}
                    for _, coin in top_5.iterrows():
                        dominance[coin['symbol']] = (coin['market_cap'] / total) * 100
                    stats['market_dominance'] = dominance
            
            return stats
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return default_stats
    
    def detect_anomalies(self, df, column='price_change_24h', threshold=3):
        """Detect anomalies using Z-score"""
        try:
            if df.empty or len(df) < 5 or column not in df.columns:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            values = df[column].dropna()
            
            if len(values) < 5:
                return pd.DataFrame()
            
            mean = values.mean()
            std = values.std()
            
            if std == 0 or pd.isna(std):
                return pd.DataFrame()
            
            df_copy = df.copy()
            df_copy['z_score'] = (df_copy[column] - mean) / std
            df_copy['z_score'] = df_copy['z_score'].fillna(0)
            
            anomalies = df_copy[abs(df_copy['z_score']) > threshold]
            
            if not anomalies.empty:
                return anomalies[['name', 'symbol', column, 'z_score']].copy()
            
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return pd.DataFrame()
    
    def get_volatility_ranking(self, df, n=10):
        """Get volatility ranking"""
        try:
            if df.empty:
                return pd.DataFrame()
            
            df = self.clean_dataframe(df)
            result = df.nlargest(n, 'volatility_score')[
                ['name', 'symbol', 'volatility_score', 'price_change_24h', 'current_price']
            ].copy()
            
            result['volatility_score'] = result['volatility_score'].fillna(0)
            result['price_change_24h'] = result['price_change_24h'].fillna(0)
            result['current_price'] = result['current_price'].fillna(0)
            
            return result
        except Exception as e:
            logger.error(f"Error in volatility ranking: {e}")
            return pd.DataFrame()