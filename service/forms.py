from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["service_type", "duration", "material", "number_of_cleaners"]
        widgets = {
            "service_type": forms.Select(attrs={"class": "form-control"}),
            "duration": forms.NumberInput(attrs={"class": "form-control"}),
            "material": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "number_of_cleaners": forms.NumberInput(attrs={"class": "form-control"}),
        }
