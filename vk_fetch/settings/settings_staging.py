from settings.settings import *

DEBUG = False

DATABASES['default'].update({
    'NAME': 'vk_fetch',
    'USER': 'vk_fetch',
    'PASSWORD': '{fqRJnKb7y!R}:2.',
    'HOST': 'vk-fetch.cjovx6nrl7nk.us-west-2.rds.amazonaws.com'
})

# BROKER_URL = os.environ.get('REDIS_URL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s: %(levelname)s/%(module)s.%(funcName)s:%(lineno)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'runner.tasks': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
}