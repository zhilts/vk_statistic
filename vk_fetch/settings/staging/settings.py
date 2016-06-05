from settings.settings import *

DEBUG = False

DATABASES['default'].update({
    'NAME': 'vk_fetch',
    'USER': 'vk_fetch',
    'PASS': '{fqRJnKb7y!R}:2.',
    'HOST': 'vk-fetch.cjovx6nrl7nk.us-west-2.rds.amazonaws.com'
})

BROKER_URL = os.environ.get('REDIS_URL')
