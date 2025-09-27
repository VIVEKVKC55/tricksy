from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from .models import Cleaner
from .forms import CleanerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from account.utils import user_has_access

class CleanerListView(LoginRequiredMixin, ListView):
    model = Cleaner
    template_name = "cleaner/list.html"
    context_object_name = "cleaners"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "view_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

        # ✅ This line is essential:
        return super().dispatch(request, *args, **kwargs)

class CleanerCreateView(LoginRequiredMixin, CreateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaner/create.html"
    success_url = reverse_lazy("cleaner:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

    def form_valid(self, form):
        messages.success(self.request, "Cleaner added successfully!")
        return super().form_valid(form)

class CleanerUpdateView(LoginRequiredMixin, UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaner/update.html"
    success_url = reverse_lazy("cleaner:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

    def form_valid(self, form):
        messages.success(self.request, "Cleaner updated successfully!")
        return super().form_valid(form)

class CleanerDeleteView(LoginRequiredMixin, DeleteView):
    model = Cleaner
    success_url = reverse_lazy("cleaner:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Cleaner deleted successfully!"})
        messages.success(request, "Cleaner deleted successfully!")
        return super().delete(request, *args, **kwargs)
