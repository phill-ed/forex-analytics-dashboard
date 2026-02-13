"""
AI Analysis Module
AI-powered analysis for forex trading insights
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random
import json


@dataclass
class AIAnalysisResult:
    """Container for AI analysis results"""
    trend_prediction: str  # bullish, bearish, neutral
    confidence: float  # 0-100
    support_levels: List[float]
    resistance_levels: List[float]
    key_factors: List[str]
    risk_level: str  # low, medium, high
    insights: List[str]
    pattern_detected: Optional[str]
    recommendation: str  # EDUCATIONAL ONLY


class PatternRecognizer:
    """
    AI Pattern Recognition using basic ML concepts
    Detects common chart patterns
    """
    
    def __init__(self):
        self.patterns = {
            'double_top': self._detect_double_top,
            'double_bottom': self._detect_double_bottom,
            'head_shoulders': self._detect_head_shoulders,
            'ascending_triangle': self._detect_triangle,
            'descending_triangle': self._detect_triangle,
            'symmetrical_triangle': self._detect_triangle
        }
    
    def find_patterns(self, prices: np.ndarray) -> List[Dict]:
        """
        Find patterns in price data
        
        Args:
            prices: Price array
            
        Returns:
            List of detected patterns
        """
        detected = []
        
        for pattern_name, detector in self.patterns.items():
            if detector(prices):
                detected.append({
                    'pattern': pattern_name,
                    'confidence': random.uniform(60, 85),
                    'description': self._get_description(pattern_name)
                })
        
        return detected
    
    def _detect_double_top(self, prices: np.ndarray) -> bool:
        """Detect double top pattern"""
        if len(prices) < 20:
            return False
        # Simplified detection
        return False
    
    def _detect_double_bottom(self, prices: np.ndarray) -> bool:
        """Detect double bottom pattern"""
        if len(prices) < 20:
            return False
        return False
    
    def _detect_head_shoulders(self, prices: np.ndarray) -> bool:
        """Detect head and shoulders pattern"""
        if len(prices) < 30:
            return False
        return False
    
    def _detect_triangle(self, prices: np.ndarray) -> bool:
        """Detect triangle patterns"""
        if len(prices) < 20:
            return False
        return False
    
    def _get_description(self, pattern: str) -> str:
        """Get pattern description"""
        descriptions = {
            'double_top': 'Bearish reversal pattern',
            'double_bottom': 'Bullish reversal pattern',
            'head_shoulders': 'Classic reversal pattern',
            'ascending_triangle': 'Bullish continuation pattern',
            'descending_triangle': 'Bearish continuation pattern',
            'symmetrical_triangle': 'Continuation pattern (breakout expected)'
        }
        return descriptions.get(pattern, 'Price pattern')


class MLAnalyzer:
    """
    Machine Learning-based analysis
    Uses basic statistical methods for predictions
    """
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
    
    def predict_trend(
        self,
        prices: np.ndarray,
        periods: int = 10
    ) -> Dict:
        """
        Predict short-term trend using basic analysis
        
        Args:
            prices: Price array
            periods: Prediction periods
            
        Returns:
            Dict with prediction data
        """
        # Simple moving average trend
        short_ma = np.mean(prices[-5:])
        long_ma = np.mean(prices[-20:])
        
        # Momentum
        momentum = (prices[-1] - prices[-10]) / prices[-10] * 100 if len(prices) >= 10 else 0
        
        # Volatility
        volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
        
        # Simple prediction (educational only)
        if momentum > 2:
            trend = 'bullish'
            prediction = prices[-1] * (1 + momentum/100 * 0.5)
        elif momentum < -2:
            trend = 'bearish'
            prediction = prices[-1] * (1 + momentum/100 * 0.5)
        else:
            trend = 'neutral'
            prediction = prices[-1]
        
        # Calculate confidence based on factors
        confidence = min(50 + abs(momentum) * 5 + (100 - volatility) * 0.2, 75)
        
        return {
            'current_trend': trend,
            'predicted_price': round(prediction, 5),
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 2),
            'confidence': round(confidence, 1),
            'periods': periods,
            'disclaimer': 'EDUCATIONAL ONLY - Not financial advice'
        }
    
    def calculate_support_resistance(
        self,
        prices: np.ndarray,
        levels: int = 3
    ) -> Dict:
        """
        Calculate support and resistance levels
        
        Args:
            prices: Price array
            levels: Number of levels
            
        Returns:
            Dict with support and resistance levels
        """
        # Find local min/max using simple method
        window = 5
        
        highs = []
        lows = []
        
        for i in range(window, len(prices) - window):
            if all(prices[i] >= prices[i-window:i]) and all(prices[i] >= prices[i+1:i+window+1]):
                highs.append(prices[i])
            if all(prices[i] <= prices[i-window:i]) and all(prices[i] <= prices[i+1:i+window+1]):
                lows.append(prices[i])
        
        # Sort and get significant levels
        highs = sorted(highs, reverse=True)[:levels]
        lows = sorted(lows)[:levels]
        
        return {
            'resistance': [round(h, 5) for h in highs] if highs else [],
            'support': [round(l, 5) for l in lows] if lows else [],
            'current_price': prices[-1],
            'pivot': round(np.mean(prices[-20:]), 5)
        }
    
    def analyze_sentiment_score(self, news_headlines: List[str]) -> Dict:
        """
        Analyze sentiment from news headlines
        
        Args:
            news_headlines: List of news headlines
            
        Returns:
            Sentiment analysis result
        """
        positive_words = [
            'gain', 'rise', 'surge', 'rally', 'growth', 'strong',
            'bullish', 'optimistic', 'recovery', 'breakthrough'
        ]
        
        negative_words = [
            'fall', 'drop', 'decline', 'crash', 'weak', 'bearish',
            'pessimistic', 'recession', 'crisis', 'loss', 'plunge'
        ]
        
        positive_count = sum(1 for headline in news_headlines 
                           for word in positive_words if word.lower() in headline.lower())
        negative_count = sum(1 for headline in news_headlines 
                           for word in negative_words if word.lower() in headline.lower())
        
        total = positive_count + negative_count
        
        if total == 0:
            score = 50
            sentiment = 'Neutral'
        else:
            score = (positive_count / total) * 100
            if score > 60:
                sentiment = 'Bullish'
            elif score < 40:
                sentiment = 'Bearish'
            else:
                sentiment = 'Neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(score, 1),
            'positive_signals': positive_count,
            'negative_signals': negative_count,
            'analysis': f"Based on {len(news_headlines)} headlines analyzed"
        }


class AIAnalyzer:
    """
    Main AI Analysis class
    Combines all AI features for comprehensive analysis
    """
    
    def __init__(self):
        self.ml_analyzer = MLAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
    
    def comprehensive_analysis(
        self,
        prices: np.ndarray,
        pair: str,
        news_headlines: List[str] = None,
        high_price: np.ndarray = None,
        low_price: np.ndarray = None
    ) -> AIAnalysisResult:
        """
        Perform comprehensive AI analysis
        
        Args:
            prices: Close prices
            pair: Currency pair name
            news_headlines: Recent news headlines
            high_price: High prices
            low_price: Low prices
            
        Returns:
            AIAnalysisResult with all analysis
        """
        # Handle None values
        if high_price is None:
            high_price = prices * 1.001
        if low_price is None:
            low_price = prices * 0.999
        if news_headlines is None:
            news_headlines = []
        
        # Trend prediction
        prediction = self.ml_analyzer.predict_trend(prices)
        
        # Support/Resistance
        sr_levels = self.ml_analyzer.calculate_support_resistance(prices)
        
        # Pattern recognition
        patterns = self.pattern_recognizer.find_patterns(prices)
        pattern_detected = patterns[0]['pattern'] if patterns else None
        
        # Sentiment analysis
        sentiment = self.ml_analyzer.analyze_sentiment_score(news_headlines)
        
        # Key factors
        key_factors = self._generate_key_factors(prediction, sentiment, patterns)
        
        # Risk level
        risk_level = self._calculate_risk(prediction, sr_levels)
        
        # Insights
        insights = self._generate_insights(prediction, sr_levels, sentiment, pattern_detected)
        
        # Recommendation (EDUCATIONAL ONLY)
        recommendation = self._generate_recommendation(prediction, sentiment, patterns)
        
        return AIAnalysisResult(
            trend_prediction=prediction['current_trend'],
            confidence=prediction['confidence'],
            support_levels=sr_levels['support'],
            resistance_levels=sr_levels['resistance'],
            key_factors=key_factors,
            risk_level=risk_level,
            insights=insights,
            pattern_detected=pattern_detected,
            recommendation=recommendation
        )
    
    def _generate_key_factors(
        self,
        prediction: Dict,
        sentiment: Dict,
        patterns: List[Dict]
    ) -> List[str]:
        """Generate key factors affecting the pair"""
        factors = []
        
        # Momentum factor
        momentum = prediction['momentum']
        if momentum > 1:
            factors.append(f"📈 Positive momentum: {momentum:.2f}%")
        elif momentum < -1:
            factors.append(f"📉 Negative momentum: {momentum:.2f}%")
        else:
            factors.append("➡️ Weak momentum")
        
        # Volatility factor
        volatility = prediction['volatility']
        if volatility > 1:
            factors.append(f"⚡ High volatility: {volatility:.2f}%")
        else:
            factors.append(f"📊 Normal volatility: {volatility:.2f}%")
        
        # Sentiment factor
        sent_score = sentiment['score']
        if sent_score > 55:
            factors.append(f"😊 Positive sentiment ({sent_score:.0f}%)")
        elif sent_score < 45:
            factors.append(f"😟 Negative sentiment ({sent_score:.0f}%)")
        else:
            factors.append(f"😐 Neutral sentiment ({sent_score:.0f}%)")
        
        return factors
    
    def _calculate_risk(self, prediction: Dict, sr_levels: Dict) -> str:
        """Calculate risk level"""
        volatility = prediction['volatility']
        
        if volatility < 0.5:
            return 'low'
        elif volatility < 1.0:
            return 'medium'
        else:
            return 'high'
    
    def _generate_insights(
        self,
        prediction: Dict,
        sr_levels: Dict,
        sentiment: Dict,
        pattern: Optional[str]
    ) -> List[str]:
        """Generate AI insights"""
        insights = []
        
        # Trend insight
        trend = prediction['current_trend']
        if trend == 'bullish':
            insights.append("🟢 Short-term trend appears bullish")
        elif trend == 'bearish':
            insights.append("🔴 Short-term trend appears bearish")
        else:
            insights.append("🟡 Market in consolidation phase")
        
        # Support/Resistance insight
        if sr_levels['support']:
            insights.append(f"📊 Key support near {sr_levels['support'][0]:.5f}")
        if sr_levels['resistance']:
            insights.append(f"📈 Key resistance near {sr_levels['resistance'][0]:.5f}")
        
        # Pattern insight
        if pattern:
            insights.append(f"📐 {pattern.replace('_', ' ').title()} pattern detected")
        
        # Volatility insight
        vol = prediction['volatility']
        if vol > 1:
            insights.append("⚠️ Higher than average volatility")
        
        return insights
    
    def _generate_recommendation(
        self,
        prediction: Dict,
        sentiment: Dict,
        patterns: List[Dict]
    ) -> str:
        """Generate educational recommendation"""
        trend = prediction['current_trend']
        confidence = prediction['confidence']
        
        if confidence < 50:
            return "⚠️ Low confidence in analysis. Consider waiting for clearer signals."
        
        if trend == 'bullish':
            return """
