# utils.py
from django.shortcuts import redirect
from django.urls import reverse
from tricksy.constants import PERMISSIONS
from account.models import Role, RolePermissions

def user_has_access(user, permission_code):
    """
    ✅ Grants access based on role permissions.
       - Superadmin → always True
       - Subadmin → check RolePermissions for 'subadmin'
    """

    # Step 1: If user not logged in → redirect to login page
    if not user.is_authenticated:
        return redirect(reverse('account:login'))  # make sure you have 'login' named URL
    # if user doesn't have a role
    if not hasattr(user, "role"):
        return False

    # Superadmin always has full access
    if user.role.role == Role.SUPERADMIN:
        return True

    # Subadmin → check in RolePermissions model
    try:
        role_perms = RolePermissions.objects.get(role=Role.SUBADMIN)
        return permission_code in (role_perms.permissions or [])
    except RolePermissions.DoesNotExist:
        return False
