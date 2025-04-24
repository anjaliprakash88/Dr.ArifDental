from rest_framework import serializers
from SUPER_ADMIN.models import Receptionist, User,PharmaceuticalMedicine,MedicineBill, BillItem
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Patient, Enquiry, PatientBooking
from DOCTOR.models import MedicinePrescription, TreatmentBill,DentalExamination



# -------------------PATIENT REGISTRATION SERIALIZER--------------------------------
class PatientSerializer(serializers.ModelSerializer):
    branch_code = serializers.ReadOnlyField(source='branch.branch_code')  # To show branch_code in response
    patient_name = serializers.SerializerMethodField()  # Custom field to combine patient details
    last_visit = serializers.SerializerMethodField()
    todays_appointment = serializers.SerializerMethodField()
    appointment_status = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
             'patient_name', 'patient_code','full_name','age','gender','phone','email','address', 'last_visit','todays_appointment',
            'branch', 'branch_code', 'occupation', 'medical_notes', 'created_at', 'is_active','appointment_status'
        ]
        extra_kwargs = {'patient_code': {'read_only': True}}

    def get_patient_name(self, obj):
        return f"{obj.full_name} - [{obj.patient_code}]"
    
    def get_last_visit(self, obj):
        last_appointment = PatientBooking.objects.filter(patient=obj, status='completed').order_by('-appointment_date').first()
        return last_appointment.appointment_date.strftime('%d %b %Y') if last_appointment else None

    # def get_todays_appointment(self, obj):
    #     today = timezone.now().date()
    #     # Get any appointment for today, regardless of status
    #     appointment = PatientBooking.objects.filter(
    #         patient=obj, 
    #         appointment_date=today,
    #         is_disabled=False  # Only active appointments
    #     ).order_by('-created_at').first()
    #     return appointment.appointment_time.strftime('%I:%M %p') if appointment else None
    
    def get_todays_appointment(self, obj):
        today = timezone.now().date()

        # Fetch the latest non-disabled appointment for today
        appointment = PatientBooking.objects.filter(
            patient=obj,
            appointment_date=today,
            is_disabled=False
        ).order_by('-created_at').first()

        if appointment:
            return appointment.appointment_time.strftime('%I:%M %p')
        
        # No appointment or all are disabled
        return None
    
    def get_appointment_status(self, obj):
        today = timezone.now().date()
        appointment = PatientBooking.objects.filter(patient=obj, appointment_date=today).order_by('-created_at').first()
        if appointment:
            return appointment.status
        return None
    
class CheckedInPatientSerializer(serializers.ModelSerializer):
    patient_code = serializers.ReadOnlyField(source='patient.patient_code')
    full_name = serializers.ReadOnlyField(source='patient.full_name')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')
    
    class Meta:
        model = PatientBooking
        fields = [
            'patient_code', 'full_name', 'appointment_time', 
            'doctor_name', 'checkin_time', 'status'
        ]
        
class MedicalHistorySerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientBooking
        fields = ['id', 'appointment_date', 'doctor', 'doctor_name','reason', 'patient_name', 'status']

    def get_patient_name(self, obj):
        return f"{obj.patient.full_name} - [{obj.patient.patient_code}]"
    
    def get_doctor_name(self, obj):
        return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}" if obj.doctor else None

    
#-----------------------------------RECEPTION LOGIN SERIALIZER--------------------------------------
class ReceptionLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # Check if user exists
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username does not exist."})

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({"password": "Incorrect password."})

        # Check if user is a receptionist
        if not hasattr(user, 'is_reception') or not user.is_reception:
            raise serializers.ValidationError({"authorization": "You are not authorized as a receptionist."})

        return {'user': user}

#---------------ReceptionUpdateSerializer---------------
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ReceptionUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()

    class Meta:
        model = Receptionist
        fields = ['id', 'user', 'phone_number', 'address', 'experience_years', 'qualification']

