# utils.py
from tricksy.constants import PERMISSIONS

def user_has_access(user, permission_code):
    """
    ✅ Always True if Superadmin
    ✅ For Subadmin → check if permission_code is in their permissions
    """
    if not hasattr(user, "role"):
        return False

    if user.role.role == "superadmin":
        return True  # full access

    return permission_code in user.role.permissions
