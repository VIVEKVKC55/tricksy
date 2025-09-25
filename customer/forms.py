from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "full_name",
            "region",
            "address",
            "google_location",
            "building",
            "unit",
            "location_notes",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "location_notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-control".strip()
