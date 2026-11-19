"""Option 4: client menu. Owner: Neema."""
"""client_menu.py - Option 4: a client checks their order."""
import os

from dotenv import load_dotenv

from db import get_connection        # Mohammed's file (confirm the name)
from models import Customer, Order

load_dotenv()
TAILOR_PHONE = os.getenv("TAILOR_PHONE", "not available")


def ask_phone():
    """Keep asking until the phone looks valid. Returns None if the user types 0."""
    while True:
        phone = input("Enter your phone number (or 0 to go back): ").strip()
        phone = phone.replace(" ", "")
        if phone == "0":
            return None
        if phone.isdigit() and len(phone) == 10:
            return phone
        print("Invalid phone number. Use 10 digits, e.g. 0788123456.\n")


def find_orders_by_phone(phone):
    """Return (Customer, [Order, ...]) or (None, [])."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
        row = cursor.fetchone()
        if row is None:
            return None, []

        customer = Customer.from_row(row)
        cursor.execute(
            "SELECT * FROM orders WHERE customer_id = %s ORDER BY delivery_date",
            (customer.customer_id,),
        )
        orders = [Order.from_row(r) for r in cursor.fetchall()]
        return customer, orders
    finally:
        conn.close()


def show_order(order):
    print("-" * 40)
    print(f"Order No:       {order.order_id:04d}")
    print(f"Item:           {order.clothing_type}")
    print(f"Status:         {order.status}")
    print(f"Delivery date:  {order.delivery_date}")
    print(f"Paid:           {order.deposit_paid:,.0f} RWF")
    print(f"Remaining:      {order.remaining:,.0f} RWF")
    print(f"Tailor's phone: {TAILOR_PHONE}")


def client_check_order():
    """Called by the main menu when the user picks option 4."""
    print("\n=== CLIENT: CHECK YOUR ORDER ===")
    phone = ask_phone()
    if phone is None:
        return

    try:
        customer, orders = find_orders_by_phone(phone)
    except Exception as e:
        print("Sorry, we could not reach the database. Try again later.")
        print(f"(Details: {e})")
        return

    if customer is None or not orders:
        print("Order not found. Check your number or ask your tailor.")
        return

    print(f"\nHello {customer.name}! Your orders:")
    for order in orders:
        show_order(order)
    print("-" * 40)
    input("\nPress Enter to go back to the main menu...")