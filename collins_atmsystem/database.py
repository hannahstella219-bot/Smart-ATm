"""
Database layer for persistent storage of accounts.

This module handles all JSON file I/O operations. By centralizing database
operations here, we maintain a clear separation of concerns and can easily
swap the storage mechanism (e.g., to a SQL database) without affecting
the business logic layer.
"""

import json
import threading
from typing import Dict, Optional
from pathlib import Path

from .models import Account
from .config import ACCOUNTS_FILE, DEBUG_MODE


class ATMDatabase:
    """
    Thread-safe JSON database for account storage.
    
    Uses a lock to ensure thread-safe access to the JSON file, preventing
    race conditions if multiple operations occur simultaneously.
    
    Design Pattern: Repository Pattern
    - Abstracts all data persistence operations
    - Business logic never directly accesses files
    """

    def __init__(self, file_path: Path = ACCOUNTS_FILE):
        """
        Initialize the database with a file path.
        
        Args:
            file_path: Path to the JSON accounts file
        """
        self.file_path = file_path
        self._lock = threading.RLock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create an empty accounts file if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_to_file({})

    def _read_from_file(self) -> Dict[str, dict]:
        """
        Read all accounts from the JSON file.
        
        Returns:
            Dictionary mapping usernames to account dictionaries
        """
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            if DEBUG_MODE:
                print(f"DEBUG: Database file not found or invalid. Creating new one.")
            return {}

    def _write_to_file(self, data: Dict[str, dict]) -> None:
        """
        Write all accounts to the JSON file.
        
        Args:
            data: Dictionary mapping usernames to account dictionaries
        """
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_account(self, account: Account) -> bool:
        """
        Create a new account.
        
        Args:
            account: Account instance to save
            
        Returns:
            True if account was created, False if username already exists
        """
        with self._lock:
            data = self._read_from_file()
            
            if account.username in data:
                return False
            
            data[account.username] = account.to_dict()
            self._write_to_file(data)
            return True

    def get_account(self, username: str) -> Optional[Account]:
        """
        Retrieve an account by username.
        
        Args:
            username: The username to look up
            
        Returns:
            Account instance if found, None otherwise
        """
        with self._lock:
            data = self._read_from_file()
            account_data = data.get(username)
            
            if account_data is None:
                return None
            
            return Account.from_dict(account_data)

    def update_account(self, account: Account) -> bool:
        """
        Update an existing account.
        
        Args:
            account: Account instance with updated data
            
        Returns:
            True if account was updated, False if not found
        """
        with self._lock:
            data = self._read_from_file()
            
            if account.username not in data:
                return False
            
            data[account.username] = account.to_dict()
            self._write_to_file(data)
            return True

    def account_exists(self, username: str) -> bool:
        """
        Check if an account exists.
        
        Args:
            username: The username to check
            
        Returns:
            True if account exists, False otherwise
        """
        with self._lock:
            data = self._read_from_file()
            return username in data

    def get_all_accounts(self) -> Dict[str, Account]:
        """
        Get all accounts (useful for debugging or admin functions).
        
        Returns:
            Dictionary mapping usernames to Account instances
        """
        with self._lock:
            data = self._read_from_file()
            return {
                username: Account.from_dict(account_data)
                for username, account_data in data.items()
            }

    def delete_account(self, username: str) -> bool:
        """
        Delete an account (for testing or admin purposes).
        
        Args:
            username: The username to delete
            
        Returns:
            True if account was deleted, False if not found
        """
        with self._lock:
            data = self._read_from_file()
            
            if username not in data:
                return False
            
            del data[username]
            self._write_to_file(data)
            return True
