import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_admin_array_files_upload.settings')

app = Celery('django_admin_array_files_upload')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
