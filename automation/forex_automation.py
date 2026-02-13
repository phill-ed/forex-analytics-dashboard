"""
Forex Analytics Automation Module
Connects OpenClaw to the Forex Dashboard for automated monitoring and alerts
"""

import schedule
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """Trading opportunity signal"""
    pair: str
    signal_type: str  # 'buy', 'sell', 'hold'
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reason: str
    indicators: Dict
    timestamp: datetime
    notified: bool = False


class ForexAutomation:
    """
    Forex Analytics Automation System
    Monitors forex pairs and generates trading signals
    """
    
    def __init__(self):
        self.signals: List[TradingSignal] = []
        self.monitored_pairs = [
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
            'AUD/USD', 'USD/CAD', 'EUR/GBP', 'USD/IDR'
        ]
        self.last_check: Dict[str, datetime] = {}
        self.check_interval = 15  # minutes
        self.running = False
        
    def analyze_pair(self, pair: str) -> Optional[TradingSignal]:
        """
        Analyze a currency pair and generate signal
        
        Args:
            pair: Currency pair to analyze
            
        Returns:
            TradingSignal or None
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.insert(0, '.')
            from src.data.forex_api import ForexAPI
            from src.analysis.indicators import TechnicalIndicators
            
            api = ForexAPI()
            indicators = TechnicalIndicators()
            
            # Get historical data
            data = api.get_historical_data(pair, '1h', 50)
            
            if data is None or data.empty:
                logger.warning(f"No data available for {pair}")
                return None
            
            closes = data['close'].values
            
            # Calculate indicators
            rsi = indicators.rsi(closes, 14)[-1]
            sma_20 = indicators.sma(closes, 20)[-1]
            sma_50 = indicators.sma(closes, 50)[-1]
            macd_line, signal_line, histogram = indicators.macd(closes)
            
            # Get current price
            current_price = closes[-1]
            
            # Generate signal based on multiple conditions
            signal_type = 'hold'
            confidence = 50.0
            reason = ""
            indicators_data = {
                'rsi': round(rsi, 2),
                'sma_20': round(sma_20, 5),
                'sma_50': round(sma_50, 5),
                'macd': round(macd_line[-1], 5),
                'histogram': round(histogram[-1], 5)
            }
            
            buy_score = 0
            sell_score = 0
            
            # RSI analysis
            if rsi < 30:
                buy_score += 2
                reason += "RSI oversold; "
            elif rsi > 70:
                sell_score += 2
                reason += "RSI overbought; "
            
            # SMA analysis
            if sma_20 > sma_50:
                buy_score += 1
                reason += "MA bullish; "
            else:
                sell_score += 1
                reason += "MA bearish; "
            
            # MACD analysis
            if macd_line[-1] > signal_line[-1]:
                buy_score += 1
                reason += "MACD bullish; "
            else:
                sell_score += 1
                reason += "MACD bearish; "
            
            # Histogram momentum
            if histogram[-1] > 0:
                buy_score += 0.5
            else:
                sell_score += 0.5
            
            # Determine final signal
            if buy_score >= 4:
                signal_type = 'buy'
                confidence = min(60 + buy_score * 5, 90)
                reason = f"BULLISH SIGNALS: {reason}"
            elif sell_score >= 4:
                signal_type = 'sell'
                confidence = min(60 + sell_score * 5, 90)
                reason = f"BEARISH SIGNALS: {reason}"
            else:
                signal_type = 'hold'
                confidence = 50
                reason = f"MIXED SIGNALS: {reason}"
            
            # Calculate stop loss and take profit
            atr = indicators.atr(
                data['high'].values,
                data['low'].values,
                data['close'].values
            )[-1]
            
            if signal_type == 'buy':
                stop_loss = current_price - (2 * atr)
                take_profit = current_price + (3 * atr)
            elif signal_type == 'sell':
                stop_loss = current_price + (2 * atr)
                take_profit = current_price - (3 * atr)
            else:
                stop_loss = current_price
                take_profit = current_price
            
            signal = TradingSignal(
                pair=pair,
                signal_type=signal_type,
                confidence=confidence,
                entry_price=current_price,
                stop_loss=round(stop_loss, 5),
                take_profit=round(take_profit, 5),
                reason=reason.strip(),
                indicators=indicators_data,
                timestamp=datetime.now()
            )
            
            logger.info(f"Analyzed {pair}: {signal_type.upper()} @ {current_price:.5f}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing {pair}: {e}")
            return None
    
    def check_all_pairs(self) -> List[TradingSignal]:
        """
        Check all monitored pairs and return signals
        
        Returns:
            List of trading signals
        """
        signals = []
        
        for pair in self.monitored_pairs:
            signal = self.analyze_pair(pair)
            if signal:
                signals.append(signal)
                self.last_check[pair] = datetime.now()
        
        return signals
    
    def get_opportunities(self, min_confidence: float = 70) -> List[TradingSignal]:
        """
        Get high-confidence trading opportunities
        
        Args:
            min_confidence: Minimum confidence level
            
        Returns:
            List of high-confidence signals
        """
        signals = self.check_all_pairs()
        
        # Filter by confidence and type
        opportunities = [
            s for s in signals
            if s.confidence >= min_confidence and s.signal_type != 'hold'
        ]
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        return opportunities
    
    def format_signal_message(self, signal: TradingSignal) -> str:
        """Format signal for notification"""
        emoji = '🟢' if signal.signal_type == 'buy' else '🔴'
        
        return f"""
{emoji} **{signal.pair} {signal.signal_type.upper()} SIGNAL**

