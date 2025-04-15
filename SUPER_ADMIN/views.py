from django.shortcuts import render, redirect
from rest_framework.response import Response
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from RECEPTION.models import Patient
from django.utils import timezone
from rest_framework import viewsets, status
import json
from django.db import models
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, action
from .models import (SuperAdmin,
                     Supplier,
                     Branch,
                     Receptionist,
                     Pharmacy,HospitalInfo,
                     Doctor,TaxRate,
                     LabOrder,
                     Hospital_Inventory,PharmaceuticalMedicine
)
from .serializer import  (SuperAdminSerializer,
                          SuperAdminLoginSerializer,
                          ReceptionCreateSerializer,
                          BranchSerializer,SupplierSerializer,
                          PharmacyCreateSerializer,
                          DoctorCreateSerializer,UserUpdateSerializer,
                          SuperAdminUpdateSerializer,HospitalInventorySerializer,LabOrderSerializer,
                          SuperadminViewProfileSerializer,ChangeSuperadminPasswordSerializer,TaxRateSerializer,
#                          TreatmentPriceSerializer, HospitalInfoSerializer,
                        
                          )


# -------------------------- Super Admin Registration --------------------------#
class SuperAdmin_Signup(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/authentication/superadmin_register.html'

    def get(self, request):
        super = SuperAdmin.objects.all()
        serializer = SuperAdminSerializer(super, many=True)
        return Response({'serializer': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SuperAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer.data, 'message': 'Superuser registered successfully!'},
                            status=status.HTTP_201_CREATED)
        return Response({'serializer': serializer.data, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
# --------------------------Doctor CREATION---------------------------------
class DoctorCreate(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    #template_name = 'superadmin/profilecreation/doctor_profile_creation.html'
    template_name = 'superadmin/doctors_list.html'

    def get(self, request):
        reception_data =Doctor.objects.all()
        serializer = DoctorCreateSerializer(reception_data, many=True)
        return Response({"serializer":serializer.data}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------- Super Admin Login --------------------------#
class SuperAdminLoginView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/authentication/superadmin_login.html'

    def get(self, request):
        serializer = SuperAdminLoginSerializer()
        return Response({'serializer': serializer.data})

    def post(self, request):
        serializer = SuperAdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            Token.objects.get_or_create(user=user)
            return HttpResponseRedirect(reverse('superadmindashboard'))
        print(serializer.errors)
        return Response({"message": "Invalid credentials", 'serializer': serializer, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

# --------------------------PHARMACY CREATION---------------------------------
class PharmacyCreate(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    # template_name = 'superadmin/profilecreation/pharmacy_profile_creation.html'
    template_name = 'superadmin/pharmacists_list.html'

    def get(self, request):
        pharmacies = Pharmacy.objects.all()
        serializer = PharmacyCreateSerializer(pharmacies, many=True)
        return Response({"serializer": serializer.data}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = PharmacyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------RECEPTION CREATION---------------------------------
class ReceptionCreate(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    #template_name = 'superadmin/profilecreation/reception_profile_creation.html'
    template_name = 'superadmin/receptionists_list.html'

    def get(self, request):
        reception_data = Receptionist.objects.all()
        serializer = ReceptionCreateSerializer(reception_data, many=True)
        return Response({"serializer":serializer.data}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = ReceptionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------- Branch Creation --------------------------#
class BranchCreate(APIView):

    def get(self, request):
            branches = Branch.objects.all().filter(is_active = True)
            serializer = BranchSerializer(branches, many=True)
            return JsonResponse(serializer.data, safe=False)


    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchDetailView(APIView):

    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        serializer = BranchSerializer(branch)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse(serializer.data)  # Correct AJAX response
        return Response({'branch': serializer.data})  # Default behavior for HTML

    def put(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        branch.is_active = False
        branch.save()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)


# -------------------------- Supplier CRUD --------------------------#
class SupplierView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/suppliers/supplier_list.html'

    def get(self, request):
        suppliers = Supplier.objects.filter(is_active=True)
        serializer = SupplierSerializer(suppliers, many=True)
        if request.accepted_renderer.format == 'html':
            return Response({'suppliers': serializer.data})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.accepted_renderer.format == 'html':
                return redirect('supplier_list')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupplierDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/suppliers/supplier_list.html'

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier)
        if request.accepted_renderer.format == 'html':
            return Response({'supplier': serializer.data})
        return Response(serializer.data)

    def put(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_active = False
        supplier.save()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
    
# ----------------------------Doctor Specialization------------------------------#
def get_specializations(request):
    specializations = dict(Doctor._meta.get_field('specialization').choices)
    return JsonResponse(specializations)

# ----------------------------Doctor Specialization------------------------------#

# ----------------------------Logout View------------------------------#
# class LogoutView(APIView):
#     #permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Delete the token to log the user out
#         request.user.auth_token.delete()
#         return Response({"message": "Successfully logged out"}, status=200)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can log out

    def post(self, request):
        logout(request)  # Log out the user
        request.session.flush()  # Clear session data to prevent reuse
        
        response = redirect('/navigation/')  # Redirect to login or home page
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response  # Redirects user to the login/home page
    
# ----------------------------Logout View------------------------------#

# ----------------------------Super_Admin_Dashboard------------------------------# 

class SuperAdminDashboard(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/superadmindashboard.html'

    @method_decorator(login_required(login_url='/superadmin/login/'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        try:
            super_admin = SuperAdmin.objects.get(user=user)
            super_admin_serializer = SuperAdminUpdateSerializer(super_admin)
        except ObjectDoesNotExist:
            super_admin_serializer = None

        user_serializer = UserUpdateSerializer(user)
        
        # Get current date for the dashboard
        current_date = timezone.now()
        
        # Get counts for statistics cards
        branches_count = Branch.objects.count()
        doctors_count = Doctor.objects.count()
        receptionists_count = Receptionist.objects.count()
        medicines_count = PharmaceuticalMedicine.objects.count()
        
        # Get low stock inventory items
        low_stock_items = Hospital_Inventory.objects.filter(
            quantity_in_stock__lte=models.F('reorder_level')
        ).order_by('quantity_in_stock')[:5]
        
        # Get low stock medicines
        low_stock_medicines = PharmaceuticalMedicine.objects.filter(
            quantity_in_stock__lte=10  # Assuming reorder level is 10 for medicines
        ).order_by('quantity_in_stock')[:5]
        
        # Get recent lab orders
        recent_lab_orders = LabOrder.objects.all().order_by('-created_at')[:5]
        
        # Get branches for branch performance section
        branches = Branch.objects.all()
        
        if request.accepted_renderer.format == 'html':
            return Response({
                'user': user_serializer.data,
                'super_admin': super_admin_serializer.data if super_admin_serializer else {},
                'current_date': current_date,
                'branches_count': branches_count,
                'doctors_count': doctors_count,
                'receptionists_count': receptionists_count,
                'medicines_count': medicines_count,
                'low_stock_items': low_stock_items,
                'low_stock_medicines': low_stock_medicines,
                'recent_lab_orders': recent_lab_orders,
                'branches': branches
            })
        else:
            # For API/JSON response format
            return Response({
                'user': user_serializer.data,
                'super_admin': super_admin_serializer.data if super_admin_serializer else {},
                'statistics': {
                    'branches_count': branches_count,
                    'doctors_count': doctors_count,
                    'receptionists_count': receptionists_count,
                    'medicines_count': medicines_count,
                }
            })

    def post(self, request):
        user = request.user
        user_data = request.data.get('user_info', {})
        super_admin_data = request.data.get('super_admin_info', {})

        # Handle User Update
        user_serializer = UserUpdateSerializer(user, data=user_data, partial=True)

        # Handle SuperAdmin Update
        try:
            super_admin = SuperAdmin.objects.get(user=user)
            super_admin_serializer = SuperAdminUpdateSerializer(super_admin, data=super_admin_data, partial=True)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'SuperAdmin profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Validate and Save Data
        if user_serializer.is_valid() and super_admin_serializer.is_valid():
            user_serializer.save()
            super_admin_serializer.save()
            return JsonResponse({
                'message': 'Profile updated successfully',
                'user_info': user_serializer.data,
                'super_admin_info': super_admin_serializer.data
            }, status=status.HTTP_200_OK)

        # Merge Errors from Both Serializers
        errors = {}
        errors.update(user_serializer.errors)
        errors.update(super_admin_serializer.errors)

        return JsonResponse({
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)


# View for SuperAdmin profile
class SuperadminProfileView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/superadmin_editprofile.html'

    def get(self, request):
        superadmin = get_object_or_404(SuperAdmin, user=request.user)
        superadmin_serializer = SuperadminViewProfileSerializer(superadmin)

        if request.accepted_renderer.format == 'json':
            return Response({'superadmin_profile': superadmin_serializer.data}, status=status.HTTP_200_OK)
        return Response({'superadmin_profile': superadmin_serializer.data}, template_name=self.template_name)

    def post(self, request):
        """Fix issue with accessing request body multiple times."""
        superadmin = get_object_or_404(SuperAdmin, user=request.user)

        # Ensure JSON decoding works correctly
        try:
            data = request.data  # DRF handles JSON and form data correctly
        except Exception:
            return JsonResponse({'error': 'Invalid data format'}, status=400)

        serializer = SuperadminViewProfileSerializer(superadmin, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Superadmin profile updated successfully"}, status=200)
        
        return JsonResponse(serializer.errors, status=400)
    
#---------------Change Superadmin Password---------------
class ChangeSuperadminPassword(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/change_superadmin_password.html'

    def get(self, request):
        serializer = SuperAdminLoginSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = ChangeSuperadminPasswordSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
#---------------------------Hospital_Inventory_Dashboard_CRUD--------------------#

def get_category(request):
    categories = dict(Hospital_Inventory._meta.get_field('category').choices)
    return JsonResponse(categories)

class SupplierListView(APIView):
    def get(self, request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        if request.accepted_renderer.format == 'html':
            return Response({'suppliers': serializer.data})
        return Response(serializer.data, status=status.HTTP_200_OK)

class HospitalInventory(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/hospital-inventory.html'

    def get(self, request):
        hospital_inventory = Hospital_Inventory.objects.all().filter(is_active=True)
        serializer = HospitalInventorySerializer(hospital_inventory, many=True)
        if request.accepted_renderer.format == 'html':
            return Response({'hospital_inventory': serializer.data})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = HospitalInventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.accepted_renderer.format == 'html':
                return redirect('hospital_inventory')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HospitalInventoryItem(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'superadmin/hospital-inventory-item.html'

    def get(self, request, pk):
        try:
            inventory_item = Hospital_Inventory.objects.get(pk=pk)
            serializer = HospitalInventorySerializer(inventory_item)
            if request.accepted_renderer.format == 'html':
                return Response({'inventory_item': serializer.data})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Hospital_Inventory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, item_id):
        try:
            inventory_item = Hospital_Inventory.objects.get(id=item_id)
            serializer = HospitalInventorySerializer(inventory_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Hospital_Inventory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DeleteInventoryItemView(APIView):
    def post(self, request, item_id):
        inventory_item = get_object_or_404(Hospital_Inventory, id=item_id)
        inventory_item.is_active = False  # Soft delete logic
        inventory_item.save()
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_200_OK)
    
#---------------------------Hospital_Inventory_Dashboard_CRUD--------------------#

# Tax Rate Views
class TaxRateListCreateView(APIView):
    def get(self, request):
        tax_rates = TaxRate.objects.all()
        serializer = TaxRateSerializer(tax_rates, many=True)
        return Response({'tax_rates': serializer.data})

    def post(self, request):
        serializer = TaxRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TaxRateRetrieveUpdateDeleteView(APIView):
    def get(self, request, pk):
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        serializer = TaxRateSerializer(tax_rate)
        return Response({'tax_rate': serializer.data})

    def put(self, request, pk):
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        serializer = TaxRateSerializer(tax_rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        tax_rate = get_object_or_404(TaxRate, pk=pk)
        tax_rate.delete()
        return Response(status=204)

class HospitalInfoAPIView(APIView):
    def get(self, request):
        """Get hospital information"""
        hospitals = HospitalInfo.objects.all()
        data = []
        for hospital in hospitals:
            data.append({
                'id': hospital.id,
                'name': hospital.name,
                'address': hospital.address,
                'phone': hospital.phone,
                'email': hospital.email,
                'website': hospital.website,
                # 'gstin': hospital.gstin
            })
        return Response({'hospitals': data})


class LabOrderListView(APIView):
    """
    List all lab orders or create a new lab order
    """
    def get(self, request):
        lab_orders = LabOrder.objects.all()
        serializer = LabOrderSerializer(lab_orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = LabOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabOrderDetailView(APIView):
    """
    Retrieve, update or delete a lab order
    """
    def get_object(self, pk):
        return get_object_or_404(LabOrder, pk=pk)
    
    def get(self, request, pk):
        lab_order = self.get_object(pk)
        serializer = LabOrderSerializer(lab_order)
        return Response(serializer.data)
    
    def put(self, request, pk):
        lab_order = self.get_object(pk)
        serializer = LabOrderSerializer(lab_order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        lab_order = self.get_object(pk)
        serializer = LabOrderSerializer(lab_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        lab_order = self.get_object(pk)
        lab_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PatientLabOrdersView(APIView):
    """
    List all lab orders for a specific patient
    """
    def get(self, request, patient_id):
        lab_orders = LabOrder.objects.filter(patient_id=patient_id)
        serializer = LabOrderSerializer(lab_orders, many=True)
        return Response(serializer.data)


