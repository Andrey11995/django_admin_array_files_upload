import io

from PIL import Image
from django.core.exceptions import ValidationError
from django.forms import (CheckboxInput, ClearableFileInput, FileField,
                          ImageField)

FILE_INPUT_CONTRADICTION = object()


class ClearableMultipleFilesInput(ClearableFileInput):
    """Виджет для поля загрузки нескольких файлов."""
    def value_from_datadict(self, data, files, name):
        upload = files.getlist(name)
        if not self.is_required and CheckboxInput().value_from_datadict(
            data, files, self.clear_checkbox_name(name)
        ):
            if upload:
                return FILE_INPUT_CONTRADICTION
            return False
        return upload


class FilesArrayField(FileField):
    """Поле формы для загрузки нескольких файлов через админку."""
    widget = ClearableMultipleFilesInput(attrs={'multiple': True})

    def to_python(self, data):
        if data in self.empty_values:
            return
        for file_upload in data:
            try:
                file_name = file_upload.name
                file_size = file_upload.size
            except AttributeError:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
            if self.max_length and len(file_name) > self.max_length:
                params = {'max': self.max_length, 'length': len(file_name)}
                raise ValidationError(
                    self.error_messages['max_length'], code='max_length', params=params
                )
            if not file_name:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
            if not self.allow_empty_file and not file_size:
                raise ValidationError(self.error_messages['empty'], code='empty')
        return data

    def clean(self, data, initial=None):
        if data is FILE_INPUT_CONTRADICTION:
            raise ValidationError(
                self.error_messages['contradiction'],
                code='contradiction'
            )
        if not data:
            if not self.required:
                return []
            data = None
        if not data and initial:
            return initial
        return self.to_python(data)


class ImagesArrayField(FilesArrayField, ImageField):
    """Поле формы для загрузки нескольких фото через админку."""
    def to_python(self, data):
        if data in self.empty_values:
            return
        data = super(ImagesArrayField, self).to_python(data)
        for file_upload in data:
            if hasattr(data, 'temporary_file_path'):
                file = file_upload.temporary_file_path()
            else:
                if hasattr(file_upload, 'read'):
                    file = io.BytesIO(file_upload.read())
                else:
                    file = io.BytesIO(file_upload['content'])
            try:
                image = Image.open(file)
                image.verify()
                file_upload.image = image
                file_upload.content_type = Image.MIME.get(image.format)
            except Exception as exc:
                raise ValidationError(
                    self.error_messages['invalid_image'],
                    code='invalid_image',
                ) from exc
            if hasattr(file_upload, 'seek') and callable(file_upload.seek):
                file_upload.seek(0)
        return data
