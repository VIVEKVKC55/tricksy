# cleaners/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from .models import Cleaner
from .forms import CleanerForm

class CleanerListView(ListView):
    model = Cleaner
    template_name = "cleaner/list.html"
    context_object_name = "cleaners"

class CleanerCreateView(CreateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaner/create.html"
    success_url = reverse_lazy("cleaner:list")

    def form_valid(self, form):
        messages.success(self.request, "Cleaner added successfully!")
        return super().form_valid(form)

class CleanerUpdateView(UpdateView):
    model = Cleaner
    form_class = CleanerForm
    template_name = "cleaner/update.html"
    success_url = reverse_lazy("cleaner:list")

    def form_valid(self, form):
        messages.success(self.request, "Cleaner updated successfully!")
        return super().form_valid(form)

class CleanerDeleteView(DeleteView):
    model = Cleaner
    success_url = reverse_lazy("cleaner:list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Cleaner deleted successfully!"})
        messages.success(request, "Cleaner deleted successfully!")
        return super().delete(request, *args, **kwargs)
