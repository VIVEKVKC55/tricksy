# tricksy/constants.py
# Define all possible permissions here

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

PERMISSIONS = {
    "manage_subadmins": "Manage Sub-admins",
    "manage_services": "Manage Services",
    "view_services": "View Services",
    "view_bookings": "View Bookings",
    "manage_bookings": "View/Add/Edit Bookings",
    "assign_cleaners": "Assign Cleaners",
    "view_cleaners": "View Cleaners",
    "manage_cleaners": "Manage Cleaners",
    "manage_payments": "View/Add Payments",
    "view_customers": "View Customer & Booking Details",
    "manage_customers": "Manage Customers",
    "dashboard_access": "Dashboard Access",
}