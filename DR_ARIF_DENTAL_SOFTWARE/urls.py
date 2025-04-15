from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doctor/', include('DOCTOR.urls')),
    path('reception/', include('RECEPTION.urls')),
    path('superadmin/', include('SUPER_ADMIN.urls')),
    path('', include('WEBSITE.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
