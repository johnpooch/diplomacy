from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

CORS_ORIGIN_WHITELIST = (
    '0.0.0.0:8000',
    'localhost:8000',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'diplomacy',
        'USER': 'APP_USER',
        'PASSWORD': 'APP_USER',
        'HOST': 'diplomacy.mysql',
        'PORT': '3306',
    },
}

# NOTE non Docker setup
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'mydatabase',
#     }
# }

FIXTURE_DIRS = (
    '/code/fixtures',
)
# NOTE non Docker setup
# FIXTURE_DIRS = (
#     'fixtures',
# )
