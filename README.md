# FilesArrayField и ImagesArrayField
### Реализация полей FilesArrayField и ImagesArrayField для загрузки нескольких файлов и изображений в поле ArrayField (PostgreSQL) в админке Django.

Поле ArrayField(FileField()) переопределяется в файле admin.py в классе формы ModelForm.
При этом необходимо унаследовать класс формы от WithArrayAbstractModelForm и передать атрибут
FILES_ARRAY_FIELD с указанием названия поля с массивом файлов или изображений.

При переопределении поля в классе формы указывается нужный класс поля FilesArrayField или ImagesArrayField,
в зависимости от содержимого массива.

Для того чтобы видеть в админке загруженные файлы, можно добавить в класс ModelAdmin метод вывода
относительных URL в виде строки и сделать полученное поле доступным только для чтения.

Виджет ClearableMultipleFilesInput позволяет добавлять в поле сразу несколько файлов.
Для этого нужно выбирать файлы с зажатым Ctrl.

![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_1.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_2.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/added.JPG)

Во избежание замусоривания хранилища при обновлении массива все старые файлы удаляются.
При удалении объектов с массивами файлы также будут удалены из хранилища.

## Наполнение env-файла:

- DEBUG (1 - вкл, 0 - выкл);
- SECRET_KEY (секретный ключ Django);
- ALLOWED_HOSTS (список доступных хостов через запятую без пробела);
- CSRF_TRUSTED_ORIGINS (список доверенных доменов через запятую без пробела)
- POSTGRES_USER (пользователь БД);
- POSTGRES_DB (название БД);
- POSTGRES_PASSWORD (пароль БД);
- POSTGRES_HOST (хост БД);
- CELERY_BROKER_URL (url брокера: redis://redis:6379/1)

Файл .env должен находиться в корне проекта.

Для каждого ключа в проекте установлено дефолтное значение.

## Запуск проекта:
```
sudo docker-compose up -d --build
```
Docker-compose состоит из Django-приложения, базы данных PostgreSQL и Nginx.

Миграции и сборка статики запускаются сами в скрипте start_server.sh.

### Админка проекта будет доступна по ссылке:
```
http://localhost/admin/
```
