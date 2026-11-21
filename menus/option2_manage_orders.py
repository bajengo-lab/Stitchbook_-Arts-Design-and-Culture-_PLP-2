"""
Option 2: View / update orders.
Allows the tailor to view all orders, search a customer by name or phone,
record a payment, change order status, add a new order for an existing customer,
and list unpaid orders.
"""

import sys
import traceback
from typing import Any, cast

from database.connection import get_connection
from menus.option1_add_order import collect_and_save_order_for_customer
from models.customer import Customer
from models.order import Order

# The four allowed status values in Stitchbook
VALID_STATUSES = ["Pending", "In progress", "Ready", "Delivered"]


def view_all_orders():
    """
    Sub-option 1: Lists every order in the database with full details.
    """
    connection = get_connection()
    if connection is None:
        print(
            "Returning to Orders Menu because the database connection is unavailable."
        )
        return

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT o.id, c.name, c.phone, o.clothing_type, o.measurements,
                   o.delivery_date, o.total_price, o.deposit_paid, o.status
            FROM orders o
            JOIN customers c ON o.customer_phone = c.phone
            ORDER BY o.id ASC
        """
        cursor.execute(query)
        rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        if not rows:
            print("\nThere are no orders recorded yet.")
            return

        print(f"\n--- ALL ORDERS ({len(rows)}) ---")
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

            print(
                f"[Order #{order.id}] Customer: {customer_name} ({customer_phone}) | "
                f"Type: {order.clothing_type} | Measurements: {order.measurements} cm | "
                f"Delivery: {order.delivery_date} | Total: {order.total_price:,} RWF | "
                f"Paid: {order.deposit_paid:,} RWF | Remaining: {remaining:,} RWF | "
                f"Status: {order.status}"
            )

    except (KeyboardInterrupt, EOFError):
        raise

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not load orders from the database.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def record_payment(connection, selected_order):
    """
    Update Menu Option a: Adds a new payment to the selected order's deposit_paid.
    """
    remaining = selected_order.get_remaining()
    if remaining <= 0:
        print("This order is already fully paid (Remaining: 0 RWF).")
        return

    while True:
        raw_payment = input(
            f"Enter amount paid now in RWF (Remaining is {remaining:,} RWF): "
        ).strip()
        cleaned_payment = raw_payment.replace(",", "")
        if not cleaned_payment.isdigit():
            print("Invalid amount. Please enter a positive whole number (e.g. 5,000).")
            continue

        payment_amount = int(cleaned_payment)
        if payment_amount <= 0:
            print("Payment amount must be greater than 0.")
            continue
        if payment_amount > remaining:
            print(
                f"Payment cannot be more than the remaining amount ({remaining:,} RWF). "
                f"Please enter an amount up to {remaining:,}."
            )
            continue
        break

    new_deposit_paid = selected_order.deposit_paid + payment_amount

    cursor = None
    try:
        cursor = connection.cursor()
        update_sql = """
            UPDATE orders
            SET deposit_paid = %s
            WHERE id = %s
        """
        cursor.execute(update_sql, (new_deposit_paid, selected_order.id))
        connection.commit()

        selected_order.deposit_paid = new_deposit_paid
        new_remaining = selected_order.get_remaining()

        print(
            f"Updated! Paid: {selected_order.deposit_paid:,} of {selected_order.total_price:,} RWF | "
            f"Remaining: {new_remaining:,} RWF"
        )
        if new_remaining == 0:
            print("Fully paid")

    except (KeyboardInterrupt, EOFError):
        try:
            connection.rollback()
        except Exception:
            sys.stderr.write(traceback.format_exc())
        raise

    except Exception:
        try:
            connection.rollback()
        except Exception:
            sys.stderr.write(traceback.format_exc())
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not update the payment in the database.")

    finally:
        if cursor is not None:
            cursor.close()


def change_order_status(connection, selected_order):
    """
    Update Menu Option b: Lets the tailor pick one of the four statuses and saves it.
    """
    print("\nSelect new status:")
    for index in range(len(VALID_STATUSES)):
        print(f" {index + 1}. {VALID_STATUSES[index]}")

    while True:
        choice = input("Type a number (1-4) and press Enter: ").strip()
        if choice in ["1", "2", "3", "4"]:
            chosen_index = int(choice) - 1
            new_status = VALID_STATUSES[chosen_index]
            break
        print("Invalid choice, please try again.")

    cursor = None
    try:
        cursor = connection.cursor()
        update_sql = """
            UPDATE orders
            SET status = %s
            WHERE id = %s
        """
        cursor.execute(update_sql, (new_status, selected_order.id))
        connection.commit()

        selected_order.status = new_status
        print(f"Updated! New status: {selected_order.status}")

    except (KeyboardInterrupt, EOFError):
        try:
            connection.rollback()
        except Exception:
            sys.stderr.write(traceback.format_exc())
        raise

    except Exception:
        try:
            connection.rollback()
        except Exception:
            sys.stderr.write(traceback.format_exc())
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not update the order status in the database.")

    finally:
        if cursor is not None:
            cursor.close()


def search_customer():
    """
    Sub-option 2: Searches for a customer by phone number (if all digits) or name,
    displays their orders, lets the tailor pick an order if there are several,
    and opens the UPDATE MENU.
    """
    while True:
        search_term = input("Enter customer name or phone number: ").strip()
        if search_term:
            break
        print("Search input cannot be empty. Please try again.")

    connection = get_connection()
    if connection is None:
        print(
            "Returning to Orders Menu because the database connection is unavailable."
        )
        return

    cursor = None
    try:
        cursor = connection.cursor()

        # If the input is all digits treat it as a phone, otherwise as a name
        if search_term.isdigit():
            customer_sql = """
                SELECT name, phone, date_registered
                FROM customers
                WHERE phone = %s
            """
            cursor.execute(customer_sql, (search_term,))
        else:
            customer_sql = """
                SELECT name, phone, date_registered
                FROM customers
                WHERE LOWER(name) = LOWER(%s)
            """
            cursor.execute(customer_sql, (search_term,))

        customer_row = cast(tuple[Any, ...] | None, cursor.fetchone())
        if customer_row is None:
            print("Not found")
            return

        customer = Customer(
            name=customer_row[0], phone=customer_row[1], date_registered=customer_row[2]
        )

        orders_sql = """
            SELECT id, customer_phone, clothing_type, measurements,
                   delivery_date, total_price, deposit_paid, status
            FROM orders
            WHERE customer_phone = %s
            ORDER BY id ASC
        """
        cursor.execute(orders_sql, (customer.phone,))
        order_rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        print(f"\n{customer.format_display()}")
        if not order_rows:
            print("This customer has no orders yet.")
            return

        customer_orders = []
        orders_by_id = {}
        for row in order_rows:
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
            customer_orders.append(order)
            orders_by_id[order.id] = order

            remaining = order.get_remaining()
            print(
                f"  [Order #{order.id}] Type: {order.clothing_type} | "
                f"Measurements: {order.measurements} cm | Delivery: {order.delivery_date} | "
                f"Total: {order.total_price:,} RWF | Paid: {order.deposit_paid:,} RWF | "
                f"Remaining: {remaining:,} RWF | Status: {order.status}"
            )

        # If the customer has more than one order, ask which one to work on
        if len(customer_orders) == 1:
            selected_order = customer_orders[0]
        else:
            while True:
                raw_id = input(
                    "This customer has multiple orders. Enter the Order # (id) to work on: "
                ).strip()
                if not raw_id.isdigit():
                    print("Please enter a valid numeric Order # from the list above.")
                    continue

                chosen_id = int(raw_id)
                if chosen_id in orders_by_id:
                    selected_order = orders_by_id[chosen_id]
                    break
                print(
                    "Order # not found for this customer. Please pick an Order # from the list above."
                )

        # Show UPDATE MENU
        while True:
            print("\nUPDATE MENU")
            print(" a. Record a payment")
            print(" b. Change status")
            print(" c. New order for this customer")
            print(" 0. Back")

            action = (
                input("Type your choice (a, b, c, 0) and press Enter: ").strip().lower()
            )

            if action == "a":
                record_payment(connection, selected_order)
                return
            elif action == "b":
                change_order_status(connection, selected_order)
                return
            elif action == "c":
                collect_and_save_order_for_customer(connection, customer.phone)
                return
            elif action == "0":
                return
            else:
                print("Invalid choice, please try again.")

    except (KeyboardInterrupt, EOFError):
        raise

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not complete the customer search.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def show_unpaid_orders():
    """
    Sub-option 3: Lists all orders where remaining (total_price - deposit_paid) is greater than 0.
    """
    connection = get_connection()
    if connection is None:
        print(
            "Returning to Orders Menu because the database connection is unavailable."
        )
        return

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT o.id, c.name, c.phone, o.clothing_type, o.measurements,
                   o.delivery_date, o.total_price, o.deposit_paid, o.status
            FROM orders o
            JOIN customers c ON o.customer_phone = c.phone
            WHERE (o.total_price - o.deposit_paid) > 0
            ORDER BY o.id ASC
        """
        cursor.execute(query)
        rows = cast(list[tuple[Any, ...]], cursor.fetchall())

        if not rows:
            print("\nThere are no unpaid orders. Every order is fully paid!")
            return

        print(f"\n--- UNPAID ORDERS ({len(rows)}) ---")
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

            print(
                f"[Order #{order.id}] Customer: {customer_name} ({customer_phone}) | "
                f"Paid/Total: {order.deposit_paid:,}/{order.total_price:,} RWF | "
                f"Remaining: {remaining:,} RWF"
            )

    except (KeyboardInterrupt, EOFError):
        raise

    except Exception:
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not load unpaid orders from the database.")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def run_orders_menu():
    """
    Runs Option 2: ORDERS MENU loop until the tailor chooses 0 to return to Main Menu.
    """
    while True:
        print("\nORDERS MENU")
        print(" 1. View all orders")
        print(" 2. Search a customer")
        print(" 3. Show unpaid orders")
        print(" 0. Back to Main Menu")

        choice = input("Type a number (0-3) and press Enter: ").strip()

        if choice == "1":
            view_all_orders()
        elif choice == "2":
            search_customer()
        elif choice == "3":
            show_unpaid_orders()
        elif choice == "0":
            return
        else:
            print("Invalid choice, please try again.")
