from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.BookingListView.as_view(), name='list'),
    path('create/', views.BookingCreateView.as_view(), name='create'),
    path('update/<int:booking_id>/', views.BookingUpdateView.as_view(), name='update'),
    path('delete/<int:booking_id>/', views.BookingDeleteView.as_view(), name='delete'),
]