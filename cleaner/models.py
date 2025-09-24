from django.db import models

class Cleaner(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    vehicle_code = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({'Available' if self.is_available else 'Unavailable'})"

    class Meta:
        db_table = 'cleaners'