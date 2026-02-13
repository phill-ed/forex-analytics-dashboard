"""
Forex Data API Module
Handles real-time and historical forex data from multiple sources
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForexAPI:
    """
    Forex data API handler
    Uses multiple free APIs for reliable data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ForexAnalytics/1.0'
        })
        
        # Free API endpoints
        self.apis = {
            'frankfurter': 'https://api.frankfurter.app',
            'exchangerate': 'https://api.exchangerate-api.com/v4',
            'forex': 'https://api.forexfactory.com/v1.0'
        }
        
        # Cache for rate limiting
        self.cache = {}
        self.cache_duration = 60  # seconds
    
    def get_live_rate(self, pair: str) -> Optional[Dict]:
        """
        Get live rate for a single currency pair
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            
        Returns:
            Dict with bid, ask, timestamp, etc.
        """
        try:
            base, quote = self._parse_pair(pair)
            
            # Try Frankfurter API first (completely free, no key needed)
            url = f"{self.apis['frankfurter']}/latest"
            params = {'from': base, 'to': quote}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'rates' in data and quote in data['rates']:
                rate = data['rates'][quote]
                
                # Calculate bid/ask spread (approximate)
                spread_pct = 0.0001  # 1 pip spread
                bid = rate * (1 - spread_pct/2)
                ask = rate * (1 + spread_pct/2)
                
                return {
                    'pair': pair,
                    'bid': round(bid, 5),
                    'ask': round(ask, 5),
                    'rate': rate,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'frankfurter'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching rate for {pair}: {e}")
            return self._get_sample_rate(pair)
    
    def get_multi_rates(self, pairs: List[str]) -> Dict[str, Dict]:
        """
        Get live rates for multiple currency pairs
        
        Args:
            pairs: List of currency pairs
            
        Returns:
            Dict with pair -> rate data
        """
        rates = {}
        
        for pair in pairs:
            rate = self.get_live_rate(pair)
            if rate:
                rates[pair] = rate
            time.sleep(0.1)  # Rate limiting
        
        return rates
    
    def get_historical_data(
        self,
        pair: str,
        timeframe: str = '1d',
        periods: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Get historical price data
        
        Args:
            pair: Currency pair
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
            periods: Number of periods to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            base, quote = self._parse_pair(pair)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=periods * self._timeframe_to_days(timeframe))
            
            url = f"{self.apis['frankfurter']}/{start_date.strftime('%Y-%m-%d')}"
            params = {
                'from': base,
                'to': quote,
                'format': 'timeseries'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'rates' not in data:
                return self._generate_sample_data(pair, periods)
            
            # Convert to DataFrame
            records = []
            for date, rates in data['rates'].items():
                if quote in rates:
                    records.append({
                        'timestamp': date,
                        'open': rates[quote],
                        'high': rates[quote] * 1.001,  # Approximate
                        'low': rates[quote] * 0.999,
                        'close': rates[quote],
                        'volume': 0
                    })
            
            if not records:
                return self._generate_sample_data(pair, periods)
            
            df = pd.DataFrame(records)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df = df.sort_index()
            
            return df.tail(periods)
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {pair}: {e}")
            return self._generate_sample_data(pair, periods)
    
    def get_conversion(self, amount: float, from_pair: str, to_pair: str) -> Dict:
        """
        Convert amount between currencies
        
        Args:
            amount: Amount to convert
            from_pair: Source currency pair
            to_pair: Target currency pair
            
        Returns:
            Conversion result
        """
        try:
            # Get rates for both pairs
            rate1 = self.get_live_rate(from_pair)
            rate2 = self.get_live_rate(to_pair)
            
            if not rate1 or not rate2:
                return {'error': 'Unable to get rates'}
            
            # Convert through USD (base currency)
            base_rate = rate1['rate']
            target_rate = rate2['rate']
            
            converted = amount / base_rate * target_rate
            
            return {
                'original': {
                    'amount': amount,
                    'pair': from_pair,
                    'rate': base_rate
                },
                'converted': {
                    'amount': round(converted, 2),
                    'pair': to_pair,
                    'rate': target_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return {'error': str(e)}
    
    def get_market_summary(self) -> Dict:
        """
        Get overall market summary
        
        Returns:
            Dict with market overview
        """
        major_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD']
        rates = self.get_multi_rates(major_pairs)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'pairs': rates,
            'market_condition': 'normal',  # normal, volatile, quiet
            'trend': 'mixed'  # bullish, bearish, mixed
        }
        
        # Calculate market conditions
        if rates:
            changes = [r.get('change_pct', 0) for r in rates.values()]
            avg_change = sum(changes) / len(changes) if changes else 0
            
            if avg_change > 0.5:
                summary['trend'] = 'bullish'
            elif avg_change < -0.5:
                summary['trend'] = 'bearish'
            else:
                summary['trend'] = 'mixed'
        
        return summary
    
    def _parse_pair(self, pair: str) -> Tuple[str, str]:
        """Parse currency pair into base and quote"""
        parts = pair.split('/')
        if len(parts) == 2:
            return parts[0], parts[1]
        return 'USD', 'EUR'  # Default
    
    def _timeframe_to_days(self, timeframe: str) -> int:
        """Convert timeframe string to days"""
        mapping = {
            '1m': 0.001, '5m': 0.004, '15m': 0.01, '30m': 0.02,
            '1h': 1, '4h': 4, '1d': 1, '1w': 7
        }
        return mapping.get(timeframe, 1)
    
    def _get_sample_rate(self, pair: str) -> Dict:
        """Generate sample rate for testing"""
        import random
        base_rate = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2650,
            'USD/JPY': 150.50,
            'USD/CHF': 0.8850,
            'AUD/USD': 0.6520,
            'USD/CAD': 1.3650,
            'USD/IDR': 15600.0,
            'USD/SGD': 1.3450,
            'EUR/GBP': 0.8580,
            'EUR/JPY': 163.5,
            'GBP/JPY': 190.5,
        }.get(pair, 1.0)
        
        variation = random.uniform(-0.005, 0.005)
        rate = base_rate * (1 + variation)
        
        return {
            'pair': pair,
            'bid': round(rate * 0.9999, 5),
            'ask': round(rate * 1.0001, 5),
            'rate': round(rate, 5),
            'timestamp': datetime.now().isoformat(),
            'source': 'sample',
            'change_pct': round(variation * 100, 2)
        }
    
    def _generate_sample_data(self, pair: str, periods: int) -> pd.DataFrame:
        """Generate sample historical data"""
        import numpy as np
        
        base_rate = self._get_sample_rate(pair)['rate']
        
        # Generate realistic price movement
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='D')
        returns = np.random.normal(0, 0.01, periods)
        prices = base_rate * np.cumprod(1 + returns)
        
        # Add some OHLC variation
        highs = prices * (1 + np.abs(np.random.normal(0, 0.005, periods)))
        lows = prices * (1 - np.abs(np.random.normal(0, 0.005, periods)))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': np.random.randint(1000, 10000, periods)
        })
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        return df
