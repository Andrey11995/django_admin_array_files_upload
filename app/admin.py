from django.contrib import admin

from app.forms import ModelWithFilesArrayForm, ModelWithImagesArrayForm
from app.models import ModelWithFilesArray, ModelWithImagesArray


@admin.register(ModelWithImagesArray)
class ModelWithImagesArrayAdmin(admin.ModelAdmin):
    form = ModelWithImagesArrayForm
    readonly_fields = ['uploaded_images']

    def uploaded_images(self, instance):
        return '\n'.join(map(str, instance.images or [])) or '-'

    uploaded_images.short_description = 'Загруженные изображения'


@admin.register(ModelWithFilesArray)
class ModelWithFilesArrayAdmin(admin.ModelAdmin):
    form = ModelWithFilesArrayForm
    readonly_fields = ['uploaded_files']

    def uploaded_files(self, instance):
        return '\n'.join(map(str, instance.files or [])) or '-'

    uploaded_files.short_description = 'Загруженные файлы'
