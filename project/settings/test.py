import os.path
from .base import *

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

ALLOWED_HOSTS = ['*']
DEBUG = False
TESTING = True

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)


FIXTURE_DIRS = (
    os.path.join(PROJECT_ROOT, 'fixtures'),
)
