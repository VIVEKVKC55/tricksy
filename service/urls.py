from django.urls import path
from . import views

app_name = "service"

urlpatterns = [
    path("list/", views.ServiceListView.as_view(), name="list"),
    path("create/", views.ServiceCreateView.as_view(), name="create"),
    path("edit/<int:pk>/", views.ServiceUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>/", views.ServiceDeleteView.as_view(), name="delete"),
]
