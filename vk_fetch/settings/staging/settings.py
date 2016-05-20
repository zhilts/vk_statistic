from settings.settings import *

import dj_database_url
DEBUG = False

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

from urllib.parse import urlparse

BROKER_URL = os.environ.get('REDIS_URL')
