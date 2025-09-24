from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    material = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'services'