"""
UI Components Module
Reusable UI components for the dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional


class UIComponents:
    """
    Reusable UI components for the forex dashboard
    """
    
    @staticmethod
    def render_rate_card(
        pair: str,
        bid: float,
        ask: float,
        change: float = 0,
        high: float = 0,
        low: float = 0
    ) -> None:
        """
        Render a currency rate card
        
        Args:
            pair: Currency pair name
            bid: Bid price
            ask: Ask price
            change: Daily change percentage
            high: Daily high
            low: Daily low
        """
        spread = ask - bid
        spread_pct = (spread / ask) * 10000  # In pips
        
        # Color based on change
        change_color = "green" if change >= 0 else "red"
        change_icon = "▲" if change >= 0 else "▼"
        
        # Format price based on pair
        if 'JPY' in pair:
            price_fmt = "{:.2f}"
            pip_fmt = "{:.2f}"
        else:
            price_fmt = "{:.5f}"
            pip_fmt = "{:.5f}"
        
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%); border-radius: 15px; color: white;">
            <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 8px;">
                {pair}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div>
                    <div style="font-size: 0.75rem; opacity: 0.8;">BID</div>
                    <div style="font-size: 1.4rem; font-weight: bold;">{price_fmt.format(bid)}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.75rem; opacity: 0.8;">ASK</div>
                    <div style="font-size: 1.4rem; font-weight: bold;">{price_fmt.format(ask)}</div>
                </div>
            </div>
            <div style="margin-top: 8px; display: flex; justify-content: space-between; font-size: 0.8rem;">
                <span class="{change_color}">{change_icon} {abs(change):.2f}%</span>
                <span>Spread: {pip_fmt.format(spread_pct)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sample_rates(pairs: List[str]) -> None:
        """Render sample rate cards when live data unavailable"""
        import random
        
        sample_rates = {
            'EUR/USD': (1.0845, 1.0855),
            'GBP/USD': (1.2640, 1.2650),
            'USD/JPY': (150.25, 150.35),
            'USD/CHF': (0.8840, 0.8850),
            'AUD/USD': (0.6510, 0.6520),
            'USD/CAD': (1.3640, 1.3650),
            'USD/IDR': (15580, 15600),
            'USD/SGD': (1.3440, 1.3450),
        }
        
        for pair in pairs:
            bid, ask = sample_rates.get(pair, (1.0000, 1.0001))
            change = random.uniform(-0.5, 0.5)
            UIComponents.render_rate_card(pair, bid, ask, change)
    
    @staticmethod
    def render_analysis_summary(analysis) -> None:
        """Render technical analysis summary"""
        if not analysis:
            return
        
        trend_colors = {
            'bullish': '🟢',
            'bearish': '🔴',
            'neutral': '🟡'
        }
        
        signal_colors = {
            'buy': 'green',
            'sell': 'red',
            'hold': 'yellow',
            'neutral': 'gray'
        }
        
        st.markdown(f"""
        ### 📊 Technical Analysis Summary
        
        | Metric | Value |
        |---------|-------|
        | **Trend** | {trend_colors.get(analysis.trend.value, '⚪')} {analysis.trend.value.upper()} |
        | **Signal** | <span style="color: {signal_colors.get(analysis.signal.value, 'gray')}">{analysis.signal.value.upper()}</span> |
        | **Confidence** | {analysis.confidence:.0f}% |
        | **RSI** | {analysis.indicators.get('rsi', 'N/A'):.1f} ({analysis.indicators.get('rsi_signal', 'N/A')}) |
        
        **{analysis.summary}**
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_news_feed(news: List[Dict], max_items: int = 10) -> None:
        """Render a news feed"""
        sentiment_icons = {
            'Bullish': '🟢',
            'Bearish': '🔴',
            'Neutral': '🟡'
        }
        
        for idx, item in enumerate(news[:max_items]):
            sentiment = item.get('sentiment', 'Neutral')
            icon = sentiment_icons.get(sentiment, '⚪')
            
            with st.expander(f"{icon} {item.get('title', 'No title')[:80]}...", expanded=idx < 3):
                st.markdown(f"""
                **Source:** {item.get('source', 'Unknown')}  
                **Sentiment:** {icon} {sentiment}  
                **Summary:** {item.get('summary', 'No summary')}  
                [Read more]({item.get('link', '#')})
                """)
    
    @staticmethod
    def render_economic_calendar(events: List[Dict]) -> None:
        """Render economic calendar"""
        impact_colors = {
            'HIGH': ('🔴', '#FFCDD2'),
            'MEDIUM': ('🟡', '#FFF9C4'),
            'LOW': ('🟢', '#C8E6C9')
        }
        
        # Group by date
        events_by_date = {}
        for event in events:
            date = event.get('date', 'Unknown')
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)
        
        for date, day_events in sorted(events_by_date.items()):
            st.subheader(f"📅 {date}")
            
            for event in day_events:
                impact, bg_color = impact_colors.get(
                    event.get('impact', 'LOW'),
                    ('⚪', '#F5F5F5')
                )
                
                st.markdown(f"""
                <div style="background: {bg_color}; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{impact} {event.get('event', 'Event')}</strong>
                        <span>{event.get('currency', '')}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #666;">
                        ⏰ {event.get('time', '')} | Forecast: {event.get('forecast', '')} | Previous: {event.get('previous', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_calculator_card() -> None:
        """Render trading calculator card"""
        with st.expander("🧮 Position Size Calculator", expanded=True):
            st.markdown("**Calculate your position size**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                account_balance = st.number_input("Account Balance ($)", value=10000, step=1000)
                risk_percent = st.slider("Risk (%)", 0.5, 5.0, 1.0, 0.1)
            
            with col2:
                stop_loss = st.number_input("Stop Loss (pips)", value=20, step=5)
                pair = st.selectbox("Currency Pair", ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/IDR'])
            
            # Calculate position size
            risk_amount = account_balance * (risk_percent / 100)
            
            # Pip value calculation (simplified)
            if 'JPY' in pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            position_size = risk_amount / (stop_loss * pip_value * 100000)  # Standard lots
            
            st.markdown(f"""
            **Results:**
            - Risk Amount: ${risk_amount:.2f}
            - Position Size: {position_size:.2f} lots
            - Units: {int(position_size * 100000):,}
            """)
    
    @staticmethod
    def render_pivot_points_card(df: Optional[pd.DataFrame] = None) -> None:
        """Render pivot points card"""
        with st.expander("📐 Pivot Points", expanded=True):
            st.markdown("**Daily Pivot Points**")
            
            if df is None or df.empty:
                # Show sample pivot points
                st.markdown("""
                | Level | Value |
                |-------|-------|
                | R4 | 1.0980 |
                | R3 | 1.0950 |
                | R2 | 1.0920 |
                | R1 | 1.0890 |
                | **PP** | **1.0860** |
                | S1 | 1.0830 |
                | S2 | 1.0800 |
                | S3 | 1.0770 |
                """)
            else:
                # Calculate from data
                high = df['high'].iloc[-1]
                low = df['low'].iloc[-1]
                close = df['close'].iloc[-1]
                
                pivot = (high + low + close) / 3
                r1 = 2 * pivot - low
                s1 = 2 * pivot - high
                r2 = pivot + (high - low)
                s2 = pivot - (high - low)
                
                st.markdown(f"""
                | Level | Value |
                |-------|-------|
                | R1 | {r1:.5f} |
                | **PP** | **{pivot:.5f}** |
                | S1 | {s1:.5f} |
                | R2 | {r2:.5f} |
                | S2 | {s2:.5f} |
                """)
    
    @staticmethod
    def render_market_overview(market_data: Dict) -> None:
        """Render market overview metrics"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Market Condition",
                market_data.get('market_condition', 'Normal').upper(),
                delta=None
            )
        
        with col2:
            trend = market_data.get('trend', 'mixed')
            st.metric(
                "Overall Trend",
                trend.upper(),
                delta=None
            )
        
        with col3:
            pairs_count = len(market_data.get('pairs', {}))
            st.metric("Active Pairs", pairs_count)
    
    @staticmethod
    def render_alert_section() -> None:
        """Render price alerts section"""
        st.subheader("🔔 Price Alerts")
        
        with st.form("add_alert"):
            col1, col2 = st.columns(2)
            
            with col1:
                pair = st.selectbox("Currency Pair", ['EUR/USD', 'GBP/USD', 'USD/JPY'])
                direction = st.selectbox("Direction", ['Above', 'Below'])
            
            with col2:
                price = st.number_input("Target Price", value=1.0000, format="%.5f")
                alert_type = st.selectbox("Notification", ['Push', 'Email', 'Sound'])
            
            if st.form_submit_button("Set Alert"):
                st.success(f"Alert set for {pair} when price goes {direction} {price}")
    
    @staticmethod
    def render_portfolio_summary(positions: List[Dict]) -> None:
        """Render portfolio/positions summary"""
        st.subheader("💼 Positions")
        
        if not positions:
            st.info("No open positions")
            return
        
        total_pnl = sum(p.get('pnl', 0) for p in positions)
        total_lots = sum(p.get('lots', 0) for p in positions)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Open Positions", len(positions))
        
        with col2:
            st.metric("Total Lots", f"{total_lots:.2f}")
        
        with col3:
            pnl_color = "normal" if total_pnl >= 0 else "inverse"
            st.metric("Total P/L", f"${total_pnl:.2f}", delta_color=pnl_color)
        
        # Position table
        df = pd.DataFrame(positions)
        st.dataframe(df, hide_index=True)
    
    @staticmethod
    def render_risk_reward_section() -> None:
        """Render risk/reward calculator"""
        with st.expander("⚖️ Risk/Reward Calculator", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                entry_price = st.number_input("Entry Price", value=1.0850, format="%.5f")
                stop_loss = st.number_input("Stop Loss", value=1.0800, format="%.5f")
            
            with col2:
                take_profit = st.number_input("Take Profit", value=1.0950, format="%.5f")
                risk_amount = abs(entry_price - stop_loss)
                reward_amount = abs(take_profit - entry_price)
                rr_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            st.markdown(f"""
            **Risk/Reward Analysis:**
            - Risk: {risk_amount:.5f} ({risk_amount * 10000:.1f} pips)
            - Reward: {reward_amount:.5f} ({reward_amount * 10000:.1f} pips)
            - **R/R Ratio: {rr_ratio:.2f}**
            
            {'✅ Good risk/reward ratio (>= 2)' if rr_ratio >= 2 else '⚠️ Consider a better risk/reward ratio'}
            """)
