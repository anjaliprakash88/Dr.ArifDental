from django.contrib import admin
from .models import Patient, PatientBooking

admin.site.register(Patient)
admin.site.register(PatientBooking)

