"""
Technical indicators for CryptoVerde
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("CryptoVerde.Indicators")

class TechnicalIndicators:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_sma(data, window):
        """Simple Moving Average"""
        try:
            if data is None or len(data) < window:
                return pd.Series(index=data.index) if data is not None else pd.Series()
            return data.rolling(window=window, min_periods=1).mean()
        except:
            return pd.Series(index=data.index) if data is not None else pd.Series()
    
    @staticmethod
    def calculate_ema(data, window):
        """Exponential Moving Average"""
        try:
            if data is None or len(data) < 2:
                return pd.Series(index=data.index) if data is not None else pd.Series()
            return data.ewm(span=window, adjust=False, min_periods=1).mean()
        except:
            return pd.Series(index=data.index) if data is not None else pd.Series()
    
    @staticmethod
    def calculate_rsi(data, window=14):
        """Relative Strength Index"""
        try:
            if data is None or len(data) < window + 1:
                return pd.Series(50, index=data.index) if data is not None else pd.Series()
            
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
            
            # Handle division by zero
            rs = gain / loss.replace(0, np.nan)
            rs = rs.fillna(0)
            
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50)
        except:
            return pd.Series(50, index=data.index) if data is not None else pd.Series()
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """MACD Indicator"""
        try:
            if data is None or len(data) < slow:
                empty = pd.Series(index=data.index) if data is not None else pd.Series()
                return empty, empty, empty
            
            ema_fast = data.ewm(span=fast, adjust=False, min_periods=1).mean()
            ema_slow = data.ewm(span=slow, adjust=False, min_periods=1).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=1).mean()
            histogram = macd_line - signal_line
            
            return macd_line.fillna(0), signal_line.fillna(0), histogram.fillna(0)
        except:
            empty = pd.Series(0, index=data.index) if data is not None else pd.Series()
            return empty, empty, empty
    
    @staticmethod
    def add_all_indicators(df):
        """Add all technical indicators"""
        if df is None or df.empty:
            return df
        
        result = df.copy()
        
        try:
            # Moving Averages
            result['SMA_20'] = TechnicalIndicators.calculate_sma(result['close'], 20)
            result['SMA_50'] = TechnicalIndicators.calculate_sma(result['close'], 50)
            result['EMA_12'] = TechnicalIndicators.calculate_ema(result['close'], 12)
            result['EMA_26'] = TechnicalIndicators.calculate_ema(result['close'], 26)
            
            # MACD
            macd, signal, hist = TechnicalIndicators.calculate_macd(result['close'])
            result['MACD'] = macd
            result['MACD_signal'] = signal
            result['MACD_histogram'] = hist
            
            # RSI
            result['RSI'] = TechnicalIndicators.calculate_rsi(result['close'])
            
            # Fill any remaining NaN values
            result = result.fillna(0)
            
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
        
        return result
    
    @staticmethod
    def detect_trend(df):
        """Detect market trend"""
        try:
            if df is None or df.empty or 'close' not in df:
                return "NO DATA", "#9E9E9E"
            
            last_price = float(df['close'].iloc[-1]) if not pd.isna(df['close'].iloc[-1]) else 0
            sma_20 = float(df['SMA_20'].iloc[-1]) if 'SMA_20' in df and not pd.isna(df['SMA_20'].iloc[-1]) else last_price
            sma_50 = float(df['SMA_50'].iloc[-1]) if 'SMA_50' in df and not pd.isna(df['SMA_50'].iloc[-1]) else last_price
            rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df and not pd.isna(df['RSI'].iloc[-1]) else 50
            
            if last_price > sma_20 and sma_20 > sma_50 and rsi > 50:
                return "STRONG UPTREND 🔥", "#4CAF50"
            elif last_price > sma_20:
                return "UPTREND 📈", "#8BC34A"
            elif last_price < sma_20 and sma_20 < sma_50 and rsi < 50:
                return "STRONG DOWNTREND 🛑", "#F44336"
            elif last_price < sma_20:
                return "DOWNTREND 📉", "#FF9800"
            else:
                return "NEUTRAL ⚖️", "#9E9E9E"
        except:
            return "NEUTRAL ⚖️", "#9E9E9E"