import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_admin_array_files_upload.settings')

application = get_wsgi_application()
