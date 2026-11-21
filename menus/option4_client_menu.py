"""
Option 4: I am a client (view-only menu for clients to check their own orders).
"""

import sys
import traceback
from typing import Any, cast

from models.order import Order

from database.connection import get_connection

# Tailor contact details shown to clients (edit these in plain sight as needed)
TAILOR_NAME = "Riah the Tailor"
TAILOR_PHONE = "0788000000"


def check_client_orders():
    """
    Prompts the client for their phone number and displays all matching orders.
    """
    while True:
        phone = input("Enter your phone number (order number): ").strip()
        if phone:
            break
        print("Phone number cannot be empty. Please try again.")

    connection = get_connection()
    if connection is None:
        print("Could not check your order because the database is unavailable.")
        return

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT id, customer_phone, clothing_type, measurements,
                   delivery_date, total_price, deposit_paid, status
            FROM orders
            WHERE customer_phone = %s
            ORDER BY id ASC
        """
        cursor.execute(query, (phone,))
        rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        if not rows:
            print("Order not found, please check your phone number.")
            return

        print(f"\nFound {len(rows)} order(s) for {phone}:")
        print("-" * 50)
        for row in rows:
            order = Order(
                order_id=row[0],
                customer_phone=row[1],
                clothing_type=row[2],
                measurements=row[3],
                delivery_date=row[4],
                total_price=row[5],
                deposit_paid=row[6],
                status=row[7],
            )
            remaining = order.get_remaining()

            if order.status == "Ready":
                status_display = "READY FOR PICKUP"
            else:
                status_display = order.status

            print(f"Clothing type : {order.clothing_type}")
            print(f"Status        : {status_display}")
            print(f"Tailor        : {TAILOR_NAME} ({TAILOR_PHONE})")
            print(f"Total price   : {order.total_price:,} RWF")
            print(f"Amount paid   : {order.deposit_paid:,} RWF")
            print(f"Remaining     : {remaining:,} RWF")
            print(f"Delivery date : {order.delivery_date}")
            print("-" * 50)

    except (KeyboardInterrupt, EOFError):
        raise

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not load your orders right now.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def run_client_menu():
    """
    Runs the CLIENT MENU loop until the client chooses 0 to go back.
    """
    while True:
        print("\nCLIENT MENU")
        print(" 1. Check my order")
        print(" 0. Back to Main Menu")

        choice = input("Type a number (0-1) and press Enter: ").strip()

        if choice == "1":
            check_client_orders()
        elif choice == "0":
            return
        else:
            print("Invalid choice, please try again.")
