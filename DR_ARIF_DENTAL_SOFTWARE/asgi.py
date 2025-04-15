"""
ASGI config for DR_ARIF_DENTAL_SOFTWARE project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DR_ARIF_DENTAL_SOFTWARE.settings')

application = get_asgi_application()
