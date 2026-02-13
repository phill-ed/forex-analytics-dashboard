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
    
    # ============================================
    # 🤖 AI Analysis Section
    # ============================================
    st.divider()
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 10px 0;'>
        <h2 style='color: white; margin: 0;'>🤖 AI Analysis</h2>
        <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0;'>AI-powered insights and predictions (EDUCATIONAL ONLY)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🤖 View AI Analysis", expanded=True):
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            st.subheader("🎯 AI Trend Prediction")
            ai_pair = st.selectbox(
                "Select pair for AI analysis:",
                st.session_state.selected_pairs or ['EUR/USD'],
                key='ai_pair_select'
            )
            
            if st.button("🔮 Generate AI Analysis", key='ai_analyze_btn'):
                with st.spinner("Analyzing market data..."):
                    # Get data for AI analysis
                    ai_chart_data = st.session_state.forex_api.get_historical_data(
                        ai_pair,
                        timeframe=timeframe,
                        periods=100
                    )
                    
                    if ai_chart_data is not None and not ai_chart_data.empty:
                        closes = ai_chart_data['close'].values
                        highs = ai_chart_data['high'].values
                        lows = ai_chart_data['low'].values
                        
                        # Get news headlines
                        news_headlines = [n.get('title', '') for n in news[:10]]
                        
                        # Run AI analysis
                        ai_result = st.session_state.ai_analyzer.comprehensive_analysis(
                            prices=closes,
                            pair=ai_pair,
                            news_headlines=news_headlines,
                            high_price=highs,
                            low_price=lows
                        )
                        
                        # Display results
                        trend_colors = {
                            'bullish': '🟢',
                            'bearish': '🔴',
                            'neutral': '🟡'
                        }
                        
                        st.markdown(f"""
                        ### 📊 AI Analysis Results for {ai_pair}
                        
                        | Metric | Value |
                        |--------|-------|
                        | **Trend Prediction** | {trend_colors.get(ai_result.trend_prediction, '⚪')} {ai_result.trend_prediction.upper()} |
                        | **Confidence** | {ai_result.confidence:.0f}% |
                        | **Risk Level** | {ai_result.risk_level.upper()} |
                        | **Pattern** | {ai_result.pattern_detected or 'None detected'} |
                        """, unsafe_allow_html=True)
                        
                        # Support & Resistance
                        st.subheader("📊 Key Levels")
                        sr_col1, sr_col2 = st.columns(2)
                        
                        with sr_col1:
                            st.markdown("**🛡️ Support Levels**")
                            for i, level in enumerate(ai_result.support_levels):
                                st.write(f"  S{i+1}: {level:.5f}")
                        
                        with sr_col2:
                            st.markdown("**📈 Resistance Levels**")
                            for i, level in enumerate(ai_result.resistance_levels):
                                st.write(f"  R{i+1}: {level:.5f}")
                        
                        # Key Factors
                        st.subheader("📋 Key Factors")
                        for factor in ai_result.key_factors:
                            st.write(f"- {factor}")
                        
                        # Insights
                        st.subheader("💡 AI Insights")
                        for insight in ai_result.insights:
                            st.write(f"- {insight}")
                        
                        # Disclaimer
                        st.warning("""
                        ⚠️ **IMPORTANT DISCLAIMER**
                        
                        This AI analysis is provided for **educational and informational purposes only**.
                        
                        - ❌ NOT financial advice
                        - ❌ NOT a buy/sell recommendation
                        - ❌ Cannot predict future prices
                        - ⚠️ Always do your own research
                        - ⚠️ Always use proper risk management
                        - ⚠️ Consider consulting licensed financial advisors
                        
                        Past performance and AI predictions do not guarantee future results.
                        """)
                        
                        # Recommendation
                        st.markdown("---")
                        st.markdown(f"**🎓 Educational Observation:**\n\n{ai_result.recommendation}")
        
        with ai_col2:
            st.subheader("🔮 Price Forecast")
            
            if st.button("📈 Generate Forecast", key='forecast_btn'):
                with st.spinner("Calculating forecasts..."):
                    forecast_data = st.session_state.ai_forecast.forecast(
                        closes,
                        periods=7
                    )
                    
                    if 'error' not in forecast_data:
                        st.markdown(f"""
                        ### 📊 {forecast_data['periods']}-Day Price Forecast
                        
                        **Current Price:** {forecast_data['current_price']}
                        
                        | Scenario | Price | Change |
                        |----------|-------|--------|
                        | 🟢 Bullish | {forecast_data['forecasts']['bullish']} | +{((forecast_data['forecasts']['bullish']/forecast_data['current_price'])-1)*100:.2f}% |
                        | 🟡 Expected | {forecast_data['forecasts']['expected']} | {((forecast_data['forecasts']['expected']/forecast_data['current_price'])-1)*100:.2f}% |
                        | 🔴 Bearish | {forecast_data['forecasts']['bearish']} | {((forecast_data['forecasts']['bearish']/forecast_data['current_price'])-1)*100:.2f}% |
                        
                        **Expected Change:** {forecast_data['expected_change_pct']}%  
                        **Volatility Index:** {forecast_data['volatility_index']}
                        """, unsafe_allow_html=True)
                        
                        st.warning(f"⚠️ {forecast_data['disclaimer']}")
                    else:
                        st.error(forecast_data['error'])
            
            # Backtest Section
            st.markdown("---")
            st.subheader("📉 Strategy Backtest")
            
            with st.form("backtest_form"):
                short_ma = st.number_input("Short MA Period", value=5, min_value=2, max_value=50)
                long_ma = st.number_input("Long MA Period", value=20, min_value=5, max_value=200)
                
                if st.form_submit_button("Run Backtest"):
                    with st.spinner("Running backtest..."):
                        bt_result = st.session_state.ai_forecast.backtest_signal(
                            closes,
                            short_period=short_ma,
                            long_period=long_ma
                        )
                        
                        if 'error' not in bt_result:
                            st.markdown(f"""
                            ### 📊 Backtest Results
                            
                            | Metric | Value |
                            |--------|-------|
                            | Total Signals | {bt_result['total_signals']} |
                            | Buy Signals | {bt_result['buy_signals']} |
                            | Sell Signals | {bt_result['sell_signals']} |
                            | Hold Signals | {bt_result['hold_signals']} |
                            
                            **Strategy:** MA Crossover ({short_ma}/{long_ma})
                            """, unsafe_allow_html=True)
                            
                            st.info(f"ℹ️ {bt_result['disclaimer']}")
    
    # ============================================
    # 🛠️ Trading Tools Section
    # ============================================
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
