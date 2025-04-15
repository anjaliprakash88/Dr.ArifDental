from django.urls import path
from django.views.generic import TemplateView
from .views import (
    SuperAdminLoginView,
    SupplierListView,
    SupplierView,
    SupplierDetailView,
    BranchCreate,
    BranchDetailView,
    BranchDetailView,
    PharmacyCreate,
    ReceptionCreate,SuperAdmin_Signup,DoctorCreate,
    SuperAdminDashboard,LogoutView,TaxRateListCreateView, TaxRateRetrieveUpdateDeleteView,
    LabOrderListView,LabOrderDetailView,PatientLabOrdersView,HospitalInfoAPIView,
    # TreatmentPriceListCreateView, TreatmentPriceRetrieveUpdateDeleteView,
    # HospitalInfoListCreateView, HospitalInfoRetrieveUpdateDeleteView,
    HospitalInventory,
    HospitalInventoryItem,
    DeleteInventoryItemView,
    SuperadminProfileView,
    ChangeSuperadminPassword,
    get_specializations,
    get_category
)

urlpatterns = [
    # Superadmin Authentication URLs
    path('signup/', SuperAdmin_Signup.as_view(), name='superuser_signup'),
    path('login/', SuperAdminLoginView.as_view(), name='superadminloginview'),

    # Supplier URLs
    path('suppliers/', SupplierView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),

    # Inventory URLs
    path('supplier_data/', SupplierListView.as_view(), name='supplier_data'),
    path('hospital-inventory/', HospitalInventory.as_view(), name='hospital_inventory'),
    path('hospital-inventory/item/<int:pk>/', HospitalInventoryItem.as_view(), name='hospital_inventory_item'),
    path('hospital-inventory/item/<int:item_id>/update/', HospitalInventoryItem.as_view(), name='update_inventory_item'),
    path('hospital-inventory/item/<int:item_id>/delete/', DeleteInventoryItemView.as_view(), name='delete_inventory_item'),
    path('category/', get_category, name='category'),

    # Branch and Pharmacy URLs
    path('branch/', BranchCreate.as_view(), name='branchCreate'), 
    path('branch/<int:pk>/', BranchDetailView.as_view(), name='branchdetailview'),   
    path('specializations/', get_specializations, name='specializations'),
    path('pharmacy-create/', PharmacyCreate.as_view(), name='pharmacy-Create'),
    path('reception-create/', ReceptionCreate.as_view(), name='receptionCreate'),
    path('doctor-create/', DoctorCreate.as_view(), name='Doctor-Create'),

    path('tax-rates/', TaxRateListCreateView.as_view(), name='tax-rate-list-create'),
    path('tax-rates/<int:pk>/', TaxRateRetrieveUpdateDeleteView.as_view(), name='tax-rate-detail'),

    # path('treatment-prices/', TreatmentPriceListCreateView.as_view(), name='treatment-price-list-create'),
    # path('treatment-prices/<int:pk>/', TreatmentPriceRetrieveUpdateDeleteView.as_view(), name='treatment-price-detail'),

    # path('hospital-info/', HospitalInfoListCreateView.as_view(), name='hospital-info-list-create'),
    # path('hospital-info/<int:pk>/', HospitalInfoRetrieveUpdateDeleteView.as_view(), name='hospital-info-detail'),

    # Dashboard  URLs
    path('superadmindashboard/', SuperAdminDashboard.as_view(), name='superadmindashboard'),
    path('change-password/', ChangeSuperadminPassword.as_view(), name='change_password'),
    path('update-profile/', SuperadminProfileView.as_view(), name='superadmin-update-profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('lab-orders/', LabOrderListView.as_view(), name='lab-order-list'),
    path('lab-orders/<int:pk>/', LabOrderDetailView.as_view(), name='lab-order-detail'),
    path('patients/<int:patient_id>/lab-orders/', PatientLabOrdersView.as_view(), name='patient-lab-orders'),

    
    # Hospital information
    path('hospital-info/', HospitalInfoAPIView.as_view(), name='hospital-info'),  # Get hospital info

    # Treatment prices and tax rates
    # path('treatment-prices/', TreatmentPricesAPIView.as_view(), name='treatment-prices'),  # Get treatment prices and tax rates
    path('medicineslist/', TemplateView.as_view(template_name="superadmin/medicine-crud.html"), name='medicine-list'),
    path('laborders/', TemplateView.as_view(template_name="superadmin/labtracking.html"), name='lab-orders'),
    path('hospital-data/', TemplateView.as_view(template_name="superadmin/hospital_info.html"), name='hospital-data'),
    path('manage-branch/', TemplateView.as_view(template_name="superadmin/branch_creation.html"), name='manage-branch'),

]

