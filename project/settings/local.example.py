from .base import *

ALLOWED_HOSTS = ['*']
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CORS_ORIGIN_WHITELIST = (
    'http://0.0.0.0:8000',
    'http://localhost:8000',
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

EMAIL_HOST = 'mailcatcher.smtp'
EMAIL_PORT = '1025'

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

CLIENT_URL = 'http://localhost:8000'

CELERY_BROKER_URL = os.environ.get('AMQP_HOST', 'brockman.rabbitmq')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 86400  # sec
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_NAME = 'DSESSIONID'
SESSION_COOKIE_SECURE = False


if DEBUG and not TESTING:
    def show_toolbar(request):
        """
        Default function to determine whether to show the toolbar on a given page.
        """
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar', 'django_extensions']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
