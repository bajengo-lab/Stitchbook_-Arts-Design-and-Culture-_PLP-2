"""
Main Menu loop for Stitchbook.
Displays options 1, 2, 3, 4, and 0, and routes the user to the chosen screen.
"""

import sys
import traceback

from menus.option1_add_order import run_add_order_menu
from menus.option2_manage_orders import run_orders_menu
from menus.option3_deadlines import run_deadlines_menu
from menus.option4_client_menu import run_client_menu


def run_main_menu():
    """
    Runs the Main Menu loop until the user selects 0 to exit.
    """
    while True:
        print("\n==================================================")
        print("  WELCOME TO STITCHBOOK")
        print("==================================================")
        print("What would you like to do today?")
        print(" 1. Add a new customer order")
        print(" 2. View / update orders")
        print(" 3. Incoming deadlines")
        print(" 4. I am a client")
        print(" 0. Exit program")

        choice = input("\nType a number (0-4) and press Enter: ").strip()

        try:
            if choice == "1":
                run_add_order_menu()
            elif choice == "2":
                run_orders_menu()
            elif choice == "3":
                run_deadlines_menu()
            elif choice == "4":
                run_client_menu()
            elif choice == "0":
                print("Thank you, goodbye!")
                break
            else:
                print("Invalid choice, please try again.")
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception:
            sys.stderr.write(traceback.format_exc())
            print("An unexpected error occurred. Returning to Main Menu.")
