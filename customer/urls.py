from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('list/', views.CustomerListView.as_view(), name='list'),
    path('create/', views.CustomerCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', views.CustomerUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.CustomerDeleteView.as_view(), name='delete'),
    # path('detail/<int:pk>/', views.CustomerDetailView.as_view(), name='detail'),
]