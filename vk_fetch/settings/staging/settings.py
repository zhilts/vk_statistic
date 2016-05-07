from settings.settings import *

import dj_database_url
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

BROKER_URL = 'redis://h:p4fseodb3ur4rt7pjrnprlgsc34@ec2-54-83-33-178.compute-1.amazonaws.com:18849'
