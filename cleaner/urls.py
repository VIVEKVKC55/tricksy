from django.urls import path
from . import views

app_name = 'cleaner'

urlpatterns = [
    path("list/", views.CleanerListView.as_view(), name="list"),
    path("create/", views.CleanerCreateView.as_view(), name="create"),
    path("edit/<int:pk>/", views.CleanerUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>/", views.CleanerDeleteView.as_view(), name="delete"),

    path("calendar/<int:cleaner_id>/", views.CleanerCalendarView.as_view(), name="cleaner-calendar"),
    path("calendar/<int:cleaner_id>/data/", views.CleanerCalendarDataView.as_view(), name="cleaner-calendar-data"),
]