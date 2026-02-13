"""
Forex Analytics Dashboard
Main Application Entry Point
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading

# Import our modules
from src.data.forex_api import ForexAPI
from src.data.news_api import NewsAPI
from src.analysis.indicators import TechnicalIndicators
from src.analysis.ai_analysis import AIAnalyzer, AIForecast
from src.ui.charts import ChartBuilder
from src.ui.components import UIComponents

# Page configuration
st.set_page_config(
    page_title="Forex Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'forex_api' not in st.session_state:
    st.session_state.forex_api = ForexAPI()
if 'news_api' not in st.session_state:
    st.session_state.news_api = NewsAPI()
if 'indicators' not in st.session_state:
    st.session_state.indicators = TechnicalIndicators()
if 'ai_analyzer' not in st.session_state:
    st.session_state.ai_analyzer = AIAnalyzer()
if 'ai_forecast' not in st.session_state:
    st.session_state.ai_forecast = AIForecast()
if 'selected_pairs' not in st.session_state:
    st.session_state.selected_pairs = ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/IDR']

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
    .price-up {
        color: #00C853;
    }
    .price-down {
        color: #D50000;
    }
    .stAlert {
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="main-header">📈 Forex Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar - Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Currency Pairs")
        all_pairs = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD',
            'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'USD/IDR', 'USD/SGD',
            'EUR/AUD', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'AUD/CAD',
            'EUR/CHF', 'GBP/CHF', 'AUD/NZD', 'EUR/NZD', 'USD/HKD', 'USD/MXN'
        ]
        
        selected = st.multiselect(
            "Select pairs to monitor:",
            all_pairs,
            default=st.session_state.selected_pairs
        )
        st.session_state.selected_pairs = selected
        
        st.divider()
        
        st.subheader("Timeframes")
        timeframe = st.selectbox(
            "Chart Timeframe:",
            ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        )
        
        st.subheader("Analysis Settings")
        show_indicators = st.multiselect(
            "Show Indicators:",
            ['SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands', 'Fibonacci']
        )
        
        st.divider()
        
        st.subheader("Data Refresh")
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 10)
    
    # Main content area
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("📊 Live Rates")
    
    with col2:
        st.subheader("📈 Market Overview")
    
    with col3:
        st.subheader("🔔 Alerts")
    
    # Get live rates
    if st.session_state.selected_pairs:
        rates_data = st.session_state.forex_api.get_multi_rates(
            st.session_state.selected_pairs
        )
        
        if rates_data:
            # Display rate cards
            cols = st.columns(len(rates_data))
            for idx, (pair, data) in enumerate(rates_data.items()):
                with cols[idx % 4]:
                    UIComponents.render_rate_card(
                        pair=pair,
                        bid=data['bid'],
                        ask=data['ask'],
                        change=data.get('change_pct', 0),
                        high=data.get('high', 0),
                        low=data.get('low', 0)
                    )
        else:
            st.warning("Unable to fetch live rates. Using sample data.")
            UIComponents.render_sample_rates(st.session_state.selected_pairs)
    
    # Charts section
    st.divider()
    st.subheader("📈 Price Charts")
    
    selected_pair = st.selectbox(
        "Select pair for analysis:",
        st.session_state.selected_pairs or ['EUR/USD']
    )
    
    # Get historical data for chart
    chart_data = st.session_state.forex_api.get_historical_data(
        selected_pair,
        timeframe=timeframe,
        periods=100
    )
    
    if chart_data is not None and not chart_data.empty:
        # Calculate indicators
        closes = chart_data['close'].values
        
        indicators_data = {}
        if 'SMA' in show_indicators:
            indicators_data['SMA 20'] = st.session_state.indicators.sma(closes, 20)
            indicators_data['SMA 50'] = st.session_state.indicators.sma(closes, 50)
        
        if 'EMA' in show_indicators:
            indicators_data['EMA 12'] = st.session_state.indicators.ema(closes, 12)
            indicators_data['EMA 26'] = st.session_state.indicators.ema(closes, 26)
        
        if 'RSI' in show_indicators:
            indicators_data['RSI'] = st.session_state.indicators.rsi(closes, 14)
        
        # Render chart
        ChartBuilder.render_candlestick_chart(
            chart_data,
            indicators=indicators_data,
            title=f"{selected_pair} - {timeframe} Chart"
        )
        
        # Technical analysis summary
        analysis = st.session_state.indicators.analyze(closes)
        UIComponents.render_analysis_summary(analysis)
    
    # News section
    st.divider()
    st.subheader("📰 Forex News")
    
    with st.expander("View Economic Calendar", expanded=False):
        economic_events = st.session_state.news_api.get_economic_calendar()
        if economic_events:
            UIComponents.render_economic_calendar(economic_events)
        else:
            st.info("No major economic events today")
    
    # Latest news
    news = st.session_state.news_api.get_latest_forex_news()
    if news:
        UIComponents.render_news_feed(news, max_items=10)
    else:
        st.info("No latest news available")
    
    # Trading tools section
    st.divider()
    st.subheader("🛠️ Trading Tools")
    
    tool_col1, tool_col2, tool_col3 = st.columns(3)
    
    with tool_col1:
        UIComponents.render_calculator_card()
    
    with tool_col2:
        UIComponents.render_pivot_points_card(chart_data if 'chart_data' in locals() else None)
    
    with tool_col3:
        st.info("💡 **Tip:** Always use stop-loss orders and manage your risk!")
    
    # Footer
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: #666;'>
            📈 Forex Analytics Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            <br><small>Data provided for educational purposes only. Not financial advice.</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
