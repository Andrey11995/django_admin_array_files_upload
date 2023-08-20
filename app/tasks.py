from django.core.files.storage import default_storage

from django_admin_array_files_upload.celery import app


@app.task
def delete_old_files_from_storage(files):
    for file in files:
        default_storage.delete(file)
