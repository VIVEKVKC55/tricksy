from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('list/', views.CustomerListView.as_view(), name='list'),
    path('create/', views.CustomerCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.CustomerUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.CustomerDeleteView.as_view(), name='delete'),
    path("check/", views.CustomerAjaxView.as_view(), name="check"),
    # path('detail/<int:pk>/', views.CustomerDetailView.as_view(), name='detail'),

    path("calendar/<int:customer_id>/", views.CustomerCalendarView.as_view(), name="customer-calendar"),
    path("calendar/<int:customer_id>/data/", views.CustomerCalendarDataView.as_view(), name="customer-calendar-data"),
]