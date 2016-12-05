import hashlib
import settings


def read_content_from_file(file_name):
    with open(file_name) as file_handle:
        content = file_handle.read()
        return content


def write_content_to_file(file_name, content):
    with open(file_name, "w") as file_handle:
        file_handle.write(content)


def generate_hash_key(content, salt=settings.HASH_SALT):
    return hashlib.sha256('%s.%s' % (content, salt)).hexdigest()
