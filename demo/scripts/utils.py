import os

def full_path(path):
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
