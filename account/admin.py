# admin.py
from django.contrib import admin
from django import forms
from .models import Role, RolePermissions
from tricksy.constants import PERMISSIONS


class RoleAdminForm(forms.ModelForm):
    """
    This form is now just for Role (user + role).
    We no longer handle permissions here, since RolePermissions is a separate model.
    """
    class Meta:
        model = Role
        fields = ['user', 'role']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ("user", "role")


class RolePermissionsAdminForm(forms.ModelForm):
    """
    Admin form for RolePermissions — allows selecting multiple permissions as checkboxes.
    """
    permissions = forms.MultipleChoiceField(
        choices=[(key, label) for key, label in PERMISSIONS.items()],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = RolePermissions
        fields = ["role", "permissions"]

    def clean_permissions(self):
        role = self.cleaned_data.get("role")
        # If superadmin, allow empty (they have full access implicitly)
        if role == Role.SUPERADMIN:
            return []  
        return self.cleaned_data["permissions"]


@admin.register(RolePermissions)
class RolePermissionsAdmin(admin.ModelAdmin):
    form = RolePermissionsAdminForm
    list_display = ("role",)

    def save_model(self, request, obj, form, change):
        """
        Ensure only one RolePermissions per role.
        If already exists, update instead of duplicate.
        """
        existing = RolePermissions.objects.filter(role=obj.role).first()
        if existing and not change:
            # Update existing instead of creating a new record
            existing.permissions = obj.permissions
            existing.save()
        else:
            super().save_model(request, obj, form, change)
