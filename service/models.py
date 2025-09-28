from django.db import models

class Service(models.Model):
    SERVICE_TYPES = [
        ('home', 'Home Cleaning'),
        ('office', 'Office Cleaning'),
    ]

    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    material = models.TextField(blank=True)
    number_of_cleaners = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.get_service_type_display()} - ({self.number_of_cleaners})"

    class Meta:
        db_table = 'services'