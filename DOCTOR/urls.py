from django.urls import path
from .import views
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', views.DoctorLoginView.as_view(), name='doctor-login'),

    path('dashboard/', views.DoctorDashboard.as_view(), name='doctor-dashboard'),

    path("patients/<int:doctor_id>/", views.DoctorPatientListView.as_view(), name="doctor-patients"),

    path('profile/', views.DoctorProfileView.as_view(), name='doctor-profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('change-password/', views.ChangeDoctorPassword.as_view(), name='change_password'),

    path('checkup/<int:booking_id>/', views.DentalExaminationCheckup.as_view(), name='checkup_page'),
    path('pediatric/<int:booking_id>/', views.PediatricExaminationCheckup.as_view(), name='checkup_page'),

    path('today_preview/<int:booking_id>/', views.TodayPreview.as_view(), name='today_preview'),
    path('pediatric_today/<int:booking_id>/', views.PediatricTodayPreview.as_view(), name='today_preview'),

    path('previous-treatment/<int:booking_id>/', views.LastAppointmentPreview.as_view(), name='previous-treatment'),
    path('pediatric_previous/<int:booking_id>/', views.PediatricLastAppointmentPreview.as_view(), name='previous-treatment'),

    path('delete-investigation/<int:id>/', views.DeleteInvestigationView.as_view(), name='delete-investigation'),

    path('medicine-prescription/<int:booking_id>/', views.MedicineAPIView.as_view(), name='medicine-prescription'),


    path("patient/<int:pk>/", views.RecentTreatmentDetailView.as_view(), name="recent-treatment"),

    path('singlepage/', TemplateView.as_view(template_name="reception/manage-patient-new.html"), name='singlepage'),

]


