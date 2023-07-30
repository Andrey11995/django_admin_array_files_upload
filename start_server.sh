#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

export DJANGO_SETTINGS_MODULE=django_admin_array_files_upload.settings

python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 django_admin_array_files_upload.asgi:application
