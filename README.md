# Forex Analytics Dashboard

A comprehensive Python-based forex trading analytics platform with live market data, technical analysis, news aggregation, and powerful trading tools.

![Dashboard Preview](docs/preview.png)

## 🌟 Features

### 📊 Live Market Data
- Real-time exchange rates from multiple sources
- Support for 30+ currency pairs
- Live price updates
- Multi-pair monitoring

### 📈 Technical Analysis
- **Moving Averages** (SMA, EMA, WMA)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Fibonacci Retracements**
- **Pivot Points**
- **Support & Resistance Levels**

### 🤖 AI Analysis (NEW!)
- **AI Trend Prediction** - ML-based trend forecasting
- **Pattern Recognition** - Auto-detect chart patterns
- **Price Forecast** - Simple educational projections
- **Strategy Backtesting** - Test MA crossover strategies
- **Sentiment Analysis** - News sentiment scoring
- **Risk Assessment** - AI-powered risk evaluation

### 📰 News Aggregator
- Real-time forex news
- Economic calendar
- Central bank announcements
- Custom news feeds
- Sentiment analysis

### 🛠️ Trading Tools
- **Position Size Calculator**
- **Risk/Reward Calculator**
- **Pip Value Calculator**
- **Margin Calculator**
- **Profit/Loss Calculator**

### 📉 Charting & Visualization
- Interactive charts
- Multiple timeframe support
- Custom indicators
- Historical data analysis

### 🔔 Alerts & Notifications
- Price alerts
- Indicator signals
- News notifications
- Customizable thresholds

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
pip install -r requirements.txt
```

### Installation

```bash
# Clone the repository
git clone https://github.com/phill-ed/forex-analytics-dashboard.git
cd forex-analytics-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python main.py
```

### Docker

```bash
# Build and run with Docker
docker build -t forex-dashboard .
docker run -p 8501:8501 forex-dashboard
```

## 📁 Project Structure

```
forex-analytics-dashboard/
├── main.py                    # Main application entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env.example              # Environment variables template
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── src/
│   ├── data/
│   │   ├── forex_api.py     # Forex data APIs
│   │   ├── news_api.py      # News aggregation
│   │   └── storage.py       # Data storage utilities
│   ├── analysis/
│   │   ├── indicators.py    # Technical indicators
│   │   ├── patterns.py      # Chart patterns
│   │   └── signals.py       # Trading signals
│   ├── ui/
│   │   ├── dashboard.py     # Main dashboard
│   │   ├── charts.py        # Chart components
│   │   └── components.py    # Reusable UI components
│   └── utils/
│       ├── config.py        # Configuration
│       └── helpers.py       # Utility functions
├── tests/                   # Unit tests
└── docs/                    # Documentation
```

## 💻 Usage

### Basic Usage

```python
from src.data.forex_api import ForexAPI
from src.analysis.indicators import TechnicalIndicators

# Get live rates
api = ForexAPI()
rates = api.get_live_rates(['EUR/USD', 'USD/IDR', 'GBP/USD'])

# Calculate indicators
indicators = TechnicalIndicators()
rsi = indicators.calculate_rsi(prices, period=14)
macd = indicators.calculate_macd(prices)
```

### Run Dashboard

```bash
# Streamlit dashboard
streamlit run ui/dashboard.py

# Or CLI version
python main.py --mode cli
```

### Configure APIs

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

## 📊 Supported Currency Pairs

| Pair | Name | Typical Spread |
|------|------|----------------|
| EUR/USD | Euro/US Dollar | 0.1 - 1.0 |
| USD/JPY | US Dollar/Japanese Yen | 0.1 - 1.0 |
| GBP/USD | British Pound/US Dollar | 0.5 - 2.0 |
| USD/CHF | US Dollar/Swiss Franc | 0.5 - 2.0 |
| AUD/USD | Australian Dollar/US Dollar | 0.5 - 2.0 |
| USD/IDR | US Dollar/Indonesian Rupiah | 10 - 50 |
| EUR/GBP | Euro/British Pound | 0.5 - 2.0 |
| USD/SGD | US Dollar/Singapore Dollar | 1.0 - 3.0 |
| And 20+ more pairs... |

## 🛠️ Technical Indicators

### Moving Averages
```python
sma = indicators.sma(prices, period=20)
ema = indicators.ema(prices, period=20)
```

### RSI
```python
rsi = indicators.rsi(prices, period=14)
# Returns: Overbought (>70), Oversold (<30), Neutral
```

### MACD
```python
macd_line, signal_line, histogram = indicators.macd(prices)
# Buy signal: MACD crosses above signal
# Sell signal: MACD crosses below signal
```

### Bollinger Bands
```python
upper, middle, lower = indicators.bollinger_bands(prices, period=20)
```

## 📰 News & Events

### Economic Calendar
```python
from src.data.news_api import NewsAPI

news = NewsAPI()
events = news.get_economic_calendar()
# Returns: Interest rates, GDP, CPI, NFP, etc.
```

### News Sentiment
```python
sentiment = news.analyze_sentiment(headlines)
# Returns: Positive, Negative, Neutral
```

## 🔔 Alert System

### Set Price Alert
```python
from src.ui.dashboard import Dashboard

dashboard = Dashboard()
dashboard.add_alert(
    pair='EUR/USD',
    target=1.1000,
    direction='above',
    notification='telegram'
)
```

## 🎨 Screenshots

### Main Dashboard
![Dashboard](docs/dashboard-main.png)

### Technical Analysis
![Analysis](docs/technical-analysis.png)

### News Feed
![News](docs/news-feed.png)

## 🤖 AI Analysis Usage

### Basic AI Analysis
```python
from src.analysis.ai_analysis import AIAnalyzer

ai = AIAnalyzer()
result = ai.comprehensive_analysis(
    prices=closes,
    pair='EUR/USD',
    news_headlines=['Headline 1', 'Headline 2']
)

print(f"Trend: {result.trend_prediction}")
print(f"Confidence: {result.confidence}%")
print(f"Support: {result.support_levels}")
print(f"Risk Level: {result.risk_level}")
```

### Price Forecast
```python
from src.analysis.ai_analysis import AIForecast

forecast = AIForecast()
result = forecast.forecast(prices, periods=7)

print(f"Bullish: {result['forecasts']['bullish']}")
print(f"Expected: {result['forecasts']['expected']}")
print(f"Bearish: {result['forecasts']['bearish']}")
```

### Strategy Backtest
```python
backtest = AIForecast()
result = backtest.backtest_signal(
    prices,
    short_period=5,
    long_period=20
)

print(f"Buy Signals: {result['buy_signals']}")
print(f"Sell Signals: {result['sell_signals']}")
```

## 📦 Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
plotly>=5.18.0
ta-lib>=0.4.24
python-dotenv>=1.0.0
httpx>=0.25.0
beautifulsoup4>=4.12.0
feedparser>=6.0.10
```

## 🔒 Security Notes

- **Never share API keys**
- Use environment variables for sensitive data
- Enable 2FA on trading accounts
- Test strategies on demo accounts first

## ⚠️ Disclaimer

> **This software is for educational and informational purposes only.**
> 
> It does **NOT** provide financial advice, trading signals, or recommendations to buy/sell any financial instruments.
> 
> **Always:**
> - Do your own research (DYOR)
> - Consult licensed financial advisors
> - Use demo accounts for testing
> - Only invest what you can afford to lose
> - Understand the risks of forex trading

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

- Open an issue for bugs
- Discussions for questions
- Wiki for documentation

---

**Built with ❤️ for traders**

🌐 **GitHub:** https://github.com/phill-ed/forex-analytics-dashboard
