# Forex Analytics Automation

Automated monitoring and alerting system for forex trading signals.

## 🚀 Features

- **Real-time Monitoring**: Automatically check forex pairs every 15 minutes
- **AI-Powered Signals**: Generate trading signals based on technical indicators
- **OpenClaw Integration**: Send Telegram notifications for trading opportunities
- **Daily Summaries**: Get daily reports of all opportunities
- **Customizable Alerts**: Set confidence thresholds and monitored pairs

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/phill-ed/forex-analytics-dashboard.git
cd forex-analytics-dashboard

# Install dependencies
pip install -r requirements.txt

# Install automation dependencies
pip install schedule
```

## 🎯 Quick Start

### Run Manual Check

```bash
python automation/forex_automation.py
```

### Setup OpenClaw Integration

```bash
python automation/openclaw_integration.py
```

### Start Continuous Monitoring

```bash
# Add to cron (every 15 minutes)
*/15 * * * * cd /path/to/forex-analytics-dashboard && python automation/forex_automation.py --daemon

# Or run as background process
nohup python automation/forex_automation.py --daemon > forex.log 2>&1 &
```

## 📊 Usage

### Python API

```python
from automation.forex_automation import ForexAutomation

# Create automation instance
forex = ForexAutomation()

# Check all pairs
signals = forex.check_all_pairs()

# Get high-confidence opportunities
opportunities = forex.get_opportunities(min_confidence=75)

# Print signals
for signal in opportunities:
    print(f"{signal.pair}: {signal.signal_type.upper()} @ {signal.confidence}%")
```

### OpenClaw Integration

```python
from automation.openclaw_integration import OpenClawForexNotifier

# Create notifier
notifier = OpenClawForexNotifier()

# Setup alerts
notifier.setup_alerts(
    min_confidence=75,
    pairs=['EUR/USD', 'USD/JPY', 'GBP/USD'],
    channels=['telegram']
)

# Check and notify
signals = notifier.check_and_notify()
```

## ⚙️ Configuration

Edit `automation/config.json`:

```json
{
  "forex_automation": {
    "enabled": true,
    "check_interval_minutes": 15,
    "min_confidence_threshold": 75,
    "monitored_pairs": [
      "EUR/USD",
      "GBP/USD",
      "USD/JPY",
      "USD/CHF",
      "AUD/USD",
      "USD/CAD",
      "EUR/GBP",
      "USD/IDR"
    ],
    "channels": ["telegram"],
    "notification_preferences": {
      "buy_signals": true,
      "sell_signals": true,
      "daily_summary": true,
      "summary_time": "08:00"
    }
  }
}
```

## 🔔 Signal Indicators Used

| Indicator | Description |
|-----------|-------------|
| **RSI** | Relative Strength Index (oversold < 30, overbought > 70) |
| **SMA** | Simple Moving Average (trend direction) |
| **EMA** | Exponential Moving Average |
| **MACD** | Moving Average Convergence Divergence |
| **ATR** | Average True Range (volatility) |

## 📈 Signal Types

- **🟢 BUY**: High confidence bullish signals
- **🔴 SELL**: High confidence bearish signals
- **🟡 HOLD**: Mixed or low confidence signals

## ⚠️ Disclaimer

> **This automation is for educational purposes only.**
> 
> It does NOT provide financial advice or trading recommendations.
> 
> Always:
> - Do your own research (DYOR)
> - Consult licensed financial advisors
> - Use proper risk management
> - Only trade with money you can afford to lose

## 🛠️ Automation Setup

### Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line (every 15 minutes)
*/15 * * * * cd /path/to/forex-analytics-dashboard && python automation/forex_automation.py >> /var/log/forex.log 2>&1
```

### Systemd (Linux)

Create `/etc/systemd/system/forex-monitor.service`:

```ini
[Unit]
Description=Forex Analytics Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/forex-analytics-dashboard
ExecStart=/usr/bin/python3 automation/forex_automation.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable forex-monitor
sudo systemctl start forex-monitor
```

## 🔗 OpenClaw Integration

To connect with OpenClaw for Telegram notifications:

1. Ensure OpenClaw is running
2. Configure Telegram channel in OpenClaw
3. Run the integration setup:

```bash
python automation/openclaw_integration.py
```

4. The system will send Telegram alerts when signals are generated

## 📱 Example Telegram Alert

```
🟢 EUR/USD BUY SIGNAL

📊 Confidence: 85%
💰 Entry: 1.08550
🛑 Stop Loss: 1.08000
🎯 Take Profit: 1.09800

📈 Indicators:
• RSI: 28.5
• SMA 20: 1.0820
• SMA 50: 1.0780
• MACD: 0.0015

📝 RSI oversold; MA bullish; MACD bullish

⏰ 14:30 2026-02-13

⚠️ Educational only - Not financial advice
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📧 Support

Open an issue on GitHub for support.

---

**Built with ❤️ for traders**

🌐 https://github.com/phill-ed/forex-analytics-dashboard
