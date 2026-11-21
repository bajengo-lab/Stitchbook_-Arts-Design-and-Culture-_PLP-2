"""
Defines the Order class for representing a clothing order in Stitchbook.
"""


class Order:
    """
    Represents one clothing order for a customer.
    """

    def __init__(
        self,
        order_id,
        customer_phone,
        clothing_type,
        measurements,
        delivery_date,
        total_price,
        deposit_paid,
        status="Pending",
    ):
        self.id = order_id
        self.customer_phone = customer_phone
        self.clothing_type = clothing_type
        self.measurements = measurements
        self.delivery_date = delivery_date
        self.total_price = int(total_price)
        self.deposit_paid = int(deposit_paid)
        self.status = status

    def get_remaining(self):
        """
        Calculates and returns the amount still owed on the order.
        Remaining is always total_price - deposit_paid.
        """
        return self.total_price - self.deposit_paid
