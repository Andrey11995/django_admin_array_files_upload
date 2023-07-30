import os
import random

from django.conf import settings
from django.contrib import admin
from django import forms
from django.core.files.storage import default_storage
from slugify import slugify

from app.fields import FilesArrayField, ImagesArrayField
from app.models import ModelWithFilesArray, ModelWithImagesArray
from app.utils import is_cyrillic


class WithArrayAbstractModelForm(forms.ModelForm):
    """Абстрактный класс с методами для массивов с файлами."""
    FILES_ARRAY_FIELD: str = None

    def save(self, commit=True):
        array = self.cleaned_data.pop(self.FILES_ARRAY_FIELD, [])
        instance = super().save(commit=False)
        if array:
            self.delete_old_files_from_storage()
            setattr(instance, self.FILES_ARRAY_FIELD, [])
            for file in array:
                file_name = self._meta.model._meta.get_field(
                    self.FILES_ARRAY_FIELD
                ).base_field.upload_to(instance, file.name)
                # при работе с дефолтным хранилищем проверку можно удалить
                file_name = self.check_file_name(file_name)
                file = default_storage.save(file_name, file)
                getattr(instance, self.FILES_ARRAY_FIELD).append(file)
        if commit:
            instance.save()
        return instance

    def delete_old_files_from_storage(self):
        for image in self.initial.get(self.FILES_ARRAY_FIELD, []):
            default_storage.delete(image)

    @staticmethod
    def check_file_name(file_name):
        """
        Метод проверки имени файла на дубликаты.
        При работе с дефолтным хранилищем django не нужен.
        Необходим при работе со сторонними хранилищами,
        так как в них такая встроенная проверка отсутствует.
        """
        full_path, extension = os.path.splitext(file_name)
        split_path = full_path.split('/')
        name = split_path[-1]
        path = '/'.join(split_path[:-1]) + '/'
        if is_cyrillic(name):
            name = slugify(name)
        file_name = f'{path}{name}{extension}'
        while default_storage.exists(file_name):
            suffix = ''.join(random.choices(settings.SYMBOLS, k=5))
            file_name = f'{path}{name}_{suffix}{extension}'
        return file_name


class ModelWithImagesArrayForm(WithArrayAbstractModelForm):
    FILES_ARRAY_FIELD = 'images'
    images = ImagesArrayField(
        label='Загрузить изображения',
        help_text='При загрузке новых изображений, старые удаляются',
        required=False
    )

    class Meta:
        model = ModelWithImagesArray
        fields = '__all__'


@admin.register(ModelWithImagesArray)
class ModelWithImagesArrayAdmin(admin.ModelAdmin):
    form = ModelWithImagesArrayForm
    readonly_fields = ['uploaded_images']

    def uploaded_images(self, instance):
        return '\n'.join(instance.images) or '-'

    uploaded_images.short_description = 'Загруженные изображения'


class ModelWithFilesArrayForm(WithArrayAbstractModelForm):
    FILES_ARRAY_FIELD = 'files'
    files = FilesArrayField(
        label='Загрузить файлы',
        help_text='При загрузке новых файлов, старые удаляются',
        required=False
    )

    class Meta:
        model = ModelWithFilesArray
        fields = '__all__'


@admin.register(ModelWithFilesArray)
class ModelWithFilesArrayAdmin(admin.ModelAdmin):
    form = ModelWithFilesArrayForm
    readonly_fields = ['uploaded_files']

    def uploaded_files(self, instance):
        return '\n'.join(instance.files) or '-'

    uploaded_files.short_description = 'Загруженные файлы'
