"""
Configuration and constants for the ATM system.

This module centralizes all configurable settings, making it easy
to adjust behavior without changing business logic code.
"""

import os
from pathlib import Path

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_NAME = "SmartATM"
APP_VERSION = "1.0.0"

# ============================================================================
# FILE PATHS
# ============================================================================

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# PIN validation
MIN_PIN_LENGTH = 4
MAX_PIN_LENGTH = 4
PIN_NUMERIC_ONLY = True

# Authentication
MAX_LOGIN_ATTEMPTS = 3
DEFAULT_BALANCE = 0.0

# ============================================================================
# TRANSACTION SETTINGS
# ============================================================================

# Transaction limits
MIN_TRANSACTION_AMOUNT = 0.01
MAX_WITHDRAWAL_AMOUNT = 10000.00

# ============================================================================
# UI SETTINGS (GUI)
# ============================================================================

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600
WINDOW_TITLE = f"{APP_NAME} - ATM System"

# ============================================================================
# LOGGING AND DEBUGGING
# ============================================================================

# Can be set to True for development
DEBUG_MODE = False
