"""
Chart Components Module
Interactive charting for forex analysis
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Optional


class ChartBuilder:
    """
    Chart building utilities for forex analysis
    """
    
    @staticmethod
    def render_candlestick_chart(
        df: pd.DataFrame,
        indicators: Optional[Dict] = None,
        title: str = "Price Chart"
    ) -> go.Figure:
        """
        Create an interactive candlestick chart
        
        Args:
            df: DataFrame with OHLC data
            indicators: Dict of indicator names -> values
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        if df is None or df.empty:
            return ChartBuilder._empty_chart(title)
        
        # Determine subplot rows based on indicators
        num_indicator_rows = 0
        if indicators:
            indicator_names = list(indicators.keys())
            if any('RSI' in name for name in indicator_names):
                num_indicator_rows += 1
            if any('MACD' in name for name in indicator_names):
                num_indicator_rows += 1
        
        if num_indicator_rows > 0:
            fig = make_subplots(
                rows=1 + num_indicator_rows,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(title,) + tuple(indicators.keys()) if indicators else (title,)
            )
        else:
            fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price',
                increasing_line_color='#00C853',
                decreasing_line_color='#D50000'
            ),
            row=1,
            col=1
        )
        
        # Add volume if available
        if 'volume' in df.columns:
            colors = ['#00C853' if df['close'].iloc[i] >= df['open'].iloc[i] else '#D50000' 
                     for i in range(len(df))]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.3
                ),
                row=1,
                col=1
            )
        
        # Add indicators
        current_row = 2
        if indicators:
            for name, values in indicators.items():
                if values is None or len(values) == 0:
                    continue
                
                if 'SMA' in name or 'EMA' in name or 'BB' in name:
                    # Price overlay indicators
                    line_color = '#2196F3' if 'SMA' in name else '#FF9800'
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=values,
                            name=name,
                            line=dict(color=line_color, width=1.5)
                        ),
                        row=1,
                        col=1
                    )
                elif 'RSI' in name:
                    # RSI in separate panel
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=values,
                            name=name,
                            line=dict(color='#9C27B0', width=1.5)
                        ),
                        row=current_row,
                        col=1
                    )
                    # Add overbought/oversold lines
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
                    current_row += 1
                elif 'MACD' in name or 'Histogram' in name:
                    # MACD in separate panel
                    if 'Histogram' in name:
                        colors = ['#00C853' if v >= 0 else '#D50000' for v in values]
                        fig.add_trace(
                            go.Bar(
                                x=df.index,
                                y=values,
                                name='Histogram',
                                marker_color=colors
                            ),
                            row=current_row,
                            col=1
                        )
                    else:
                        fig.add_trace(
                            go.Scatter(
                                x=df.index,
                                y=values,
                                name=name,
                                line=dict(color='#2196F3', width=1.5)
                            ),
                            row=current_row,
                            col=1
                        )
                    current_row += 1
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def render_line_chart(
        data: Dict[str, pd.Series],
        title: str = "Comparison Chart"
    ) -> go.Figure:
        """
        Create a multi-line comparison chart
        
        Args:
            data: Dict of series names -> data
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        colors = ['#2196F3', '#00C853', '#FF9800', '#E91E63', '#9C27B0']
        
        for idx, (name, series) in enumerate(data.items()):
            fig.add_trace(
                go.Scatter(
                    x=series.index,
                    y=series.values,
                    name=name,
                    line=dict(color=colors[idx % len(colors)], width=2)
                )
            )
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=400,
            xaxis_title="Date",
            yaxis_title="Rate"
        )
        
        return fig
    
    @staticmethod
    def render_forex_heatmap(data: Dict[str, float]) -> go.Figure:
        """
        Create a heatmap of currency correlations or rates
        
        Args:
            data: Dict of currency pairs -> rates
            
        Returns:
            Plotly figure object
        """
        # Create simple heatmap data
        pairs = list(data.keys())
        values = list(data.values())
        
        # Normalize values for color scale
        min_val = min(values)
        max_val = max(values)
        normalized = [(v - min_val) / (max_val - min_val) if max_val > min_val else 0.5 
                     for v in values]
        
        fig = go.Figure(data=go.Scatter(
            x=pairs,
            y=['Rate'] * len(pairs),
            mode='markers+text',
            marker=dict(
                size=100,
                color=normalized,
                colorscale='RdYlGn',
                showscale=True
            ),
            text=[f'{v:.5f}' for v in values],
            textposition='middle center',
            hoverinfo='text',
            hovertext=[f'{p}: {v:.5f}' for p, v in zip(pairs, values)]
        ))
        
        fig.update_layout(
            title="Live Rates Heatmap",
            template='plotly_dark',
            height=200,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def render_pie_chart(
        labels: list,
        values: list,
        title: str = "Distribution"
    ) -> go.Figure:
        """
        Create a pie chart
        
        Args:
            labels: List of labels
            values: List of values
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(
                colors=['#2196F3', '#00C853', '#FF9800', '#E91E63', '#9C27B0']
            )
        )])
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=350
        )
        
        return fig
    
    @staticmethod
    def render_bar_chart(
        categories: list,
        values: list,
        title: str = "Chart"
    ) -> go.Figure:
        """
        Create a bar chart
        
        Args:
            categories: List of categories
            values: List of values
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=values,
            marker_color=['#00C853' if v >= 0 else '#D50000' for v in values]
        )])
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=350
        )
        
        return fig
    
    @staticmethod
    def _empty_chart(title: str) -> go.Figure:
        """Create an empty chart placeholder"""
        fig = go.Figure()
        
        fig.update_layout(
            title=title,
            template='plotly_dark',
            annotations=[dict(
                text="No data available",
                showarrow=False,
                x=0.5,
                y=0.5
            )]
        )
        
        return fig
