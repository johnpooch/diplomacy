import os

import dj_database_url

from .base import *


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


DATABASES = {
    'default': dj_database_url.parse(os.environ.get("DATABASE_URL"))
}
