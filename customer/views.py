from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm
from django.http import JsonResponse

# List View with DataTable
class CustomerListView(ListView):
    model = Customer 
    template_name = "customer/list.html"
    context_object_name = "customers"

# Create View
class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/create.html"
    success_url = reverse_lazy("customer:list")

    def form_valid(self, form):
        messages.success(self.request, "Customer created successfully!")
        return super().form_valid(form)

# Update View
class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "customer/update.html"
    success_url = reverse_lazy("customer:list")

    def form_valid(self, form):
        messages.success(self.request, "Customer updated successfully!")
        return super().form_valid(form)

# Delete View
class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy("customer:list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({"success": True, "message": "Customer deleted successfully!"})
