"""
Dashboard UI for CryptoVerde
"""

import streamlit as st
import pandas as pd
import time
import logging
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import DatabaseManager
from api_handler import CoinGeckoAPI
from analysis_engine import AnalysisEngine
from indicators import TechnicalIndicators
from config import Config

logger = logging.getLogger("CryptoVerde.Dashboard")

class CryptoDashboard:
    """Professional Streamlit Dashboard"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api = CoinGeckoAPI()
        self.analysis = AnalysisEngine(self.db)
        self.indicators = TechnicalIndicators()
        
        # Page config
        st.set_page_config(
            page_title="CryptoVerde",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self.apply_custom_css()
    
    def apply_custom_css(self):
        """Apply professional CSS"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .main-header h1 {
            color: white !important;
            font-size: 2.5rem !important;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        .positive { color: #10B981; font-weight: bold; }
        .negative { color: #EF4444; font-weight: bold; }
        .trading-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_chart(self, ohlc_data, coin_name):
        """Create professional candlestick chart"""
        try:
            if ohlc_data is None or ohlc_data.empty:
                return None
            
            ohlc = self.indicators.add_all_indicators(ohlc_data.copy())
            trend, trend_color = self.indicators.detect_trend(ohlc)
            
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.4, 0.2, 0.2, 0.2],
                subplot_titles=(
                    f'{coin_name} - Price Action',
                    'Volume',
                    'MACD',
                    'RSI'
                )
            )
            
            # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=ohlc.index,
                    open=ohlc['open'],
                    high=ohlc['high'],
                    low=ohlc['low'],
                    close=ohlc['close'],
                    name='Price',
                    increasing_line_color='#10B981',
                    decreasing_line_color='#EF4444'
                ),
                row=1, col=1
            )
            
            # Moving Averages
            if 'SMA_20' in ohlc.columns and not ohlc['SMA_20'].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=ohlc.index,
                        y=ohlc['SMA_20'],
                        name='SMA 20',
                        line=dict(color='#667eea', width=1.5)
                    ),
                    row=1, col=1
                )
            
            if 'SMA_50' in ohlc.columns and not ohlc['SMA_50'].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=ohlc.index,
                        y=ohlc['SMA_50'],
                        name='SMA 50',
                        line=dict(color='#f39c12', width=1.5)
                    ),
                    row=1, col=1
                )
            
            # Volume
            if 'volume' in ohlc.columns:
                colors = ['#10B981' if ohlc['close'].iloc[i] >= ohlc['open'].iloc[i] 
                         else '#EF4444' for i in range(len(ohlc))]
                
                fig.add_trace(
                    go.Bar(
                        x=ohlc.index,
                        y=ohlc['volume'],
                        name='Volume',
                        marker_color=colors,
                        showlegend=False
                    ),
                    row=2, col=1
                )
            
            # MACD
            if all(col in ohlc.columns for col in ['MACD', 'MACD_signal', 'MACD_histogram']):
                fig.add_trace(
                    go.Scatter(
                        x=ohlc.index,
                        y=ohlc['MACD'],
                        name='MACD',
                        line=dict(color='#667eea', width=2)
                    ),
                    row=3, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=ohlc.index,
                        y=ohlc['MACD_signal'],
                        name='Signal',
                        line=dict(color='#f39c12', width=2)
                    ),
                    row=3, col=1
                )
                
                hist_colors = ['#10B981' if x >= 0 else '#EF4444' 
                              for x in ohlc['MACD_histogram'].fillna(0)]
                fig.add_trace(
                    go.Bar(
                        x=ohlc.index,
                        y=ohlc['MACD_histogram'],
                        name='Histogram',
                        marker_color=hist_colors,
                        showlegend=False
                    ),
                    row=3, col=1
                )
            
            # RSI
            if 'RSI' in ohlc.columns:
                fig.add_trace(
                    go.Scatter(
                        x=ohlc.index,
                        y=ohlc['RSI'],
                        name='RSI',
                        line=dict(color='#9b59b6', width=2)
                    ),
                    row=4, col=1
                )
                
                fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", 
                             opacity=0.5, row=4, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#10B981", 
                             opacity=0.5, row=4, col=1)
            
            fig.update_layout(
                template='plotly_white',
                height=800,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                title=f"{coin_name} - Technical Analysis [{trend}]",
                title_x=0.5
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return None
    
    def render_kpi_cards(self, stats):
        """Render KPI cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>💰 Total Market Cap</h3>
                <div style="font-size: 1.8rem; font-weight: bold;">
                    ${stats['total_market_cap']/1e12:.2f}T
                </div>
                <div class="positive">↑ Active: {stats['total_coins']} coins</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📊 24h Volume</h3>
                <div style="font-size: 1.8rem; font-weight: bold;">
                    ${stats['total_volume']/1e9:.2f}B
                </div>
                <div>Gainers: {stats['total_gainers']} | Losers: {stats['total_losers']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3>💵 Average Price</h3>
                <div style="font-size: 1.8rem; font-weight: bold;">
                    ${stats['avg_price']:,.2f}
                </div>
                <div>Median: ${stats['median_price']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h3>⚡ Avg Volatility</h3>
                <div style="font-size: 1.8rem; font-weight: bold;">
                    {stats['avg_volatility']:,.0f}
                </div>
                <div>Volatility Score</div>
            </div>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main dashboard runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 CRYPTOVERDE - Professional Trading Platform</h1>
            <p>Real-time Analytics • Technical Indicators • Market Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.markdown("### ⚙️ Platform Controls")
            
            if st.button("🔄 SYNC MARKET DATA", use_container_width=True):
                with st.spinner("Fetching live data..."):
                    from etl_pipeline import ETLPipeline
                    etl = ETLPipeline()
                    if etl.run():
                        st.success("✅ Data synced successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Sync failed - Check connection")
            
            st.markdown("---")
            st.markdown("### 📊 Chart Settings")
            days = st.select_slider("Timeframe", options=[1, 7, 14, 30, 90], value=30)
            auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", value=True)
            
            st.markdown("---")
            st.markdown("### 📈 Market Stats")
        
        # Get data
        coins = self.db.get_coins()
        
        if not coins:
            st.warning("⏳ No data available. Click 'SYNC MARKET DATA' to start.")
            if auto_refresh:
                time.sleep(5)
                st.rerun()
            return
        
        # Convert to DataFrame and clean
        df = pd.DataFrame(coins)
        df = self.analysis.clean_dataframe(df)
        
        # Calculate stats
        stats = self.analysis.calculate_market_stats(df)
        
        # KPI Cards
        self.render_kpi_cards(stats)
        
        st.markdown("---")
        
        # Market Dominance
        if stats['market_dominance']:
            st.markdown("### 🏆 Market Dominance")
            dom_cols = st.columns(len(stats['market_dominance']))
            for idx, (symbol, percentage) in enumerate(stats['market_dominance'].items()):
                with dom_cols[idx]:
                    st.markdown(f"""
                    <div class="trading-card" style="text-align: center;">
                        <h3>{symbol}</h3>
                        <h2>{percentage:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Top Coins
        st.markdown("### 🔥 Top 10 Cryptocurrencies")
        top_10 = df.nlargest(10, 'market_cap')[['name', 'symbol', 'current_price', 'price_change_24h', 'market_cap']]
        
        cols = st.columns(5)
        for idx, (_, coin) in enumerate(top_10.head(5).iterrows()):
            with cols[idx]:
                change_class = "positive" if coin['price_change_24h'] >= 0 else "negative"
                st.markdown(f"""
                <div class="trading-card">
                    <h4>{coin['name']}</h4>
                    <p style="color: #718096;">{coin['symbol']}</p>
                    <h3>${coin['current_price']:,.2f}</h3>
                    <p class="{change_class}">{coin['price_change_24h']:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Main Chart
        st.markdown("### 📈 Advanced Charting")
        
        coin_options = [f"{row['name']} ({row['symbol']})" for _, row in df.iterrows()]
        selected = st.selectbox("Select Cryptocurrency", coin_options, index=0)
        selected_coin = df[df['name'] == selected.split(' (')[0]].iloc[0]
        
        with st.spinner("Loading chart data..."):
            historical = self.api.get_historical_data(selected_coin['coin_id'], days)
            
            if historical is not None and len(historical) > 5:
                fig = self.create_chart(historical, selected_coin['name'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Coin metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Price", f"${selected_coin['current_price']:,.2f}")
                    with col2:
                        st.metric("24h Change", f"{selected_coin['price_change_24h']:+.2f}%")
                    with col3:
                        st.metric("Market Cap", f"${selected_coin['market_cap']:,.0f}")
                    with col4:
                        st.metric("Volume", f"${selected_coin['total_volume']:,.0f}")
                else:
                    st.warning("Could not generate chart")
            else:
                st.warning("Insufficient historical data")
        
        st.markdown("---")
        
        # Analysis Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Market Movers",
            "⚡ Volatility Analysis",
            "📈 Top Gainers/Losers",
            "📋 Complete Data"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🚀 Top 10 Gainers")
                gainers = self.analysis.get_top_gainers(df, 10)
                if not gainers.empty:
                    fig = px.bar(
                        gainers,
                        x='name',
                        y='price_change_24h',
                        color='price_change_24h',
                        color_continuous_scale='RdYlGn',
                        title="Top Gainers (24h)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📉 Top 10 Losers")
                losers = self.analysis.get_top_losers(df, 10)
                if not losers.empty:
                    fig = px.bar(
                        losers,
                        x='name',
                        y='price_change_24h',
                        color='price_change_24h',
                        color_continuous_scale='RdYlGn_r',
                        title="Top Losers (24h)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⚡ Most Volatile")
                volatile = self.analysis.get_most_volatile(df, 10)
                if not volatile.empty:
                    fig = px.bar(
                        volatile,
                        x='name',
                        y='volatility_score',
                        color='volatility_score',
                        title="Volatility Ranking"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🚨 Anomaly Detection")
                anomalies = self.analysis.detect_anomalies(df)
                if not anomalies.empty:
                    st.dataframe(anomalies, use_container_width=True)
                else:
                    st.info("No anomalies detected")
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Top by Market Cap")
                top_mcap = self.analysis.get_top_by_market_cap(df, 10)
                if not top_mcap.empty:
                    fig = px.bar(
                        top_mcap,
                        x='name',
                        y='market_cap',
                        color='market_cap',
                        title="Largest by Market Cap"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Volatility vs Price Change")
                vol_df = self.analysis.get_volatility_ranking(df, 20)
                if not vol_df.empty:
                    fig = px.scatter(
                        vol_df,
                        x='volatility_score',
                        y='price_change_24h',
                        size='current_price',
                        color='price_change_24h',
                        hover_name='name',
                        title="Volatility vs Price Change"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.markdown("#### 📋 Complete Market Data")
            
            display_df = df[[
                'name', 'symbol', 'current_price', 'price_change_24h',
                'market_cap', 'total_volume', 'volatility_score', 'market_cap_rank'
            ]].copy()
            
            # Format columns
            display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:,.2f}")
            display_df['price_change_24h'] = display_df['price_change_24h'].apply(lambda x: f"{x:+.2f}%")
            display_df['market_cap'] = display_df['market_cap'].apply(lambda x: f"${x:,.0f}")
            display_df['total_volume'] = display_df['total_volume'].apply(lambda x: f"${x:,.0f}")
            display_df['volatility_score'] = display_df['volatility_score'].apply(lambda x: f"{x:,.0f}")
            
            display_df.columns = [
                'Name', 'Symbol', 'Price', '24h %',
                'Market Cap', 'Volume', 'Volatility', 'Rank'
            ]
            
            st.dataframe(display_df, use_container_width=True, height=500)
            
            # Export
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"crypto_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #718096; padding: 2rem;">
            <p>🌿 CryptoVerde • Powered by CoinGecko API • Supabase • Streamlit</p>
            <p>© 2024 Professional Crypto Trading Platform • Hackathon Ready</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(Config.DASHBOARD_REFRESH_SECONDS)
            st.rerun()