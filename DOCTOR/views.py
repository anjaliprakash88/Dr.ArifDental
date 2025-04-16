from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect
from django.urls import reverse
from .serializer import (DoctorLoginSerializer,
                         DentalExaminationSerializer,
                         DoctorViewProfileSerializer,
                         MedicineSerializer,
                         PrescriptionSerializer, 
                         TreatmentBillSerializer,
                         LastAppointmentPreviewSerializer,
                         ChangeDoctorPasswordSerializer,
                         DoctorPatientSerializer,
                         RecentTreatmentSerializer,
                         DentitionSerializer,
                         TodayPreviewSerializer,
                         DentitionTreatmentSerializer,
                         DiagnosisSerializer,
                         InvestigationSerializer)
from RECEPTION.serializer import PatientBookingSerializer
from SUPER_ADMIN.models import Doctor, PharmaceuticalMedicine
from RECEPTION.models import PatientBooking, Patient
from .models import (DentalExamination,
                     Investigation,
                     Dentition,
                     TreatmentBill,
                     DentitionTreatment,
                     MedicinePrescription,
                     Diagnosis)
from django.shortcuts import get_object_or_404,render
from django.utils.timezone import localdate
from rest_framework.permissions import IsAuthenticated
import json
from datetime import date
from decimal import Decimal, InvalidOperation


class DeleteInvestigationView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def post(self, request, id, format=None):
        investigation = get_object_or_404(Investigation, id=id)
        serializer = InvestigationSerializer(investigation)
        investigation.delete()
        return Response(
            {
                "message": "Investigation image deleted successfully.",
                "deleted_image": serializer.data
            },
            status=status.HTTP_200_OK
        )

