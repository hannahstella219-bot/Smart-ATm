"""
Main entry point for the ATM system.

Allows users to choose between CLI and GUI interfaces.
Both interfaces share the same business logic through ATMService.
"""

import sys
import argparse
from .cli import run_cli
from .gui import run_gui
from .config import APP_NAME, APP_VERSION


def main() -> None:
    """
    Main entry point that handles CLI argument parsing and mode selection.
    """
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - ATM Banking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m atm_system              # Interactive mode selection
  python -m atm_system --cli        # Run CLI interface
  python -m atm_system --gui        # Run GUI interface
        """
    )

    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run command-line interface'
    )

    parser.add_argument(
        '--gui',
        action='store_true',
        help='Run graphical user interface'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} {APP_VERSION}'
    )

    args = parser.parse_args()

    # Handle mode selection
    if args.cli:
        run_cli()
    elif args.gui:
        run_gui()
    else:
        # Interactive mode selection
        show_mode_selection()


def show_mode_selection() -> None:
    """Display interactive mode selection menu."""
    print(f"\n{'=' * 60}")
    print(f"{f'{APP_NAME} v{APP_VERSION}'.center(60)}")
    print(f"{'=' * 60}\n")

    print("Select Interface Mode:")
    print("1. Command-Line Interface (CLI)")
    print("2. Graphical User Interface (GUI)")
    print("3. Exit")

    try:
        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            run_cli()
        elif choice == "2":
            run_gui()
        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice")
            show_mode_selection()

    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
