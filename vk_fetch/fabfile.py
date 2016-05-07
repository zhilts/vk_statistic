from fabric.decorators import task
from fabric.operations import local


@task()
def pysetup():
    local('./pysetup.sh')


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
def migrate():
    manage('migrate --run-syncdb')


@task(alias='rdb')
def recreate_database():
    local('dropdb vk-fetch --if-exists')
    local('createdb vk-fetch --owner=user')
    migrate()
    # superuser: root/1qaz@WSX
    load_data('entities/datafixtures/users.json')
    load_data('entities/datafixtures/vk_groups.json')