# -------------LAST APPOINTMENT PREVIEW------------
class LastAppointmentPreview(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'doctor/last_appointment_preview.html'

    def get(self, request, booking_id, format=None):
        last_booking = get_object_or_404(PatientBooking, id=booking_id)
        patient = last_booking.patient

        current_booking = PatientBooking.objects.filter(
            patient=patient,
            appointment_date__gte=date.today()
        ).order_by('appointment_date').first()

        if not current_booking:
            return render(request, self.template_name, {
                "data": {},
                "message": "No current appointment found."
            })

        serializer = LastAppointmentPreviewSerializer(last_booking)
        serialized_data = serializer.data

        # Get all notes from the serialized data
        all_notes = []
        if serialized_data.get('dentition') and serialized_data['dentition'].get('all_notes'):
            all_notes = serialized_data['dentition']['all_notes']

        dentitions = Dentition.objects.filter(booking=last_booking)
        past_dentitions = Dentition.objects.filter(booking__patient=patient).order_by('booking__appointment_date')

        # Build note map
        from collections import defaultdict
        tooth_notes_map = defaultdict(list)
        for d in past_dentitions:
            for tooth_id in d.selected_teeth:  # Loop through each selected tooth
                if d.note and d.note.strip().lower() != "healthy":
                    note_str = f"{d.booking.appointment_date}: {d.treatment} - {d.note}"
                    tooth_notes_map[tooth_id].append(note_str)

        # Append history and all_notes for each tooth
        # Safely handle possible missing 'dentition' key
        dentition_serialized = serialized_data.get('dentition') or {}
        all_notes = dentition_serialized.get('all_notes', [])
        tooth_history = dentition_serialized.get('tooth_history', {})

        dentition_data = []

        for tooth_id, treatments in tooth_history.items():
            for treatment_entry in treatments:
                dentition_data.append({
                    "tooth_id": tooth_id,
                    "treatment": treatment_entry['treatment'],
                    "color_code": treatment_entry['color_code'],
                    "note": treatment_entry['note'],
                    "date": treatment_entry['date'],
                    "all_notes": tooth_notes_map[tooth_id]
                })

        dentition_data_json = json.dumps(dentition_data)

        prescriptions = MedicinePrescription.objects.filter(booking=last_booking)

        prescription_data = [
            {
                "medicine": {
                    "id": p.medicine.id,
                    "name": p.medicine.medicine_name
                },
                "medicine_name": p.medicine.medicine_name,
                "dosage_days": p.dosage_days,
                "medicine_times": p.medicine_times,
                "meal_times": p.meal_times,
            }
            for p in prescriptions
        ]

        prescription_data_json = json.dumps(prescription_data)

        treatments = DentitionTreatment.objects.all()

        if format == 'json' or request.headers.get('Accept') == 'application/json':
            return Response(serializer.data)

        return render(request, self.template_name, {
            "data": serializer.data,
            "booking_id": current_booking.id,
            "last_booking_id": last_booking.id,
            "patient_name": patient.full_name,
            "appointment_date": last_booking.appointment_date,
            "appointment_time": last_booking.appointment_time,
            "patient_email": patient.email,
            "patient_age": patient.age,
            "dentition_data_json": dentition_data_json,
            "treatments": DentitionTreatmentSerializer(treatments, many=True).data,
            "prescription_data_json": prescription_data_json,
            "tooth_history_json": json.dumps(tooth_history),
        })

# -------------TODAY PREVIEW------------
class TodayPreview(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "doctor/today_preview.html"

    def get(self, request, booking_id, format=None):
        booking = get_object_or_404(PatientBooking, id=booking_id)
        patient = booking.patient
        serializer = TodayPreviewSerializer(booking)

        # 🔽 Add this: Query your dentition data
        dentitions = Dentition.objects.filter(booking_id=booking.id)
        dentition_data = []

        for d in dentitions:
            for tooth_id in d.selected_teeth:
                dentition_data.append({
                    "tooth_id": tooth_id,
                    "treatment": d.treatment.name if d.treatment else "Healthy",
                    "color_code": d.treatment.color_code if d.treatment else "#229954",  # default green
                    "note": d.note or "",
                })

        dentition_data_json = json.dumps(dentition_data)
        treatments = DentitionTreatment.objects.all()

        prescriptions = MedicinePrescription.objects.filter(booking_id=booking.id)
        prescription_data = []

        for p in prescriptions:
            prescription_data.append({
                "medicine": {
                    "id": p.medicine.id,
                    "name": p.medicine.medicine_name
                },
                "medicine_name": p.medicine.medicine_name,
                "dosage_days": p.dosage_days,
                "medicine_times": p.medicine_times,
                "meal_times": p.meal_times,
            })

        prescription_data_json = json.dumps(prescription_data)

        if format == 'json' or request.headers.get('Accept') == 'application/json':
            return Response(serializer.data, status=status.HTTP_200_OK)

        return render(request, self.template_name, {
            "data": serializer.data,
            "booking": booking,
            "patient_name": patient.full_name,
            "appointment_date": booking.appointment_date,
            "appointment_time": booking.appointment_time,
            "patient_email": patient.email,
            "patient_age": patient.age,
            "dentition_data_json": dentition_data_json,
            "treatments": DentitionTreatmentSerializer(treatments, many=True).data,
            "prescription_data_json": prescription_data_json
        })

# ---------------DENTAL EXAMINATION--------------
class DentalExaminationCheckup(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "doctor/checkup_page.html"

    def get(self, request, booking_id, format=None):
        doctor = request.user.doctor
        booking = get_object_or_404(PatientBooking, id=booking_id)
        patient = booking.patient
        age = patient.age
        examination, created = DentalExamination.objects.get_or_create(patient=patient, booking=booking)
        examination_serializer = DentalExaminationSerializer(examination)
        patient_name = patient.full_name

        previous_booking = (
            PatientBooking.objects
            .filter(patient=patient, appointment_date__lt=booking.appointment_date)
            .order_by('-appointment_date', '-id')
            .first()
        )

        dentition = Dentition.objects.filter(patient=patient, booking=booking).first()
        if dentition:
            dentition_serializer = DentitionSerializer(dentition)
        else:
            dentition_serializer = None
        treatments = DentitionTreatment.objects.all()

        treatment_bill, created = TreatmentBill.objects.get_or_create(
            booking=booking,
            dental_examination=examination,
            defaults={'patient': patient, 'total_amount': 0.00, 'paid_amount': 0.00}
        )
        treatment_bill_serializer = TreatmentBillSerializer(treatment_bill)

        if format == 'json':
            return Response({
                "dentition": dentition_serializer.data if dentition_serializer else {},
                "previous_booking_id": previous_booking.id if previous_booking else None,
                "examination": examination_serializer.data,
                "treatment_bill": treatment_bill_serializer.data,
                "treatments": DentitionTreatmentSerializer(treatments, many=True).data,
                "age": age
            }, status=status.HTTP_200_OK)

        return render(request, self.template_name, {
            "dentition": dentition_serializer.data if dentition_serializer else {},
            "examination": examination_serializer.data,
            "booking": booking,
            'doctor': doctor,
            "previous_booking_id": previous_booking.id if previous_booking else None,
            "booking_id": booking.id,
            "patient_name": patient_name,
            "treatments": treatments,
            "treatment_bill": treatment_bill_serializer.data,
            "age": age
        })

    def post(self, request, booking_id, format=None):
        booking = get_object_or_404(PatientBooking, id=booking_id)
        patient = booking.patient

        # Fetch or create the examination entry
        examination = DentalExamination.objects.filter(patient=patient, booking=booking).order_by('-created_at').first()
        if not examination:
            examination = DentalExamination.objects.create(patient=patient, booking=booking)

        # Update examination fields
        examination_fields = [
            "chief_complaints", "history_of_present_illness", "medical_history",
            "personal_history", "general_examination", "general_examination_intraoral",
            "local_examination_extraoral", "soft_tissue", "periodontal_status", "treatment_plan"
        ]

        if any(field in request.POST for field in examination_fields):
            examination.chief_complaints = request.data.get("chief_complaints", examination.chief_complaints)
            examination.history_of_present_illness = request.data.get("history_of_present_illness",
                                                                      examination.history_of_present_illness)
            examination.medical_history = request.data.get("medical_history", examination.medical_history)
            examination.personal_history = request.data.get("personal_history", examination.personal_history)
            examination.general_examination = request.data.get("general_examination", examination.general_examination)
            examination.general_examination_intraoral = request.data.get("general_examination_intraoral",
                                                                         examination.general_examination_intraoral)
            examination.local_examination_extraoral = request.data.get("local_examination_extraoral",
                                                                       examination.local_examination_extraoral)
            examination.soft_tissue = request.data.get("soft_tissue", examination.soft_tissue)
            examination.periodontal_status = request.data.get("periodontal_status", examination.periodontal_status)
            examination.treatment_plan = request.data.get("treatment_plan", examination.treatment_plan)
            examination.save()

        # ✅ Handle investigations (files)
        if 'investigation[]' in request.FILES:
            for file in request.FILES.getlist('investigation[]'):
                if not Investigation.objects.filter(dental_examination=examination, image=file.name).exists():
                    Investigation.objects.create(
                        dental_examination=examination,
                        image=file
                    )

        # ✅ FIX: Get dentitions from request data
        dentitions = request.data.get("dentitions", [])  # Ensure it's a list

        created_dentitions = []
        for dentition_data in dentitions:
            selected_teeth = dentition_data.get("selected_teeth")
            treatment_name = dentition_data.get("treatment")

            # Fetch or create the treatment
            treatment, created = DentitionTreatment.objects.get_or_create(
                name=treatment_name,
                defaults={"color_code": request.data.get("color_code", "#000000")}
            )

            # Create Dentition instance
            dentition, created = Dentition.objects.update_or_create(
                patient=patient,
                booking=booking,
                selected_teeth=selected_teeth,
                treatment=treatment,
                note=dentition_data.get("note", "")
            )
            created_dentitions.append(dentition)

        diagnosis_text = request.data.get("diagnosis", "").strip()
        if diagnosis_text:
            diagnosis_obj, created = Diagnosis.objects.update_or_create(
                patient=patient,
                booking=booking,
                defaults={"diagnosis": diagnosis_text}
            )
        else:
            diagnosis_obj = None

        medicines_data = request.data.get('medicines', [])
        created_prescriptions = []
        errors = []

        for med in medicines_data:
            try:
                medicine_id = med.get('medicine')
                medicine = get_object_or_404(PharmaceuticalMedicine, id=medicine_id)

                prescription_data = {
                    'booking': booking.id,  # Pass actual booking instance
                    'medicine': medicine.id,
                    'dosage_days': med.get('dosage_days', 1),
                    'medicine_times': med.get('medicine_times', []),  # Now expects a JSON list
                    'meal_times': med.get('meal_times', [])  # Now expects a JSON list
                }

                serializer = PrescriptionSerializer(data=prescription_data)
                if serializer.is_valid():
                    prescription = serializer.save()
                    created_prescriptions.append(PrescriptionSerializer(prescription).data)
                else:
                    errors.append(serializer.errors)
            except Exception as e:
                errors.append(str(e))

        if errors:
            return Response(
                {"error": "Some medicines could not be saved", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        treatment_bill, created = TreatmentBill.objects.get_or_create(
            booking=booking,
            dental_examination=examination,
            defaults={'patient': patient, 'total_amount': 0.00, 'paid_amount': 0.00, 'balance_amount': 0.00}
        )

        def safe_decimal(value, default=Decimal('0.00')):
            try:
                return Decimal(value)
            except (InvalidOperation, TypeError, ValueError):
                return default

        treatment_bill.total_amount = safe_decimal(request.data.get("total_amount"))
        treatment_bill.paid_amount = safe_decimal(request.data.get("paid_amount"))
        treatment_bill.balance_amount = treatment_bill.total_amount - treatment_bill.paid_amount
        treatment_bill.save()

        booking.status = 'completed'
        booking.save()

        return Response({
            "message": "Checkup details and dentition data saved successfully!",
            "examination": DentalExaminationSerializer(examination).data,
            "diagnosis": DiagnosisSerializer(diagnosis_obj).data if diagnosis_obj else None,
            "treatment_bill": TreatmentBillSerializer(treatment_bill).data,
            "created_prescriptions": created_prescriptions
        }, status=status.HTTP_200_OK)

#------------CHANGE DOCTOR PASSWORD------------
class ChangeDoctorPassword(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'doctor/doctor_dashboard.html'

    def get(self, request):
        serializer = DoctorLoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer =ChangeDoctorPasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------LOGOUT ---------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the token to log the user out
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"}, status=200)

# ---------------DOCTOR PROFILE ---------------
class DoctorProfileView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'doctor/doctor_profile.html'

    def get(self, request):
        try:
            doctor = get_object_or_404(Doctor, user=request.user)
            if request.accepted_renderer.format == 'json':
                doctor_serializer = DoctorViewProfileSerializer(doctor)
                return Response({'doctors': doctor_serializer.data}, status=status.HTTP_200_OK)
            return Response({'doctors': doctor}, template_name=self.template_name)

        except Doctor.DoesNotExist:
            return Response({'message': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        doctor = get_object_or_404(Doctor, user=request.user)
        user_data = {
            "username": request.data.get("username"),
            "first_name": request.data.get("first_name"),
            "last_name": request.data.get("last_name"),
            "email": request.data.get("email"),
        }
        for attr, value in user_data.items():
            if value:
                setattr(doctor.user, attr, value)
            doctor.user.save()

        doctor_data = {
            "phone_number": request.data.get("phone_number"),
            "experience_years": request.data.get("experience_years"),
            "qualification": request.data.get("qualification"),
            "address": request.data.get("address"),
            "specialization": request.data.get("specialization"),
        }

        for attr, value in doctor_data.items():
            if value:
                setattr(doctor, attr, value)

        if "educational_certificate" in request.FILES:
            doctor.educational_certificate = request.FILES["educational_certificate"]
        if "medical_license" in request.FILES:
            doctor.medical_license = request.FILES["medical_license"]
        doctor.save()
        return Response({"message": "Doctor profile updated successfully"}, status=status.HTTP_200_OK)

# ---------------DOCTOR PATIENT LIST---------------
class DoctorPatientListView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'doctor/patient_list.html'

    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # If HTML view requested, render with just patient bookings
        if request.accepted_renderer.format == 'html':
            bookings = PatientBooking.objects.filter(doctor=doctor).select_related('patient').order_by('-appointment_date')
            patient_data = {}

            for booking in bookings:
                if booking.patient.id not in patient_data:
                    patient_data[booking.patient.id] = {
                        "patient": booking.patient,
                        "bookings": [booking]
                    }
                else:
                    patient_data[booking.patient.id]["bookings"].append(booking)

            patients_with_bookings = list(patient_data.values())

            return render(request, self.template_name, {
                "doctor": doctor,
                "patients_with_bookings": patients_with_bookings,
            })

        # Else, return full JSON including recent treatment for each patient
        return Response({
            "doctor": DoctorPatientSerializer(doctor).data
        })


class RecentTreatmentDetailView(APIView):
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        serializer = RecentTreatmentSerializer(patient)
        return Response(serializer.data)
#---------------MEDICINE---------------
class MedicineAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "doctor/checkup_page.html"

    def get(self, request, booking_id, *args, **kwargs):
        medicines = PharmaceuticalMedicine.objects.all()
        doctor = get_object_or_404(Doctor, user=request.user)
        booking = get_object_or_404(PatientBooking, id=booking_id)

        if request.accepted_renderer.format == "html":
            return render(request, self.template_name, {'medicines': medicines, 'booking': booking})

        serializer = MedicineSerializer(medicines, many=True)
        return Response({'medicines': serializer.data})

# ---------------DOCTOR DASHBOARD ---------------
class DoctorDashboard(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'doctor/doctor_dashboard.html'

    def get(self, request, format=None):
        doctor = get_object_or_404(Doctor, user=request.user)

        today_appointment = PatientBooking.objects.filter(
            doctor=doctor,
            appointment_date=localdate(),
            status='upcoming'
        ).select_related('patient')

        serialized_data = PatientBookingSerializer(today_appointment, many=True).data

        if request.accepted_renderer.format == 'html':
            return render(request, self.template_name, {"doctor": doctor, "patient_data": serialized_data})

        return Response({"appointments": serialized_data}, status=status.HTTP_200_OK)

# ---------------DOCTOR LOGIN ---------------
class DoctorLoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'doctor/docter_login.html'

    def get(self, request):
        serializer = DoctorLoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = DoctorLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            Token.objects.get_or_create(user=user)
            return HttpResponseRedirect(reverse('doctor-dashboard'))
        print(serializer.errors)
        return Response({"message": "Invalid credentials", 'serializer': serializer, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

