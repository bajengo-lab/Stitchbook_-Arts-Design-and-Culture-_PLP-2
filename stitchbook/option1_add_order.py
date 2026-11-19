"""Option 1: add order. Owner: Gloria."""
"""
option1_add_order.py
StitchBook - Option 1: Add a new customer order.

Owner: Gloria Hirwa Kayitaba
Branch: feature/option-1-add-order

Flow: name -> phone -> clothing type -> measurements -> delivery date
      -> total price -> deposit -> save customer + order -> success message.

Uses Neema's Customer and Order classes from models.py.

ASSUMPTIONS (confirm with Mohammed):
  * His connection file is db_connection.py and has get_connection().
  * Tables match the column names Neema's from_row() methods read:
        customers(id, name, phone, date_registered)
        orders(id, customer_id, clothing_type, measurements,
               delivery_date, total_price, deposit_paid, status)
  * orders.delivery_date is a DATE column (best for Aristide's deadlines).
"""

from datetime import date, datetime

from db_connection import get_connection  # Mohammed's file
from models import Customer, Order        # Neema's file

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------

# What we measure for each clothing type, in cm (agree on these with the group)
MEASUREMENTS = {
    "shirt": ["chest", "waist", "length", "sleeve"],
    "pant": ["waist", "hip", "length"],
    "suit": ["chest", "waist", "hip", "length", "sleeve"],
    "hat": ["head circumference"],
    "shoes": ["foot length"],
}


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------

def format_rwf(amount):
    """20000 -> '20,000'"""
    return f"{amount:,.0f}"


class CancelOrder(Exception):
    """Raised when the user cancels in the middle of adding an order."""


