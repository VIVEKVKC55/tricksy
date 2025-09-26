from django import forms
from .models import Booking, BookingService, BookingCleaner
import uuid


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "cleaning_instructions",
            "special_request",
            "entry_instruction",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "cleaning_instructions": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "special_request": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "entry_instruction": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        # Auto-generate booking_reference only if new
        if not instance.booking_reference:
            instance.booking_reference = f"BK-{uuid.uuid4().hex[:8].upper()}"
        if user:
            instance.created_by = user
        if commit:
            instance.save()
        return instance


class BookingServiceForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ["service", "number_of_cleaners"]
        widgets = {
            "service": forms.Select(attrs={"class": "form-select"}),
            "number_of_cleaners": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


class BookingCleanerForm(forms.ModelForm):
    class Meta:
        model = BookingCleaner
        fields = ["cleaner"]
        widgets = {
            "cleaner": forms.Select(attrs={"class": "form-select"}),
        }
