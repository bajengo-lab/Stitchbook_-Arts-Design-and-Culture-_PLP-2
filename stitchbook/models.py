"""Customer and Order classes. Owner: Neema."""
"""models.py - Customer and Order classes for StitchBook."""

VALID_STATUSES = ("pending", "in progress", "ready", "delivered")


class Customer:
    def __init__(self, name, phone, date_registered=None, customer_id=None):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.date_registered = date_registered

    @classmethod
    def from_row(cls, row):
        """Build a Customer from a database row (a dictionary)."""
        return cls(
            name=row["name"],
            phone=row["phone"],
            date_registered=row.get("date_registered"),
            customer_id=row.get("id"),
        )

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Order:
    def __init__(self, clothing_type, measurements, delivery_date,
                 total_price, deposit_paid, status="pending",
                 order_id=None, customer_id=None):
        if total_price < 0 or deposit_paid < 0:
            raise ValueError("Price and deposit cannot be negative.")
        if deposit_paid > total_price:
            raise ValueError("Deposit cannot be more than the total price.")
        if status not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")

        self.order_id = order_id
        self.customer_id = customer_id
        self.clothing_type = clothing_type
        self.measurements = measurements
        self.delivery_date = delivery_date
        self.total_price = total_price
        self.deposit_paid = deposit_paid
        self.status = status

    @property
    def remaining(self):
        """Amount the customer still owes."""
        return self.total_price - self.deposit_paid

    @property
    def is_fully_paid(self):
        return self.remaining == 0

    @classmethod
    def from_row(cls, row):
        """Build an Order from a database row (a dictionary)."""
        return cls(
            clothing_type=row["clothing_type"],
            measurements=row["measurements"],
            delivery_date=row["delivery_date"],
            total_price=float(row["total_price"]),
            deposit_paid=float(row["deposit_paid"]),
            status=row["status"],
            order_id=row.get("id"),
            customer_id=row.get("customer_id"),
        )

    def __str__(self):
        return (f"Order {self.order_id}: {self.clothing_type} | {self.status} | "
                f"Paid {self.deposit_paid:,.0f} of {self.total_price:,.0f} RWF")


# Quick test without the database: run `python models.py`
if __name__ == "__main__":
    o = Order("pant", "72, 95, 105", "11/15", 20000, 15000)
    print(o)
    print("Remaining:", o.remaining)   # should print 5000
    try:
        Order("pant", "72, 95, 105", "11/15", 20000, 25000)
    except ValueError as e:
        print("Caught error:", e)      # deposit bigger than total