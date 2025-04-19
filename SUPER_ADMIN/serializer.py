import random
import string
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    SuperAdmin, User,
    Supplier, Doctor, 
    Branch, Pharmacy,
    Receptionist,Hospital_Inventory,
    TaxRate, HospitalInfo,LabOrder

)


# ----------------------------- USER SERIALIZER ----------------------------- #
""" ONLY FOR SUPER-ADMIN """
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

# ----------------------------- USER SERIALIZER ----------------------------- #

class UserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}
    
# --------------------------- SUPER ADMIN SERIALIZER ------------------------- #
class SuperAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = SuperAdmin
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email',
            'phone_number', 'address', 'designation', 'profile_image'
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')

        # Create User with superadmin flag
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_superadmin=True
        )
        user.set_password(password)
        user.save()

        # Create SuperAdmin linked to user
        superadmin = SuperAdmin.objects.create(user=user, **validated_data)
        return superadmin


# ---------------------------- SUPER ADMIN LOGIN ----------------------------- #
class SuperAdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_superadmin:
            raise serializers.ValidationError("You are not authorized as a superadmin")
        return {'user': user}
    
class ChangeSuperadminPasswordSerializer(serializers.Serializer):
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

#----------------------Reception--------------------------------#
class ReceptionCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer2()
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)
    branch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Receptionist
        fields = ['id', 'experience_years', 'qualification', 'phone_number', 'address', 'user', 'branch','branch_name']

    def get_branch_name(self,obj):
        return obj.branch.name if obj.branch else None
    
    def create(self, validated_data):
        user_data = validated_data.pop('user', None)

        password = user_data.pop('password', None)
        if not password:
            password=self._generate_random_password()

        username=user_data.get('username', None)
        if not username:
            username = f"{user_data['first_name'].lower()}_{user_data['last_name'].lower()}"

        user_instance = get_user_model()(**user_data)
        user_instance.username = username
        user_instance.set_password(password)
        user_instance.is_reception=True
        user_instance.save()

        reception_instance = Receptionist.objects.create(
            user = user_instance,
            **validated_data
        )
        self.send_reception_id_email(user_instance.email, user_instance.username, password)
        return  reception_instance


    def send_reception_id_email(self, email, username, password):
        subject ="Your Receptionist Account Details"
        message = f"Dear Receptionist,\n\n Your account has been created. Here the login details \n\n Username: {username}\nPassword:{password} \n\n Thank You !"
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(subject, message, from_email, [email])

    def _generate_random_password(self):
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return password
    
# ---------------------------- SUPPLIER SERIALIZER --------------------------- #
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

# ----------------------------- BRANCH SERIALIZER ---------------------------- #
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


# ----------------------------- PHARMACY SERIALIZER -------------------------- #
class PharmacyCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer2()
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Pharmacy
        fields = ['id', 'experience_years', 'qualification', 'phone_number', 'address', 'user', 'branch','branch_name']
    
    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None
    
    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        password = user_data.pop('password', None)
        if not password:
            password = self._generate_random_password()

        username = user_data.get('username', None)
        if not username:
            username = f"{user_data['first_name'].lower()}_{user_data['last_name'].lower()}"

        user_instance = get_user_model()(**user_data)
        user_instance.username = username
        user_instance.set_password(password)
        user_instance.is_pharmacy = True
        user_instance.save()

        pharmacy_instance = Pharmacy.objects.create(user=user_instance, **validated_data)
        self.send_pharmacy_id_email(user_instance.email, user_instance.username, password)

        return pharmacy_instance

    def send_pharmacy_id_email(self, email, username, password):
        subject = "Your Pharmacy Account Details"
        message = f"Dear Pharmacist,\n\nYour account has been created. Here are your login details:\n\nUsername: {username}\nPassword: {password}\n\nThank you!"
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(subject, message, from_email, [email])

    def _generate_random_password(self):
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return password

#----------------------Doctor Serializer--------------------------------

class DoctorCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=True)
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'experience_years', 'specialization', 'qualification',
            'phone_number', 'address', 'branch', 'branch_name', 'profile_image',
            'first_name', 'last_name', 'email'
        ]

    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None

    def create(self, validated_data):
        # Extract user-related fields
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')

        password = self._generate_random_password()
        username = f"{first_name.lower()}_{last_name.lower()}"

        user_instance = get_user_model()(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_doctor=True
        )
        user_instance.set_password(password)
        user_instance.save()

        profile_image = validated_data.pop('profile_image', None)

        doctor_instance = Doctor.objects.create(
            user=user_instance,
            profile_image=profile_image,
            **validated_data
        )

        self.send_reception_id_email(email, username, password)
        return doctor_instance

    def send_reception_id_email(self, email, username, password):
        subject = "Doctor Account Details"
        message = (
            f"Dear Doctor,\n\n"
            f"Your account has been created. Here are the login details:\n\n"
            f"Username: {username}\nPassword: {password}\n\n"
            f"Thank you!"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [email])

    def _generate_random_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


    
#---------------------------
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class SuperAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ['phone_number', 'address', 'designation']

#----------------------Hospital Inventory Serializer--------------------------------
class HospitalInventorySerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=True)
    class Meta:
        model = Hospital_Inventory
        fields = '__all__'

class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'

class HospitalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalInfo
        fields = '__all__'

# Serializer for User model
class UserViewProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Serializer for SuperAdmin model
class SuperadminViewProfileSerializer(serializers.ModelSerializer):
    user = UserViewProfileSerializer()
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = SuperAdmin
        fields = ['user', 'phone_number', 'address', 'designation', 'profile_image']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        user = instance.user

        if user_data:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class LabOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LabOrder
        fields = ('id', 'patient', 'patient_name', 'lab_name', 'item_description', 'amount', 
                  'ordered_date', 'expected_delivery_date', 'actual_delivery_date', 
                  'status', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_patient_name(self, obj):
        """Returns the patient's full name"""
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}"
        return "Unknown Patient"