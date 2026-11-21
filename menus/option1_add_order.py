"""
Option 1: Add a new customer order.
Also provides collect_and_save_order_for_customer() so Option 2c can add
a new order for an existing customer without repeating the prompts.
"""

import sys
import traceback
from datetime import date

from models.customer import Customer
from models.order import Order

from database.connection import get_connection

# Dictionary mapping each valid clothing type to its required measurements and example
MEASUREMENT_PROMPTS = {
    "shirt": {"labels": "chest, waist and length", "count": 3, "example": "96, 82, 70"},
    "pant": {"labels": "waist, hip and length", "count": 3, "example": "72, 95, 105"},
    "suit": {"labels": "chest, waist and length", "count": 3, "example": "100, 88, 75"},
    "hat": {"labels": "head size", "count": 1, "example": "58"},
    "shoes": {"labels": "foot length", "count": 1, "example": "27"},
}


def has_at_least_one_letter(text):
    """
    Returns True if the string contains at least one alphabetical letter.
    Prevents all-digit customer names so name search and phone search never conflict.
    """
    for character in text:
        if character.isalpha():
            return True
    return False


def is_valid_measurement_number(piece):
    """
    Checks that a measurement string contains only digits with at most one decimal point
    (rejecting nan, inf, exponent notation like 1e5, and negative signs),
    and represents a number greater than 0.
    """
    if not piece:
        return False

    if piece.count(".") > 1:
        return False

    digits_only = piece.replace(".", "")
    if not digits_only or not digits_only.isdigit():
        return False

    try:
        value = float(piece)
        return value > 0
    except ValueError:
        return False


def ask_order_details(customer_phone):
    """
    Asks questions 3 to 7 (clothing type, measurements, delivery date,
    total price, deposit paid) and returns an unsaved Order object.
    """
    # Step 3: Clothing type
    while True:
        clothing_type = (
            input("Enter clothing type (shirt, pant, suit, hat, shoes): ")
            .strip()
            .lower()
        )
        if clothing_type in MEASUREMENT_PROMPTS:
            break
        print(
            "Invalid clothing type. Please type one of: shirt, pant, suit, hat, shoes."
        )

    # Step 4: Measurements in cm, comma-separated
    prompt_info = MEASUREMENT_PROMPTS[clothing_type]
    expected_count = prompt_info["count"]
    labels = prompt_info["labels"]
    example = prompt_info["example"]

    while True:
        raw_measurements = input(f"Enter {labels} in cm (e.g. {example}): ").strip()
        if not raw_measurements:
            print(f"Measurements cannot be empty. Example: {example}")
            continue

        parts = raw_measurements.split(",")
        if len(parts) != expected_count:
            print(
                f"Please enter {expected_count} value(s) separated by commas (e.g. {example})."
            )
            continue

        cleaned_values = []
        all_valid = True
        for part in parts:
            piece = part.strip()
            if not is_valid_measurement_number(piece):
                all_valid = False
                break

            number_value = float(piece)
            if number_value.is_integer():
                cleaned_values.append(str(int(number_value)))
            else:
                cleaned_values.append(str(number_value))

        if not all_valid:
            print(
                f"Invalid measurements. Please enter positive numbers using digits only (e.g. {example})."
            )
            continue

        measurements_str = ",".join(cleaned_values)
        break

    # Step 5: Delivery date as yy/mm/dd
    while True:
        raw_date = input("Enter delivery date as yy/mm/dd (e.g. 26/07/24): ").strip()
        if "/" not in raw_date:
            print("Invalid date format. Please use yy/mm/dd (e.g. 26/07/24).")
            continue

        date_parts = raw_date.split("/")
        if len(date_parts) != 3:
            print("Invalid date format. Please use yy/mm/dd (e.g. 26/07/24).")
            continue

        year_text = date_parts[0].strip()
        month_text = date_parts[1].strip()
        day_text = date_parts[2].strip()
        if (
            not year_text.isdigit()
            or not month_text.isdigit()
            or not day_text.isdigit()
        ):
            print(
                "Year, month and day must be numbers in yy/mm/dd format (e.g. 26/07/24)."
            )
            continue

        if len(year_text) != 2:
            print("The year must have 2 digits (e.g. 26 for 2026).")
            continue

        today = date.today()

        try:
            year = 2000 + int(year_text)
            month = int(month_text)
            day = int(day_text)
            delivery_date = date(year, month, day)
        except ValueError:
            print(
                "Invalid calendar date. Please enter a real date as yy/mm/dd (e.g. 26/07/24)."
            )
            continue

        if delivery_date < today:
            print(
                "The delivery date cannot be in the past. Please enter today or a later date."
            )
            continue

        break

    # Step 6: Total price in RWF
    while True:
        raw_total = input("Enter total price in RWF (e.g. 20,000): ").strip()
        cleaned_total = raw_total.replace(",", "")
        if not cleaned_total.isdigit():
            print("Invalid price. Please enter a positive whole number (e.g. 20,000).")
            continue

        total_price = int(cleaned_total)
        if total_price <= 0:
            print("Total price must be greater than 0 (e.g. 20,000).")
            continue
        break

    # Step 7: Deposit paid in RWF
    while True:
        raw_deposit = input("Enter deposit paid in RWF (e.g. 15,000 or 0): ").strip()
        cleaned_deposit = raw_deposit.replace(",", "")
        if not cleaned_deposit.isdigit():
            print(
                "Invalid deposit. Please enter 0 or a positive whole number (e.g. 15,000)."
            )
            continue

        deposit_paid = int(cleaned_deposit)
        if deposit_paid > total_price:
            print(
                f"Deposit paid cannot be more than the total price ({total_price:,} RWF). "
                f"Please enter an amount up to {total_price:,}."
            )
            continue
        break

    new_order = Order(
        order_id=None,
        customer_phone=customer_phone,
        clothing_type=clothing_type,
        measurements=measurements_str,
        delivery_date=delivery_date,
        total_price=total_price,
        deposit_paid=deposit_paid,
        status="Pending",
    )
    return new_order


