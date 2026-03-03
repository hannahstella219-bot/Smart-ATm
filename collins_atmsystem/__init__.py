"""
SmartATM - A production-quality ATM system with CLI and GUI interfaces.

This package provides a complete banking simulation system with:
- Account creation and authentication
- Deposit, withdraw, and balance operations
- Transaction history tracking
- Both CLI and GUI interfaces
- Persistent JSON storage

Author: ATM System
Version: 1.0.0
"""

from .models import Account, Transaction
from .services import ATMService
from .database import ATMDatabase
from .cli import ATMCLI, run_cli
from .gui import ATMGUI, run_gui

__all__ = [
    'Account',
    'Transaction',
    'ATMService',
    'ATMDatabase',
    'ATMCLI',
    'ATMGUI',
    'run_cli',
    'run_gui',
]

__version__ = '1.0.0'
