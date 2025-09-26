from django.db import models
from customer.models import Customer
from service.models import Service
from cleaner.models import Cleaner
from django.contrib.auth.models import User


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="bookings")
    booking_reference = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    cleaning_instructions = models.TextField(blank=True)
    special_request = models.TextField(blank=True)
    entry_instruction = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_bookings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking_reference} ({self.customer.full_name})"

    def calculate_total_amount(self):
        """
        Calculates total amount based on all assigned services and their cleaner count.
        """
        total = 0
        for bs in self.booking_services.select_related("service").all():
            total += bs.service.base_price * bs.number_of_cleaners
        return total

    def total_required_cleaners(self):
        """
        Returns total number of cleaners required across all services in the booking.
        """
        return sum(bs.number_of_cleaners for bs in self.booking_services.all())

    class Meta:
        db_table = 'bookings'

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_services")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="service_bookings")
    number_of_cleaners = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("booking", "service")

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.service.name}"
    class Meta:
        db_table = 'booking_services'

class BookingCleaner(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_cleaners")
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE, related_name="cleaner_bookings")

    class Meta:
        unique_together = ("booking", "cleaner")

    def __str__(self):
        return f"{self.cleaner.name} -> {self.booking.booking_reference}"
    class Meta:
        db_table = 'booking_cleaners'

