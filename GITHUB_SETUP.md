# Forex Analytics Dashboard - GitHub Setup

## 🚀 Quick Push to GitHub

Since I cannot authenticate to GitHub directly, here's how to push the repository:

### Option 1: Using GitHub CLI (gh)

```bash
# Install GitHub CLI (if not installed)
brew install gh  # Mac
# or
winget install gh

# Authenticate
gh auth login

# Create repository
cd /root/.openclaw/workspace/forex-analytics-dashboard
gh repo create forex-analytics-dashboard --public --source=. --push
```

### Option 2: Using Username + Personal Access Token

```bash
cd /root/.openclaw/workspace/forex-analytics-dashboard

# Set remote URL with token
git remote set-url origin https://phill-ed:YOUR_GITHUB_TOKEN@github.com/phill-ed/forex-analytics-dashboard.git

# Push
git push -u origin main
```

**To create a Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`
4. Copy the token

### Option 3: Manual Upload

1. Go to: https://github.com/new
2. Repository name: `forex-analytics-dashboard`
3. Description: "A comprehensive Python-based forex trading analytics platform with live market data, technical analysis, news aggregation, and powerful trading tools."
4. Public: ✅
5. Don't initialize with README
6. Click "Create repository"
7. Follow the commands shown:

```bash
cd /root/.openclaw/workspace/forex-analytics-dashboard
git remote add origin https://github.com/phill-ed/forex-analytics-dashboard.git
git branch -M main
git push -u origin main
```

---

## 📦 What's Included

```
forex-analytics-dashboard/
├── main.py                      # Streamlit dashboard entry point
├── README.md                    # Full documentation
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── .env.example                 # Environment template
├── .gitignore                  # Git ignore rules
└── src/
    ├── data/
    │   ├── forex_api.py        # Live forex data APIs
    │   └── news_api.py         # News aggregation
    ├── analysis/
    │   └── indicators.py       # Technical indicators
    ├── ui/
    │   ├── charts.py           # Interactive charts
    │   └── components.py       # UI components
    └── utils/
        └── helpers.py          # Utility functions
```

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 📊 Live Rates | Real-time currency prices |
| 📈 Technical Analysis | RSI, MACD, SMA, EMA, Bollinger Bands |
| 📰 News Feed | Forex news aggregation |
| 📅 Economic Calendar | Economic events schedule |
| 🧮 Trading Tools | Position size, risk/reward calculators |
| 📉 Interactive Charts | Plotly-powered visualizations |
| 🔔 Alerts | Price notifications |
| 🐳 Docker Ready | Easy container deployment |

---

## 🚀 Quick Start

```bash
# Clone (after pushing)
git clone https://github.com/phill-ed/forex-analytics-dashboard.git
cd forex-analytics-dashboard

# Install
pip install -r requirements.txt

# Run
streamlit run main.py

# Or with Docker
docker build -t forex-dashboard .
docker run -p 8501:8501 forex-dashboard
```

---

**Once pushed, share the repo URL!** 🔗
