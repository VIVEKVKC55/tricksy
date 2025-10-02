from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    material = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    def calculate_price(self, requested_hours, num_cleaners=1):
        """
        Calculate price per hour per cleaner.
        Example:
        base_price = 500 for 1 hour
        requested_hours = 3
        num_cleaners = 3
        => total = 500 * 3 * 3
        """
        if not requested_hours or requested_hours <= 0:
            return 0

        # price per hour for one cleaner
        price_per_hour = self.base_price / self.duration

        total_price = price_per_hour * requested_hours * num_cleaners
        return round(total_price, 2)

    class Meta:
        db_table = "services"