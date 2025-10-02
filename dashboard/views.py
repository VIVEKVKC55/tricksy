from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta

from customer.models import Region
from booking.models import Booking, BookingService
from payment.models import Payment
from service.models import Service  # ✅ Import your Service model
from tricksy.constants import GOOGLE_MAPS_API_KEY
from django.db.models import Sum, Prefetch, Q


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"
    login_url = "account:login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["google_maps_api_key"] = GOOGLE_MAPS_API_KEY

        # === Earnings Chart (Last 7 Days) ===
        today = now().date()
        earnings_labels, earnings_data = [], []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            total_earnings = (
                Payment.objects.filter(paid_at__date=day)
                .aggregate(total=Sum("net_amount"))["total"]
                or 0
            )
            earnings_labels.append(day.strftime("%a"))
            earnings_data.append(float(total_earnings))

        context["earnings_labels"] = earnings_labels
        context["earnings_data"] = earnings_data

        # === Pending Payments ===
        pending_payments = Booking.objects.filter(payments__isnull=True)
        context["pending_payment_count"] = pending_payments.count()

        # === Revenue by Service Type ===
        service_labels, service_data = [], []
        for service in Service.objects.all():
            total = (
                Payment.objects.filter(booking__booking_services__service=service)
                .aggregate(total=Sum("net_amount"))["total"]
                or 0
            )
            # 🔧 FIXED: Use field instead of calling like a function
            service_labels.append(service.name)
            service_data.append(float(total))

        context["service_labels"] = service_labels
        context["service_data"] = service_data

        # === Total Summary ===
        context["total_earnings"] = (
            Payment.objects.aggregate(total=Sum("net_amount"))["total"] or 0
        )

        today_bookings = (
            Booking.objects.select_related("customer")
            .prefetch_related(
                Prefetch("booking_services", queryset=BookingService.objects.select_related("service")),
                Prefetch("payments", queryset=Payment.objects.order_by("-paid_at")),
            )
            .filter(created_at__date=today)
            .order_by("-created_at")
        )

        booking_list = []
        for booking in today_bookings:
            payments = booking.payments.all()
            total_paid = sum(p.net_amount for p in payments)

            service_names = ", ".join(
                bs.service.name() for bs in booking.booking_services.all()
            )

            payment_status = "Confirmed ✅" if payments.exists() else "Pending ❌"

            region = getattr(booking.customer, "region", None) or getattr(booking, "region", "N/A")

            booking_list.append({
                "reference": booking.booking_reference,
                "customer_name": booking.customer.full_name if booking.customer else "N/A",
                "region": region,
                "service_names": service_names,
                "payment_status": payment_status,
                "created_at": booking.created_at,
                "total_paid": total_paid,
            })

        context["today_bookings"] = booking_list
        context["today_date"] = today

        return context

class RegionBookingDataView(LoginRequiredMixin, View):
    def get(self, request):
        data = []
        regions = Region.objects.all()

        for region in regions:
            booking_count = sum(
                customer.bookings.count() for customer in region.customers.all()
            )

            data.append({
                "region_name": region.region_name,
                "latitude": float(region.latitude) if region.latitude else None,
                "longitude": float(region.longitude) if region.longitude else None,
                "booking_count": booking_count,
            })

        return JsonResponse({"regions": data})
