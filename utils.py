"""
Utility functions for CryptoVerde
"""

import os
import json
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger("CryptoVerde.Utils")

def setup_directories():
    """Create necessary directories"""
    os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)

def save_json(data, filename):
    """Save data as JSON"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        return False

def load_json(filename):
    """Load data from JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return {}

def format_timestamp(dt=None):
    """Format timestamp for filenames"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y%m%d_%H%M%S")

def safe_divide(a, b, default=0):
    """Safe division to avoid zero division"""
    try:
        return a / b if b != 0 else default
    except:
        return default