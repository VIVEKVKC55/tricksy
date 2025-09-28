from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"  # Move to dashboard app
    login_url = "login"  # Redirect to this URL if user is not logged in
    redirect_field_name = "next"  # Redirect back after successful login
