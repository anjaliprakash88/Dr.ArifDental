from django.contrib import admin
from .models import User, Doctor, Receptionist, SuperAdmin,Supplier,Hospital_Inventory, Branch, PharmaceuticalMedicine

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Receptionist)
admin.site.register(SuperAdmin)
admin.site.register(Hospital_Inventory)
admin.site.register(Supplier)
admin.site.register(Branch)
admin.site.register(PharmaceuticalMedicine)
