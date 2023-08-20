import os
import random

from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField
from django.core.files.storage import default_storage
from django.forms import FileField, ImageField
from slugify import slugify

from app.fields import (FilesArrayField, FilesArrayURLField, ImagesArrayField,
                        ImagesArrayURLField)
from app.models import ModelWithFilesArray, ModelWithImagesArray
from app.tasks import delete_old_files_from_storage
from app.utils import is_cyrillic


class WithArrayAbstractModelForm(forms.ModelForm):
    """
    Абстрактный класс с методами для массивов с файлами.
    Пока что поддерживает только один массив файлов на модель.
    """
    FILES_ARRAY_FIELD_USE_URL = False
    FILES_ARRAY_FIELD_LABEL = None
    FILES_ARRAY_FIELD_HELP_TEXT = None
    FILES_ARRAY_FIELD_REQUIRED = False

    def __init__(self, *args, **kwargs):
        super(WithArrayAbstractModelForm, self).__init__(*args, **kwargs)
        self.FILES_ARRAY_FIELD = None
        label = None
        FIELD_CLASS = None
        # URL_FIELD_CLASS = None
        for field_name, field_class in self.fields.items():
            if isinstance(field_class, SimpleArrayField):
                self.FILES_ARRAY_FIELD = field_name
                if isinstance(field_class.base_field, ImageField):
                    FIELD_CLASS = ImagesArrayField
                    # URL_FIELD_CLASS = ImagesArrayURLField
                    label = 'Загрузить изображения'
                elif isinstance(field_class.base_field, FileField):
                    FIELD_CLASS = FilesArrayField
                    # URL_FIELD_CLASS = FilesArrayURLField
                    label = 'Загрузить файлы'
        assert self.FILES_ARRAY_FIELD and FIELD_CLASS, (
            'В модели отсутствует массив файлов'
        )
        self.old_array = self.initial.pop(self.FILES_ARRAY_FIELD, [])
        self.fields[self.FILES_ARRAY_FIELD] = FIELD_CLASS(
            label=self.FILES_ARRAY_FIELD_LABEL or label,
            help_text=self.FILES_ARRAY_FIELD_HELP_TEXT,
            required=self.FILES_ARRAY_FIELD_REQUIRED
        )
        # if self.FILES_ARRAY_FIELD_USE_URL:
        #     url_field = 'upload_from_url'
        #     self._meta.fields.append(url_field)
        #     help_text = ('Введите абсолютные ссылки на файлы. '
        #                  'Каждая ссылка с новой строки без запятых. ')
        #     self.fields[url_field] = URL_FIELD_CLASS(
        #         label=self.FILES_ARRAY_FIELD_LABEL or label,
        #         help_text=help_text + self.FILES_ARRAY_FIELD_HELP_TEXT or '',
        #         required=self.FILES_ARRAY_FIELD_REQUIRED
        #     )


    def save(self, commit=True):
        array = self.cleaned_data.get(self.FILES_ARRAY_FIELD, [])
        instance = super().save(commit=False)
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
            # если в хранилище есть старые файлы
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
    FILES_ARRAY_FIELD_USE_URL = True
    FILES_ARRAY_FIELD_LABEL = 'Загрузить изображения'
    FILES_ARRAY_FIELD_HELP_TEXT = ('При загрузке новых изображений, '
                                   'старые удаляются')

    class Meta:
        model = ModelWithImagesArray
        fields = '__all__'


class ModelWithFilesArrayForm(WithArrayAbstractModelForm):
    FILES_ARRAY_FIELD_USE_URL = True
    FILES_ARRAY_FIELD_LABEL = 'Загрузить файлы'
    FILES_ARRAY_FIELD_HELP_TEXT = 'При загрузке новых файлов, старые удаляются'

    class Meta:
        model = ModelWithFilesArray
        fields = '__all__'
