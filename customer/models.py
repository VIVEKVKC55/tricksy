from django.db import models


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    google_location = models.URLField(blank=True)
    building = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    location_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.region})"
    class Meta:
        db_table = 'customers'