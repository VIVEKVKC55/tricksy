from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking_home, name='booking_home'),
    # path('create/', views.create_booking, name='create_booking'),
    # path('view/<int:booking_id>/', views.view_booking, name='view_booking'),
    # path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]