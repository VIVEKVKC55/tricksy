from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path("api/region-bookings/", views.RegionBookingDataView.as_view(), name="region_bookings_api"),
]