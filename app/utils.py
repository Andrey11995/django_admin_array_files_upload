from urllib.parse import unquote


def upload_files_path(instance, filename):
    return f'path/to/files/{filename}'


def is_cyrillic(name):
    return any(ord(c) > 127 for c in unquote(name))
