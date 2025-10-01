from django import forms
from .models import Customer, Region


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "full_name",
            "email",
            "region",
            "address",
            "google_location",
            "building",
            "unit",
            "location_notes",
        ]
        widgets = {
            "region": forms.Select(attrs={"class": "form-select"}),  # dropdown style
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "location_notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # sort regions alphabetically
        self.fields["region"].queryset = Region.objects.all().order_by("region_name")

        # add consistent Bootstrap styling
        for field_name, field in self.fields.items():
            if field_name != "region":  # region already uses form-select
                existing_classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing_classes} form-control".strip()
