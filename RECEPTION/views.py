from rest_framework.views import APIView
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.response import Response  
from django.http import JsonResponse  
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status
from SUPER_ADMIN.models import Receptionist, Doctor, Branch,PharmaceuticalMedicine, MedicineBill
from .models import Patient, Enquiry, PatientBooking
from RECEPTION.serializer import (ReceptionLoginSerializer, PatientSerializer,
                                ReceptionEditSerializer, EnquirySerializer,
                                ReceptionUpdateSerializer,ChangeReceptionPasswordSerializer,
                                PatientBookingSerializer,PharmaceuticalMedicineSerializer,
                                MedicineBillSerializer,
                                MedicineBillCreateSerializer,
                                PharmaceuticalMedicineSerializerBill,MedicalHistorySerializer,
                                CheckedInPatientSerializer,TreatmentBillSerializer, TreatmentBillDetailSerializer, MedicinePrescriptionSerializer
                                  )
from django.urls import reverse
from DOCTOR.models import TreatmentBill, PatientBooking, DentalExamination, MedicinePrescription
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status, filters
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import uuid




# ----------------------------Reception Specialization------------------------------
def get_gender(request):
    genders = dict(Patient.GENDER_CHOICES)  
    return JsonResponse(genders) 

def base(request):
    return render(request, 'reception/base.html', {'user': request.user})

#---------------------PATIENT REGISTERATION-------------
class Patient_Signup(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reception/patient_register.html'

    def get(self, request):
        super = Patient.objects.all()
        serializer = PatientSerializer(super, many=True)
        return Response({'serializer': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer, 'message': 'Patient registered successfully!'},
                            status=status.HTTP_201_CREATED)
        return Response({'serializer': serializer, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#---------------------PATIENT MANAGEMENT-------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class PatientManagement(APIView):
    # renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    # template_name = 'reception/manage_patients.html'

    def get(self, request):
        # Order the queryset by patient_code (or another field like id)
        patients = Patient.objects.all().order_by('patient_code')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(patients, request)
        serializer = PatientSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        # Create a new patient from the request data
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new patient to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientDetailView(APIView):
    def get(self, request, patient_code):
        patient = get_object_or_404(Patient, patient_code=patient_code)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, patient_code):
        patient = get_object_or_404(Patient, patient_code=patient_code)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReceptionLoginView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reception/reception_login.html'

    def get(self, request):
        serializer = ReceptionLoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = ReceptionLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)

            if request.accepted_renderer.format == 'html':
                return Response(
                    {"message": "Login successful", "redirect": reverse('reception-dashboard')},
                    status=status.HTTP_200_OK
                )
            else:  # JSON response
                return Response(
                    {"message": "Login successful", "token": token.key},
                    status=status.HTTP_200_OK
                )
        
        # **Explicitly handling the error for HTML requests**
        if request.accepted_renderer.format == 'html':
            return Response(
                {"serializer": serializer, "message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # JSON response for invalid credentials
        return Response(
            {"message": "Invalid credentials", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to log the user out
        try:
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out. Please log in again."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred during logout. Please try again."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

#----------------------------------Reception Dashboard-------------------
class ReceptionDashboardAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get current date for filtering
            today = timezone.now().date()
            this_month_start = today.replace(day=1)
            this_month_end = (this_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Get reception data
            reception = Receptionist.objects.get(user=request.user)
            reception_serializer = ReceptionUpdateSerializer(reception)
            
            # Today's appointments
            today_appointments = PatientBooking.objects.filter(
                appointment_date=today,
                is_disabled=False
            ).order_by('appointment_time')
            
            today_appointments_count = today_appointments.count()
            
            # Process appointments for JSON response
            appointments_data = []
            for appointment in today_appointments[:5]:
                appointments_data.append({
                    'id': appointment.id,
                    'time': appointment.appointment_time.strftime('%H:%M'),
                    'time_formatted': appointment.appointment_time.strftime('%I:%M %p'),
                    'patient_name': f"{appointment.patient.full_name}",
                    'doctor_name': f"Dr. {appointment.doctor.user.last_name}" if appointment.doctor.user else "",
                    'status': appointment.status,
                    'url': f"/reception/bookings/{appointment.id}/"
                })
            
            # New enquiries
            new_enquiries = Enquiry.objects.filter(status='new')
            new_enquiries_count = new_enquiries.count()
            
            # Process recent enquiries for JSON
            enquiries_data = []
            for enquiry in Enquiry.objects.all().order_by('-created_at')[:5]:
                enquiries_data.append({
                    'id': enquiry.id,
                    'patient_name': enquiry.patient_name,
                    'contact_number': enquiry.contact_number,
                    'preferred_date': enquiry.preferred_date.strftime('%b %d') if enquiry.preferred_date else None,
                    'preferred_time': enquiry.preferred_time.strftime('%I:%M %p') if enquiry.preferred_time else None,
                    'status': enquiry.status,
                    'status_display': enquiry.get_status_display()
                })
            
            # Low stock medicines
            low_stock_medicines = PharmaceuticalMedicine.objects.filter(
                Q(quantity_in_stock__lte=F('reorder_level')) & 
                Q(is_active=True)
            )
            low_stock_count = low_stock_medicines.count()
            
            # Process medicines for JSON
            medicines_data = []
            for medicine in low_stock_medicines[:5]:
                medicines_data.append({
                    'id': medicine.id,
                    'name': medicine.medicine_name,
                    'category': medicine.get_category_display(),
                    'stock': medicine.quantity_in_stock,
                    'expiry_date': medicine.expiry_date.strftime('%b %d, %Y') if medicine.expiry_date else None,
                    'is_expired': medicine.is_expired if hasattr(medicine, 'is_expired') else False
                })
            
            # Active patients (patients with appointments this month)
            active_patients_count = Patient.objects.filter(
                bookings__appointment_date__range=[this_month_start, this_month_end],
                bookings__is_disabled=False
            ).distinct().count()
            
            # Doctor availability today
            doctors_availability = []
            all_doctors = Doctor.objects.all()
            
            for doctor in all_doctors:
                # Check if doctor has any appointments today
                has_appointments = PatientBooking.objects.filter(
                    doctor=doctor,
                    appointment_date=today,
                    is_disabled=False
                ).exists()
                
                doctors_availability.append({
                    'id': doctor.id,
                    'first_name': doctor.user.first_name if doctor.user else "",
                    'last_name': doctor.user.last_name if doctor.user else "",
                    'specialization': doctor.specialization,
                    'is_available': has_appointments
                })
            
            # Prepare response data
            response_data = {
                'user': {
                    'full_name': request.user.get_full_name() or request.user.username,
                    'username': request.user.username
                },
                'today_date': timezone.now().strftime('%A, %B %d, %Y'),
                'today_appointments': appointments_data,
                'today_appointments_count': today_appointments_count,
                'new_enquiries_count': new_enquiries_count,
                'recent_enquiries': enquiries_data,
                'low_stock_medicines': medicines_data,
                'low_stock_count': low_stock_count,
                'active_patients_count': active_patients_count,
                'doctors_availability': doctors_availability
            }
            
            return Response(response_data)
            
        except Receptionist.DoesNotExist:
            return Response({'error': 'Receptionist profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------Reception Profile EditView----------
class ReceptionProfileEditView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reception/receptionprofile_edit.html'

    def get(self, request, pk):
        try:
            # reception = Receptionist.objects.get(pk=pk)
            reception = get_object_or_404(Receptionist, user=request.user)
            serializer = ReceptionEditSerializer(reception)
            if request.accepted_renderer.format == 'html':
                # Return actual Receptionist object instead of serialized data
                return Response({'reception_profile': reception})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Receptionist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        try:
            reception = Receptionist.objects.get(pk=pk)
            serializer = ReceptionEditSerializer(reception, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Receptionist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

#---------------Change Reception Password---------------
class ChangeReceptionPassword(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reception/change_reception_password.html'

    def get(self, request):
        serializer = ReceptionLoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = ChangeReceptionPasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#---------------ENQUIRY CRUD OPERATIONS---------------
class EnquiryView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'reception/manage_enquiry.html'

    def get(self, request):
        """Fetch all enquiries"""
        enquiries = Enquiry.objects.all().order_by('-created_at')
        serializer = EnquirySerializer(enquiries, many=True)

        if request.accepted_renderer.format == 'html':
            return Response({'enquiries': serializer.data})  # Pass data inside a dictionary for HTML
        return Response(serializer.data, status=status.HTTP_200_OK)  # JSON response

    def post(self, request):
        """Create a new enquiry and assign the receptionist handling it"""
        try:
            receptionist = Receptionist.objects.get(user=request.user)
        except Receptionist.DoesNotExist:
            return Response({"error": "Receptionist not found"}, status=status.HTTP_403_FORBIDDEN)

        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(handled_by=receptionist.user)  # Assign logged-in receptionist
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EnquiryDetailView(APIView):
    def get(self, request,pk):
        enquiries = get_object_or_404(Enquiry, pk=pk)
        serializer = EnquirySerializer(enquiries)
        return Response(serializer.data, status=status.HTTP_200_OK)  # JSON response
     
    def put(self, request, pk):

        try:
            receptionist = Receptionist.objects.get(user=request.user)
        except Receptionist.DoesNotExist:
            return Response({"error": "Receptionist not found"}, status=status.HTTP_403_FORBIDDEN)
        
        enquiry = get_object_or_404(Enquiry, pk=pk)
        serializer = EnquirySerializer(enquiry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(handled_by=receptionist.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        enquiry = get_object_or_404(Enquiry, pk=pk)
        enquiry.delete()
        return Response({"message": "Enquiry deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
#---------------PATIENT BOOKING OPERATIONS---------------
def get_dropdown_data(request):
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    branches = Branch.objects.filter(is_active=True)

    # Modify patient_options to include contact and email
    patient_options = [
        {
            'id': patient.id,
            'name': f"{patient.full_name} - {patient.patient_code}",
            'contact': patient.phone,  # Add contact field
            'email': patient.email       # Add email field
        }
        for patient in patients
    ]

    doctor_options = [
        {
            'id': doctor.id,
            'name': f"{doctor.user.first_name} {doctor.user.last_name}"
        }
        for doctor in doctors
    ]

    branch_options = [
        {
            'id': branch.id,
            'name': branch.name
        }
        for branch in branches
    ]

    return JsonResponse({
        'patients': patient_options,
        'doctors': doctor_options,
        'branches': branch_options
    })

# def get_all_dropdown_data(request):
#     # Get data for patients, doctors, and branches
#     patient_response = get_patient_options(request)
#     doctor_response = get_doctor_options(request)
#     branch_response = get_branch_options(request)

#     # Combine and return in one response if needed
#     return JsonResponse({
#         'patients': patient_response.json(),
#         'doctors': doctor_response.json(),
#         'branches': branch_response.json()
#     })


def get_patient_options(request):
    patients = Patient.objects.all()
    patient_options = [
        {
            'id': patient.id,
            'name': f"{patient.full_name} - {patient.patient_code}",
            'contact': patient.phone,  # Add contact field
            'email': patient.email       # Add email field
        }
        for patient in patients
    ]
    
    return JsonResponse({'patients': patient_options})

# Function to fetch doctor options and return as JsonResponse
def get_doctor_options(request):
     # Retrieve doctors' first name, last name, and id
    doctors = Doctor.objects.all().values('id', 'user__first_name', 'user__last_name')
    
    # Create a new list with full name instead of first and last name separately
    doctor_data = [
        {
            'id': doctor['id'],
            'full_name': f"{doctor['user__first_name']} {doctor['user__last_name']}"
        }
        for doctor in doctors
    ]
    
    return JsonResponse(doctor_data, safe=False)

# Function to fetch branch options and return as JsonResponse
def get_branch_options(request):
    branches = Branch.objects.filter(is_active=True)
    
    # Initialize an empty dictionary to hold the branch options
    branch_options = {}
    
    for branch in branches:
        branch_options[branch.id] = {
            'id': branch.id,
            'name': branch.name
        }
    
    return JsonResponse({'branches': branch_options})


class PatientBookingView(APIView):
    def get(self, request, patient_code):
        # Retrieve bookings for a specific patient
        bookings = PatientBooking.objects.filter(patient__patient_code=patient_code)
        serializer = PatientBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, patient_code):
        # Create a new booking for a specific patient
        data = request.data.copy()
        # Get the patient object and use its ID in the booking
        data['patient'] = get_object_or_404(Patient, patient_code=patient_code).id
        
        serializer = PatientBookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, patient_code, booking_id):
        appointment = get_object_or_404(PatientBooking, id=booking_id, patient__patient_code=patient_code)
        appointment.status = 'cancelled'
        appointment.is_disabled = True
        appointment.cancellation_reason = request.data.get('cancellation_reason', '')
        appointment.cancellation_notes = request.data.get('cancellation_notes', '')
        appointment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MedicalHistoryView(APIView):
    def get(self, request, patient_code):
        history = PatientBooking.objects.filter(patient__patient_code=patient_code)
        serializer = MedicalHistorySerializer(history, many=True)
        return Response(serializer.data)
    
class BillingView(APIView):
    def get(self, request, patient_code):
        bills = TreatmentBill.objects.filter(patient__patient_code=patient_code)
        serializer = TreatmentBillDetailSerializer(bills, many=True)
        return Response(serializer.data)

    def post(self, request, patient_code):
        data = request.data.copy()
        data['patient'] = get_object_or_404(Patient, patient_code=patient_code).id
        if 'date' not in data:
            data['date'] = timezone.now().date()
        
        serializer = TreatmentBillDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, patient_code, billing_id=None):
        if billing_id:
            bill = get_object_or_404(TreatmentBill, id=billing_id, patient__patient_code=patient_code)
            data = request.data
            paid_amount = Decimal(data.get('paid_amount', 0))

            bill.paid_amount += paid_amount
            if bill.paid_amount >= bill.total_amount:
                bill.payment_status = 'paid'
            elif bill.paid_amount > 0:
                bill.payment_status = 'partial'
            else:
                bill.payment_status = 'pending'
            
            bill.payment_method = data.get('payment_method', bill.payment_method)
            
            serializer = TreatmentBillDetailSerializer(bill, data={'paid_amount': bill.paid_amount, 'payment_status': bill.payment_status, 'payment_method': bill.payment_method}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Billing ID required for update"}, status=status.HTTP_400_BAD_REQUEST)


class PatientBookingDetailView(APIView):
    def get(self, request, patient_code, booking_id):
        # Retrieve an individual booking for a specific patient
        try:
            booking = PatientBooking.objects.get(
                id=booking_id, 
                patient__patient_code=patient_code
            )
        except PatientBooking.DoesNotExist:
            return Response(
                {'detail': 'Booking not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PatientBookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, patient_code, booking_id):
        # Handle updating an individual booking for a specific patient
        try:
            booking = PatientBooking.objects.get(
                id=booking_id, 
                patient__patient_code=patient_code
            )
        except PatientBooking.DoesNotExist:
            return Response(
                {'detail': 'Booking not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PatientBookingSerializer(
            booking, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientPrescriptionAPIView(APIView):
    """
    API view to retrieve all medicine prescriptions for a patient by patient_code.
    """
    def get(self, request, patient_code, format=None):
        try:
            # Fetch bookings for the patient
            bookings = PatientBooking.objects.filter(patient__patient_code=patient_code)
            if not bookings.exists():
                return Response(
                    {"message": "No medicines are prescribed for this patient."},
                    status=status.HTTP_200_OK
                )
            
            # Fetch prescriptions related to those bookings
            prescriptions = MedicinePrescription.objects.filter(booking__in=bookings)
            if not prescriptions.exists():
                return Response(
                    {"message": "No medicines are prescribed for this patient."},
                    status=status.HTTP_200_OK
                )
            
            # Serialize and return prescriptions if they exist
            serializer = MedicinePrescriptionSerializer(prescriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PharmaceuticalMedicineListCreateAPIView(generics.ListCreateAPIView):
    queryset = PharmaceuticalMedicine.objects.all().filter(is_active=True)
    serializer_class = PharmaceuticalMedicineSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['medicine_name', 'batch_number', 'category']
    ordering_fields = ['medicine_name', 'expiry_date', 'quantity_in_stock', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter options
        category = self.request.query_params.get('category', None)
        medicine_type = self.request.query_params.get('medicine_type', None)
        is_active = self.request.query_params.get('is_active', None)
        is_expired = self.request.query_params.get('is_expired', None)
        is_low_stock = self.request.query_params.get('is_low_stock', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if medicine_type:
            queryset = queryset.filter(medicine_type=medicine_type)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        if is_expired is not None:
            from datetime import date
            is_expired_bool = is_expired.lower() == 'true'
            if is_expired_bool:
                queryset = queryset.filter(expiry_date__lt=date.today())
            else:
                queryset = queryset.filter(expiry_date__gte=date.today())
        if is_low_stock is not None:
            is_low_stock_bool = is_low_stock.lower() == 'true'
            if is_low_stock_bool:
                queryset = queryset.filter(quantity_in_stock__lte=models.F('reorder_level'))
            else:
                queryset = queryset.filter(quantity_in_stock__gt=models.F('reorder_level'))
        
        return queryset
    
class PharmaceuticalMedicineRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PharmaceuticalMedicine.objects.all()
    serializer_class = PharmaceuticalMedicineSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Instead of deleting, mark as inactive
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_update(self, serializer):
        serializer.save()
        return Response(serializer.data)
    
#BILL_GENERATION

class MedicineListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        medicines = PharmaceuticalMedicine.objects.filter(is_active=True)
        serializer = PharmaceuticalMedicineSerializerBill(medicines, many=True)
        return Response(serializer.data)

class MedicineBillListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        bills = MedicineBill.objects.filter(is_active=True)
        serializer = MedicineBillSerializer(bills, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MedicineBillCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            bill = serializer.save()
            response_serializer = MedicineBillSerializer(bill)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicineBillDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return MedicineBill.objects.get(pk=pk)
        except MedicineBill.DoesNotExist:
            return None
    
    def get(self, request, pk):
        bill = self.get_object(pk)
        if not bill:
            return Response(
                {"detail": "Bill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MedicineBillSerializer(bill)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        bill = self.get_object(pk)
        if not bill:
            return Response(
                {"detail": "Bill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MedicineBillSerializer(bill, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        bill = self.get_object(pk)
        if not bill:
            return Response(
                {"detail": "Bill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # Soft delete
        bill.is_active = False
        bill.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class PatientPrescriptionAPIView(APIView):
#     permission_classes = [AllowAny]
    
#     def get(self, request, format=None):
#         # Get query parameters for filtering
#         patient_id = request.query_params.get('patient_id')
#         booking_id = request.query_params.get('booking_id')
#         appointment_date = request.query_params.get('appointment_date')
        
#         # Start with all bookings that have prescriptions
#         queryset = PatientBooking.objects.filter(
#             prescriptions__isnull=False,
#             is_disabled=False
#         ).distinct()
        
#         # Apply filters based on parameters
#         if patient_id:
#             queryset = queryset.filter(patient_id=patient_id)
        
#         if booking_id:
#             queryset = queryset.filter(id=booking_id)
            
#         if appointment_date:
#             queryset = queryset.filter(appointment_date=appointment_date)
        
#         # Serialize the data
#         serializer = PatientBookingSerializerBill(queryset, many=True)
#         return Response(serializer.data)
    
#     def post(self, request, format=None):
#         # This would handle searching by other parameters if needed
#         patient_name = request.data.get('patient_name')
#         doctor_name = request.data.get('doctor_name')
#         date_range_start = request.data.get('date_from')
#         date_range_end = request.data.get('date_to')
        
#         queryset = PatientBooking.objects.filter(
#             prescriptions__isnull=False,
#             is_disabled=False
#         ).distinct()
        
#         if patient_name:
#             queryset = queryset.filter(
#                 patient__first_name__icontains=patient_name) | queryset.filter(
#                 patient__last_name__icontains=patient_name
#             )
        
#         if doctor_name:
#             queryset = queryset.filter(doctor__name__icontains=doctor_name)
        
#         if date_range_start and date_range_end:
#             queryset = queryset.filter(
#                 appointment_date__gte=date_range_start,
#                 appointment_date__lte=date_range_end
#             )
        
#         serializer = PatientBookingSerializer(queryset, many=True)
#         return Response(serializer.data)
    
#Patient--BILL-GENERATION
class TreatmentBillListView(APIView):
    """
    API view to list all treatment bills or create a new one
    """
    def get(self, request):
        bills = TreatmentBill.objects.all().order_by('-created_at')
        serializer = TreatmentBillSerializer(bills, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TreatmentBillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TreatmentBillDetailView(APIView):
    """
    API view to retrieve, update or delete a specific treatment bill
    """
    def get_object(self, pk):
        return get_object_or_404(TreatmentBill, pk=pk)
    
    def get(self, request, pk):
        bill = self.get_object(pk)
        serializer = TreatmentBillDetailSerializer(bill)
        return Response(serializer.data)
    
    def put(self, request, pk):
        bill = self.get_object(pk)
        serializer = TreatmentBillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        bill = self.get_object(pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PatientBillsView(APIView):
    """
    API view to get all bills for a specific patient
    """
    def get(self, request, patient_id):
        bills = TreatmentBill.objects.filter(
            booking__patient__id=patient_id
        ).order_by('-created_at')
        serializer = TreatmentBillSerializer(bills, many=True)
        return Response(serializer.data)

class GenerateBillView(APIView):
    """
    API view to generate a new bill for a specific dental examination
    """
    def post(self, request):
        booking_id = request.data.get('booking_id')
        dental_exam_id = request.data.get('dental_examination_id')
        
        if not booking_id or not dental_exam_id:
            return Response(
                {"error": "Booking ID and Dental Examination ID are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            booking = PatientBooking.objects.get(id=booking_id)
            dental_exam = DentalExamination.objects.get(id=dental_exam_id)
            
            # Calculate total amount based on treatments
            treatments = dental_exam.treatments
            total_amount = sum(float(treatment.get('price', 0)) for treatment in treatments)
            
            # Create new bill
            bill = TreatmentBill.objects.create(
                booking=booking,
                dental_examination=dental_exam,
                total_amount=total_amount,
                paid_amount=0,  # Initially zero
                balance_amount=total_amount  # Initially equal to total
            )
            
            serializer = TreatmentBillDetailSerializer(bill)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except (PatientBooking.DoesNotExist, DentalExamination.DoesNotExist) as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdatePaymentView(APIView):
    """
    API view to update payment details for a bill
    """
    def put(self, request, bill_id):
        try:
            bill = TreatmentBill.objects.get(id=bill_id)
            paid_amount = float(request.data.get('paid_amount', 0))
            
            # Update paid amount and recalculate balance
            bill.paid_amount = paid_amount
            bill.balance_amount = float(bill.total_amount) - paid_amount
            bill.save()
            
            serializer = TreatmentBillDetailSerializer(bill)
            return Response(serializer.data)
            
        except TreatmentBill.DoesNotExist:
            return Response(
                {"error": "Bill not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# class AvailableSlotsView(APIView):
#     def get(self, request):
#         # Example logic: fetch available slots per doctor
#         appointments = PatientBooking.objects.filter(appointment_date=timezone.now().date(), status='upcoming')
#         booked_slots = {appt.doctor: appt.time.strftime('%I:%M %p') for appt in appointments}
#         doctors = Doctor.objects.all()
#         slots = {}
#         all_times = ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM", "3:00 PM"]
#         for doctor in doctors:
#             booked = booked_slots.get(doctor.user.username, [])
#             slots[doctor.user.username] = [t for t in all_times if t not in booked]
#         return Response(slots)
    
class TimeSlotListView(APIView):
    def get(self, request):
        # Example static time slots; replace with your logic
        time_slots = [
            "9:00 AM", "10:00 AM", "11:00 AM", 
             "1:00 PM","2:00 PM",
            "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"
        ]
        return Response(time_slots)
    
class PatientCheckInView(APIView):
    def post(self, request, patient_code):
        try:
            # Get the patient
            patient = Patient.objects.get(patient_code=patient_code)
            
            # Find today's pending booking for this patient
            today = timezone.now().date()
            booking = PatientBooking.objects.filter(
                patient=patient,
                appointment_date=today,
                status='pending',
                is_disabled=False
            ).order_by('-created_at').first()
            
            if booking:
                # Update the status to upcoming
                booking.status = 'upcoming'
                booking.checkin_time = timezone.now()
                booking.save()
                
                return Response({
                    'status': 'success',
                    'message': f'Patient {patient.full_name} checked in successfully'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No pending appointment found for today'
                }, status=status.HTTP_404_NOT_FOUND)
        
        except Patient.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Patient not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckedInPatientsView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            print(f"Request received for {request.path} on {today}")
            
            bookings = PatientBooking.objects.filter(
                appointment_date=today,
                status='upcoming',
                is_disabled=False
            ).select_related('patient', 'doctor')
            print(f"Found {bookings.count()} bookings")
            
            serializer = CheckedInPatientSerializer(bookings, many=True)
            print(f"Serialized data: {serializer.data}")
            
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'results': serializer.data
            })
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)