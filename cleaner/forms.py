from django import forms
from .models import Cleaner

class CleanerForm(forms.ModelForm):
    class Meta:
        model = Cleaner
        fields = ["name", "company", "vehicle_code", "is_available"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "vehicle_code": forms.TextInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }