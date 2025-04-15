from django.db import models
from RECEPTION.models import Patient, PatientBooking
from SUPER_ADMIN.models import PharmaceuticalMedicine
from decimal import Decimal

# ---------------DIAGNOSIS---------------
class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    booking = models.ForeignKey(PatientBooking, on_delete=models.CASCADE, related_name='diagnoses')

    diagnosis = models.TextField(blank=True, null=True, help_text="Enter diagnosis summary")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Diagnosis for {self.patient.full_name} on {self.booking.appointment_date}"

# -----------------DENTAL EXAMINATION--------------
class DentalExamination(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dental_examinations')
    booking = models.ForeignKey(PatientBooking, on_delete=models.CASCADE, related_name='dental_examinations')
    chief_complaints = models.TextField(blank=True, null=True)
    history_of_present_illness = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    personal_history = models.TextField(blank=True, null=True)
    general_examination = models.TextField(blank=True, null=True)
    general_examination_intraoral = models.TextField(blank=True, null=True)
    local_examination_extraoral = models.TextField(blank=True, null=True)
    soft_tissue = models.TextField(blank=True, null=True)
    periodontal_status = models.TextField(blank=True, null=True)
    treatment_plan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dental Examination for {self.patient.full_name}"

class Investigation(models.Model):
    dental_examination = models.ForeignKey(DentalExamination, on_delete=models.CASCADE, related_name='investigations')
    image = models.ImageField(upload_to='investigations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Investigation for {self.dental_examination.patient.full_name}"

# ---------------DENTITION-------------
class DentitionTreatment(models.Model):
    name = models.CharField(max_length=255)
    color_code = models.CharField(max_length=7, help_text="Hex color code for treatment (e.g., #FF0000 for red)")

    def __str__(self):
        return self.name

class Dentition(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dentitions')
    booking = models.ForeignKey(PatientBooking, on_delete=models.CASCADE, related_name='dentitions')
    selected_teeth = models.JSONField()
    treatment = models.ForeignKey(DentitionTreatment, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='dentition_treatments')
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.treatment:
            self.color_code = "#00FF00"
        else:
            self.color_code = self.treatment.color_code

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dentition for {self.patient.full_name} - Booking {self.booking.id}"

# ---------------MEDICINE PRESCRIPTION-------------
class MedicinePrescription(models.Model):
    booking = models.ForeignKey(
        PatientBooking, on_delete=models.CASCADE, related_name="prescriptions"
    )
    medicine = models.ForeignKey(
        PharmaceuticalMedicine, on_delete=models.CASCADE, related_name="prescriptions"
    )
    dosage_days = models.IntegerField(default=1)
    medicine_times = models.JSONField()
    meal_times = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medicine.medicine_name

# ---------------TREATMENT BILL-------------
class TreatmentBill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    booking = models.ForeignKey(PatientBooking, on_delete=models.CASCADE, related_name="treatment_bills")
    dental_examination = models.ForeignKey(DentalExamination, on_delete=models.CASCADE, related_name="treatment_bills")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ✅ Now a database field
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], default='pending')
    payment_method = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        self.balance_amount = (self.total_amount or Decimal(0)) - (self.paid_amount or Decimal(0))  # ✅ Auto-calculate balance
        super().save(*args, **kwargs)

    def _str_(self):
        return f"Bill for {self.booking.patient.full_name} - ${self.total_amount}"

