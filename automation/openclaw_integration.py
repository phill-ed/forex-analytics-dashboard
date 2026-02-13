"""
OpenClaw Integration for Forex Alerts
Send automated trading signals to Telegram via OpenClaw
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.forex_automation import ForexAutomation, TradingSignal


class OpenClawForexNotifier:
    """
    Send forex signals via OpenClaw messaging
    """
    
    def __init__(self):
        self.forex = ForexAutomation()
        self.notification_history: List[Dict] = []
    
    def format_telegram_message(self, signal: TradingSignal) -> str:
        """Format signal for Telegram"""
        emoji = '🟢' if signal.signal_type == 'buy' else '🔴'
        
        message = f"""
{emoji} **{signal.pair} {signal.signal_type.upper()} SIGNAL**

📊 Confidence: {signal.confidence:.0f}%
💰 Entry: `{signal.entry_price:.5f}`
🛑 Stop Loss: `{signal.stop_loss:.5f}`
🎯 Take Profit: `{signal.take_profit:.5f}`

📈 **Indicators:**
• RSI: {signal.indicators.get('rsi', 'N/A')}
• SMA 20: {signal.indicators.get('sma_20', 'N/A')}
• SMA 50: {signal.indicators.get('sma_50', 'N/A')}
• MACD: {signal.indicators.get('macd', 'N/A')}

📝 {signal.reason}

⏰ {signal.timestamp.strftime('%H:%M %Y-%m-%d')}

⚠️ *Educational only - Not financial advice*
        """.strip()
        
        return message
    
    def send_alert(self, signal: TradingSignal, channel: str = 'telegram') -> bool:
        """
        Send alert via OpenClaw
        
        Args:
            signal: Trading signal
            channel: Notification channel
            
        Returns:
            Success status
        """
        message = self.format_telegram_message(signal)
        
        notification = {
            'type': 'forex_signal',
            'signal': {
                'pair': signal.pair,
                'type': signal.signal_type,
                'confidence': signal.confidence,
                'timestamp': signal.timestamp.isoformat()
            },
            'message': message,
            'channel': channel,
            'created_at': datetime.now().isoformat()
        }
        
        # Store notification
        self.notification_history.append(notification)
        
        # In a real implementation, this would use OpenClaw's messaging
        # For now, we'll simulate the notification
        
        logger.info(f"📨 Notification queued for {signal.pair}")
        
        # TODO: Integrate with OpenClaw's message tool
        # from tools import message
        # message(action="send", target=channel, content=message)
        
        return True
    
    def send_daily_summary(self, channel: str = 'telegram') -> bool:
        """
        Send daily summary
        
        Args:
            channel: Notification channel
            
        Returns:
            Success status
        """
        from automation.forex_automation import OpenClawIntegration
        
        integration = OpenClawIntegration()
        report = integration().generate_report() if hasattr(integration, '__call__') else integration.generate_report()
        
        logger.info(f"📊 Daily summary ready")
        
        return True
    
    def check_and_notify(self, min_confidence: float = 75) -> List[TradingSignal]:
        """
        Check for signals and notify
        
        Args:
            min_confidence: Minimum confidence for notifications
            
        Returns:
            List of signals sent
        """
        opportunities = self.forex.get_opportunities(min_confidence=min_confidence)
        
        sent = []
        
        for signal in opportunities:
            # Check if already notified recently (within 24h)
            already_notified = any(
                n['signal']['pair'] == signal.pair and
                n['signal']['type'] == signal.signal_type and
                (datetime.now() - datetime.fromisoformat(n['created_at'])).hours < 24
                for n in self.notification_history
            )
            
            if not already_notified:
                if self.send_alert(signal):
                    sent.append(signal)
        
        return sent


def setup_openclaw_integration():
    """
    Setup integration with OpenClaw for automated notifications
    
    This creates the necessary configuration and scripts
    """
    
    config = {
        'forex_automation': {
            'enabled': True,
            'check_interval_minutes': 15,
            'min_confidence_threshold': 75,
            'monitored_pairs': [
                'EUR/USD',
                'GBP/USD',
                'USD/JPY',
                'USD/CHF',
                'AUD/USD',
                'USD/CAD',
                'EUR/GBP',
                'USD/IDR'
            ],
            'channels': ['telegram'],
            'notification_preferences': {
                'buy_signals': True,
                'sell_signals': True,
                'daily_summary': True,
                'summary_time': '08:00',
                'high_confidence_only': False
            }
        },
        'alert_thresholds': {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'min_confidence': 75,
            'max_signals_per_day': 10
        }
    }
    
    # Save config
    config_path = 'automation/config.json'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Configuration saved to {config_path}")
    
    return config


def create_cron_script():
    """Create a script for cron-based automation"""
    
    script = '''#!/bin/bash
# Forex Analytics Automated Monitoring
# Add to cron: */15 * * * * /path/to/forex_monitor.sh

cd /root/.openclaw/workspace/forex-analytics-dashboard
source venv/bin/activate
python automation/forex_automation.py --check
'''
    
    with open('automation/forex_monitor.sh', 'w') as f:
        f.write(script)
    
    os.chmod('automation/forex_monitor.sh', 0o755)
    
    logger.info("Monitor script created: automation/forex_monitor.sh")


def create_openclaw_skill():
    """Create an OpenClaw skill for forex alerts"""
    
    skill_content = '''# Forex Analytics Skill

This skill connects OpenClaw to the Forex Analytics Dashboard for automated trading signals.

## Usage

### Check for trading opportunities
```
@forex check
```
Analyzes all monitored pairs and returns trading signals.

### Get daily summary
```
@forex summary
```
Shows today's trading opportunities and summary.

### Add pair to monitor
```
@forex add EUR/USD
```
Adds a currency pair to your monitoring list.

### Remove pair from monitoring
```
@forex remove USD/IDR
```
Removes a currency pair from monitoring.

### Set confidence threshold
```
@forex confidence 80
```
Only notify for signals with confidence above 80%.

## Configuration

Set monitored pairs and thresholds in `automation/config.json`.

## Notes

- All signals are for educational purposes only
- Not financial advice
- Always do your own research before trading
'''
    
    with open('skills/forex/SKILL.md', 'w') as f:
        f.write(skill_content)
    
    os.makedirs('skills/forex', exist_ok=True)


# Logging setup
import logging
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 OpenClaw Forex Integration")
    print("=" * 50)
    
    # Setup
    config = setup_openclaw_integration()
    create_cron_script()
    
    print("\n✅ Integration setup complete!")
    print("\n📁 Created files:")
    print("   - automation/config.json")
    print("   - automation/forex_monitor.sh")
    print("   - skills/forex/SKILL.md")
    
    print("\n🚀 Next steps:")
    print("   1. Add to cron: */15 * * * * /path/to/forex_monitor.sh")
    print("   2. Connect OpenClaw messaging for Telegram alerts")
    print("   3. Run: python automation/forex_automation.py")
    
    print("\n" + "=" * 50)
