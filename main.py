"""
Entry point for the Stitchbook application.
Run this file with: python main.py
"""

import sys
import traceback

from menus.main_menu import run_main_menu


def main():
    """
    Starts the Stitchbook Main Menu loop and handles keyboard interrupts cleanly.
    """
    try:
        run_main_menu()
    except KeyboardInterrupt:
        print("\nThank you, goodbye!")
    except EOFError:
        print("\nThank you, goodbye!")
    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("\nA critical error occurred. Exiting Stitchbook.")


if __name__ == "__main__":
    main()
