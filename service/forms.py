from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "duration", "material", "base_price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter service name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Enter service description"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Duration (minutes)"}),
            "material": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "List of materials used"}),
            "base_price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter base price"}),
        }
