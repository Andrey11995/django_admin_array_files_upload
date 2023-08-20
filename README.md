# FilesArrayField и ImagesArrayField
### Реализация полей FilesArrayField и ImagesArrayField для загрузки нескольких файлов и изображений в поле ArrayField (PostgreSQL) в админке Django.

Поле ArrayField в моделях по умолчанию использует форму SimpleArrayField.

При наследовании класса формы от WithArrayAbstractModelForm поле формы SimpleArrayField
переопределится на FilesArrayField или ImagesArrayField в зависимости от вложенного в ArrayField
файлового поля (FileField или ImageField). При этом атрибуты наследуются от поля ArrayField.

Также можно явно объявить нужное поле FilesArrayField или ImagesArrayField в классе формы
и при этом указать нужные аттрибуты.

Есть возможность добавить аттрибут use_url=True, тем самым изменить виджет на большое текстовое поле
для ввода абсолютных url файлов и изображений, если нам требуется загрузить контент со стороннего ресурса.
При этом важно вводить каждый url с новой строки без запятых и пробелов, так как разделитель указан \n.
Также важно, чтобы в конце ссылки было допустимое в Django расширение (.png, .jpg и т.д.).

Для того чтобы видеть в админке загруженные файлы, можно добавить в класс ModelAdmin метод вывода
относительных URL в виде строки и сделать полученное поле доступным только для чтения.
В будущем планирую поработать над методом, чтобы он выводил кликабельные ссылки на файлы.

Виджет ClearableMultipleFilesInput позволяет добавлять в поле сразу несколько файлов.
Для этого нужно выбирать файлы с зажатым Ctrl.

## Загрузка с устройства:
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_1.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_2.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/added.JPG)

## Загрузка через URL:
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_url_1.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/add_url_2.JPG)
![Image](https://github.com/Andrey11995/django_admin_array_files_upload/raw/main/github_static/added_url.JPG)

Во избежание замусоривания хранилища при обновлении массива все старые файлы удаляются
посредством задачи Celery.
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
Docker-compose состоит из Django-приложения, базы данных PostgreSQL, Celery, его брокера Redis и Nginx.

Миграции и сборка статики запускаются сами в скрипте start_server.sh.

При первом запуске нужно будет лишь создать суперпользователя.
```
sudo docker exec -it app bash

python manage.py createsuperuser
```

### Админка проекта будет доступна по ссылке:
```
http://localhost/admin/
```
