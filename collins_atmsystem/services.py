"""
Business logic layer for ATM operations.

This module contains the core banking operations and is completely
independent of UI concerns. Both CLI and GUI interfaces use these
services, ensuring consistent behavior across all interfaces.

Design Pattern: Service Layer
- Encapsulates all business rules
- No UI dependencies
- Highly testable and reusable
"""

from typing import Optional, Tuple, List
from decimal import Decimal

from .models import Account, Transaction
from .database import ATMDatabase
from .config import (
    MAX_LOGIN_ATTEMPTS,
    MIN_PIN_LENGTH,
    MAX_PIN_LENGTH,
    PIN_NUMERIC_ONLY,
    MIN_TRANSACTION_AMOUNT,
    MAX_WITHDRAWAL_AMOUNT,
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InsufficientFundsError(Exception):
    """Raised when withdrawal amount exceeds balance."""
    pass


class ATMService:
    """
    Core ATM service providing all banking operations.
    
    This service is the single source of truth for business logic.
    All UI components delegate to this service for user-facing operations.
    """

    def __init__(self, database: ATMDatabase):
        """
        Initialize the ATM service with a database instance.
        
        Args:
            database: ATMDatabase instance for persistence
        """
        self.db = database
        self.current_user: Optional[Account] = None
        self.login_attempts = 0

    # ========================================================================
    # ACCOUNT MANAGEMENT
    # ========================================================================

    def create_account(self, username: str, pin: str) -> Tuple[bool, str]:
        """
        Create a new bank account.
        
        Validates input and prevents duplicate usernames.
        
        Args:
            username: Desired username (must be unique)
            pin: 4-digit PIN for authentication
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Input validation
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if not pin or not isinstance(pin, str):
            return False, "PIN is required"
        
        pin = pin.strip()
        
        # PIN validation
        if len(pin) != MAX_PIN_LENGTH:
            return False, f"PIN must be exactly {MAX_PIN_LENGTH} characters"
        
        if PIN_NUMERIC_ONLY and not pin.isdigit():
            return False, "PIN must contain only digits"
        
        # Check for duplicate username
        if self.db.account_exists(username):
            return False, "Username already exists"
        
        # Create and save account
        account = Account(username=username, pin=pin)
        if self.db.create_account(account):
            return True, f"Account '{username}' created successfully"
        else:
            return False, "Failed to create account (database error)"

    def authenticate(self, username: str, pin: str) -> Tuple[bool, str]:
        """
        Authenticate a user with username and PIN.
        
        Tracks login attempts and locks account after max attempts.
        Note: This is a simple implementation. In production, implement
        proper account locking with unlock mechanisms.
        
        Args:
            username: Username to authenticate
            pin: PIN to verify
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Input validation
        if not username or not pin:
            self.login_attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - self.login_attempts
            return False, f"Username and PIN required ({remaining} attempts left)"
        
        # Get account from database
        account = self.db.get_account(username)
        if account is None:
            self.login_attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - self.login_attempts
            return False, f"Invalid username or PIN ({remaining} attempts left)"
        
        # Verify PIN (plaintext comparison for now)
        # TODO: In production, use: if not verify_hash(pin, account.pin_hash):
        if account.pin != pin:
            self.login_attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - self.login_attempts
            return False, f"Invalid username or PIN ({remaining} attempts left)"
        
        # Check max login attempts
        if self.login_attempts >= MAX_LOGIN_ATTEMPTS:
            return False, "Maximum login attempts exceeded. Please try again later."
        
        # Successful authentication
        self.current_user = account
        self.login_attempts = 0
        return True, f"Welcome, {username}!"

    def logout(self) -> Tuple[bool, str]:
        """
        Log out the current user.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.current_user is None:
            return False, "No user currently logged in"
        
        username = self.current_user.username
        self.current_user = None
        self.login_attempts = 0
        return True, f"Logged out successfully"

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None

    # ========================================================================
    # BALANCE AND TRANSACTION OPERATIONS
    # ========================================================================

    def get_balance(self) -> Tuple[bool, float, str]:
        """
        Get the current balance of the authenticated user.
        
        Returns:
            Tuple of (success: bool, balance: float, message: str)
        """
        if not self.is_authenticated():
            return False, 0.0, "Not authenticated"
        
        return True, self.current_user.balance, f"Current balance: ${self.current_user.balance:.2f}"

    def deposit(self, amount: float) -> Tuple[bool, str]:
        """
        Deposit funds into the account.
        
        Args:
            amount: Amount to deposit (must be positive)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"
        
        # Input validation
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Invalid amount. Please enter a valid number."
        
        if amount <= 0:
            return False, "Deposit amount must be positive"
        
        if amount < MIN_TRANSACTION_AMOUNT:
            return False, f"Minimum deposit amount is ${MIN_TRANSACTION_AMOUNT:.2f}"
        
        # Process deposit
        self.current_user.balance += amount
        self.current_user.add_transaction('DEPOSIT', amount)
        
        # Persist changes
        if not self.db.update_account(self.current_user):
            return False, "Failed to process deposit (database error)"
        
        return True, f"Deposited ${amount:.2f}. New balance: ${self.current_user.balance:.2f}"

    def withdraw(self, amount: float) -> Tuple[bool, str]:
        """
        Withdraw funds from the account.
        
        Args:
            amount: Amount to withdraw (must be positive and available)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"
        
        # Input validation
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Invalid amount. Please enter a valid number."
        
        if amount <= 0:
            return False, "Withdrawal amount must be positive"
        
        if amount < MIN_TRANSACTION_AMOUNT:
            return False, f"Minimum withdrawal amount is ${MIN_TRANSACTION_AMOUNT:.2f}"
        
        if amount > MAX_WITHDRAWAL_AMOUNT:
            return False, f"Maximum withdrawal amount is ${MAX_WITHDRAWAL_AMOUNT:.2f}"
        
        # Check sufficient funds
        if amount > self.current_user.balance:
            return False, f"Insufficient funds. Available balance: ${self.current_user.balance:.2f}"
        
        # Process withdrawal
        self.current_user.balance -= amount
        self.current_user.add_transaction('WITHDRAWAL', amount)
        
        # Persist changes
        if not self.db.update_account(self.current_user):
            return False, "Failed to process withdrawal (database error)"
        
        return True, f"Withdrew ${amount:.2f}. New balance: ${self.current_user.balance:.2f}"

    # ========================================================================
    # TRANSACTION HISTORY
    # ========================================================================

    def get_transaction_history(self, limit: Optional[int] = None) -> Tuple[bool, List[Transaction], str]:
        """
        Get transaction history for the authenticated user.
        
        Args:
            limit: Maximum number of recent transactions to return (None = all)
            
        Returns:
            Tuple of (success: bool, transactions: List[Transaction], message: str)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"
        
        transactions = self.current_user.transactions
        
        if limit:
            transactions = transactions[-limit:]
        
        if not transactions:
            return True, [], "No transactions found"
        
        return True, transactions, f"Retrieved {len(transactions)} transaction(s)"

    def get_formatted_transaction_history(self, limit: Optional[int] = None) -> str:
        """
        Get a formatted string of transaction history for display.
        
        Args:
            limit: Maximum number of recent transactions to return
            
        Returns:
            Formatted transaction history string
        """
        success, transactions, message = self.get_transaction_history(limit)
        
        if not success or not transactions:
            return message
        
        output = f"Transaction History (Last {limit or len(transactions)} transactions):\n"
        output += "=" * 70 + "\n"
        output += f"{'Date/Time':<25} {'Type':<12} {'Amount':<15} {'Balance':<12}\n"
        output += "-" * 70 + "\n"
        
        for txn in transactions:
            dt = txn.timestamp.split('T')[0] + ' ' + txn.timestamp.split('T')[1][:8]
            output += f"{dt:<25} {txn.transaction_type:<12} ${txn.amount:>10.2f}   ${txn.balance_after:>10.2f}\n"
        
        output += "=" * 70
        return output

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def get_current_username(self) -> Optional[str]:
        """Get the username of the currently authenticated user."""
        if self.current_user:
            return self.current_user.username
        return None

    def reset_login_attempts(self) -> None:
        """Reset login attempt counter (useful after successful login)."""
        self.login_attempts = 0
