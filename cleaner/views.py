from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from .models import Cleaner
from .forms import CleanerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from account.utils import user_has_access

from django.utils import timezone
from datetime import datetime
from django.views import View
from booking.models import BookingCleaner

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
    template_name = "cleaner/form.html"
    success_url = reverse_lazy("cleaner:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Cleaner added successfully!")
        return super().form_valid(form)

class CleanerUpdateView(LoginRequiredMixin, UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaner/form.html"
    success_url = reverse_lazy("cleaner:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_cleaners"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        
        return super().dispatch(request, *args, **kwargs)

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

        # ✅ Must return this line for valid HttpResponse
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # ✅ Support AJAX delete
            return JsonResponse({
                "success": True,
                "message": "Cleaner deleted successfully!"
            })

        messages.success(request, "Cleaner deleted successfully!")
        return super().delete(request, *args, **kwargs)

class CleanerCalendarView(View):
    """Render the calendar view for a specific cleaner."""
    template_name = "cleaner/calendar.html"

    def get(self, request, cleaner_id):
        cleaner = get_object_or_404(Cleaner, id=cleaner_id)
        return render(request, self.template_name, {"cleaner": cleaner})

class CleanerCalendarDataView(View):
    def get(self, request, cleaner_id):
        events = []
        now = timezone.now()

        assignments = (
            BookingCleaner.objects
            .select_related("booking", "cleaner")
            .filter(cleaner_id=cleaner_id)
        )

        for assign in assignments:
            booking = assign.booking
            start_dt = datetime.combine(booking.start_date, booking.start_time)
            end_dt = datetime.combine(booking.end_date, booking.end_time)

            # Make both datetimes timezone-aware
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)

            # Determine booking status
            if end_dt < now:
                color = "#4CAF50"   # ✅ Completed
                status = "Completed"
            elif start_dt > now:
                color = "#2196F3"   # 🔵 Upcoming
                status = "Upcoming"
            else:
                color = "#FFC107"   # 🟡 Ongoing
                status = "Ongoing"

            events.append({
                "id": booking.id,
                "title": f"{booking.booking_reference} — {booking.customer.full_name}",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "color": color,
                "extendedProps": {
                    "status": status,
                    "customer": booking.customer.full_name,
                    "address": booking.customer.address,
                    "duration_hours": round((end_dt - start_dt).total_seconds() / 3600, 1),
                    "region": booking.customer.region.region_name if booking.customer.region else "N/A",
                }
            })

        return JsonResponse(events, safe=False)
