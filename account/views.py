from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from .utils import user_has_access
from django.contrib.auth.models import User
from .models import Role, RolePermissions
from tricksy.constants import PERMISSIONS


def custom_permission_denied(request, exception=None):
    return render(request, "errors/forbidden_alert.html", {"message": "Access Denied"}, status=403)


def manage_services_view(request):
    if not user_has_access(request.user, "manage_services"):
        return messages.error(request, "Access denied")

    # Your normal view logic
    return JsonResponse({"detail": "Service management allowed!"})

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/list.html"
    context_object_name = "users"
    paginate_by = 10  # Show 10 users per page

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_subadmins"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.select_related("role").order_by("id")
        query = self.request.GET.get("q", "")
        if query:
            queryset = queryset.filter(username__icontains=query)
        return queryset

class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        """Render login page on GET request."""
        return render(request, self.template_name)

    def post(self, request):
        """Handle login logic on POST request."""
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.GET.get("next") or request.POST.get("next")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            if next_url:
                return redirect(next_url)
            return redirect("/")  # Fallback to dashboard/home
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name, {"next": next_url})


class LogoutView(View):
    def get(self, request):
        """Log the user out and redirect to login page."""
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("account:login")  # Named URL for login page


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        """Render registration page on GET request."""
        return render(request, self.template_name)

    def post(self, request):
        """Handle user registration logic on POST request."""
        username = request.POST.get("username")
        password = request.POST.get("password")
        # Add additional fields as necessary

        if not user_has_access(request.user, "manage_subadmins"):
            messages.error(request, "You do not have permission to register new users.")
            return render(request, self.template_name)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, self.template_name)

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful! Please log in.")
        return redirect("user:login")  # Named URL for login page
    


class CreateSubadminView(LoginRequiredMixin, View):
    template_name = "accounts/create_subadmin.html"

    def get(self, request):
        # Only Superadmins can create Subadmins
        if not hasattr(request.user, "role") or request.user.role.role != Role.SUPERADMIN:
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return render(request, self.template_name)

    def post(self, request):
        if not hasattr(request.user, "role") or request.user.role.role != Role.SUPERADMIN:
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("create_subadmin")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("create_subadmin")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Assign Subadmin role
        Role.objects.create(user=user, role=Role.SUBADMIN)

        messages.success(request, f"Subadmin '{username}' created successfully.")
        return redirect("account:list")  # Redirect to your user list page


class ManageSubadminPermissionsView(LoginRequiredMixin, View):
    template_name = "accounts/manage_permissions.html"

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "role") or request.user.role.role != Role.SUPERADMIN:
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """ ✅ Render permission management page for Subadmin """
        role_permissions, _ = RolePermissions.objects.get_or_create(role=Role.SUBADMIN)

        context = {
            "permissions": PERMISSIONS,
            "selected_permissions": role_permissions.permissions or [],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """ ✅ Handle permission updates for Subadmin """
        selected_perms = request.POST.getlist("permissions")

        role_permissions, _ = RolePermissions.objects.get_or_create(role=Role.SUBADMIN)
        role_permissions.permissions = selected_perms
        role_permissions.save()

        messages.success(request, "✅ Permissions updated successfully for Subadmins.")
        return redirect("account:list")