#---------------ReceptionEditSerializer---------------
class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ReceptionEditSerializer(serializers.ModelSerializer):
    user = UserEditSerializer(required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Receptionist
        fields = ['id', 'user', 'phone_number', 'address', 'experience_years', 'qualification', 'profile_image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        # ✅ Update User model (excluding 'username')
        if user_data:
            user_instance = instance.user
            user_data.pop('username', None)
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        # ✅ Update remaining fields in Receptionist model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



#-----------------------------------Reception Change Password SERIALIZER--------------------------------------
class ChangeReceptionPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match"})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data["new_password"])  # Hashes password automatically
        user.save()
        return user
#-----------------------------------ENQUIRY SERIALIZER--------------------------------------
class EnquirySerializer(serializers.ModelSerializer):
    handled_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Enquiry
        fields = '__all__'
        extra_kwargs = {'handled_by': {'read_only': True}}

    def get_handled_by_name(self, obj):
        return obj.handled_by.username if obj.handled_by else "Not Assigned"
    
#-----------------------------------ENQUIRY SERIALIZER--------------------------------------    
class PatientBookingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.username', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = PatientBooking
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name', 'branch', 'branch_name',
            'appointment_date', 'appointment_time', 'status', 'created_at', 'gender', 'age','reason'
        ]

    def get_patient_name(self, obj):
        return f" {obj.patient.patient_code} - {obj.patient.full_name}"

    def get_doctor_name(self, obj):
        return obj.doctor.user.username if obj.doctor else None

    def get_gender(self, obj):
        return obj.patient.gender

    def get_age(self, obj):
        return obj.patient.age
    
class HospitalInfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.EmailField()

class PharmaceuticalMedicineSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = PharmaceuticalMedicine
        fields = [
            'id', 'medicine_name', 'medicine_type', 'supplier', 'category',
            'batch_number', 'quantity_in_stock', 'reorder_level', 'unit_price',
            'expiry_date', 'storage_instructions', 'is_active', 'branch',
            'created_at', 'updated_at', 'is_expired', 'is_low_stock', 'branch_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_expired', 'is_low_stock', 'branch_name']

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None


#BILL GENERATION

class PharmaceuticalMedicineSerializerBill(serializers.ModelSerializer):
    class Meta:
        model = PharmaceuticalMedicine
        fields = ['id', 'medicine_name', 'medicine_type', 'batch_number', 'unit_price']

class BillItemSerializer(serializers.ModelSerializer):
    medicine_detail = PharmaceuticalMedicineSerializer(source='medicine', read_only=True)
    
    class Meta:
        model = BillItem
        fields = ['id', 'medicine', 'medicine_detail', 'quantity', 'unit_price', 'get_item_total']
        read_only_fields = ['get_item_total']

class BillItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['medicine', 'quantity']
    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        # Use the current price of the medicine when creating the bill item
        return BillItem.objects.create(
            bill=validated_data['bill'],
            medicine=medicine,
            quantity=validated_data['quantity'],
            unit_price=medicine.unit_price or 0.00  # Default to 0 if no price is set
        )

class MedicineBillSerializer(serializers.ModelSerializer):
    bill_items = BillItemSerializer(source='billitem_set', many=True, read_only=True)
    total_amount = serializers.DecimalField(
        source='get_total_amount', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = MedicineBill
        fields = [
            'id', 'bill_number', 'patient', 'patient_name', 'patient_contact', 
            'doctor_name', 'bill_date', 'discount', 'tax', 'payment_method', 
            'payment_status', 'notes', 'bill_items', 'total_amount', 'is_active'
        ]
        read_only_fields = ['bill_number', 'created_by', 'bill_date']

class MedicineBillCreateSerializer(serializers.ModelSerializer):
    bill_items = BillItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = MedicineBill
        fields = [
            'patient', 'patient_name', 'patient_contact', 'doctor_name',
            'discount', 'tax', 'payment_method', 'payment_status', 'notes',
            'bill_items'
        ]
    
    def create(self, validated_data):
        bill_items_data = validated_data.pop('bill_items')
        
        # Generate a unique bill number
        import uuid
        bill_number = f"BILL-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the bill
        bill = MedicineBill.objects.create(
            bill_number=bill_number,
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create bill items
        for item_data in bill_items_data:
            BillItem.objects.create(
                bill=bill,
                medicine=item_data['medicine'],
                quantity=item_data['quantity'],
                unit_price=item_data['medicine'].unit_price or 0.00
            )
            
            # Update inventory quantity
            medicine = item_data['medicine']
            medicine.quantity_in_stock = max(0, medicine.quantity_in_stock - item_data['quantity'])
            medicine.save()
        
        return bill
    
#MedicinePrecription serializer    
class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    medicine = PharmaceuticalMedicineSerializerBill(read_only=True)
    
    class Meta:
        model = MedicinePrescription
        fields = ['id', 'medicine', 'dosage_days', 'medicine_times', 'meal_times', 'created_at']

class PatientBookingSerializerBill(serializers.ModelSerializer):
    prescriptions = MedicinePrescriptionSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientBooking
        fields = ['id', 'patient_name', 'doctor_name', 'appointment_date', 
                 'appointment_time', 'status', 'prescriptions']
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    
    def get_doctor_name(self, obj):
        return str(obj.doctor)
        

#SERIALIZERS--FOR--PATIENT--BILL--GENERATION

class PatientSerializerPatientBill(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'phone']

class PatientBookingSerializerPatientBill(serializers.ModelSerializer):
    patient = PatientSerializerPatientBill(read_only=True)
    
    class Meta:
        model = PatientBooking
        fields = ['id', 'patient', 'appointment_date', 'appointment_time']

class DentalExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalExamination
        fields = ['id', 'selected_teeth', 'treatments']

class TreatmentBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentBill
        fields = ['id', 'booking', 'total_amount', 'paid_amount', 'balance_amount', 'created_at']

class DentalExaminationSerializerForBilling(serializers.ModelSerializer):
    class Meta:
        model = DentalExamination
        fields = ['treatment_plan']

class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.medicine_name', read_only=True)
    booking_date = serializers.DateField(source='booking.appointment_date', read_only=True)
    doctor_name = serializers.SerializerMethodField()  # Use SerializerMethodField to customize

    class Meta:
        model = MedicinePrescription
        fields = ['id', 'medicine_name', 'dosage_days', 'medicine_times', 'meal_times', 'created_at', 'booking_date', 'doctor_name']

    def get_doctor_name(self, obj):
        # Assuming the doctor is linked via the booking and is a User instance
        doctor = obj.booking.doctor
        if doctor:
            return f"{doctor.user.first_name} {doctor.user.last_name}".strip()
        return "N/A"

class TreatmentBillDetailSerializer(serializers.ModelSerializer):
    booking = PatientBookingSerializerPatientBill(read_only=True)
    balance_amount = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    treatment_plan = DentalExaminationSerializerForBilling(source='dental_examination', read_only=True)  # Include treatment_plan

    
    class Meta:
        model = TreatmentBill
        fields = ['id', 'booking', 'total_amount', 'paid_amount', 'balance_amount', 'created_at','payment_status','payment_method','treatment_plan']
    

