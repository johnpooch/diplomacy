import os

import dj_database_url

from .base import *

DATABASES = {
    'default': dj_database_url.parse(os.environ.get("DATABASE_URL"))
}