def collect_and_save_order_for_customer(connection, customer_phone):
    """
    Collects order details (steps 3 to 7) and saves the new order for an existing customer.
    Used by Option 2c (New order for this customer).
    """
    order = ask_order_details(customer_phone)
    cursor = None
    try:
        cursor = connection.cursor()
        insert_order_sql = """
            INSERT INTO orders (
                customer_phone, clothing_type, measurements,
                delivery_date, total_price, deposit_paid, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_order_sql,
            (
                order.customer_phone,
                order.clothing_type,
                order.measurements,
                order.delivery_date,
                order.total_price,
                order.deposit_paid,
                order.status,
            ),
        )
        connection.commit()

        remaining = order.get_remaining()
        print(
            f"Order saved! Paid: {order.deposit_paid:,} of {order.total_price:,} RWF | "
            f"Remaining: {remaining:,} RWF"
        )
    except Exception:
        try:
            connection.rollback()
        except Exception:
            sys.stderr.write(traceback.format_exc())
        sys.stderr.write(traceback.format_exc())
        print("Error: Could not save the order to the database.")
    finally:
        if cursor is not None:
            cursor.close()


def run_add_order_menu():
    """
    Runs Option 1: Add a new customer order.
    """
    print("\n--- ADD A NEW CUSTOMER ORDER ---")

    connection = get_connection()
    if connection is None:
        print("Returning to Main Menu because the database connection is unavailable.")
        return

    cursor = None
    try:
        # Step 1: Customer name (3 to 12 letters or digits, no spaces, at least one letter)
        while True:
            customer_name = input(
                "Enter customer name (3-12 letters or digits, at least one letter, no spaces): "
            ).strip()
            if not customer_name:
                print("Customer name cannot be empty.")
                continue
            if (
                " " in customer_name
                or not customer_name.isalnum()
                or len(customer_name) < 3
                or len(customer_name) > 12
                or not has_at_least_one_letter(customer_name)
            ):
                print(
                    "Invalid name. Use 3 to 12 letters or digits with at least one letter and no spaces (e.g. Jean or Marie1)."
                )
                continue
            break

        # Step 2: Phone number (10 digits starting with 07)
        while True:
            customer_phone = input(
                "Enter phone number (10 digits starting with 07, e.g. 0788123456): "
            ).strip()
            if (
                len(customer_phone) == 10
                and customer_phone.isdigit()
                and customer_phone.startswith("07")
            ):
                break
            print(
                "Invalid phone number. Must be 10 digits starting with 07 (e.g. 0788123456)."
            )

        # Check if the customer name (case-insensitive) OR phone already exists
        cursor = connection.cursor()
        check_sql = """
            SELECT phone, name
            FROM customers
            WHERE LOWER(name) = LOWER(%s) OR phone = %s
        """
        cursor.execute(check_sql, (customer_name, customer_phone))
        existing_row = cursor.fetchone()

        if existing_row is not None:
            print(
                "Error: That customer name or phone number already exists. "
                "Please use Option 2 (View / update orders) to add a new order for them."
            )
            return

        # Steps 3 to 7: Collect clothing type, measurements, delivery date, price, deposit
        customer = Customer(
            name=customer_name, phone=customer_phone, date_registered=date.today()
        )
        order = ask_order_details(customer.phone)

        # Save both the customer and the order in one transaction
        insert_customer_sql = """
            INSERT INTO customers (phone, name, date_registered)
            VALUES (%s, %s, %s)
        """
        cursor.execute(
            insert_customer_sql,
            (customer.phone, customer.name, customer.date_registered),
        )

        insert_order_sql = """
            INSERT INTO orders (
                customer_phone, clothing_type, measurements,
                delivery_date, total_price, deposit_paid, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_order_sql,
            (
                order.customer_phone,
                order.clothing_type,
                order.measurements,
                order.delivery_date,
                order.total_price,
                order.deposit_paid,
                order.status,
            ),
        )

        # Commit once after both inserts succeed
        connection.commit()

        remaining = order.get_remaining()
        print(
            f"Order saved! Paid: {order.deposit_paid:,} of {order.total_price:,} RWF | "
            f"Remaining: {remaining:,} RWF"
        )

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
        print(
            "Error: Could not save the customer and order. Any partial changes were rolled back."
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
