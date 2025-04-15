from django.urls import path
from .import views

urlpatterns = [
    path('login/', views.DoctorLoginView.as_view(), name='doctor-login'),

    path('dashboard/', views.DoctorDashboard.as_view(), name='doctor-dashboard'),

    path("patients/<int:doctor_id>/", views.DoctorPatientListView.as_view(), name="doctor-patients"),

    path('profile/', views.DoctorProfileView.as_view(), name='doctor-profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangeDoctorPassword.as_view(), name='change_password'),

    path('checkup/<int:booking_id>/', views.DentalExaminationCheckup.as_view(), name='checkup_page'),

    path('today_preview/<int:booking_id>/', views.TodayPreview.as_view(), name='today_preview'),

    path('medicine-prescription/<int:booking_id>/', views.MedicineAPIView.as_view(), name='medicine-prescription'),

    path('previous-treatment/<int:booking_id>/', views.LastAppointmentPreview.as_view(), name='previous-treatment'),



    path("patient/<int:pk>/", views.RecentTreatmentDetailView.as_view(), name="recent-treatment"),


]


