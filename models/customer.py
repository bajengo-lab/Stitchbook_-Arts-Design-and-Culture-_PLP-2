"""
Defines the Customer class for representing a client in Stitchbook.
"""


class Customer:
    """
    Represents a customer record with name, phone number, and registration date.
    """

    def __init__(self, name, phone, date_registered):
        self.name = name
        self.phone = phone
        self.date_registered = date_registered

    def format_display(self):
        """
        Returns a readable plain-text summary of the customer.
        """
        return f"Customer: {self.name} | Phone: {self.phone} | Registered: {self.date_registered}"
