"""
WSGI config for vk_fetch project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

from .gevent_init import patch_world
patch_world()
import os

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# import djcelery
# djcelery.setup_loader()
