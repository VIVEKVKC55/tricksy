from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Service
from .forms import ServiceForm
from django.http import JsonResponse


class ServiceListView(ListView):
    model = Service
    template_name = "service/list.html"
    context_object_name = "services"


class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "service/form.html"
    success_url = reverse_lazy("service:list")

    def form_valid(self, form):
        messages.success(self.request, "Service created successfully!")
        return super().form_valid(form)


class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "service/form.html"
    success_url = reverse_lazy("service:list")

    def form_valid(self, form):
        messages.success(self.request, "Service updated successfully!")
        return super().form_valid(form)


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy("service:list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Service deleted successfully!"})
        
        messages.success(request, "Service deleted successfully!")
        return super().delete(request, *args, **kwargs)