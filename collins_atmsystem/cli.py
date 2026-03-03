"""
Command-line interface for the ATM system.

This module provides a menu-driven CLI that uses the ATMService layer
for all operations. The CLI is completely independent of business logic,
making it easy to maintain and test.

Design Pattern: View (MVC)
- Handles all user interaction via CLI
- Delegates all operations to ATMService
- Formats output for terminal display
"""

import sys
from typing import Optional

from .services import ATMService
from .database import ATMDatabase


class ATMCLI:
    """
    Command-line interface for ATM operations.
    
    Provides a menu-driven interface for user interaction while
    maintaining complete separation from business logic.
    """

    def __init__(self, service: ATMService):
        """
        Initialize the CLI with an ATM service.
        
        Args:
            service: ATMService instance for business logic
        """
        self.service = service

    def print_header(self, title: str) -> None:
        """Print a formatted header."""
        print(f"\n{'=' * 60}")
        print(f"{title.center(60)}")
        print(f"{'=' * 60}\n")

    def print_section(self, title: str) -> None:
        """Print a formatted section separator."""
        print(f"\n{title}")
        print("-" * 60)

    def print_success(self, message: str) -> None:
        """Print a success message."""
        print(f"✓ {message}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        print(f"✗ {message}")

    def print_info(self, message: str) -> None:
        """Print an informational message."""
        print(f"ℹ {message}")

    def get_input(self, prompt: str) -> str:
        """Get input from user, handling EOF gracefully."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return ""

    def run(self) -> None:
        """
        Main entry point for the CLI.
        
        Displays the authentication menu until user logs in,
        then shows the ATM menu with available operations.
        """
        self.print_header("Welcome to SmartATM")

        while True:
            if not self.service.is_authenticated():
                self.show_authentication_menu()
            else:
                self.show_atm_menu()

    # ========================================================================
    # AUTHENTICATION MENU
    # ========================================================================

    def show_authentication_menu(self) -> None:
        """Display the authentication menu (login/register)."""
        self.print_section("Authentication Menu")
        print("1. Login to existing account")
        print("2. Create new account")
        print("3. Exit")

        choice = self.get_input("\nEnter your choice (1-3): ")

        if choice == "1":
            self.handle_login()
        elif choice == "2":
            self.handle_create_account()
        elif choice == "3":
            self.print_info("Thank you for using SmartATM. Goodbye!")
            sys.exit(0)
        else:
            self.print_error("Invalid choice. Please try again.")

    def handle_login(self) -> None:
        """Handle user login."""
        self.print_section("Login")

        username = self.get_input("Enter username: ")
        pin = self.get_input("Enter PIN: ")

        success, message = self.service.authenticate(username, pin)

        if success:
            self.print_success(message)
        else:
            self.print_error(message)

    def handle_create_account(self) -> None:
        """Handle new account creation."""
        self.print_section("Create New Account")

        username = self.get_input("Enter desired username (min 3 characters): ")
        pin = self.get_input("Enter 4-digit PIN: ")
        pin_confirm = self.get_input("Confirm PIN: ")

        if pin != pin_confirm:
            self.print_error("PINs do not match")
            return

        success, message = self.service.create_account(username, pin)

        if success:
            self.print_success(message)
        else:
            self.print_error(message)

    # ========================================================================
    # ATM MENU
    # ========================================================================

    def show_atm_menu(self) -> None:
        """Display the main ATM menu."""
        username = self.service.get_current_username()
        self.print_section(f"ATM Menu - {username}")

        print("1. Check Balance")
        print("2. Deposit Funds")
        print("3. Withdraw Funds")
        print("4. Transaction History")
        print("5. Logout")

        choice = self.get_input("\nEnter your choice (1-5): ")

        if choice == "1":
            self.handle_check_balance()
        elif choice == "2":
            self.handle_deposit()
        elif choice == "3":
            self.handle_withdraw()
        elif choice == "4":
            self.handle_transaction_history()
        elif choice == "5":
            self.handle_logout()
        else:
            self.print_error("Invalid choice. Please try again.")

    def handle_check_balance(self) -> None:
        """Handle balance inquiry."""
        success, balance, message = self.service.get_balance()
        if success:
            self.print_success(f"Balance: ${balance:.2f}")
        else:
            self.print_error(message)

    def handle_deposit(self) -> None:
        """Handle deposit operation."""
        self.print_section("Deposit Funds")

        try:
            amount_str = self.get_input("Enter deposit amount: $")
            if not amount_str:
                self.print_error("Cancelled")
                return

            amount = float(amount_str)
            success, message = self.service.deposit(amount)

            if success:
                self.print_success(message)
            else:
                self.print_error(message)

        except ValueError:
            self.print_error("Invalid amount entered")

    def handle_withdraw(self) -> None:
        """Handle withdrawal operation."""
        self.print_section("Withdraw Funds")

        try:
            amount_str = self.get_input("Enter withdrawal amount: $")
            if not amount_str:
                self.print_error("Cancelled")
                return

            amount = float(amount_str)
            success, message = self.service.withdraw(amount)

            if success:
                self.print_success(message)
            else:
                self.print_error(message)

        except ValueError:
            self.print_error("Invalid amount entered")

    def handle_transaction_history(self) -> None:
        """Handle transaction history display."""
        self.print_section("Transaction History")

        history = self.service.get_formatted_transaction_history(limit=10)
        print(history)

    def handle_logout(self) -> None:
        """Handle logout operation."""
        success, message = self.service.logout()
        if success:
            self.print_success(message)


def run_cli() -> None:
    """
    Initialize and run the CLI application.
    
    This is the entry point for command-line mode.
    """
    db = ATMDatabase()
    service = ATMService(db)
    cli = ATMCLI(service)
    cli.run()
