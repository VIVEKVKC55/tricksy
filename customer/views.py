from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.views import View
from account.utils import user_has_access
from .models import Customer
from .forms import CustomerForm
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime
from booking.models import Booking
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
        

class CustomerCalendarView(View):
    """Render FullCalendar for customer's bookings."""
    template_name = "customer/calendar.html"

    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        return render(request, self.template_name, {"customer": customer})


class CustomerCalendarDataView(View):
    """Provide all bookings of a specific customer in JSON format."""

    def get(self, request, customer_id):
        now = timezone.localtime(timezone.now())
        events = []

        bookings = (
            Booking.objects
            .select_related("customer")
            .filter(customer__customer_id=customer_id)
        )

        for booking in bookings:
            start_dt = timezone.make_aware(datetime.combine(booking.start_date, booking.start_time))
            end_dt = timezone.make_aware(datetime.combine(booking.end_date, booking.end_time))

            if end_dt < now:
                color = "#4CAF50"  # ✅ Completed
                status = "Completed"
            elif start_dt > now:
                color = "#2196F3"  # 🔵 Upcoming
                status = "Upcoming"
            else:
                color = "#FFC107"  # 🟡 Ongoing
                status = "Ongoing"

            events.append({
                "id": booking.id,
                "title": f"{booking.booking_reference} — {booking.customer.full_name}",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "color": color,
                "extendedProps": {
                    "status": status,
                    "address": booking.customer.address,
                    "duration_hours": round((end_dt - start_dt).total_seconds() / 3600, 1),
                    "region": booking.customer.region.region_name if booking.customer.region else "N/A",
                },
            })

        return JsonResponse(events, safe=False)