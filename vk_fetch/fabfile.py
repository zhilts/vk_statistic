import os
from contextlib import contextmanager

import posixpath
from fabric.context_managers import prefix, shell_env
from fabric.decorators import task
from fabric.operations import local

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")


@contextmanager
def virtualenv(path='./env'):
    activate = posixpath.join(path, 'bin/activate')
    if not posixpath.exists(activate):
        raise OSError("Cannot activate virtualenv %s" % path)
    with prefix('. %s' % activate):
        yield


@task()
def pysetup(args=''):
    local('./pysetup.sh {args}'.format(args=args))


@task()
def runserver():
    manage("runserver 0.0.0.0:8000")


@task()
def manage(command):
    local('./pyenv.sh ./manage.py {command}'.format(command=command))


@task
def load_data(path):
    manage('loaddata {path}'.format(path=path))


@task()
def celery(mode=''):
    manage('celery {mode}'.format(mode=mode))


@task()
def celery_worker(args=''):
    celery('worker {args}'.format(args=args))


@task()
def celery_beat():
    celery('beat')


@task()
def list_celery_tasks():
    celery('inspect registered')


@task(alias='mkm')
def make_migrations():
    manage('makemigrations')


@task()
def migrate():
    manage('migrate --run-syncdb')


@task(alias='msgm')
def make_messages(args='-l ru'):
    with virtualenv():
        local('./manage.py makemessages --ignore\=env {}'.format(args))


@task(alias='msgc')
def compile_messages(args='--locale\=ru'):
    with virtualenv():
        local('./manage.py compilemessages {}'.format(args))


@task(alias='rdb')
def recreate_database():
    local('sudo service postgresql restart')
    local('dropdb vk-fetch --if-exists')
    local('createdb vk-fetch --owner=user')
    migrate()
    # superuser: root/1qaz@WSX
    load_data('entities/datafixtures/users.json')
    load_data('entities/datafixtures/vk_groups.json')
