from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from customer.models import Region


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"
    login_url = "account:login"
    redirect_field_name = "next"


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
