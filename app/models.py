from django.contrib.postgres.fields import ArrayField
from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver

from app.utils import upload_files_path


class ModelWithImagesArray(models.Model):
    images = ArrayField(
        models.ImageField(upload_to=upload_files_path),
        null=True, blank=True, default=list
    )

    class Meta:
        verbose_name = 'Объект с массивом изображений'
        verbose_name_plural = 'Объекты с массивами изображений'


class ModelWithFilesArray(models.Model):
    files = ArrayField(
        models.FileField(upload_to=upload_files_path),
        null=True, blank=True, default=list
    )

    class Meta:
        verbose_name = 'Объект с массивом файлов'
        verbose_name_plural = 'Объекты с массивами файлов'


@receiver(models.signals.pre_delete, sender=ModelWithImagesArray)
def delete_images(sender, instance, **kwargs):
    for image in instance.images:
        default_storage.delete(image)


@receiver(models.signals.pre_delete, sender=ModelWithFilesArray)
def delete_files(sender, instance, **kwargs):
    for file in instance.files:
        default_storage.delete(file)
