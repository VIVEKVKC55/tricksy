from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "duration", "material", "base_price"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "duration": forms.NumberInput(attrs={"class": "form-control"}),
            "material": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "base_price": forms.NumberInput(attrs={"class": "form-control"}),
        }
