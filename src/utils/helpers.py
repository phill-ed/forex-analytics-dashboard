"""
Utility Functions Module
"""

import os
from datetime import datetime
from typing import Any, Dict
import json


def load_config() -> Dict:
    """Load configuration from .env file"""
    config = {}
    
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config


def save_config(config: Dict) -> None:
    """Save configuration to .env file"""
    with open('.env', 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")


def format_timestamp(ts: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts


def format_currency(value: float, currency: str = 'USD') -> str:
    """Format currency value"""
    if currency == 'USD':
        return f"${value:,.2f}"
    elif currency == 'IDR':
        return f"Rp {value:,.0f}"
    elif currency == 'JPY':
        return f"¥{value:,.0f}"
    else:
        return f"{value:,.2f}"


def calculate_pip_value(
    pair: str,
    lot_size: float = 100000,
    account_currency: str = 'USD'
) -> float:
    """
    Calculate pip value for a currency pair
    
    Args:
        pair: Currency pair
        lot_size: Position size in base currency
        account_currency: Account currency
        
    Returns:
        Pip value in account currency
    """
    # Pip size for most pairs
    if 'JPY' in pair:
        pip_size = 0.01
    else:
        pip_size = 0.0001
    
    return pip_size * lot_size


def validate_pair(pair: str) -> bool:
    """Validate currency pair format"""
    valid_pairs = [
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD',
        'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'USD/IDR', 'USD/SGD',
        'EUR/AUD', 'AUD/JPY', 'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'AUD/CAD',
        'EUR/CHF', 'GBP/CHF', 'AUD/NZD', 'EUR/NZD', 'USD/HKD', 'USD/MXN'
    ]
    
    return pair in valid_pairs


def get_pair_info(pair: str) -> Dict[str, str]:
    """Get information about a currency pair"""
    info = {
        'EUR/USD': {'base': 'Euro', 'quote': 'US Dollar', 'pip': '0.0001'},
        'GBP/USD': {'base': 'British Pound', 'quote': 'US Dollar', 'pip': '0.0001'},
        'USD/JPY': {'base': 'US Dollar', 'quote': 'Japanese Yen', 'pip': '0.01'},
        'USD/CHF': {'base': 'US Dollar', 'quote': 'Swiss Franc', 'pip': '0.0001'},
        'USD/IDR': {'base': 'US Dollar', 'quote': 'Indonesian Rupiah', 'pip': '1'},
    }
    
    return info.get(pair, {'base': 'Unknown', 'quote': 'Unknown', 'pip': '0.0001'})
