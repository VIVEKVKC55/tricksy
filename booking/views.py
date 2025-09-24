from django.shortcuts import render

# Create your views here.

def booking_home(request):
    return render(request, 'booking/booking_home.html')