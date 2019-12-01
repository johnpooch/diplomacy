from .base import *

ALLOWED_HOSTS = ['*']
DEBUG = False
TESTING = True

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)