from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Service
from .forms import ServiceForm
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from account.utils import user_has_access
from django.shortcuts import render


class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = "service/list.html"
    context_object_name = "services"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "view_services"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)

        # ✅ This line is essential:
        return super().dispatch(request, *args, **kwargs)


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "service/form.html"
    success_url = reverse_lazy("service:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_services"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Service created successfully!")
        return super().form_valid(form)


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "service/form.html"
    success_url = reverse_lazy("service:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_services"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Service updated successfully!")
        return super().form_valid(form)


class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    success_url = reverse_lazy("service:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_services"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Service deleted successfully!"})
        
        messages.success(request, "Service deleted successfully!")
        return super().delete(request, *args, **kwargs)