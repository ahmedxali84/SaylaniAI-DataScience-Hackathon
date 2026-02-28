"""
Price Predictor for CryptoVerde
Uses trained models to predict next 10 days
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import joblib
import os
import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger("CryptoVerde.Predictor")

class CryptoPredictor:
    """Predicts future prices using trained models"""
    
    def __init__(self, db_manager, model_trainer):
        self.db = db_manager
        self.trainer = model_trainer
        self.model_dir = "trained_models"
    
    def prepare_prediction_features(self, coin_data, days=10):
        """Prepare features for prediction"""
        try:
            df = pd.DataFrame([coin_data])
            
            # Create features matching training data
            features = {
                'price_lag_1': coin_data.get('price_lag_1', coin_data['current_price']),
                'price_lag_2': coin_data.get('price_lag_2', coin_data['current_price']),
                'price_lag_3': coin_data.get('price_lag_3', coin_data['current_price']),
                'price_lag_7': coin_data.get('price_lag_7', coin_data['current_price']),
                'price_ma_7': coin_data.get('price_ma_7', coin_data['current_price']),
                'price_ma_30': coin_data.get('price_ma_30', coin_data['current_price']),
                'price_std_7': coin_data.get('price_std_7', 0),
                'volatility': coin_data.get('volatility', 0),
                'rsi': coin_data.get('rsi', 50),
                'macd': coin_data.get('macd', 0),
                'volume_lag_1': coin_data.get('volume_lag_1', coin_data['total_volume']),
                'volume_ma_7': coin_data.get('volume_ma_7', coin_data['total_volume'])
            }
            
            return pd.DataFrame([features])
            
        except Exception as e:
            logger.error(f"❌ Error preparing features: {e}")
            return None
    
    def predict_next_10_days(self, coin_id):
        """Predict prices for next 10 days"""
        try:
            # Load model
            model, scaler = self.trainer.load_model(coin_id)
            if model is None:
                return None
            
            # Get latest coin data
            coins = self.db.get_coins()
            if not coins:
                return None
            
            df = pd.DataFrame(coins)
            coin_data_df = df[df['coin_id'] == coin_id]
            
            if coin_data_df.empty:
                logger.error(f"❌ No data for {coin_id}")
                return None
            
            coin_data = coin_data_df.iloc[0].to_dict()
            
            # Get historical data for feature calculation
            historical = self.db.get_historical_data(coin_id, days=30)
            hist_df = pd.DataFrame(historical) if historical else pd.DataFrame()
            
            # Calculate rolling features
            if not hist_df.empty:
                hist_df = hist_df.sort_values('extracted_at')
                prices = hist_df['current_price'].tolist() + [coin_data['current_price']]
                
                # Calculate features
                coin_data['price_lag_1'] = prices[-2] if len(prices) > 1 else coin_data['current_price']
                coin_data['price_lag_2'] = prices[-3] if len(prices) > 2 else coin_data['current_price']
                coin_data['price_lag_3'] = prices[-4] if len(prices) > 3 else coin_data['current_price']
                coin_data['price_lag_7'] = prices[-8] if len(prices) > 8 else coin_data['current_price']
                
                coin_data['price_ma_7'] = np.mean(prices[-7:]) if len(prices) >= 7 else coin_data['current_price']
                coin_data['price_ma_30'] = np.mean(prices[-30:]) if len(prices) >= 30 else coin_data['current_price']
                coin_data['price_std_7'] = np.std(prices[-7:]) if len(prices) >= 7 else 0
            
            predictions = []
            current_data = coin_data.copy()
            
            # Predict next 10 days iteratively
            for day in range(1, 11):
                # Prepare features
                features_df = self.prepare_prediction_features(current_data)
                if features_df is None:
                    break
                
                # Scale features
                features_scaled = scaler.transform(features_df)
                
                # Predict
                predicted_price = model.predict(features_scaled)[0]
                
                # Calculate confidence based on model metrics
                confidence = min(95, max(60, 100 - (abs(predicted_price - coin_data['current_price']) / coin_data['current_price'] * 100)))
                
                prediction_date = datetime.now() + timedelta(days=day)
                
                predictions.append({
                    'day': day,
                    'date': prediction_date.strftime('%Y-%m-%d'),
                    'predicted_price': float(predicted_price),
                    'confidence': confidence,
                    'trend': 'up' if predicted_price > current_data['current_price'] else 'down',
                    'change_percent': ((predicted_price - coin_data['current_price']) / coin_data['current_price']) * 100
                })
                
                # Update current data for next prediction
                current_data['current_price'] = predicted_price
                current_data['price_lag_3'] = current_data['price_lag_2']
                current_data['price_lag_2'] = current_data['price_lag_1']
                current_data['price_lag_1'] = predicted_price
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Prediction failed for {coin_id}: {e}")
            return None
    
    def get_prediction_summary(self, coin_id):
        """Get summary of predictions"""
        predictions = self.predict_next_10_days(coin_id)
        
        if not predictions:
            return None
        
        df = pd.DataFrame(predictions)
        
        summary = {
            'coin_id': coin_id,
            'current_price': predictions[0]['predicted_price'] if len(predictions) > 1 else 0,
            'predicted_price_10d': predictions[-1]['predicted_price'],
            'total_change': predictions[-1]['change_percent'],
            'avg_confidence': df['confidence'].mean(),
            'max_price': df['predicted_price'].max(),
            'min_price': df['predicted_price'].min(),
            'volatility': df['predicted_price'].std(),
            'trend': 'BULLISH' if predictions[-1]['change_percent'] > 5 else 'BEARISH' if predictions[-1]['change_percent'] < -5 else 'NEUTRAL'
        }
        
        return summary
    
    def get_all_predictions(self, top_n=10):
        """Get predictions for top N coins"""
        coins = self.db.get_coins()
        if not coins:
            return None
        
        df = pd.DataFrame(coins)
        top_coins = df.nlargest(top_n, 'market_cap')
        
        all_predictions = []
        
        for _, coin in top_coins.iterrows():
            predictions = self.predict_next_10_days(coin['coin_id'])
            if predictions:
                all_predictions.append({
                    'coin_id': coin['coin_id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'current_price': coin['current_price'],
                    'predictions': predictions
                })
        
        return all_predictions
    
    def render_prediction_chart(self, predictions, coin_name, historical_data=None):
        """Render prediction chart with plotly"""
        if not predictions:
            return None
        
        pred_df = pd.DataFrame(predictions)
        
        fig = go.Figure()
        
        # Add historical price if available
        if historical_data is not None and not historical_data.empty:
            hist_df = historical_data.reset_index()
            fig.add_trace(go.Scatter(
                x=hist_df['timestamp'][-20:],
                y=hist_df['close'][-20:],
                mode='lines',
                name='Historical',
                line=dict(color='#2196F3', width=2)
            ))
        
        # Add predictions
        pred_dates = [datetime.now() + timedelta(days=d) for d in range(1, 11)]
        
        fig.add_trace(go.Scatter(
            x=pred_dates,
            y=pred_df['predicted_price'],
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#4CAF50', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        # Add confidence bands
        fig.add_trace(go.Scatter(
            x=pred_dates + pred_dates[::-1],
            y=list(pred_df['predicted_price'] * (1 + (100 - pred_df['confidence'])/100)) + 
              list(pred_df['predicted_price'] * (1 - (100 - pred_df['confidence'])/100))[::-1],
            fill='toself',
            fillcolor='rgba(76, 175, 80, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Range'
        ))
        
        fig.update_layout(
            title=f"{coin_name} - 10-Day Price Prediction",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        return fig