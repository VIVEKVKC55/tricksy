from django.db import models
from booking.models import Booking

class Payment(models.Model):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (CARD, "Card"),
        (UPI, "UPI"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.payment_method} - {self.net_amount}"
    
    class Meta:
        db_table = 'payments'