📊 *Confidence:* {signal.confidence:.0f}%
💰 *Entry:* {signal.entry_price:.5f}
🛑 *Stop Loss:* {signal.stop_loss:.5f}
🎯 *Take Profit:* {signal.take_profit:.5f}

📈 *Indicators:*
• RSI: {signal.indicators.get('rsi', 'N/A')}
• SMA 20: {signal.indicators.get('sma_20', 'N/A')}
• SMA 50: {signal.indicators.get('sma_50', 'N/A')}
• MACD: {signal.indicators.get('macd', 'N/A')}

📝 *Reason:* {signal.reason}

⏰ *Time:* {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ *Educational Only - Not Financial Advice*
        """.strip()
    
    def start_monitoring(self, interval_minutes: int = 15):
        """
        Start automated monitoring
        
        Args:
            interval_minutes: How often to check
        """
        self.check_interval = interval_minutes
        self.running = True
        
        # Schedule checks
        schedule.every(interval_minutes).minutes.do(self.check_all_pairs)
        
        logger.info(f"Started monitoring {len(self.monitored_pairs)} pairs every {interval_minutes} minutes")
        
        # Main loop
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        schedule.clear()
        logger.info("Stopped monitoring")


class OpenClawIntegration:
    """
    Integration with OpenClaw for notifications
    """
    
    def __init__(self):
        self.forex = ForexAutomation()
        self.notification_queue: List[Dict] = []
    
    def setup_alerts(
        self,
        min_confidence: float = 75,
        pairs: List[str] = None,
        channels: List[str] = ['telegram']
    ):
        """
        Setup automated alerts
        
        Args:
            min_confidence: Minimum confidence for alerts
            pairs: Specific pairs to monitor (or all)
            channels: Notification channels
        """
        if pairs:
            self.forex.monitored_pairs = pairs
        
        logger.info(f"Setup alerts for {len(self.forex.monitored_pairs)} pairs")
        logger.info(f"Min confidence: {min_confidence}%")
        logger.info(f"Channels: {channels}")
    
    def run_check(self) -> List[TradingSignal]:
        """
        Run a single check and return signals
        
        Returns:
            List of trading signals
        """
        return self.forex.get_opportunities(min_confidence=70)
    
    def get_daily_summary(self) -> Dict:
        """
        Get daily trading summary
        
        Returns:
            Summary dict
        """
        opportunities = self.run_check()
        
        buy_signals = [s for s in opportunities if s.signal_type == 'buy']
        sell_signals = [s for s in opportunities if s.signal_type == 'sell']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'pairs_checked': len(self.forex.monitored_pairs),
            'total_signals': len(opportunities),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'top_opportunity': opportunities[0] if opportunities else None,
            'pairs': [s.pair for s in opportunities]
        }
    
    def generate_report(self) -> str:
        """
        Generate human-readable daily report
        
        Returns:
            Report string
        """
        summary = self.get_daily_summary()
        
        report = f"""
📊 **Forex Daily Report**
⏰ {summary['timestamp']}

📈 **Summary:**
• Pairs Checked: {summary['pairs_checked']}
• Total Signals: {summary['total_signals']}
• 🟢 Buy Signals: {summary['buy_signals']}
• 🔴 Sell Signals: {summary['sell_signals']}

🎯 **Top Opportunity:**
"""
        
        if summary['top_opportunity']:
            signal = summary['top_opportunity']
            report += self.forex.format_signal_message(signal)
        else:
            report += "_No high-confidence signals today_"
        
        report += """

⚠️ *Educational Only - Not Financial Advice*
        """
        
        return report.strip()


def main():
    """Main automation entry point"""
    print("=" * 50)
    print("🤖 Forex Analytics Automation")
    print("=" * 50)
    
    # Create integration
    integration = OpenClawIntegration()
    
    # Setup alerts
    integration.setup_alerts(
        min_confidence=75,
        pairs=['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/IDR'],
        channels=['telegram']
    )
    
    # Run initial check
    print("\n🔍 Running initial check...")
    opportunities = integration.run_check()
    
    print(f"\n📊 Found {len(opportunities)} opportunities:")
    
    for signal in opportunities[:5]:  # Top 5
        print(f"\n{'-' * 40}")
        print(f"📌 {signal.pair} - {signal.signal_type.upper()}")
        print(f"   Confidence: {signal.confidence:.0f}%")
        print(f"   Entry: {signal.entry_price:.5f}")
        print(f"   Stop: {signal.stop_loss:.5f}")
        print(f"   Target: {signal.take_profit:.5f}")
    
    # Generate report
    print("\n" + "=" * 50)
    print(integration.generate_report())
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete!")
    print("\n💡 To start continuous monitoring:")
    print("   python automation/forex_monitor.py --daemon")
    print("=" * 50)


if __name__ == "__main__":
    main()
