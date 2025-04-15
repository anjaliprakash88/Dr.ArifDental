from django.db import models
from SUPER_ADMIN.models import Doctor, Branch, User




#---------------Patient Registration Form---------------
class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male',),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    address = models.TextField(null=True)
    occupation = models.CharField(max_length=50, blank=True)
    patient_code = models.CharField(max_length=20, unique=True, blank=True)  # Will be auto-generated
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    medical_notes = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.patient_code:  # Generate only if patient_code is empty
            last_patient = Patient.objects.filter(branch=self.branch).order_by('-id').first()
            if last_patient:
                last_number = int(last_patient.patient_code[len(self.branch.branch_code):])  # Extract numeric part
                new_number = last_number + 1
            else:
                new_number = 1  # First patient in this branch

            self.patient_code = f"{self.branch.branch_code}{new_number}"  # Format as KZ0001, KZ0002, etc.{new_number:04d}

        super().save(*args, **kwargs)  # Call original save method

    def __str__(self):
        return f"{self.full_name} ({self.patient_code})"

#---------------Patient Booking Form---------------
class PatientBooking(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bookings')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending')
    ], default='pending')
    checkin_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=50, blank=True)
    cancellation_notes = models.TextField(blank=True)
    is_disabled = models.BooleanField(default=False) # New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.patient.full_name} with {self.doctor} on {self.appointment_date} at {self.appointment_time}"

class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]
    
    patient_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    enquiry_type = models.CharField(max_length=255)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)  # New field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    comments = models.TextField(null=True, blank=True)  # New field
    contacted_by = models.CharField(max_length=255, null=True, blank=True)  # New optional field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.OneToOneField(PatientBooking, on_delete=models.SET_NULL, null=True, blank=True)  # Link to PatientBooking

    def __str__(self):
        return f"{self.patient_name} - {self.status}"
