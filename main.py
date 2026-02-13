"""
Forex Analytics Dashboard
Main Application Entry Point - Enhanced Version
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List, Optional

# Import our modules
from src.data.forex_api import ForexAPI
from src.data.news_api import NewsAPI
from src.analysis.indicators import TechnicalIndicators
from src.analysis.ai_analysis import AIAnalyzer, AIForecast
from src.ui.charts import ChartBuilder
from src.ui.components import UIComponents

# Page configuration
st.set_page_config(
    page_title="📈 Forex Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💹"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Rate cards */
    .rate-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .rate-card-bullish {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .rate-card-bearish {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Signal badges */
    .signal-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .signal-sell {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .signal-hold {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: #333;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Analysis section */
    .analysis-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
    }
    
    /* News cards */
    .news-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 8px 0;
        border-left: 4px solid #667eea;
    }
    
    /* Tab styling */
    .stTabs {
        background: white;
        border-radius: 12px;
        padding: 10px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)


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
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0


def main():
    """Main application function"""
    
    # Header
    col_header1, col_header2, col_header3 = st.columns([3, 1, 1])
    
    with col_header1:
        st.markdown('<div class="main-header">📈 Forex Analytics Dashboard</div>', unsafe_allow_html=True)
        st.markdown(f"<small style='color: #666;'>🕐 Last updated: {datetime.now().strftime('%H:%M:%S')}</small>", unsafe_allow_html=True)
    
    with col_header2:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, key="auto_refresh")
    
    with col_header3:
        # Refresh button
        if st.button("↻ Refresh", type="secondary"):
            st.session_state.refresh_trigger += 1
            st.rerun()
    
    st.divider()
    
    # ============================================
    # SIDEBAR - Settings & Pair Selection
    # ============================================
    with st.sidebar:
        st.header("⚙️ Analysis Settings")
        
        st.subheader("🎯 Currency Pair Selection")
        
        # All available pairs
        all_pairs = {
            'Major Pairs': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD'],
            'Cross Pairs': ['EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'EUR/AUD', 'AUD/JPY', 'CAD/JPY', 'EUR/CAD', 'EUR/CHF'],
            'Asia-Pacific': ['USD/IDR', 'USD/SGD', 'USD/HKD', 'AUD/NZD', 'USD/MXN'],
            'Commodity': ['USD/CNY', 'EUR/AUD', 'AUD/CAD', 'EUR/CAD']
        }
        
        # Category selector
        selected_category = st.selectbox("📁 Select Category", list(all_pairs.keys()))
        
        # Pair dropdown based on category
        pairs_in_category = all_pairs[selected_category]
        selected_pair = st.selectbox("💱 Select Pair", pairs_in_category, key="selected_pair")
        
        # Quick pairs (favorites)
        st.subheader("⭐ Quick Pairs")
        quick_pairs = st.multiselect(
            "Watchlist:",
            [p for cats in all_pairs.values() for p in cats if p != selected_pair],
            default=['EUR/USD', 'USD/JPY', 'GBP/USD']
        )
        
        st.divider()
        
        # Timeframe selector
        st.subheader("📊 Timeframe")
        timeframe = st.selectbox(
            "Chart Period:",
            ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'],
            index=4,
            key="timeframe"
        )
        
        # Analysis settings
        st.subheader("🧠 AI Analysis")
        show_ai = st.toggle("Enable AI Analysis", value=True)
        show_patterns = st.toggle("Show Patterns", value=True)
        show_forecast = st.toggle("Price Forecast", value=True)
        
        st.divider()
        
        # Indicator settings
        st.subheader("📈 Indicators")
        selected_indicators = st.multiselect(
            "Add Indicators:",
            ['SMA 20', 'SMA 50', 'EMA 12', 'EMA 26', 'RSI', 'MACD', 'Bollinger Bands', 'Fibonacci']
        )
        
        # Risk disclaimer
        st.warning("""
        ⚠️ **Disclaimer**
        
        This dashboard is for **educational purposes only**.
        
        It does NOT provide financial advice.
        
        Always do your own research (DYOR).
        """)
    
    # ============================================
    # MAIN CONTENT AREA
    # ============================================
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🧠 AI Analysis", 
        "📰 News",
        "🛠️ Tools",
        "📈 Portfolio"
    ])
    
    # ------------------------------------------
    # TAB 1: MAIN DASHBOARD
    # ------------------------------------------
    with tab1:
        # Live rates section
        st.subheader("💹 Live Rates")
        
        # Get live rates for selected and quick pairs
        display_pairs = [selected_pair] + quick_pairs
        rates_data = st.session_state.forex_api.get_multi_rates(display_pairs)
        
        # Display rate cards
        rate_cols = st.columns(len(display_pairs))
        
        for idx, pair in enumerate(display_pairs):
            if pair in rates_data:
                data = rates_data[pair]
                change = data.get('change_pct', 0)
                with rate_cols[idx % 4]:
                    UIComponents.render_rate_card(
                        pair=pair,
                        bid=data['bid'],
                        ask=data['ask'],
                        change=change,
                        high=data.get('high', 0),
                        low=data.get('low', 0)
                    )
            else:
                with rate_cols[idx % 4]:
                    UIComponents.render_rate_card(
                        pair=pair,
                        bid=1.0000,
                        ask=1.0001,
                        change=0
                    )
        
        st.divider()
        
        # Chart section
        col_chart1, col_chart2 = st.columns([3, 1])
        
        with col_chart1:
            # Get historical data for selected pair
            chart_data = st.session_state.forex_api.get_historical_data(
                selected_pair,
                timeframe=timeframe,
                periods=100
            )
            
            if chart_data is not None and not chart_data.empty:
                # Prepare indicators
                indicators_data = {}
                closes = chart_data['close'].values
                
                # Calculate selected indicators
                if 'SMA 20' in selected_indicators:
                    indicators_data['SMA 20'] = st.session_state.indicators.sma(closes, 20)
                if 'SMA 50' in selected_indicators:
                    indicators_data['SMA 50'] = st.session_state.indicators.sma(closes, 50)
                if 'EMA 12' in selected_indicators:
                    indicators_data['EMA 12'] = st.session_state.indicators.ema(closes, 12)
                if 'EMA 26' in selected_indicators:
                    indicators_data['EMA 26'] = st.session_state.indicators.ema(closes, 26)
                if 'RSI' in selected_indicators:
                    indicators_data['RSI'] = st.session_state.indicators.rsi(closes, 14)
                if 'Bollinger Bands' in selected_indicators:
                    upper, middle, lower = st.session_state.indicators.bollinger_bands(closes)
                    indicators_data['BB Upper'] = upper
                    indicators_data['BB Middle'] = middle
                    indicators_data['BB Lower'] = lower
                
                # Render chart
                fig = ChartBuilder.render_candlestick_chart(
                    chart_data,
                    indicators=indicators_data,
                    title=f"📈 {selected_pair} - {timeframe} Chart"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Chart data unavailable. Showing sample data.")
                # Generate sample data for display
                sample_data = st.session_state.forex_api._generate_sample_data(selected_pair, 50)
                fig = ChartBuilder.render_candlestick_chart(
                    sample_data,
                    title=f"📈 {selected_pair} - Sample Data"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            # Quick analysis panel
            st.subheader("📊 Quick Analysis")
            
            if chart_data is not None and not chart_data.empty:
                closes = chart_data['close'].values
                analysis = st.session_state.indicators.analyze(closes)
                
                # Trend indicator
                trend_colors = {'bullish': '🟢', 'bearish': '🔴', 'neutral': '🟡'}
                trend_emoji = trend_colors.get(analysis.trend.value, '⚪')
                
                st.markdown(f"""
                <div class="analysis-section">
                    <h3>{trend_emoji} Trend</h3>
                    <p style="font-size: 1.5rem; font-weight: bold;">{analysis.trend.value.upper()}</p>
                    <hr style="border-color: rgba(255,255,255,0.3);">
                    <p><strong>Signal:</strong> <span class="signal-{analysis.signal.value}">{analysis.signal.value.upper()}</span></p>
                    <p><strong>Confidence:</strong> {analysis.confidence:.0f}%</p>
                    <p><strong>RSI:</strong> {analysis.indicators.get('rsi', 50):.1f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Pivot points
                if 'high' in chart_data.columns:
                    pivots = st.session_state.indicators.pivot_points(
                        chart_data['high'].values,
                        chart_data['low'].values,
                        chart_data['close'].values
                    )
                    
                    st.markdown("### 📐 Pivot Points")
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.metric("R1", f"{pivots.get('R1', 0):.5f}")
                        st.metric("PP", f"{pivots.get('PP', 0):.5f}")
                    with col_p2:
                        st.metric("S1", f"{pivots.get('S1', 0):.5f}")
                        st.metric("Spread", f"{(pivots.get('R1', 0) - pivots.get('S1', 0)):.5f}")
            else:
                st.info("Analysis unavailable")
    
    # ------------------------------------------
    # TAB 2: AI ANALYSIS
    # ------------------------------------------
    with tab2:
        if show_ai:
            col_ai1, col_ai2 = st.columns([2, 1])
            
            with col_ai1:
                st.subheader("🧠 AI-Powered Analysis")
                
                if chart_data is not None and not chart_data.empty:
                    closes = chart_data['close'].values
                    
                    # Perform AI analysis
                    ai_result = st.session_state.ai_analyzer.comprehensive_analysis(
                        prices=closes,
                        pair=selected_pair,
                        news_headlines=[]
                    )
                    
                    # Display AI insights
                    st.markdown(f"""
                    <div class="analysis-section">
                        <h2>📊 AI Analysis for {selected_pair}</h2>
                        <div style="display: flex; gap: 20px; margin-top: 20px;">
                            <div style="flex: 1;">
                                <h4>Trend Prediction</h4>
                                <p style="font-size: 2rem; font-weight: bold;">
                                    {ai_result.trend_prediction.upper()}
                                </p>
                                <p>Confidence: {ai_result.confidence:.0f}%</p>
                            </div>
                            <div style="flex: 1;">
                                <h4>Risk Level</h4>
                                <p style="font-size: 1.5rem;">
                                    {'🔴 HIGH' if ai_result.risk_level == 'high' else '🟡 MEDIUM' if ai_result.risk_level == 'medium' else '🟢 LOW'}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Support & Resistance
                    st.subheader("📊 Support & Resistance")
                    
                    sr_col1, sr_col2 = st.columns(2)
                    
                    with sr_col1:
                        st.markdown("**🟢 Resistance Levels**")
                        for idx, level in enumerate(ai_result.resistance_levels[:3]):
                            st.code(f"R{idx+1}: {level:.5f}")
                    
                    with sr_col2:
                        st.markdown("**🔴 Support Levels**")
                        for idx, level in enumerate(ai_result.support_levels[:3]):
                            st.code(f"S{idx+1}: {level:.5f}")
                    
                    # Key factors
                    st.subheader("🔑 Key Factors")
                    for factor in ai_result.key_factors:
                        st.markdown(f"- {factor}")
                    
                    # Insights
                    st.subheader("💡 AI Insights")
                    for insight in ai_result.insights:
                        st.markdown(f"- {insight}")
                    
                    # Educational recommendation
                    st.info(ai_result.recommendation)
                    
                    # Price forecast
                    if show_forecast:
                        st.divider()
                        st.subheader("🔮 Price Forecast (Educational)")
                        
                        forecast = st.session_state.ai_forecast.forecast(closes, periods=7)
                        
                        if 'error' not in forecast:
                            fc_col1, fc_col2, fc_col3 = st.columns(3)
                            
                            with fc_col1:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                            padding: 20px; border-radius: 12px; color: white; text-align: center;">
                                    <h4>🐂 Bullish</h4>
                                    <p style="font-size: 1.5rem; font-weight: bold;">{:.5f}</p>
                                    <p>+{:.1f}%</p>
                                </div>
                                """.format(forecast['forecasts']['bullish'], 
                                           forecast['forecasts']['bullish'] / forecast['current_price'] * 100 - 100),
                                unsafe_allow_html=True)
                            
                            with fc_col2:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                            padding: 20px; border-radius: 12px; color: white; text-align: center;">
                                    <h4>📊 Expected</h4>
                                    <p style="font-size: 1.5rem; font-weight: bold;">{:.5f}</p>
                                    <p>{:+.1f}%</p>
                                </div>
                                """.format(forecast['forecasts']['expected'],
                                           forecast['forecasts']['expected'] / forecast['current_price'] * 100 - 100),
                                unsafe_allow_html=True)
                            
                            with fc_col3:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); 
                                            padding: 20px; border-radius: 12px; color: white; text-align: center;">
                                    <h4>🐻 Bearish</h4>
                                    <p style="font-size: 1.5rem; font-weight: bold;">{:.5f}</p>
                                    <p>{:.1f}%</p>
                                </div>
                                """.format(forecast['forecasts']['bearish'],
                                           forecast['forecasts']['bearish'] / forecast['current_price'] * 100 - 100),
                                unsafe_allow_html=True)
                            
                            st.caption(f"""
                            **{forecast['disclaimer']}**
                            Volatility Index: {forecast.get('volatility_index', 0)}%
                            """)
                        else:
                            st.warning(forecast.get('error', 'Forecast unavailable'))
                else:
                    st.info("Chart data required for AI analysis")
            
            with col_ai2:
                # Pattern recognition
                if show_patterns and chart_data is not None and not chart_data.empty:
                    closes = chart_data['close'].values
                    patterns = st.session_state.ai_analyzer.pattern_recognizer.find_patterns(closes)
                    
                    st.subheader("📐 Pattern Detection")
                    
                    if patterns:
                        for pattern in patterns:
                            st.markdown(f"""
                            <div class="news-card" style="border-left-color: #764ba2;">
                                <strong>{pattern['pattern'].replace('_', ' ').title()}</strong>
                                <br>
                                <small>{pattern['description']}</small>
                                <br>
                                <span style="color: #667eea;">Confidence: {pattern['confidence']:.0f}%</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No patterns detected")
                
                # Sentiment
                st.divider()
                st.subheader("😊 Market Sentiment")
                
                sentiment_data = st.session_state.news_api.get_market_sentiment()
                
                sentiment_col1, sentiment_col2 = st.columns(2)
                
                with sentiment_col1:
                    st.metric("Fear/Greed", f"{sentiment_data.get('fear_greed_index', 55)}/100")
                
                with sentiment_col2:
                    st.metric("Sentiment", sentiment_data.get('sentiment_label', 'Neutral'))
                
                # Positions
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <div style="flex: 1; background: #e8f5e9; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong style="color: #2e7d32;">Long: {sentiment_data.get('long_positions', 52)}%</strong>
                    </div>
                    <div style="flex: 1; background: #ffebee; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong style="color: #c62828;">Short: {sentiment_data.get('short_positions', 48)}%</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Enable AI Analysis in sidebar to view")
    
    # ------------------------------------------
    # TAB 3: NEWS
    # ------------------------------------------
    with tab3:
        col_news1, col_news2 = st.columns([2, 1])
        
        with col_news1:
            st.subheader("📰 Latest Forex News")
            
            # Get latest news
            news = st.session_state.news_api.get_latest_forex_news(max_items=15)
            
            for idx, item in enumerate(news):
                sentiment_icon = '🟢' if item.get('sentiment') == 'Bullish' else ('🔴' if item.get('sentiment') == 'Bearish' else '🟡')
                
                with st.expander(f"{sentiment_icon} {item.get('title', 'No title')[:80]}...", expanded=idx < 5):
                    st.markdown(f"""
                    **{item.get('title', '')}**  
                    Source: {item.get('source', 'Unknown')} | Sentiment: {sentiment_icon} {item.get('sentiment', 'Neutral')}
                    
                    {item.get('summary', 'No summary available')}...
                    
                    [Read More →]({item.get('link', '#')})
                    """)
        
        with col_news2:
            st.subheader("📅 Economic Calendar")
            
            events = st.session_state.news_api.get_economic_calendar(days=7)
            
            # Group by date
            events_by_date = {}
            for event in events:
                date = event.get('date', 'Unknown')
                if date not in events_by_date:
                    events_by_date[date] = []
                events_by_date[date].append(event)
            
            for date, day_events in sorted(list(events_by_date.items())[:5]):
                with st.expander(f"📅 {date}", expanded=False):
                    for event in day_events[:3]:
                        impact_icon = event.get('indicator', '⚪')
                        st.markdown(f"""
                        <div class="news-card">
                            <strong>{impact_icon} {event.get('event', 'Event')}</strong>
                            <br>
                            <small>{event.get('currency', '')} | {event.get('time', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
    
    # ------------------------------------------
    # TAB 4: TRADING TOOLS
    # ------------------------------------------
    with tab4:
        col_tools1, col_tools2 = st.columns(2)
        
        with col_tools1:
            # Position Size Calculator
            st.subheader("🧮 Position Size Calculator")
            
            with st.form("position_calculator"):
                tool_col1, tool_col2 = st.columns(2)
                
                with tool_col1:
                    account_balance = st.number_input("Account Balance ($)", value=10000, step=1000)
                    risk_percent = st.slider("Risk (%)", 0.5, 5.0, 1.0, 0.1)
                
                with tool_col2:
                    stop_loss = st.number_input("Stop Loss (pips)", value=20, step=5)
                    pair = st.selectbox("Pair", display_pairs)
                
                submitted = st.form_submit_button("Calculate", type="primary")
                
                if submitted:
                    risk_amount = account_balance * (risk_percent / 100)
                    
                    # Simplified pip value calculation
                    pip_value = 0.01 if 'JPY' in pair else 0.0001
                    position_size = risk_amount / (stop_loss * pip_value * 100000)
                    
                    st.success(f"""
                    **Results:**
                    - Risk Amount: ${risk_amount:.2f}
                    - Position Size: {position_size:.2f} lots
                    - Units: {int(position_size * 100000):,}
                    """)
        
        with col_tools2:
            # Risk/Reward Calculator
            st.subheader("⚖️ Risk/Reward Calculator")
            
            with st.form("rr_calculator"):
                rr_col1, rr_col2 = st.columns(2)
                
                with rr_col1:
                    entry_price = st.number_input("Entry Price", value=1.0850, format="%.5f")
                    stop_loss = st.number_input("Stop Loss", value=1.0800, format="%.5f")
                
                with rr_col2:
                    take_profit = st.number_input("Take Profit", value=1.0950, format="%.5f")
                
                submitted = st.form_submit_button("Calculate R/R")
                
                if submitted:
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                    rr_ratio = reward / risk if risk > 0 else 0
                    
                    st.markdown(f"""
                    **Analysis:**
                    - Risk: {risk:.5f} ({risk * 10000:.1f} pips)
                    - Reward: {reward:.5f} ({reward * 10000:.1f} pips)
                    - **R/R Ratio: {rr_ratio:.2f}**
                    
                    {'✅ Good risk/reward ratio' if rr_ratio >= 2 else '⚠️ Consider 2:1 or better'}
                    """)
        
        # More tools
        st.divider()
        
        col_tools3, col_tools4 = st.columns(2)
        
        with col_tools3:
            # Pip Value Calculator
            st.subheader("💰 Pip Value Calculator")
            
            pip_pair = st.selectbox("Select Pair", display_pairs, key="pip_pair")
            lot_size = st.number_input("Lot Size", value=1.0, step=0.1)
            
            pip_value = 10 if 'JPY' in pip_pair else 10
            if 'USD' not in pip_pair and 'JPY' not in pip_pair:
                pip_value = 10 / 1.0850
            
            st.info(f"**Pip Value: ${pip_value * lot_size:.2f}** per standard lot")
        
        with col_tools4:
            # Margin Calculator
            st.subheader("📊 Margin Calculator")
            
            margin_pair = st.selectbox("Select Pair", display_pairs, key="margin_pair")
            margin_lots = st.number_input("Lots", value=1.0, step=0.1, key="margin_lots")
            
            # Approximate margin requirement (1% for majors)
            margin_req = 1000 * margin_lots  # $1000 per lot approx
            
            st.info(f"**Estimated Margin: ${margin_req:,.0f}**")
    
    # ------------------------------------------
    # TAB 5: PORTFOLIO/WATCHLIST
    # ------------------------------------------
    with tab5:
        st.subheader("👀 Watchlist")
        
        # Add to watchlist
        watch_col1, watch_col2 = st.columns([3, 1])
        
        with watch_col1:
            new_pair = st.selectbox("Add Pair to Watchlist", [p for cats in all_pairs.values() for p in cats])
        
        with watch_col2:
            if st.button("➕ Add"):
                if new_pair not in quick_pairs:
                    st.session_state.quick_pairs = quick_pairs + [new_pair]
                    st.success(f"Added {new_pair}")
        
        # Watchlist table
        if quick_pairs:
            watch_data = st.session_state.forex_api.get_multi_rates(quick_pairs)
            
            # Create DataFrame for display
            watchlist_df = []
            for pair in quick_pairs:
                if pair in watch_data:
                    data = watch_data[pair]
                    watchlist_df.append({
                        'Pair': pair,
                        'Bid': data['bid'],
                        'Ask': data['ask'],
                        'Change %': data.get('change_pct', 0),
                        'Spread': round((data['ask'] - data['bid']) * 10000, 1)
                    })
            
            if watchlist_df:
                watchlist_df = pd.DataFrame(watchlist_df)
                
                # Color code changes
                def color_change(val):
                    color = 'green' if val >= 0 else 'red'
                    return f'color: {color}'
                
                st.dataframe(
                    watchlist_df.style.applymap(color_change, subset=['Change %']),
                    use_container_width=True
                )
            
            # Charts for watchlist
            st.subheader("📈 Watchlist Comparison")
            
            compare_pairs = st.multiselect(
                "Compare pairs:",
                quick_pairs,
                default=quick_pairs[:2]
            )
            
            if len(compare_pairs) >= 2:
                compare_data = {}
                for pair in compare_pairs:
                    hist_data = st.session_state.forex_api.get_historical_data(pair, '1d', 30)
                    if hist_data is not None and not hist_data.empty:
                        # Normalize to percentage change
                        normalized = (hist_data['close'] / hist_data['close'].iloc[0] - 1) * 100
                        compare_data[pair] = normalized
                
                if compare_data:
                    compare_df = pd.DataFrame(compare_data)
                    fig = ChartBuilder.render_line_chart(
                        {col: compare_df[col] for col in compare_df.columns},
                        title="Performance Comparison (30-Day % Change)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add pairs to your watchlist in the sidebar")
    
    # ============================================
    # FOOTER
    # ============================================
    st.divider()
    
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("""
        **📊 Data Sources:**
        - Frankfurter API
        - ExchangeRate-API
        - Forex Factory News
        """)
    
    with footer_col2:
        st.markdown("""
        **⚠️ Disclaimer:**
        This dashboard is for educational purposes only.
        Not financial advice. Trade responsibly.
        """)
    
    with footer_col3:
        st.markdown("""
        **🔗 Links:**
        - [GitHub](https://github.com/phill-ed/forex-analytics-dashboard)
        - [Issues](https://github.com/phill-ed/forex-analytics-dashboard/issues)
        """)


if __name__ == "__main__":
    main()
