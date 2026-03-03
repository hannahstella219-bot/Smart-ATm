"""
Data models for the ATM system.

This module defines the core data structures used throughout the application:
- Account: Represents a user account with authentication and balance
- Transaction: Represents a single banking operation with timestamp
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List


@dataclass
class Transaction:
    """
    Represents a single transaction in the transaction history.
    
    Attributes:
        timestamp: When the transaction occurred (ISO format string)
        transaction_type: 'DEPOSIT' or 'WITHDRAWAL'
        amount: Transaction amount in decimal format (float)
        balance_after: Account balance immediately after transaction
    """
    timestamp: str
    transaction_type: str  # 'DEPOSIT' or 'WITHDRAWAL'
    amount: float
    balance_after: float

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create a Transaction instance from a dictionary."""
        return cls(**data)

    def to_dict(self) -> dict:
        """Convert Transaction to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Account:
    """
    Represents a user account with authentication and transaction history.
    
    Attributes:
        username: Unique identifier for the account
        pin: 4-digit PIN (stored as string for flexibility with hashing)
        balance: Current account balance (float)
        transactions: List of Transaction objects
        created_at: Account creation timestamp
    
    Note: PIN is currently stored in plaintext. For production, implement
    hashing using bcrypt, argon2, or similar. The structure supports this
    easily by modifying the services layer to hash/verify instead of comparing.
    """
    username: str
    pin: str
    balance: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """
        Create an Account instance from a dictionary (from JSON storage).
        
        Args:
            data: Dictionary with account data
            
        Returns:
            Account instance with transactions properly deserialized
        """
        transactions = [
            Transaction.from_dict(t) for t in data.get('transactions', [])
        ]
        return cls(
            username=data['username'],
            pin=data['pin'],
            balance=data.get('balance', 0.0),
            transactions=transactions,
            created_at=data.get('created_at', datetime.now().isoformat())
        )

    def to_dict(self) -> dict:
        """
        Convert Account to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all account data, transactions serialized as dicts
        """
        return {
            'username': self.username,
            'pin': self.pin,
            'balance': self.balance,
            'transactions': [t.to_dict() for t in self.transactions],
            'created_at': self.created_at
        }

    def add_transaction(self, transaction_type: str, amount: float) -> None:
        """
        Add a transaction to the account's history.
        
        Args:
            transaction_type: 'DEPOSIT' or 'WITHDRAWAL'
            amount: Transaction amount
        """
        transaction = Transaction(
            timestamp=datetime.now().isoformat(),
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance
        )
        self.transactions.append(transaction)
