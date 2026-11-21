"""
Option 3: Incoming deadlines.
Shows all orders whose status is not 'Delivered', sorted by nearest delivery date.
"""

import sys
import traceback
from datetime import date
from typing import Any, cast

from models.order import Order

from database.connection import get_connection


def run_deadlines_menu():
    """
    Reads all non-delivered orders sorted by delivery_date (nearest first)
    and displays customer, clothing type, delivery date, days left (or overdue),
    and remaining amount.
    """
    print("\n--- INCOMING DEADLINES ---")

    connection = get_connection()
    if connection is None:
        print("Returning to Main Menu because the database connection is unavailable.")
        return

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT o.id, c.name, c.phone, o.clothing_type, o.measurements,
                   o.delivery_date, o.total_price, o.deposit_paid, o.status
            FROM orders o
            JOIN customers c ON o.customer_phone = c.phone
            WHERE o.status != %s
            ORDER BY o.delivery_date ASC, o.id ASC
        """
        cursor.execute(query, ("Delivered",))
        rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        if not rows:
            print(
                "There are no active incoming deadlines (all orders are Delivered or none exist)."
            )
            return

        today = date.today()

        for row in rows:
            order_id = row[0]
            customer_name = row[1]
            customer_phone = row[2]
            order = Order(
                order_id=order_id,
                customer_phone=customer_phone,
                clothing_type=row[3],
                measurements=row[4],
                delivery_date=row[5],
                total_price=row[6],
                deposit_paid=row[7],
                status=row[8],
            )
            remaining = order.get_remaining()
            days_left = (order.delivery_date - today).days

            if days_left < 0:
                overdue_days = abs(days_left)
                time_status = f"OVERDUE by {overdue_days} days"
            else:
                time_status = f"{days_left} days left"

            print(
                f"Customer: {customer_name} ({customer_phone}) | "
                f"Type: {order.clothing_type} | "
                f"Delivery: {order.delivery_date} ({time_status}) | "
                f"Remaining: {remaining:,} RWF | "
                f"Status: {order.status}"
            )

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not load incoming deadlines from the database.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
