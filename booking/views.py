
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy


from .models import Booking, BookingService, BookingCleaner
from .forms import BookingForm, BookingServiceForm, BookingCleanerForm


def home(request):
    return render(request, 'booking/home.html')


class BookingListView(ListView):
    model = Booking
    template_name = "booking/list.html"
    context_object_name = "bookings"
    paginate_by = 10  # optional for pagination

    def get_queryset(self):
        return Booking.objects.select_related("customer", "created_by").prefetch_related("booking_services__service", "booking_cleaners__cleaner").order_by("-created_at")


class BookingCreateView(View):
    def get(self, request):
        form = BookingForm()
        ServiceFormSet = modelformset_factory(BookingService, form=BookingServiceForm, extra=1, can_delete=True)
        CleanerFormSet = modelformset_factory(BookingCleaner, form=BookingCleanerForm, extra=1, can_delete=True)

        service_formset = ServiceFormSet(queryset=BookingService.objects.none())
        cleaner_formset = CleanerFormSet(queryset=BookingCleaner.objects.none())

        return render(request, "booking/create.html", {
            "form": form,
            "service_formset": service_formset,
            "cleaner_formset": cleaner_formset,
        })

    def post(self, request):
        form = BookingForm(request.POST)
        ServiceFormSet = modelformset_factory(BookingService, form=BookingServiceForm, extra=1, can_delete=True)
        CleanerFormSet = modelformset_factory(BookingCleaner, form=BookingCleanerForm, extra=1, can_delete=True)

        service_formset = ServiceFormSet(request.POST, queryset=BookingService.objects.none())
        cleaner_formset = CleanerFormSet(request.POST, queryset=BookingCleaner.objects.none())

        if form.is_valid() and service_formset.is_valid() and cleaner_formset.is_valid():
            booking = form.save(user=request.user)

            for sf in service_formset:
                if sf.cleaned_data and not sf.cleaned_data.get("DELETE"):
                    booking_service = sf.save(commit=False)
                    booking_service.booking = booking
                    booking_service.save()

            for cf in cleaner_formset:
                if cf.cleaned_data and not cf.cleaned_data.get("DELETE"):
                    booking_cleaner = cf.save(commit=False)
                    booking_cleaner.booking = booking
                    booking_cleaner.save()

            messages.success(request, "Booking created successfully!")
            return redirect("booking:list")

        return render(request, "booking/booking_form.html", {
            "form": form,
            "service_formset": service_formset,
            "cleaner_formset": cleaner_formset,
        })


class BookingUpdateView(View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = BookingForm(instance=booking)
        ServiceFormSet = modelformset_factory(BookingService, form=BookingServiceForm, extra=0, can_delete=True)
        CleanerFormSet = modelformset_factory(BookingCleaner, form=BookingCleanerForm, extra=0, can_delete=True)

        service_formset = ServiceFormSet(queryset=booking.booking_services.all())
        cleaner_formset = CleanerFormSet(queryset=booking.booking_cleaners.all())

        return render(request, "booking/update.html", {
            "form": form,
            "service_formset": service_formset,
            "cleaner_formset": cleaner_formset,
            "booking": booking,
        })

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = BookingForm(request.POST, instance=booking)
        ServiceFormSet = modelformset_factory(BookingService, form=BookingServiceForm, extra=0, can_delete=True)
        CleanerFormSet = modelformset_factory(BookingCleaner, form=BookingCleanerForm, extra=0, can_delete=True)

        service_formset = ServiceFormSet(request.POST, queryset=booking.booking_services.all())
        cleaner_formset = CleanerFormSet(request.POST, queryset=booking.booking_cleaners.all())

        if form.is_valid() and service_formset.is_valid() and cleaner_formset.is_valid():
            booking = form.save(user=request.user)

            for sf in service_formset:
                if sf.cleaned_data:
                    if sf.cleaned_data.get("DELETE") and sf.instance.pk:
                        sf.instance.delete()
                    else:
                        booking_service = sf.save(commit=False)
                        booking_service.booking = booking
                        booking_service.save()

            for cf in cleaner_formset:
                if cf.cleaned_data:
                    if cf.cleaned_data.get("DELETE") and cf.instance.pk:
                        cf.instance.delete()
                    else:
                        booking_cleaner = cf.save(commit=False)
                        booking_cleaner.booking = booking
                        booking_cleaner.save()

            messages.success(request, "Booking updated successfully!")
            return redirect("booking:list")

        return render(request, "booking/booking_form.html", {
            "form": form,
            "service_formset": service_formset,
            "cleaner_formset": cleaner_formset,
            "booking": booking,
        })


class BookingDeleteView(DeleteView):
    model = Booking
    success_url = reverse_lazy("booking:list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Booking deleted successfully!"})
        messages.success(request, "Booking deleted successfully!")
        return super().delete(request, *args, **kwargs)