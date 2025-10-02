from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.generic import ListView, DeleteView, TemplateView
from django.urls import reverse_lazy

from django.db.models import Count, Prefetch, Q
from .models import Booking, BookingService, BookingCleaner
from .forms import BookingForm, BookingServiceForm
from customer.forms import CustomerForm
from payment.models import Payment
from cleaner.models import Cleaner
from customer.models import Customer
from django.db import transaction
from account.utils import user_has_access
from django.utils import timezone
from datetime import datetime
from decimal import Decimal


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
            # Step 1: Extract email from POST
            email = request.POST.get("email")
            existing_customer = None
            if email:
                existing_customer = Customer.objects.filter(email=email).first()
            if existing_customer:
                customer_form = CustomerForm(request.POST, instance=existing_customer)
            else:
                customer_form = CustomerForm(request.POST)
            if all([booking_form.is_valid(), customer_form.is_valid(), service_formset.is_valid()]):
                customer = customer_form.save()

                # Save booking linked to this customer
                booking = booking_form.save(commit=False)
                booking.customer = customer
                booking.created_by = request.user
                booking.save()

                # Step 7: Save all services
                for sf in service_formset:
                    service = sf.save(commit=False)
                    service.booking = booking
                    service.save()

                messages.success(request, "Booking and customer saved successfully!")
                return redirect("booking:list")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            print(str(e))

        return render(
            request,
            "booking/create.html",
            {
                "booking_form": booking_form,
                "customer_form": customer_form,
                "service_formset": service_formset,
            },
        )



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

        service_formset = ServiceFormSet(queryset=booking.booking_services.all())

        return render(request, "booking/update.html", {
            "form": form,
            "service_formset": service_formset,
            "booking": booking,
        })

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        form = BookingForm(request.POST, instance=booking)
        ServiceFormSet = modelformset_factory(BookingService, form=BookingServiceForm, extra=0, can_delete=True)

        service_formset = ServiceFormSet(request.POST, queryset=booking.booking_services.all())
        try:
            if form.is_valid() and service_formset.is_valid():
                booking = form.save(commit=False)
                booking.save()

                for sf in service_formset:
                    if sf.cleaned_data:
                        booking_service = sf.save(commit=False)
                        booking_service.booking = booking
                        booking_service.save()

                messages.success(request, "Booking updated successfully!")
                return redirect("booking:list")
        except Exception as e:
            print(e)
            messages.error(request, f"An error occurred: {str(e)}")

        return render(request, "booking/update.html", {
            "form": form,
            "service_formset": service_formset,
            "booking": booking,
        })


