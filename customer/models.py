from django.db import models


class Region(models.Model):
    region_name = models.CharField(max_length=100, unique=True)
    region_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'regions'
        ordering = ['region_name']

    def __str__(self):
        return self.region_name


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='customers')
    address = models.TextField()
    google_location = models.URLField(blank=True)
    building = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    location_notes = models.TextField(blank=True)

    def __str__(self):
        region_name = self.region.region_name if self.region else "No Region"
        return f"{self.full_name} ({region_name})"

    class Meta:
        db_table = 'customers'