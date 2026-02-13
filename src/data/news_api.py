"""
News API Module
Aggregates forex news from multiple sources
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAPI:
    """
    News aggregation for forex trading
    Collects news from multiple free sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ForexAnalytics/1.0'
        })
        
        # News sources
        self.feeds = {
            'forex_factory': 'https://www.forexfactory.com/rss/news',
            'investing': 'https://www.investing.com/rss/news.rss',
            'reuters': 'https://www.reutersagency.com/feed/',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss'
        }
        
        # Economic calendar events (sample - in production, use API)
        self.economic_events = {
            'HIGH': [
                'FOMC Meeting Minutes',
                'NFP - Non-Farm Payrolls',
                'GDP - Gross Domestic Product',
                'CPI - Consumer Price Index',
                'Interest Rate Decision',
                'ECB Press Conference'
            ],
            'MEDIUM': [
                'Retail Sales',
                'Industrial Production',
                'Trade Balance',
                'Consumer Confidence',
                'Manufacturing PMI',
                'Services PMI'
            ],
            'LOW': [
                'Housing Starts',
                'Building Permits',
                'Initial Jobless Claims',
                ' Durable Goods Orders',
                'Personal Income/Spending'
            ]
        }
    
    def get_latest_forex_news(self, max_items: int = 10) -> List[Dict]:
        """
        Get latest forex-related news
        
        Args:
            max_items: Maximum number of news items to return
            
        Returns:
            List of news articles
        """
        news = []
        
        # Parse RSS feeds
        for source, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:max_items]:
                    news.append({
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200],
                        'source': source.replace('_', ' ').title(),
                        'sentiment': self._analyze_sentiment(
                            entry.get('title', '') + ' ' + entry.get('summary', '')
                        ),
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing feed {source}: {e}")
        
        # Remove duplicates and sort by date
        unique_news = self._deduplicate_news(news)
        unique_news.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        return unique_news[:max_items]
    
    def get_economic_calendar(self, days: int = 7) -> List[Dict]:
        """
        Get economic calendar events
        
        Args:
            days: Number of days to include
            
        Returns:
            List of economic events
        """
        events = []
        today = datetime.now()
        
        # Generate sample economic events
        # In production, this would call an actual economic calendar API
        
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD']
        impact_colors = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
        
        for i in range(days):
            date = today + timedelta(days=i)
            
            # Add 2-4 events per day
            num_events = 2 + (i % 3)
            
            for j in range(num_events):
                impact = 'HIGH' if j == 0 else ('MEDIUM' if j == 1 else 'LOW')
                currency = currencies[(i + j) % len(currencies)]
                
                event = {
                    'date': date.strftime('%Y-%m-%d'),
                    'time': f"{9 + (j * 2):02d}:00 GMT",
                    'event': self._get_random_event(impact),
                    'currency': currency,
                    'impact': impact,
                    'indicator': impact_colors[impact],
                    'forecast': self._get_forecast(impact),
                    'previous': self._get_previous(impact)
                }
                
                events.append(event)
        
        return events
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment analysis
        """
        # Simple keyword-based sentiment analysis
        # In production, use NLP library or API
        
        positive_words = [
            'bullish', 'rise', 'gain', 'surge', 'rally', 'growth',
            'strong', 'recovery', 'optimistic', 'positive'
        ]
        
        negative_words = [
            'bearish', 'fall', 'drop', 'decline', 'slump', 'contraction',
            'weak', 'recession', 'pessimistic', 'negative', 'crash'
        ]
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = 'Bullish'
            score = min(pos_count / (pos_count + neg_count + 1), 1.0)
        elif neg_count > pos_count:
            sentiment = 'Bearish'
            score = min(neg_count / (pos_count + neg_count + 1), 1.0)
        else:
            sentiment = 'Neutral'
            score = 0.5
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'positive': pos_count,
            'negative': neg_count
        }
    
    def get_central_bank_news(self) -> List[Dict]:
        """
        Get news from central banks (Fed, ECB, BoE, etc.)
        
        Returns:
            List of central bank news
        """
        # In production, this would scrape actual bank websites
        return [
            {
                'bank': 'Federal Reserve',
                'title': 'FOMC maintains interest rates',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impact': 'HIGH'
            },
            {
                'bank': 'European Central Bank',
                'title': 'ECB President speaks on inflation',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impact': 'MEDIUM'
            }
        ]
    
    def get_market_sentiment(self) -> Dict:
        """
        Get overall market sentiment indicators
        
        Returns:
            Dict with sentiment metrics
        """
        # In production, this would use actual market data
        
        return {
            'fear_greed_index': 55,  # 0-100
            'sentiment_label': 'Neutral',
            'long_positions': 52,  # percentage
            'short_positions': 48,
            'retail_long': 45,
            'retail_short': 55,
            'last_updated': datetime.now().isoformat()
        }
    
    def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search news for specific keywords
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of matching news
        """
        all_news = self.get_latest_forex_news(max_results * 2)
        
        query_lower = query.lower()
        filtered = [
            n for n in all_news
            if query_lower in n.get('title', '').lower() or
               query_lower in n.get('summary', '').lower()
        ]
        
        return filtered[:max_results]
    
    def _parse_feed_entry(self, entry) -> Dict:
        """Parse a single RSS feed entry"""
        return {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'summary': entry.get('summary', '')[:300],
            'source': 'RSS Feed'
        }
    
    def _analyze_sentiment(self, text: str) -> str:
        """Quick sentiment analysis for news"""
        analysis = self.analyze_sentiment(text)
        return analysis['sentiment']
    
    def _deduplicate_news(self, news: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        seen = set()
        unique = []
        
        for item in news:
            title = item.get('title', '')[:50]  # Use first 50 chars
            if title not in seen:
                seen.add(title)
                unique.append(item)
        
        return unique
    
    def _get_random_event(self, impact: str) -> str:
        """Get a random economic event based on impact level"""
        events = self.economic_events.get(impact, self.economic_events['MEDIUM'])
        import random
        return random.choice(events)
    
    def _get_forecast(self, impact: str) -> str:
        """Generate sample forecast"""
        if impact == 'HIGH':
            return 'Various forecasts'
        elif impact == 'MEDIUM':
            return 'Consensus expected'
        return 'No forecast'
    
    def _get_previous(self, impact: str) -> str:
        """Generate sample previous value"""
        import random
        values = ['0.5%', '1.2%', '2.1%', '3.4%']
        return random.choice(values)
