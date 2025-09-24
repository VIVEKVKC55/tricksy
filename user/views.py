from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from .utils import user_has_access
from django.contrib.auth.models import User

def manage_services_view(request):
    if not user_has_access(request.user, "manage_services"):
        return HttpResponseForbidden("Access denied")

    # Your normal view logic
    return JsonResponse({"detail": "Service management allowed!"})

class LoginView(View):
    template_name = "user/login.html"

    def get(self, request):
        """Render login page on GET request."""
        return render(request, self.template_name)

    def post(self, request):
        """Handle login logic on POST request."""
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("/")  # Change to dashboard or home page
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        """Log the user out and redirect to login page."""
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("user:login")  # Named URL for login page


class RegisterView(View):
    template_name = "user/register.html"

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