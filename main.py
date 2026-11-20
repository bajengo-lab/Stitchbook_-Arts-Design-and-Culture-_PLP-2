import os
from dotenv import load_dotenv
from stitchbook.option1_add_order import add_order
from stitchbook.option2_manage_orders import run_orders_menu
from stitchbook.option3_deadlines import view_incoming_deadlines
from stitchbook.option4_client_menu import client_check_order

load_dotenv()
TAILOR_PIN = os.getenv("TAILOR_PIN", "1234")


def tailor_menu():
    """Tailor Dashboard connecting Options 1, 2, and 3."""
    while True:
        print("\n" + "=" * 48)
        print("           STITCHBOOK - TAILOR MENU")
        print("=" * 48)
        print("1. Add New Order")
        print("2. View / Update Orders")
        print("3. Incoming Deadlines")
        print("0. Back to Main Menu")
        print("-" * 48)

        choice = input("Select an option (0-3): ").strip()

        if choice == "1":
            add_order()
        elif choice == "2":
            run_orders_menu()
        elif choice == "3":
            view_incoming_deadlines()
        elif choice == "0":
            print("Returning to Main Menu...")
            break
        else:
            print("[Invalid Input] Please enter 1, 2, 3, or 0.")


def main():
    """Main entry point separating Tailor and Client user roles."""
    while True:
        print("\n" + "*" * 48)
        print("          WELCOME TO STITCHBOOK CLI")
        print("       Tailoring & Order Management System")
        print("*" * 48)
        print("1. Tailor Portal (Manage Orders & Deadlines)")
        print("2. Client Portal (Check My Order Status)")
        print("0. Exit")
        print("-" * 48)

        role_choice = input("Select an option (0-2): ").strip()

        if role_choice == "1":
            pin = input("Enter Tailor PIN (default 1234): ").strip()
            if pin == TAILOR_PIN:
                tailor_menu()
            else:
                print("[Access Denied] Incorrect Tailor PIN.")
        elif role_choice == "2":
            client_check_order()
        elif role_choice == "0":
            print("\nThank you for using StitchBook. Goodbye!")
            break
        else:
            print("[Invalid Input] Please enter 1, 2, or 0.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication closed safely. Goodbye!")
