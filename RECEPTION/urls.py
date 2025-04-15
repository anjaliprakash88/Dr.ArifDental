from django.urls import path
from django.views.generic import TemplateView
from .views import (
                    ReceptionLoginView,
                    # ReceptionDashboard,
                    ReceptionProfileEditView,
                    ChangeReceptionPassword,
                    Patient_Signup,
                    EnquiryView,
                    PatientBookingView,
                    PatientBookingDetailView,
                    EnquiryDetailView,   TreatmentBillListView, 
                    TreatmentBillDetailView, 
                    PatientBillsView,
                    GenerateBillView,
                    UpdatePaymentView,
                    PatientManagement,
                    PatientDetailView,
                    LogoutView,
                    ReceptionDashboardAPI,
                    MedicalHistoryView,
                    BillingView,
                    # AvailableSlotsView,
                    TimeSlotListView,CheckedInPatientsView,
                    
                    #Pharmacy-Imports
                    PharmaceuticalMedicineListCreateAPIView,
                    PharmaceuticalMedicineRetrieveUpdateDestroyAPIView,
                    MedicineListView, MedicineBillListView, MedicineBillDetailView,PatientPrescriptionAPIView,PatientCheckInView
                    )
from .import views

urlpatterns = [
    

    #Patients-Management
    path('patientsignup/', Patient_Signup.as_view(), name='patientsignup'), 
    path('patients/', PatientManagement.as_view(), name='get_all_patients'),
    path('patients/<str:patient_code>/', PatientDetailView.as_view(), name='get_patients'),

    #Enquiry-Management
    path('enquiries/', EnquiryView.as_view(), name='enquiries-list'),
    path('enquiries/<int:pk>/', EnquiryDetailView.as_view(), name='enquiries-detail'),

    #Bookings-Management
    path("get_dropdown_data/", views.get_dropdown_data, name="get_dropdown_data"),
    path('dropdown/patients/', views.get_patient_options, name='get_patient_options'),
    path('dropdown/doctors/', views.get_doctor_options, name='get_doctor_options'),
    path('dropdown/branches/', views.get_branch_options, name='get_branch_options'),

    path('appointments/<str:patient_code>/', PatientBookingView.as_view(), name='patient-booking'),
    path('appointments/<str:patient_code>/<int:booking_id>/', PatientBookingView.as_view(), name='appointment-detail'),
    path('history/<str:patient_code>/', MedicalHistoryView.as_view(), name='history-list'),
    path('billing/<str:patient_code>/', BillingView.as_view(), name='billing'),
    path('billing/<str:patient_code>/<int:billing_id>/', BillingView.as_view(), name='billing-update'),
    path('prescriptions/<str:patient_code>/', PatientPrescriptionAPIView.as_view(), name='patient-prescriptions'),
    # path('bookings/<int:booking_id>/', PatientBookingDetailView.as_view(), name='update-booking'),
    path('appointments/edit/<str:patient_code>/', PatientBookingDetailView.as_view(), name='appointment-list'),
    # path('available-slots/', AvailableSlotsView.as_view(), name='available-slots'),
    path('time-slots/', TimeSlotListView.as_view(), name='time-slot-list'),

    #Reception-Dashboard
    path('genders/', views.get_gender, name='get_gender'),
    # path('dashboard/', ReceptionDashboard.as_view(), name='reception-dashboard'),
    path('api/dashboard/', ReceptionDashboardAPI.as_view(), name='reception_dashboard_api'),
    path('profile/edit/<int:pk>/', ReceptionProfileEditView.as_view(), name='receptionprofile_edit'),
    

    #Reception-Login
    path('login/', ReceptionLoginView.as_view(), name='reception-login'),
    path('change-password/', ChangeReceptionPassword.as_view(), name='change_password-reception'),
    path('logout/', LogoutView.as_view(), name='logout'),

    #MEDICINE-BILLS
    path('pharmaceuticals/', PharmaceuticalMedicineListCreateAPIView.as_view(), name='pharmaceutical-list-create'),
    path('pharmaceuticals/<int:pk>/', PharmaceuticalMedicineRetrieveUpdateDestroyAPIView.as_view(), name='pharmaceutical-detail'),
    path('medicines/', MedicineListView.as_view(), name='medicine-list'),
    path('bills/', MedicineBillListView.as_view(), name='bill-list'),
    path('bills/<int:pk>/', MedicineBillDetailView.as_view(), name='bill-detail'),
    # path('api/patient-prescriptions/', PatientPrescriptionAPIView.as_view(), name='patient_prescriptions'),

    #PATIENT-BILLS
    path('patientbills/', TreatmentBillListView.as_view(), name='patient-bill-list'),
    path('patient-bill/<int:pk>/', TreatmentBillDetailView.as_view(), name='patient-bill-detail'),
    path('patient/<int:patient_id>/bills/', PatientBillsView.as_view(), name='patient-bills'),
    path('generate-patient-bill/', GenerateBillView.as_view(), name='generate-patient-bill'),
    path('update-payment/<int:bill_id>/', UpdatePaymentView.as_view(), name='update-payment'),
    path('patients/<str:patient_code>/checkin/', PatientCheckInView.as_view(), name='patient-checkin'),
    path('checked-in/', CheckedInPatientsView.as_view(), name='checked-in-patients'),
   
    #RenderHTMLPages

    path('medicineslist/', TemplateView.as_view(template_name="reception/manage-medicine.html"), name='medicine-list'),
    path('pharmacybill/', TemplateView.as_view(template_name="reception/phamarcy_bill.html"), name='pharmacy-bill'),
    path('phamarcybilllist/', TemplateView.as_view(template_name="reception/phamarcy_bill-list.html"), name='phamarcy-bill-list'),
    path('patient-prescription/', TemplateView.as_view(template_name="reception/patient_prescriptions.html"), name='patient-prescription'),
    path('patientbilling/', TemplateView.as_view(template_name="reception/patient-billing.html"), name='patient-billing'),
    path('billing-options/', TemplateView.as_view(template_name="reception/billing_options.html"), name='billing-options'),
    path('dashboard/', TemplateView.as_view(template_name="reception/reception_dashboard.html"), name='reception-dashboard'),
    path('singlepage/', TemplateView.as_view(template_name="reception/manage-patient-new.html"), name='singlepage'),




]
