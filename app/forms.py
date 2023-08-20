import os
import random

from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField
from django.core.files.storage import default_storage
from django.forms import ImageField
from slugify import slugify

from app.fields import FilesArrayField, ImagesArrayField
from app.models import ModelWithFilesArray, ModelWithImagesArray
from app.tasks import delete_old_files_from_storage
from app.utils import is_cyrillic


class WithArrayAbstractModelForm(forms.ModelForm):
    """
    Абстрактный класс с методами для массивов с файлами.
    Пока что поддерживает только один массив файлов на модель.
    """
    def __init__(self, *args, **kwargs):
        super(WithArrayAbstractModelForm, self).__init__(*args, **kwargs)
        self.FILES_ARRAY_FIELD, field = self.get_file_field()
        assert field, 'В модели отсутствует массив файлов'
        self.old_array = self.initial.get(self.FILES_ARRAY_FIELD, [])
        self.fields[self.FILES_ARRAY_FIELD] = field

    def get_file_field(self):
        for field_name, field_class in self.fields.items():
            if isinstance(field_class, SimpleArrayField):
                kwargs = {
                    'label': field_class.label,
                    'help_text': field_class.help_text,
                    'required': field_class.required,
                    'use_url': False
                }
                if isinstance(field_class.base_field, ImageField):
                    return field_name, ImagesArrayField(**kwargs)
                return field_name, FilesArrayField(**kwargs)
            elif (isinstance(field_class, FilesArrayField) or
                  isinstance(field_class, ImagesArrayField)):
                kwargs = field_class.__dict__
                kwargs.pop('field')
                return field_name, field_class.__class__(**kwargs)
        return None, None

    def save(self, commit=True):
        array = self.cleaned_data.get(self.FILES_ARRAY_FIELD, [])
        instance = super().save(commit=False)
        if array is None:
            instance.images = self.initial.get(self.FILES_ARRAY_FIELD, [])
        delete_old_array = False
        if array:
            upload_to = self._meta.model._meta.get_field(
                self.FILES_ARRAY_FIELD
            ).base_field.upload_to
            setattr(instance, self.FILES_ARRAY_FIELD, [])
            delete_old_array = True
            for file in array:
                if callable(upload_to):
                    file_name = upload_to(instance, file.name)
                else:
                    file_name = upload_to + file.name
                # при работе с дефолтным хранилищем проверку можно удалить
                file_name = self.check_file_name(file_name)
                file = default_storage.save(file_name, file)
                getattr(instance, self.FILES_ARRAY_FIELD).append(file)
        if commit:
            instance.save()
        if delete_old_array and self.old_array:
            # если в хранилище есть старые файлы и загружаем новые
            # отправляем в celery задачу на их удаление
            delete_old_files_from_storage.apply_async([self.old_array])
        return instance

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
    images = ImagesArrayField(
        label='Загрузить изображения',
        help_text='Каждая ссылка с новой строки без запятых!',
        required=False,
        use_url=True
    )

    class Meta:
        model = ModelWithImagesArray
        fields = '__all__'


class ModelWithFilesArrayForm(WithArrayAbstractModelForm):
    files = FilesArrayField(
        label='Загрузить файлы',
        help_text='При загрузке новых файлов, старые удаляются!',
        required=False
    )

    class Meta:
        model = ModelWithFilesArray
        fields = '__all__'
