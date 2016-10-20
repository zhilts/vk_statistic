from datetime import datetime

from fabric.api import settings
from fabric.context_managers import lcd, cd
from fabric.decorators import task
from fabric.operations import local, put, run
from fabric.state import env

KEY_PATH_ENV = 'HEROKU_KEY'
env.hosts = ['vk-aws']
env.use_ssh_config = True
base_path = '/usr/run/vk-fetch/api'


class Stashed(object):
    def __init__(self):
        super(Stashed, self).__init__()
        self.stashed = False

    def __enter__(self):
        with settings(warn_only=True):
            result = local('git diff-index --quiet HEAD --')
            if result.return_code == 0:
                self.stashed = False
            else:
                self.stashed = True
                local('git stash')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stashed:
            local('git stash pop')


@task()
def pysetup(args=None):
    command = 'fab pysetup'
    if args is not None:
        command += ':{args}'.format(args=args)
    with lcd('./vk_fetch'):
        local(command)


@task()
def runserver():
    with lcd('./vk_fetch'):
        local('fab runserver')


@task()
def start(mode='release'):
    with lcd('vk_fetch'):
        if mode == 'release':
            local('gunicorn settings.wsgi --bind 0.0.0.0:$PORT')
        else:
            local('./pyenv.sh gunicorn settings.wsgi --bind 0.0.0.0:$PORT')


def checkout(branch, remote='origin'):
    with settings(warn_only=True):
        res = local('git rev-parse --verify {branch}'.format(branch=branch))
        branch_exists = res.succeeded
        if branch_exists:
            local('git checkout {branch} && git pull {remote} {branch}'.format(branch=branch, remote=remote))
        else:
            local('git checkout -b {branch} origin/{branch}'.format(branch=branch))


def git_current_branch():
    return local('git rev-parse --abbrev-ref HEAD', capture=True)


@task()
def release_develop():
    start_branch = git_current_branch()
    with Stashed():
        checkout('release')

        local('git fetch origin')
        local('git merge --log --no-edit origin/develop')
        local('git push --set-upstream origin release')

        checkout(start_branch)


@task()
def vk(command):
    with lcd('vk_fetch'):
        local('fab {command}'.format(command=command))


# ALIASES
@task()
def rdb():
    local('fab vk:rdb')


@task()
def migrate():
    local('fab vk:migrate')


@task()
def start_fetching():
    local('fab vk:"manage:start_fetching"')


@task()
def collectstatic():
    local('fab vk:"manage:\'collectstatic --noinput\'"')


@task()
def salt_update():
    salt_pack = 'dist/salt.tgz'
    local('tar -C saltstack/base -czf {salt_pack} salt'.format(salt_pack=salt_pack))
    put(salt_pack, '/tmp/salt.tgz')
    run('sudo rm -rf /srv/salt && sudo mkdir /srv/salt')
    run('sudo tar zxf /tmp/salt.tgz -C /srv')
    run('rm -rf /tmp/salt.tgz')
    run('sudo salt-call --local state.highstate')


@task()
def pack():
    local('rm -rf dist/src.tgz')
    local('tar -C vk_fetch -czf dist/src.tgz --exclude=env .')


@task()
def upload_src(version):
    put('dist/src.tgz', '/tmp/src.tgz')
    current_path = '{base_path}/releases/{current}'.format(base_path=base_path, current=version)
    run('mkdir -p {path}'.format(path=current_path))
    run('tar zxf /tmp/src.tgz -C {path}'.format(path=current_path))
    run('rm -rf /tmp/src.tgz')
    with cd(current_path):
        run('sudo supervisorctl stop celery-workers')
        run('./pysetup.sh')
        run('./pyenv.sh ./manage.py migrate --run-syncdb')
        run('./pyenv.sh ./manage.py collectstatic --noinput')
        run('./pyenv.sh fab msgc')


def move_link(version):
    current_path = '{base_path}/releases/{current}'.format(base_path=base_path, current=version)
    current_link = '{base_path}/current'.format(base_path=base_path, current=version)
    run('sudo supervisorctl stop all')
    run('rm -f {current_link}'.format(current_link=current_link))
    run('ln -s {current_path} {current_link}'.format(current_path=current_path, current_link=current_link))
    run('sudo supervisorctl reread; sudo supervisorctl update; sudo supervisorctl start all')


@task()
def deploy_src(version=None):
    version = version or datetime.now().strftime('%Y-%m-%d_%H-%M')
    pack()
    upload_src(version)
    move_link(version)


@task()
def deploy(version=None):
    salt_update()
    deploy_src(version)
