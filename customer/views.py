from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.views import View
from account.utils import user_has_access
from .models import Customer
from .forms import CustomerForm
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

# List View with DataTable
class CustomerListView(LoginRequiredMixin, ListView):
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
class CustomerCreateView(LoginRequiredMixin, CreateView):
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
class CustomerUpdateView(LoginRequiredMixin, UpdateView):
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
class CustomerDeleteView(LoginRequiredMixin, DeleteView):
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


class CustomerAjaxView(View):
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        try:
            customer = Customer.objects.select_related("region").get(email=email)
            data = {
                "full_name": customer.full_name,
                "region": customer.region.id if customer.region else "",
                "region_name": customer.region.region_name if customer.region else "",
                "address": customer.address,
                "google_location": customer.google_location,
                "building": customer.building,
                "unit": customer.unit,
                "location_notes": customer.location_notes,
            }
            return JsonResponse({"exists": True, "data": data})
        except Customer.DoesNotExist:
            return JsonResponse({"exists": False})