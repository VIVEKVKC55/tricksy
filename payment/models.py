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

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default="pending")

    def save(self, *args, **kwargs):
        # Auto calculate net amount
        self.net_amount = self.amount - self.discount
        if self.net_amount < 0:
            self.net_amount = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.payment_method} - {self.net_amount} AED"

    class Meta:
        db_table = "payments"