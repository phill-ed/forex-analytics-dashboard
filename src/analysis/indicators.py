"""
Technical Analysis Indicators Module
Calculates various technical indicators for forex analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class Trend(Enum):
    """Trend direction enum"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Signal(Enum):
    """Trading signal enum"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NEUTRAL = "neutral"


@dataclass
class AnalysisResult:
    """Container for analysis results"""
    trend: Trend
    signal: Signal
    confidence: float  # 0-100
    indicators: Dict
    summary: str


class TechnicalIndicators:
    """
    Technical analysis indicators calculator
    Includes popular indicators used in forex trading
    """
    
    def __init__(self):
        pass
    
    # ==================== Moving Averages ====================
    
    def sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """
        Simple Moving Average
        
        Args:
            data: Price array
            period: SMA period
            
        Returns:
            SMA values
        """
        return pd.Series(data).rolling(window=period).mean().values
    
    def ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """
        Exponential Moving Average
        
        Args:
            data: Price array
            period: EMA period
            
        Returns:
            EMA values
        """
        return pd.Series(data).ewm(span=period, adjust=False).mean().values
    
    def wma(self, data: np.ndarray, period: int) -> np.ndarray:
        """
        Weighted Moving Average
        
        Args:
            data: Price array
            period: WMA period
            
        Returns:
            WMA values
        """
        weights = np.arange(1, period + 1)
        return pd.Series(data).rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum()
        ).values
    
    def hma(self, data: np.ndarray, period: int) -> np.ndarray:
        """
        Hull Moving Average
        
        Args:
            data: Price array
            period: HMA period
            
        Returns:
            HMA values
        """
        half_period = int(period / 2)
        sqrt_period = int(np.sqrt(period))
        
        wma_half = self.wma(data, half_period)
        wma_full = self.wma(data, period)
        
        hma = 2 * wma_half - wma_full
        return self.wma(hma, sqrt_period)
    
    # ==================== Momentum Indicators ====================
    
    def rsi(self, data: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Relative Strength Index
        
        Args:
            data: Price array (typically close prices)
            period: RSI period
            
        Returns:
            RSI values (0-100)
        """
        prices = pd.Series(data)
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = (-delta).where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gain = gains.rolling(window=period).mean()
        avg_loss = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.values
    
    def stochastic(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: %K period
            d_period: %D period
            
        Returns:
            Tuple of (%K, %D) arrays
        """
        low_min = pd.Series(low).rolling(window=k_period).min()
        high_max = pd.Series(high).rolling(window=k_period).max()
        
        stoch_k = 100 * (pd.Series(close) - low_min) / (high_max - low_min)
        stoch_d = stoch_k.rolling(window=d_period).mean()
        
        return stoch_k.values, stoch_d.values
    
    def roc(self, data: np.ndarray, period: int = 10) -> np.ndarray:
        """
        Rate of Change
        
        Args:
            data: Price array
            period: ROC period
            
        Returns:
            ROC values
        """
        return pd.Series(data).pct_change(periods=period) * 100
    
    def momentum(self, data: np.ndarray, period: int = 10) -> np.ndarray:
        """
        Momentum indicator
        
        Args:
            data: Price array
            period: Momentum period
            
        Returns:
            Momentum values
        """
        return pd.Series(data) - pd.Series(data).shift(period)
    
    # ==================== Trend Indicators ====================
    
    def macd(
        self,
        data: np.ndarray,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Moving Average Convergence Divergence
        
        Args:
            data: Price array
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = self.ema(data, fast_period)
        ema_slow = self.ema(data, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def adx(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Average Directional Index
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period
            
        Returns:
            Tuple of (ADX, +DI, -DI)
        """
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        # Calculate True Range
        tr1 = high_series - low_series
        tr2 = abs(high_series - close_series.shift(1))
        tr3 = abs(low_series - close_series.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        plus_dm = high_series.diff()
        minus_dm = -low_series.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Smoothed values
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx.values, plus_di.values, minus_di.values
    
    # ==================== Volatility Indicators ====================
    
    def bollinger_bands(
        self,
        data: np.ndarray,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Bollinger Bands
        
        Args:
            data: Price array
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle = self.sma(data, period)
        std = pd.Series(data).rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper.values, middle.values, lower.values
    
    def atr(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Average True Range
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
            
        Returns:
            ATR values
        """
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        
        tr1 = high_series - low_series
        tr2 = abs(high_series - close_series.shift(1))
        tr3 = abs(low_series - close_series.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return tr.rolling(window=period).mean().values
    
    def donchian_channel(
        self,
        high: np.ndarray,
        low: np.ndarray,
        period: int = 20
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Donchian Channel
        
        Args:
            high: High prices
            low: Low prices
            period: Channel period
            
        Returns:
            Tuple of (Upper, Middle, Lower)
        """
        upper = pd.Series(high).rolling(window=period).max()
        lower = pd.Series(low).rolling(window=period).min()
        middle = (upper + lower) / 2
        
        return upper.values, middle.values, lower.values
    
    # ==================== Support/Resistance ====================
    
    def fibonacci_retracements(
        self,
        high: np.ndarray,
        low: np.ndarray
    ) -> Dict[float, float]:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            high: Swing high
            low: Swing low
            
        Returns:
            Dict of level -> price
        """
        diff = high - low
        levels = {
            0: high,
            0.236: high - (diff * 0.236),
            0.382: high - (diff * 0.382),
            0.5: high - (diff * 0.5),
            0.618: high - (diff * 0.618),
            0.786: high - (diff * 0.786),
            1: low
        }
        return levels
    
    def pivot_points(
        self,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate pivot points
        
        Args:
            high: Previous high
            low: Previous low
            close: Previous close
            
        Returns:
            Dict of pivot levels
        """
        pivot = (high + low + close) / 3
        
        return {
            'R4': high + 3 * (pivot - low),
            'R3': high + 2 * (pivot - low),
            'R2': pivot + (high - low),
            'R1': 2 * pivot - low,
            'PP': pivot,
            'S1': 2 * pivot - high,
            'S2': pivot - (high - low),
            'S3': low - 2 * (high - pivot),
            'S4': low - 3 * (high - pivot)
        }
    
    # ==================== Analysis Functions ====================
    
    def analyze(self, data: np.ndarray) -> AnalysisResult:
        """
        Perform complete technical analysis
        
        Args:
            data: Price array (OHLC close)
            
        Returns:
            AnalysisResult with all indicators and signals
        """
        indicators = {}
        
        # Moving averages
        indicators['sma_20'] = self.sma(data, 20)[-1]
        indicators['sma_50'] = self.sma(data, 50)[-1]
        indicators['sma_200'] = self.sma(data, 200)[-1] if len(data) > 200 else None
        
        # EMA
        indicators['ema_12'] = self.ema(data, 12)[-1]
        indicators['ema_26'] = self.ema(data, 26)[-1]
        
        # RSI
        rsi_val = self.rsi(data, 14)[-1]
        indicators['rsi'] = rsi_val
        indicators['rsi_signal'] = 'overbought' if rsi_val > 70 else ('oversold' if rsi_val < 30 else 'neutral')
        
        # MACD
        macd_line, signal_line, histogram = self.macd(data)
        indicators['macd'] = macd_line[-1]
        indicators['macd_signal'] = signal_line[-1]
        indicators['macd_histogram'] = histogram[-1]
        
        # Bollinger Bands
        upper, middle, lower = self.bollinger_bands(data)
        indicators['bb_upper'] = upper[-1]
        indicators['bb_middle'] = middle[-1]
        indicators['bb_lower'] = lower[-1]
        
        # Determine trend
        trend = self._determine_trend(indicators)
        
        # Generate signal
        signal, confidence = self._generate_signal(indicators, rsi_val)
        
        # Generate summary
        summary = self._generate_summary(trend, signal, indicators)
        
        return AnalysisResult(
            trend=trend,
            signal=signal,
            confidence=confidence,
            indicators=indicators,
            summary=summary
        )
    
    def _determine_trend(self, indicators: Dict) -> Trend:
        """Determine current trend from indicators"""
        price = indicators.get('ema_12', 0)
        sma20 = indicators.get('sma_20', 0)
        sma50 = indicators.get('sma_50', 0)
        
        bullish_count = 0
        bearish_count = 0
        
        if price > sma20:
            bullish_count += 1
        else:
            bearish_count += 1
        
        if sma20 > sma50:
            bullish_count += 1
        else:
            bearish_count += 1
        
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        
        if macd > macd_signal:
            bullish_count += 1
        else:
            bearish_count += 1
        
        if bullish_count > bearish_count:
            return Trend.BULLISH
        elif bearish_count > bullish_count:
            return Trend.BEARISH
        else:
            return Trend.NEUTRAL
    
    def _generate_signal(
        self,
        indicators: Dict,
        rsi_val: float
    ) -> Tuple[Signal, float]:
        """Generate trading signal with confidence"""
        score = 0
        max_score = 100
        
        # RSI signals
        if rsi_val < 30:
            score += 30  # Oversold - buy signal
        elif rsi_val > 70:
            score -= 30  # Overbought - sell signal
        
        # MACD signals
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        
        if macd > macd_signal:
            score += 20
        else:
            score -= 20
        
        # Price vs SMA
        price = indicators.get('ema_12', 0)
        sma20 = indicators.get('sma_20', 0)
        
        if price > sma20:
            score += 20
        else:
            score -= 20
        
        # Bollinger Band position
        price = indicators.get('bb_middle', price)
        bb_upper = indicators.get('bb_upper', price * 1.02)
        bb_lower = indicators.get('bb_lower', price * 0.98)
        
        if price < bb_lower:
            score += 15  # Near lower band - potentially oversold
        elif price > bb_upper:
            score -= 15  # Near upper band - potentially overbought
        
        # Convert score to signal
        if score > 40:
            return Signal.BUY, min(score, 95)
        elif score < -40:
            return Signal.SELL, min(abs(score), 95)
        else:
            return Signal.HOLD, 50
    
    def _generate_summary(
        self,
        trend: Trend,
        signal: Signal,
        indicators: Dict
    ) -> str:
        """Generate human-readable analysis summary"""
        parts = []
        
        # Trend summary
        parts.append(f"Trend: {trend.value.upper()}")
        
        # RSI summary
        rsi = indicators.get('rsi', 50)
        parts.append(f"RSI: {rsi:.1f} ({indicators.get('rsi_signal', 'neutral')})")
        
        # MACD summary
        macd = indicators.get('macd', 0)
        parts.append(f"MACD: {macd:.5f}")
        
        # Signal
        parts.append(f"Signal: {signal.value.upper()}")
        
        return " | ".join(parts)
