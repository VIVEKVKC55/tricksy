from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

from account.utils import user_has_access
from .models import Customer
from .forms import CustomerForm
from django.http import JsonResponse

# List View with DataTable
class CustomerListView(ListView):
    model = Customer 
    template_name = "customer/list.html"
    context_object_name = "customers"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "view_customers"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

# Create View
class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/create.html"
    success_url = reverse_lazy("customer:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_customers"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Customer created successfully!")
        return super().form_valid(form)

# Update View
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/update.html"
    success_url = reverse_lazy("customer:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_customers"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Customer updated successfully!")
        return super().form_valid(form)

# Delete View
class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy("customer:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_customers"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({"success": True, "message": "Customer deleted successfully!"})