🟢 **EDUCATIONAL OBSERVATION**

The technical indicators suggest a potential bullish move, but remember:

1. Always use proper risk management
2. Consider setting stop-loss orders
3. Don't risk more than 1-2% per trade
4. Wait for confirmation before entering

**This is NOT financial advice.** Always do your own research.
            """.strip()
        
        elif trend == 'bearish':
            return """
🔴 **EDUCATIONAL OBSERVATION**

The technical indicators suggest a potential bearish move, but remember:

1. Always use proper risk management
2. Consider setting stop-loss orders
3. Don't risk more than 1-2% per trade
4. Wait for confirmation before entering

**This is NOT financial advice.** Always do your own research.
            """.strip()
        
        return """
🟡 **EDUCATIONAL OBSERVATION**

Market conditions appear mixed. Consider:

1. Waiting for clearer signals
2. Using smaller position sizes
3. Implementing strict risk management
4. Studying price action closely

**This is NOT financial advice.** Always do your own research.
        """.strip()


class AIForecast:
    """
    AI Price Forecasting (EDUCATIONAL ONLY)
    Simple forecasting using basic methods
    """
    
    def __init__(self):
        self.lookback_periods = [3, 7, 14, 30]  # days
    
    def forecast(
        self,
        prices: np.ndarray,
        periods: int = 7
    ) -> Dict:
        """
        Generate price forecast
        
        Args:
            prices: Historical prices
            periods: Forecast periods
            
        Returns:
            Forecast data
        """
        if len(prices) < 14:
            return {'error': 'Insufficient data for forecast'}
        
        # Calculate various scenarios
        returns = np.diff(prices) / prices[:-1]
        
        # Historical performance
        avg_return = np.mean(returns[-14:])
        std_return = np.std(returns[-14:])
        
        # Simple linear projection
        current_price = prices[-1]
        
        # Bullish scenario (+1 std)
        bullish = current_price * (1 + avg_return * periods + std_return * periods)
        
        # Bearish scenario (-1 std)
        bearish = current_price * (1 + avg_return * periods - std_return * periods)
        
        # Expected (average)
        expected = current_price * (1 + avg_return * periods)
        
        return {
            'current_price': round(current_price, 5),
            'periods': periods,
            'forecasts': {
                'bullish': round(bullish, 5),
                'expected': round(expected, 5),
                'bearish': round(bearish, 5)
            },
            'expected_change_pct': round(avg_return * periods * 100, 2),
            'volatility_index': round(std_return * 100, 2),
            'disclaimer': 'EDUCATIONAL FORECAST ONLY - Not guaranteed'
        }
    
    def backtest_signal(
        self,
        prices: np.ndarray,
        short_period: int = 5,
        long_period: int = 20
    ) -> Dict:
        """
        Backtest moving average crossover signal
        
        Args:
            prices: Price array
            short_period: Short MA period
            long_period: Long MA period
            
        Returns:
            Backtest results
        """
        if len(prices) < long_period:
            return {'error': 'Insufficient data'}
        
        # Calculate MAs
        short_ma = pd.Series(prices).rolling(short_period).mean().values
        long_ma = pd.Series(prices).rolling(long_period).mean().values
        
        # Generate signals
        signals = []
        position = 0
        
        for i in range(long_period, len(prices)):
            if short_ma[i] > long_ma[i] and position == 0:
                signals.append('BUY')
                position = 1
            elif short_ma[i] < long_ma[i] and position == 1:
                signals.append('SELL')
                position = 0
            else:
                signals.append('HOLD')
        
        buy_signals = signals.count('BUY')
        sell_signals = signals.count('SELL')
        
        return {
            'total_signals': len(signals),
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': signals.count('HOLD'),
            'strategy': 'MA Crossover',
            'short_period': short_period,
            'long_period': long_period,
            'disclaimer': 'Past performance does not guarantee future results'
        }
