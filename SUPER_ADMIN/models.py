from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

#------------------------USER MODEL-------------------------#
class User(AbstractUser):
    is_superadmin = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_pharmacy = models.BooleanField(default=False)
    is_reception = models.BooleanField(default=False)

    def __str__(self):
        return self.username

#----------------------------BRANCH MODEL-------------------------------#
class Branch(models.Model):
    branch_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

#----------------------------SUPER-ADMIN MODEL-------------------------------#
class SuperAdmin(models.Model):
    user = models.OneToOneField(User, related_name="super_admin", on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=100, default="Clinic Administrator")

    def __str__(self):
        return self.user.username

#-----------------------------DOCTOR MODEL-----------------------------------#
class Doctor(models.Model):
    user = models.OneToOneField(User, related_name="doctor", on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', related_name="doctors", on_delete=models.CASCADE)

    specialization = models.CharField(
        max_length=100,
        choices=[
            ('General Dentist', 'General Dentist'),
            ('Orthodontist', 'Orthodontist'),
            ('Periodontist', 'Periodontist'),
            ('Endodontist', 'Endodontist'),
            ('Prosthodontist', 'Prosthodontist')
        ]
    )
    experience_years = models.PositiveIntegerField()
    qualification = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    # Certificate & License Uploads
    educational_certificate = models.FileField(upload_to='DOCTOR/certificates/', null=True, blank=True)
    medical_license = models.FileField(upload_to='DOCTOR/licenses/', null=True, blank=True)

    def __str__(self):
        return self.user.username


#--------------------------------------PHARMACY MODEL------------------------------------#
class Pharmacy(models.Model):
    user = models.OneToOneField(User, related_name="pharmacy", on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name="pharmacies", on_delete=models.CASCADE)
    experience_years = models.PositiveIntegerField()
    qualification = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

#-----------------------------------RECEPTIONIST MODEL----------------------------------------#
class Receptionist(models.Model):
    user = models.OneToOneField(User, related_name="receptionist", on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name="receptionists", on_delete=models.CASCADE)
    experience_years = models.PositiveIntegerField()
    qualification = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
#----------------------------------SUPPLIER MODEL----------------------------------------#
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField()
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
#-----------------------------------HOSPITAL INVENTORY MODEL----------------------------------------#    
class Hospital_Inventory(models.Model):
    supplier = models.ForeignKey(Supplier, related_name="supplier", on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=100,
        choices=[
            ('equipment', 'Equipment'),
            ('supplies', 'Supplies'),
            ('tools', 'Dental Tools'),
            ('other', 'Other')
        ]
    )
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Minimum stock level before reorder.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_order_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def __str__(self):
        return f"{self.item_name} ({self.category}) from {self.supplier.name}"

#-----------------------------------HOSPITAL SERVICES MODEL----------------------------------------# 

class TaxRate(models.Model):
    cgst = models.DecimalField(max_digits=5, decimal_places=2, help_text="Central GST (%)")
    sgst = models.DecimalField(max_digits=5, decimal_places=2, help_text="State GST (%)")
    effective_date = models.DateField(help_text="Date from which the tax rates are applicable")
    is_active = models.BooleanField(default=True, help_text="Set to False when rates are no longer applicable")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CGST: {self.cgst}%, SGST: {self.sgst}% (Effective from {self.effective_date})"
    
class HospitalInfo(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    established_year = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    
class LabOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey('RECEPTION.Patient', on_delete=models.CASCADE, related_name='lab_orders')
    lab_name = models.CharField(max_length=100)
    item_description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Capitalize lab_name before saving
        self.lab_name = self.lab_name.title()
        super().save(*args, **kwargs)    
        
    def __str__(self):
        return f"Order for {self.patient} - {self.lab_name} ({self.ordered_date})"
    
class PharmaceuticalMedicine(models.Model):
    medicine_name = models.CharField(max_length=255)  # Required
    medicine_type = models.CharField(
        max_length=100,
        choices=[
            ('tablet', 'Tablet'),
            ('capsule', 'Capsule'),
            ('syrup', 'Syrup'),
            ('gel', 'Gel'),
            ('injection', 'Injection'),
            ('other', 'Other')
        ],
        null=True, blank=True
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=50, choices=[
        ('painkiller', 'Painkiller'),
        ('antibiotic', 'Antibiotic'),
        ('anesthetic', 'Anesthetic'),
        ('antiseptic', 'Antiseptic'),
        ('other', 'Other'),
    ], default='other')
    batch_number = models.CharField(max_length=100, unique=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5, help_text="Minimum stock level before reorder.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    storage_instructions = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        from datetime import date
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def __str__(self):
        return f"{self.medicine_name} ({self.batch_number})"
    

class MedicineBill(models.Model):
    bill_number = models.CharField(max_length=100, unique=True)
    patient_name = models.CharField(max_length=255)
    patient_contact = models.CharField(max_length=100, null=True, blank=True)
    doctor_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Optional foreign key if you have a Patient/Doctor model
    patient = models.ForeignKey('RECEPTION.Patient', on_delete=models.SET_NULL, null=True)
    # doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    
    bill_date = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('upi', 'UPI'),
            ('insurance', 'Insurance'),
            ('other', 'Other')
        ],
        default='cash'
    )
    payment_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ],
        default='pending'
    )
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-bill_date']
    
    def get_total_amount(self):
        bill_items = self.billitem_set.all()
        subtotal = sum(item.get_item_total() for item in bill_items)
        discount_amount = (subtotal * self.discount) / 100
        tax_amount = ((subtotal - discount_amount) * self.tax) / 100
        return subtotal - discount_amount + tax_amount
    
    def __str__(self):
        return f"Bill #{self.bill_number} - {self.patient_name}"


class BillItem(models.Model):
    bill = models.ForeignKey(MedicineBill, on_delete=models.CASCADE)
    medicine = models.ForeignKey(PharmaceuticalMedicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # This stores the price at the time of billing, which might differ from current medicine price
    
    def get_item_total(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.medicine.medicine_name} x {self.quantity}"

