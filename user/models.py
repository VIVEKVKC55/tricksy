from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    SUPERADMIN = "superadmin"
    SUBADMIN = "subadmin"
    ROLE_CHOICES = [
        (SUPERADMIN, "Superadmin"),
        (SUBADMIN, "Subadmin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="role")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SUBADMIN)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    class Meta:
        db_table = 'user_roles'


class RolePermissions(models.Model):
    """
    ✅ Stores global permissions for each role
    Example:
    - 1 record for Sub-admin
    - 1 record for Superadmin (optional, can be empty)
    """
    role = models.CharField(max_length=20, choices=Role.ROLE_CHOICES, unique=True)
    permissions = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Permissions for {self.role}"
    class Meta:
        db_table = 'role_permissions'