class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy("booking:list")

    def dispatch(self, request, *args, **kwargs):
        if not user_has_access(request.user, "manage_bookings"):
            context = {"message": "🚫 Access denied: Superadmins only!"}
            return render(request, "errors/forbidden_alert.html", context, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        booking_id = self.kwargs.get("booking_id")
        return get_object_or_404(Booking, id=booking_id)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Booking deleted successfully!"})
        messages.success(request, "✅ Booking deleted successfully!")
        return redirect(self.success_url)

    

class BookingAssignView(LoginRequiredMixin, View):
    """View to assign cleaners to a booking and record payment."""
    template_name = "booking/assign.html"

    def dispatch(self, request, *args, **kwargs):
        """Restrict access to only users with assign_cleaners permission."""
        if not user_has_access(request.user, "assign_cleaners"):
            return render(
                request,
                "errors/forbidden_alert.html",
                {"message": "🚫 Access denied: Superadmins only!"},
                status=403,
            )
        return super().dispatch(request, *args, **kwargs)

    def calculate_booking_cost(self, booking):
        """Calculate total booking cost based on services, duration, and cleaners."""
        total_cost = Decimal("0.00")

        # Combine start + end times
        start_dt = datetime.combine(booking.start_date, booking.start_time)
        end_dt = datetime.combine(booking.end_date, booking.end_time)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        duration_hours = Decimal(duration_minutes) / Decimal(60)

        # Get all booking services
        for bs in booking.booking_services.all():
            base_price = bs.service.base_price  # Decimal
            num_cleaners = Decimal(bs.number_of_cleaners)

            cost = base_price * duration_hours * num_cleaners
            total_cost += cost

        # Round to 2 decimal places for currency
        return total_cost.quantize(Decimal("0.01"))

    def get(self, request, pk):
        """Display the cleaner assignment and payment form."""
        booking = get_object_or_404(Booking, pk=pk)

        booking_start = datetime.combine(booking.start_date, booking.start_time)
        booking_end = datetime.combine(booking.end_date, booking.end_time)

        overlapping_cleaners = BookingCleaner.objects.filter(
            booking__start_date__lte=booking.end_date,
            booking__end_date__gte=booking.start_date,
        ).filter(
            Q(booking__start_time__lt=booking.end_time) &
            Q(booking__end_time__gt=booking.start_time)
        ).exclude(booking=booking).values_list("cleaner_id", flat=True)

        assigned_cleaners = list(booking.booking_cleaners.values_list("cleaner_id", flat=True))

        available_cleaners = Cleaner.objects.filter(
            Q(is_available=True) | Q(id__in=assigned_cleaners)
        ).exclude(id__in=overlapping_cleaners)

        payment = Payment.objects.filter(booking=booking).first()
        total_required_cleaners = booking.total_required_cleaners()

        # 💰 Calculate auto total price
        estimated_amount = self.calculate_booking_cost(booking)

        context = {
            "booking": booking,
            "cleaners": available_cleaners,
            "assigned_cleaners": assigned_cleaners,
            "payment": payment,
            "total_required_cleaners": total_required_cleaners,
            "estimated_amount": estimated_amount,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk):
        """Handle cleaner assignment and payment processing."""
        booking = get_object_or_404(Booking, pk=pk)

        try:
            # --- Cleaners Selection ---
            cleaners_raw = request.POST.get("cleaners", "")
            cleaner_ids = [cid for cid in cleaners_raw.split(",") if cid.strip()]

            required_cleaners = booking.total_required_cleaners()
            if len(cleaner_ids) != required_cleaners:
                messages.error(
                    request,
                    f"❌ You must assign exactly {required_cleaners} cleaners (selected {len(cleaner_ids)}).",
                )
                return redirect("booking:assign", pk=pk)

            # --- Payment Details ---
            payment_method = request.POST.get("payment_method")
            amount = float(request.POST.get("amount", 0) or 0)
            discount = float(request.POST.get("discount", 0) or 0)
            net_amount = float(request.POST.get("net_amount", amount - discount))

            if not payment_method:
                messages.error(request, "⚠️ Please select a payment method.")
                return redirect("booking:assign", pk=pk)

            # --- Assign Cleaners ---
            BookingCleaner.objects.filter(booking=booking).delete()
            BookingCleaner.objects.bulk_create([
                BookingCleaner(booking=booking, cleaner_id=cid) for cid in cleaner_ids
            ])

            # --- Create or Update Payment ---
            Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    "payment_method": payment_method,
                    "amount": amount,
                    "discount": discount,
                    "net_amount": net_amount,
                },
            )

            messages.success(
                request,
                f"✅ {required_cleaners} cleaners assigned successfully. "
                f"Payment of {net_amount:.2f} AED recorded!"
            )
            return redirect("booking:list")

        except Exception as e:
            messages.error(request, f"⚠️ Error processing request: {str(e)}")
            return redirect("booking:assign", pk=pk)

        

class BookingCalendarView(LoginRequiredMixin, TemplateView):
    """Render the Booking Calendar page with FullCalendar.js"""
    template_name = "booking/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Bookings Calendar"
        return context


class BookingCalendarDataView(LoginRequiredMixin, View):
    """Provide booking data as JSON for FullCalendar or React Big Calendar"""

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.all()

        events = []
        for booking in bookings:
            # Format start & end datetime properly for FullCalendar
            start_datetime = timezone.make_naive(
                timezone.localtime(booking.start_datetime)
            ).isoformat()
            end_datetime = timezone.make_naive(
                timezone.localtime(booking.end_datetime)
            ).isoformat()

            events.append({
                "id": booking.id,
                "title": f"{booking.customer.full_name} - {booking.region}",
                "start": start_datetime,
                "end": end_datetime,
                "backgroundColor": "#007bff" if booking.status == "confirmed" else "#ffc107",
                "borderColor": "#007bff",
                "extendedProps": {
                    "email": booking.customer.email,
                    "address": booking.customer.address,
                    "status": booking.status,
                    "cleaners": getattr(booking, "number_of_cleaners", 0),
                },
            })

        return JsonResponse(events, safe=False)