def ask(prompt):
    """input() that never crashes on Ctrl+D / Ctrl+C."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        raise CancelOrder


# ----------------------------------------------------------------------
# Database checks
# ----------------------------------------------------------------------

def customer_exists(cursor, column, value):
    """True if a customer with this name or phone is already saved."""
    if column not in ("name", "phone"):  # safety: only allow these two columns
        raise ValueError("Invalid column")
    cursor.execute(f"SELECT id FROM customers WHERE {column} = %s", (value,))
    return cursor.fetchone() is not None


# ----------------------------------------------------------------------
# Input questions (each repeats until the answer is valid)
# ----------------------------------------------------------------------

def handle_duplicate(what):
    """Tell the user a name/phone is taken and let them choose what to do."""
    print(f"  Error: this {what} already exists.")
    print("  Type 'r' to try again, or 'm' to go back to the main menu")
    print("  (then use option 2 to add a new order for that customer).")
    while True:
        choice = ask("  Your choice (r/m): ").lower()
        if choice == "r":
            return
        if choice == "m":
            raise CancelOrder
        print("  Please type 'r' or 'm'.")


def get_name(cursor):
    while True:
        name = ask("Customer name (short, no spaces): ")
        if not name:
            print("  Error: name cannot be empty. Example: aline")
        elif " " in name:
            print("  Error: no spaces allowed. Example: aline or aline_u")
        elif len(name) > 30:
            print("  Error: name is too long (maximum 30 characters).")
        elif not name.replace("_", "").isalpha():
            print("  Error: use letters only (and _ if needed). Example: aline")
        elif customer_exists(cursor, "name", name.lower()):
            handle_duplicate("name")
        else:
            return name.lower()


def get_phone(cursor):
    while True:
        phone = ask("Phone number: ").replace(" ", "")
        if phone.startswith("+250"):
            phone = "0" + phone[4:]
        if not phone.isdigit():
            print("  Error: digits only. Example: 0788123456")
        elif len(phone) != 10 or not phone.startswith("07"):
            print("  Error: must be 10 digits starting with 07. Example: 0788123456")
        elif customer_exists(cursor, "phone", phone):
            handle_duplicate("phone number")
        else:
            return phone


def get_clothing_type():
    options = ", ".join(MEASUREMENTS)
    while True:
        clothing = ask(f"Type of clothing ({options}): ").lower()
        if clothing in MEASUREMENTS:
            return clothing
        print(f"  Error: choose one of: {options}")


def get_measurements(clothing):
    fields = MEASUREMENTS[clothing]
    example = ", ".join(str(70 + 10 * i) for i in range(len(fields)))
    label = ", ".join(fields)
    prompt = f"Enter {label} in cm (e.g. {example}): "

    while True:
        raw = ask(prompt)
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) != len(fields):
            print(f"  Error: I need exactly {len(fields)} number(s): {label}. "
                  f"Example: {example}")
            continue
        try:
            values = [float(p) for p in parts]
        except ValueError:
            print(f"  Error: numbers only, separated by commas. Example: {example}")
            continue
        if any(v <= 0 or v > 300 for v in values):
            print("  Error: each measurement must be between 1 and 300 cm.")
            continue
        # Show whole numbers without .0 (72.0 -> 72)
        cleaned = [str(int(v)) if v == int(v) else str(v) for v in values]
        return ", ".join(cleaned)


def get_delivery_date():
    today = date.today()
    while True:
        raw = ask("Delivery date (mm/dd, e.g. 07/24): ")
        try:
            parsed = datetime.strptime(f"{today.year}/{raw}", "%Y/%m/%d").date()
        except ValueError:
            print("  Error: use mm/dd with a real date. Example: 07/24")
            continue
        if parsed < today:
            print(f"  Error: that date has already passed (today is "
                  f"{today.strftime('%m/%d')}). Enter a future date.")
            continue
        return parsed


def parse_money(raw):
    """'20,000' -> 20000. Returns None if it is not a whole number."""
    cleaned = raw.replace(",", "").replace(" ", "")
    if cleaned.isdigit():
        return int(cleaned)
    return None


def get_total_price():
    while True:
        price = parse_money(ask("Total price (RWF): "))
        if price is None:
            print("  Error: numbers only. Example: 20,000")
        elif price <= 0:
            print("  Error: price must be more than 0.")
        else:
            return price


def get_deposit(total_price):
    # Friendly check here so the user is asked again straight away.
    # Neema's Order class repeats this check as a safety net.
    while True:
        deposit = parse_money(ask("Deposit paid (RWF): "))
        if deposit is None:
            print("  Error: numbers only. Example: 15,000 (or 0 if none)")
        elif deposit > total_price:
            print(f"  Error: deposit cannot be more than the total "
                  f"({format_rwf(total_price)} RWF).")
        else:
            return deposit


# ----------------------------------------------------------------------
# Saving
# ----------------------------------------------------------------------

def save_customer_and_order(connection, cursor, customer, order):
    """
    Save the Customer and Order in ONE transaction.
    Fills in customer.customer_id, order.customer_id and order.order_id.
    """
    try:
        cursor.execute(
            "INSERT INTO customers (name, phone, date_registered) "
            "VALUES (%s, %s, %s)",
            (customer.name, customer.phone, customer.date_registered),
        )
        customer.customer_id = cursor.lastrowid
        order.customer_id = customer.customer_id

        cursor.execute(
            """INSERT INTO orders
               (customer_id, clothing_type, measurements, delivery_date,
                total_price, deposit_paid, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (order.customer_id, order.clothing_type, order.measurements,
             order.delivery_date, order.total_price, order.deposit_paid,
             order.status),
        )
        order.order_id = cursor.lastrowid
        connection.commit()
    except Exception:
        connection.rollback()  # never leave a customer without an order
        raise


# ----------------------------------------------------------------------
# Main function (Aristide's main menu calls this)
# ----------------------------------------------------------------------

def add_order():
    """Option 1: ask the questions, validate, save, show the result."""
    print("\n--- ADD A NEW CUSTOMER ORDER ---")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        name = get_name(cursor)
        phone = get_phone(cursor)
        clothing = get_clothing_type()
        measurements = get_measurements(clothing)
        delivery_date = get_delivery_date()
        total_price = get_total_price()
        deposit = get_deposit(total_price)

        # Build Neema's objects (Order checks price, deposit and status)
        customer = Customer(name=name, phone=phone,
                            date_registered=date.today())
        order = Order(clothing_type=clothing, measurements=measurements,
                      delivery_date=delivery_date, total_price=total_price,
                      deposit_paid=deposit)  # status defaults to "pending"

        save_customer_and_order(connection, cursor, customer, order)

        print(f"\nOrder saved! Order No: {order.order_id:04d} | "
              f"Paid: {format_rwf(order.deposit_paid)} of "
              f"{format_rwf(order.total_price)} RWF | "
              f"Remaining: {format_rwf(order.remaining)} RWF")

    except CancelOrder:
        print("Order not saved. Returning to main menu.")
    except ValueError as error:  # Order rejected the values
        print(f"\nOrder not saved: {error}")
    except Exception as error:  # DB down, SSL problem, etc. Never crash the app
        print("\nSorry, something went wrong and the order was NOT saved.")
        print(f"Details: {error}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    # Returning here sends the user back to the main menu.


if __name__ == "__main__":
    add_order()

