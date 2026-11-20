from datetime import date, datetime
from stitchbook.db import get_connection


def view_incoming_deadlines():
    """Display active orders sorted by nearest delivery date with overdue flags."""
    print("\n" + "=" * 76)
    print("                     INCOMING & OVERDUE DEADLINES")
    print("=" * 76)

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                o.order_id,
                c.name AS customer_name,
                c.phone AS customer_phone,
                o.clothing_type,
                o.delivery_date,
                o.price,
                o.deposit,
                o.status
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE LOWER(o.status) NOT IN ('delivered', 'completed', 'cancelled')
            ORDER BY o.delivery_date ASC
        """
        cursor.execute(query)
        orders = cursor.fetchall()

        if not orders:
            print("No active upcoming deadlines found.")
            print("=" * 76)
            return

        today = date.today()
        header = (
            f"{'ID':<6} {'Customer':<18} {'Item':<14} "
            f"{'Due Date':<12} {'Remaining (RWF)':<16} {'Status / Urgency'}"
        )
        print(header)
        print("-" * 76)

        for order in orders:
            due_date = order["delivery_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            days_left = (due_date - today).days
            if days_left < 0:
                urgency = f"[OVERDUE by {abs(days_left)}d]"
            elif days_left == 0:
                urgency = "[DUE TODAY]"
            elif days_left <= 3:
                urgency = f"[URGENT: {days_left}d left]"
            else:
                urgency = f"In {days_left} days"

            remaining = float(order["price"]) - float(order["deposit"])
            print(
                f"{order['order_id']:04d}   "
                f"{order['customer_name'][:17]:<18} "
                f"{order['clothing_type'][:13]:<14} "
                f"{str(due_date):<12} "
                f"{remaining:<16,.0f} "
                f"{urgency}"
            )

        print("=" * 76)

    except Exception as e:
        print(f"\n[Database Error] Could not load deadlines: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
