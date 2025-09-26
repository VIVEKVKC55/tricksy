from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy

from django.db.models import Count, Prefetch
from .models import Booking, BookingService, BookingCleaner
from .forms import BookingForm, BookingServiceForm, BookingCleanerForm
from customer.forms import CustomerForm
from payment.models import Payment
from cleaner.models import Cleaner
from django.db import transaction
from account.utils import user_has_access


def home(request):
    return render(request, 'booking/home.html')


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "booking/list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "view_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Prefetch all related objects to minimize database hits.
        """
        return (
            Booking.objects.select_related("customer", "created_by")
            .prefetch_related(
                Prefetch("booking_services", queryset=BookingService.objects.select_related("service")),
                Prefetch("booking_cleaners", queryset=BookingCleaner.objects.select_related("cleaner")),
                Prefetch("payments", queryset=Payment.objects.order_by("-paid_at")),
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        """
        Adds latest payment info and cleaner assignment status to each booking.
        """
        context = super().get_context_data(**kwargs)
        for booking in context["bookings"]:
            payments = booking.payments.all()
            booking.latest_payment = payments[0] if payments else None
            booking.is_cleaner_assigned = booking.booking_cleaners.exists()
            booking.payment_status = "Completed" if payments.exists() else "Pending"
            # booking.total_cleaners = sum(bs.number_of_cleaners for bs in booking.booking_services.all())
        return context

class BookingCreateView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        booking_form = BookingForm()
        customer_form = CustomerForm()

        # Only service formset now
        ServiceFormSet = modelformset_factory(
            BookingService, form=BookingServiceForm, extra=1, can_delete=True
        )
        service_formset = ServiceFormSet(queryset=BookingService.objects.none())

        return render(request, "booking/create.html", {
            "booking_form": booking_form,
            "customer_form": customer_form,
            "service_formset": service_formset,
        })

    def post(self, request):
        booking_form = BookingForm(request.POST)
        customer_form = CustomerForm(request.POST)

        ServiceFormSet = modelformset_factory(
            BookingService, form=BookingServiceForm, extra=1, can_delete=True
        )
        service_formset = ServiceFormSet(request.POST, queryset=BookingService.objects.none())
        try:
            if all([booking_form.is_valid(), customer_form.is_valid(), service_formset.is_valid()]):
                # Save customer
                customer = customer_form.save()

                # Save booking linked to customer
                booking = booking_form.save(commit=False, user=request.user)
                booking.customer = customer
                booking.created_by = request.user
                booking.save()


                # Save services
                for sf in service_formset:
                    service = sf.save(commit=False)
                    service.booking = booking
                    service.save()

                messages.success(request, "Booking and customer created successfully!")
                return redirect("booking:list")  # redirect to booking list page
        except Exception as e:
            print(e)
            messages.error(request, f"An error occurred: {str(e)}")
        return render(request, "booking/create.html", {
            "booking_form": booking_form,
            "customer_form": customer_form,
            "service_formset": service_formset,
        })


class BookingUpdateView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
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

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
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

        return render(request, "booking/update.html", {
            "form": form,
            "service_formset": service_formset,
            "cleaner_formset": cleaner_formset,
            "booking": booking,
        })


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy("booking:list")

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Booking deleted successfully!"})
        messages.success(request, "Booking deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
class BookingAssignView(LoginRequiredMixin, View):
    template_name = "booking/assign.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch() to check permission before processing the view.
        """
        if not user_has_access(request.user, "manage_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        cleaners = Cleaner.objects.all()
        assigned_cleaners = list(booking.booking_cleaners.values_list("cleaner_id", flat=True))

        total_required_cleaners = booking.total_required_cleaners()
        total_amount = booking.calculate_total_amount()

        return render(request, self.template_name, {
            "booking": booking,
            "cleaners": cleaners,
            "assigned_cleaners": assigned_cleaners,
            "total_required_cleaners": total_required_cleaners,
            "total_amount": total_amount,
        })

    @transaction.atomic
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        cleaner_ids = request.POST.getlist("cleaners")
        payment_method = request.POST.get("payment_method")

        # Validation 1: Check cleaner count
        required_cleaners = booking.total_required_cleaners()
        if len(cleaner_ids) != required_cleaners:
            messages.error(
                request,
                f"You must assign exactly {required_cleaners} cleaners (selected {len(cleaner_ids)})."
            )
            return redirect("booking:assign", pk=pk)

        # Validation 2: Payment method required
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("booking:assign", pk=pk)

        # Assign cleaners
        BookingCleaner.objects.filter(booking=booking).delete()
        for cid in cleaner_ids:
            BookingCleaner.objects.create(booking=booking, cleaner_id=cid)

        # Calculate and save payment
        amount = booking.calculate_total_amount()
        Payment.objects.create(
            booking=booking,
            payment_method=payment_method,
            amount=amount,
            discount=0,
            net_amount=amount,
        )

        messages.success(request, "✅ Cleaners assigned and payment recorded successfully!")
        return redirect("booking:list")
